"""
聊天 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import json
import logging

from app.models.database import get_db, ChatMessage
from app.models.schemas import (
    ChatMessageCreate,
    ChatMessageResponse,
    ChatHistoryResponse,
    SourceReference,
    MessageResponse
)
from app.core.retriever import get_retriever
from app.core.llm_service import get_llm_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("", response_model=ChatMessageResponse)
async def send_message(
    chat_data: ChatMessageCreate,
    db: AsyncSession = Depends(get_db)
):
    """发送消息并获取回答"""
    try:
        # 保存用户消息
        user_message = ChatMessage(
            session_id=chat_data.session_id,
            role="user",
            content=chat_data.message
        )
        db.add(user_message)
        await db.commit()
        await db.refresh(user_message)
        
        # 检索相关知识
        retriever = get_retriever(n_results=3)
        retrieval_results = retriever.retrieve(
            query=chat_data.message,
            knowledge_base_id=chat_data.knowledge_base_id
        )
        
        # 格式化上下文
        context = retriever.format_context(retrieval_results)
        
        # 获取聊天历史
        history_result = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == chat_data.session_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(10)
        )
        history_messages = history_result.scalars().all()
        
        chat_history = [
            {"role": msg.role, "content": msg.content}
            for msg in reversed(history_messages)
        ]
        
        # 构建 Prompt 并生成回答
        llm_service = get_llm_service()
        prompt = llm_service.build_prompt(
            question=chat_data.message,
            context=context,
            chat_history=chat_history
        )
        
        # 生成回答
        answer = await llm_service.generate(prompt)
        
        # 构建引用来源（去重）
        sources = []
        seen_sources = set()
        for result in retrieval_results:
            source_name = result["source"]
            if source_name not in seen_sources:
                seen_sources.add(source_name)
                sources.append(
                    SourceReference(
                        content=result["content"][:200] + "..." if len(result["content"]) > 200 else result["content"],
                        source=source_name,
                        score=result["score"]
                    )
                )
        
        # 保存助手回答
        assistant_message = ChatMessage(
            session_id=chat_data.session_id,
            role="assistant",
            content=answer,
            sources=json.dumps([s.model_dump() for s in sources]) if sources else None
        )
        db.add(assistant_message)
        await db.commit()
        await db.refresh(assistant_message)
        
        logger.info(f"聊天完成: session_id={chat_data.session_id}")
        
        return ChatMessageResponse(
            id=assistant_message.id,
            session_id=assistant_message.session_id,
            role=assistant_message.role,
            content=assistant_message.content,
            sources=sources if sources else None,
            created_at=assistant_message.created_at
        )
        
    except Exception as e:
        logger.error(f"发送消息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"发送失败: {str(e)}")


@router.get("/history/{session_id}", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取聊天历史"""
    try:
        # 查询聊天历史
        result = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
        )
        messages = result.scalars().all()
        
        message_list = []
        for msg in messages:
            # 解析引用来源
            sources = None
            if msg.sources:
                try:
                    sources_data = json.loads(msg.sources)
                    sources = [SourceReference(**s) for s in sources_data]
                except Exception as e:
                    logger.warning(f"解析引用来源失败: {str(e)}")
            
            message_list.append(ChatMessageResponse(
                id=msg.id,
                session_id=msg.session_id,
                role=msg.role,
                content=msg.content,
                sources=sources,
                created_at=msg.created_at
            ))
        
        return ChatHistoryResponse(
            session_id=session_id,
            messages=message_list,
            total=len(message_list)
        )
        
    except Exception as e:
        logger.error(f"获取聊天历史失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@router.delete("/history/{session_id}", response_model=MessageResponse)
async def clear_chat_history(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """清空聊天历史"""
    try:
        # 查询所有相关消息
        result = await db.execute(
            select(ChatMessage).where(ChatMessage.session_id == session_id)
        )
        messages = result.scalars().all()
        
        # 删除所有消息
        for msg in messages:
            await db.delete(msg)
        
        await db.commit()
        
        logger.info(f"清空聊天历史: session_id={session_id}, 删除 {len(messages)} 条消息")
        
        return MessageResponse(
            message=f"已清空 {len(messages)} 条聊天记录",
            success=True
        )
        
    except Exception as e:
        logger.error(f"清空聊天历史失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"清空失败: {str(e)}")


@router.get("/sessions", response_model=List[str])
async def list_chat_sessions(
    db: AsyncSession = Depends(get_db)
):
    """获取所有聊天会话 ID"""
    try:
        # 查询所有不同的 session_id
        result = await db.execute(
            select(ChatMessage.session_id).distinct()
        )
        session_ids = [row[0] for row in result.fetchall()]
        
        return session_ids
        
    except Exception as e:
        logger.error(f"获取聊天会话列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")
