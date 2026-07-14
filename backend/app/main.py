"""
FastAPI 应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.models.database import init_db
from app.api import chat, knowledge, files


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("正在初始化数据库...")
    await init_db()
    logger.info("数据库初始化完成")
    
    yield
    
    # 关闭时执行
    logger.info("应用正在关闭...")


# 创建 FastAPI 应用
app = FastAPI(
    title="知识库聊天机器人 API",
    description="基于 RAG 的知识库聊天机器人系统",
    version="0.1.0",
    lifespan=lifespan
)


# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # 前端开发服务器
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 注册路由
app.include_router(chat.router, prefix="/api/chat", tags=["聊天"])
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["知识库"])
app.include_router(files.router, prefix="/api/files", tags=["文件"])


@app.get("/")
async def root():
    """根路由"""
    return {
        "message": "知识库聊天机器人 API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "knowledge-base-chatbot"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True
    )
