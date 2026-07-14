"""
文件上传 API
"""
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import os
import uuid
import logging

from app.config import settings
from app.models.database import get_db, KnowledgeBase, Document
from app.models.schemas import DocumentResponse, MessageResponse
from app.core.document_parser import DocumentParser
from app.core.text_splitter import TextSplitter
from app.core.vector_store import get_vector_store

logger = logging.getLogger(__name__)

router = APIRouter()


async def process_document(document_id: int, file_path: str, file_type: str, knowledge_base_id: int):
    """
    后台任务：处理文档（解析、分块、向量化）
    
    Args:
        document_id: 文档 ID
        file_path: 文件路径
        file_type: 文件类型
        knowledge_base_id: 知识库 ID
    """
    from app.models.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        try:
            # 更新文档状态为处理中
            result = await db.execute(select(Document).where(Document.id == document_id))
            doc = result.scalar_one_or_none()
            
            if not doc:
                logger.error(f"文档不存在: id={document_id}")
                return
            
            doc.status = "processing"
            await db.commit()
            
            # 解析文档
            logger.info(f"开始解析文档: {doc.filename}")
            text_content = DocumentParser.parse(file_path, file_type)
            
            if not text_content:
                raise Exception("文档解析失败，无法提取文本内容")
            
            # 文本分块
            logger.info(f"开始文本分块: {doc.filename}")
            splitter = TextSplitter()
            chunks = splitter.split_text(
                text_content,
                metadata={
                    "filename": doc.filename,
                    "document_id": document_id,
                    "knowledge_base_id": knowledge_base_id
                }
            )
            
            if not chunks:
                raise Exception("文本分块失败")
            
            # 向量化并存储
            logger.info(f"开始向量化: {doc.filename}, 共 {len(chunks)} 个文本块")
            vector_store = get_vector_store()
            success = vector_store.add_documents(chunks, knowledge_base_id)
            
            if not success:
                raise Exception("向量化存储失败")
            
            # 更新文档状态为完成
            doc.status = "completed"
            await db.commit()
            
            logger.info(f"文档处理完成: {doc.filename}")
            
        except Exception as e:
            logger.error(f"文档处理失败: {str(e)}")
            
            # 更新文档状态为失败
            try:
                result = await db.execute(select(Document).where(Document.id == document_id))
                doc = result.scalar_one_or_none()
                if doc:
                    doc.status = "failed"
                    await db.commit()
            except Exception as db_error:
                logger.error(f"更新文档状态失败: {str(db_error)}")


@router.post("/upload/{kb_id}", response_model=DocumentResponse)
async def upload_file(
    kb_id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """上传文件到知识库"""
    try:
        # 检查知识库是否存在
        result = await db.execute(
            select(KnowledgeBase).where(KnowledgeBase.id == kb_id)
        )
        kb = result.scalar_one_or_none()
        
        if not kb:
            raise HTTPException(status_code=404, detail="知识库不存在")
        
        # 检查文件类型
        filename = file.filename or "unknown"
        file_type = DocumentParser.get_file_type(filename)
        
        if file_type not in ["pdf", "docx", "doc"]:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型: {file_type}，仅支持 PDF 和 Word 文档"
            )
        
        # 生成唯一文件名
        unique_filename = f"{uuid.uuid4()}.{file_type}"
        file_path = os.path.join(settings.upload_dir, unique_filename)
        
        # 保存文件
        with open(file_path, "wb") as f:
            content = await file.read()
            
            # 检查文件大小
            if len(content) > settings.max_file_size:
                os.remove(file_path)
                raise HTTPException(
                    status_code=413,
                    detail=f"文件大小超过限制: {settings.max_file_size / 1024 / 1024:.1f}MB"
                )
            
            f.write(content)
        
        logger.info(f"文件保存成功: {file_path}, 大小: {len(content)} bytes")
        
        # 创建文档记录
        new_doc = Document(
            knowledge_base_id=kb_id,
            filename=filename,
            file_path=file_path,
            file_type=file_type,
            file_size=len(content),
            status="pending"
        )
        db.add(new_doc)
        await db.commit()
        await db.refresh(new_doc)
        
        # 添加后台任务处理文档
        background_tasks.add_task(
            process_document,
            new_doc.id,
            file_path,
            file_type,
            kb_id
        )
        
        logger.info(f"文档上传成功: id={new_doc.id}, filename={filename}")
        
        return DocumentResponse(
            id=new_doc.id,
            knowledge_base_id=new_doc.knowledge_base_id,
            filename=new_doc.filename,
            file_type=new_doc.file_type,
            file_size=new_doc.file_size,
            status=new_doc.status,
            created_at=new_doc.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"上传文件失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.delete("/{document_id}", response_model=MessageResponse)
async def delete_file(
    document_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除文档"""
    try:
        # 查询文档
        result = await db.execute(
            select(Document).where(Document.id == document_id)
        )
        doc = result.scalar_one_or_none()
        
        if not doc:
            raise HTTPException(status_code=404, detail="文档不存在")
        
        # 删除物理文件
        if os.path.exists(doc.file_path):
            os.remove(doc.file_path)
            logger.info(f"删除物理文件: {doc.file_path}")
        
        # 删除数据库记录
        await db.delete(doc)
        await db.commit()
        
        logger.info(f"删除文档成功: id={document_id}")
        
        return MessageResponse(
            message=f"文档 '{doc.filename}' 已成功删除",
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除文档失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")
