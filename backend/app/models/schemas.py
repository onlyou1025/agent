"""
Pydantic 数据模型，用于 API 请求和响应验证
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ============ 知识库相关模型 ============

class KnowledgeBaseCreate(BaseModel):
    """创建知识库请求模型"""
    name: str = Field(..., min_length=1, max_length=100, description="知识库名称")
    description: Optional[str] = Field(None, description="知识库描述")


class KnowledgeBaseResponse(BaseModel):
    """知识库响应模型"""
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    document_count: int = 0
    
    class Config:
        from_attributes = True


class KnowledgeBaseList(BaseModel):
    """知识库列表响应模型"""
    knowledge_bases: List[KnowledgeBaseResponse]
    total: int


# ============ 文档相关模型 ============

class DocumentResponse(BaseModel):
    """文档响应模型"""
    id: int
    knowledge_base_id: int
    filename: str
    file_type: str
    file_size: Optional[int]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class DocumentList(BaseModel):
    """文档列表响应模型"""
    documents: List[DocumentResponse]
    total: int


# ============ 聊天相关模型 ============

class ChatMessageCreate(BaseModel):
    """创建聊天消息请求模型"""
    session_id: str = Field(..., description="会话 ID")
    message: str = Field(..., min_length=1, description="用户消息")
    knowledge_base_id: Optional[int] = Field(None, description="知识库 ID，可选")


class SourceReference(BaseModel):
    """引用来源模型"""
    content: str = Field(..., description="引用内容")
    source: str = Field(..., description="来源文件名")
    score: float = Field(..., description="相似度分数")


class ChatMessageResponse(BaseModel):
    """聊天消息响应模型"""
    id: int
    session_id: str
    role: str
    content: str
    sources: Optional[List[SourceReference]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatHistoryResponse(BaseModel):
    """聊天历史响应模型"""
    session_id: str
    messages: List[ChatMessageResponse]
    total: int


# ============ 通用响应模型 ============

class MessageResponse(BaseModel):
    """通用消息响应"""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """错误响应模型"""
    error: str
    detail: Optional[str] = None
    success: bool = False
