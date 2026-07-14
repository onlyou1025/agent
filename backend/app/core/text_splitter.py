"""
文本分块模块
将长文档分割成适合向量化的文本块
"""
import logging
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings

logger = logging.getLogger(__name__)


class TextSplitter:
    """文本分块器"""
    
    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None
    ):
        """
        初始化文本分块器
        
        Args:
            chunk_size: 每个文本块的最大字符数
            chunk_overlap: 文本块之间的重叠字符数
        """
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", "。", ".", " ", ""]
        )
        
        logger.info(f"文本分块器初始化完成: chunk_size={self.chunk_size}, overlap={self.chunk_overlap}")
    
    def split_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        将文本分割成多个文本块
        
        Args:
            text: 待分割的文本
            metadata: 元数据（如文件名、页码等）
            
        Returns:
            文本块列表，每个块包含内容和元数据
        """
        if not text or not text.strip():
            logger.warning("输入文本为空，跳过分块")
            return []
        
        try:
            # 分割文本
            chunks = self.splitter.split_text(text)
            
            # 构建结果
            result = []
            metadata = metadata or {}
            
            for idx, chunk in enumerate(chunks):
                chunk_data = {
                    "content": chunk.strip(),
                    "metadata": {
                        **metadata,
                        "chunk_index": idx,
                        "total_chunks": len(chunks)
                    }
                }
                result.append(chunk_data)
            
            logger.info(f"文本分块完成: 生成了 {len(result)} 个文本块")
            return result
            
        except Exception as e:
            logger.error(f"文本分块失败: {str(e)}")
            return []
    
    def split_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        批量分割多个文档
        
        Args:
            documents: 文档列表，每个文档包含 content 和 metadata
            
        Returns:
            所有文本块的列表
        """
        all_chunks = []
        
        for doc in documents:
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})
            
            chunks = self.split_text(content, metadata)
            all_chunks.extend(chunks)
        
        logger.info(f"批量分块完成: 处理了 {len(documents)} 个文档，生成了 {len(all_chunks)} 个文本块")
        return all_chunks
