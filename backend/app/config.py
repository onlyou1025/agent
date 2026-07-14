"""
应用配置模块
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """应用配置"""
    
    # Ollama 配置
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama2"
    
    # 数据库配置
    database_url: str = "sqlite+aiosqlite:///./data/app.db"
    
    # ChromaDB 配置
    chroma_persist_dir: str = "./data/vector_db"
    chroma_collection: str = "knowledge_base"
    
    # Embedding 模型
    embedding_model: str = "all-MiniLM-L6-v2"
    
    # 文件上传配置
    upload_dir: str = "./data/uploads"
    max_file_size: int = 52428800  # 50MB
    
    # 应用配置
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    
    # 文本分块配置
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# 创建全局配置实例
settings = Settings()

# 确保必要的目录存在
os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(settings.chroma_persist_dir, exist_ok=True)
os.makedirs("./data", exist_ok=True)
