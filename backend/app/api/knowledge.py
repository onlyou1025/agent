"""
知识库管理 API
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
import logging
import json

from app.models.database import get_db, KnowledgeBase, Document
from app.models.schemas import (
    KnowledgeBaseCreate,
    KnowledgeBaseResponse,
    KnowledgeBaseList,
    DocumentResponse,
    DocumentList,
    MessageResponse,
    ErrorResponse
)
from app.core.vector_store import get_vector_store

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("", response_model=KnowledgeBaseResponse)
async def create_knowledge_base(
    kb_data: KnowledgeBaseCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建新知识库"""
    try:
        # 创建知识库
        new_kb = KnowledgeBase(
            name=kb_data.name,
            description=kb_data.description
        )
        db.add(new_kb)
        await db.commit()
        await db.refresh(new_kb)
        
        logger.info(f"创建知识库成功: id={new_kb.id}, name={new_kb.name}")
        
        return KnowledgeBaseResponse(
            id=new_kb.id,
            name=new_kb.name,
            description=new_kb.description,
            created_at=new_kb.created_at,
            updated_at=new_kb.updated_at,
            document_count=0
        )
        
    except Exception as e:
        logger.error(f"创建知识库失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建失败: {str(e)}")


@router.get("", response_model=KnowledgeBaseList)
async def list_knowledge_bases(
    db: AsyncSession = Depends(get_db)
):
    """获取知识库列表"""
    try:
        # 查询所有知识库
        result = await db.execute(select(KnowledgeBase))
        knowledge_bases = result.scalars().all()
        
        # 构建响应列表
        kb_list = []
        for kb in knowledge_bases:
            # 查询每个知识库的文档数量
            doc_count_result = await db.execute(
                select(func.count(Document.id)).where(Document.knowledge_base_id == kb.id)
            )
            doc_count = doc_count_result.scalar() or 0
            
            kb_list.append(KnowledgeBaseResponse(
                id=kb.id,
                name=kb.name,
                description=kb.description,
                created_at=kb.created_at,
                updated_at=kb.updated_at,
                document_count=doc_count
            ))
        
        return KnowledgeBaseList(
            knowledge_bases=kb_list,
            total=len(kb_list)
        )
        
    except Exception as e:
        logger.error(f"获取知识库列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@router.get("/{kb_id}", response_model=KnowledgeBaseResponse)
async def get_knowledge_base(
    kb_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取知识库详情"""
    try:
        # 查询知识库
        result = await db.execute(
            select(KnowledgeBase).where(KnowledgeBase.id == kb_id)
        )
        kb = result.scalar_one_or_none()
        
        if not kb:
            raise HTTPException(status_code=404, detail="知识库不存在")
        
        # 查询文档数量
        doc_count_result = await db.execute(
            select(func.count(Document.id)).where(Document.knowledge_base_id == kb_id)
        )
        doc_count = doc_count_result.scalar() or 0
        
        return KnowledgeBaseResponse(
            id=kb.id,
            name=kb.name,
            description=kb.description,
            created_at=kb.created_at,
            updated_at=kb.updated_at,
            document_count=doc_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取知识库详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@router.delete("/{kb_id}", response_model=MessageResponse)
async def delete_knowledge_base(
    kb_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除知识库及其所有文档"""
    try:
        # 查询知识库
        result = await db.execute(
            select(KnowledgeBase).where(KnowledgeBase.id == kb_id)
        )
        kb = result.scalar_one_or_none()
        
        if not kb:
            raise HTTPException(status_code=404, detail="知识库不存在")
        
        # 删除向量数据库中的相关数据
        vector_store = get_vector_store()
        vector_store.delete_by_knowledge_base(kb_id)
        
        # 删除知识库（级联删除文档）
        await db.delete(kb)
        await db.commit()
        
        logger.info(f"删除知识库成功: id={kb_id}")
        
        return MessageResponse(
            message=f"知识库 '{kb.name}' 已成功删除",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除知识库失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.get("/{kb_id}/documents", response_model=DocumentList)
async def list_documents(
    kb_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取知识库的文档列表"""
    try:
        # 检查知识库是否存在
        result = await db.execute(
            select(KnowledgeBase).where(KnowledgeBase.id == kb_id)
        )
        kb = result.scalar_one_or_none()
        
        if not kb:
            raise HTTPException(status_code=404, detail="知识库不存在")
        
        # 查询文档列表
        result = await db.execute(
            select(Document).where(Document.knowledge_base_id == kb_id)
        )
        documents = result.scalars().all()
        
        doc_list = [
            DocumentResponse(
                id=doc.id,
                knowledge_base_id=doc.knowledge_base_id,
                filename=doc.filename,
                file_type=doc.file_type,
                file_size=doc.file_size,
                status=doc.status,
                created_at=doc.created_at
            )
            for doc in documents
        ]
        
        return DocumentList(
            documents=doc_list,
            total=len(doc_list)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取文档列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")
