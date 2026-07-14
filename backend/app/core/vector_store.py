"""
向量存储模块
管理 ChromaDB 向量数据库
"""
import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from app.config import settings

logger = logging.getLogger(__name__)


class VectorStore:
    """向量存储管理器"""
    
    def __init__(self):
        """初始化向量存储"""
        # 初始化 ChromaDB 客户端（使用新的 API）
        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # 初始化 Embedding 模型
        logger.info(f"正在加载 Embedding 模型: {settings.embedding_model}")
        self.embedding_model = SentenceTransformer(settings.embedding_model)
        logger.info("Embedding 模型加载完成")
        
        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name=settings.chroma_collection,
            metadata={"description": "知识库向量集合"}
        )
        
        logger.info(f"向量存储初始化完成，集合: {settings.chroma_collection}")
    
    def add_documents(
        self,
        documents: List[Dict[str, Any]],
        knowledge_base_id: int
    ) -> bool:
        """
        添加文档到向量数据库
        
        Args:
            documents: 文档列表，每个文档包含 content 和 metadata
            knowledge_base_id: 知识库 ID
            
        Returns:
            是否成功
        """
        if not documents:
            logger.warning("文档列表为空，跳过添加")
            return False
        
        try:
            # 准备数据
            ids = []
            texts = []
            metadatas = []
            embeddings = []
            
            for idx, doc in enumerate(documents):
                content = doc.get("content", "")
                metadata = doc.get("metadata", {})
                
                if not content.strip():
                    continue
                
                # 生成唯一 ID
                doc_id = f"kb_{knowledge_base_id}_doc_{idx}_{hash(content) % 1000000}"
                ids.append(doc_id)
                texts.append(content)
                
                # 添加知识库 ID 到元数据
                metadata["knowledge_base_id"] = knowledge_base_id
                metadatas.append(metadata)
                
                # 生成向量
                embedding = self.embedding_model.encode(content).tolist()
                embeddings.append(embedding)
            
            if not ids:
                logger.warning("没有有效的文档可添加")
                return False
            
            # 添加到 ChromaDB
            self.collection.add(
                ids=ids,
                documents=texts,
                metadatas=metadatas,
                embeddings=embeddings
            )
            
            logger.info(f"成功添加 {len(ids)} 个文档到向量数据库")
            return True
            
        except Exception as e:
            logger.error(f"添加文档到向量数据库失败: {str(e)}")
            return False
    
    def search(
        self,
        query: str,
        knowledge_base_id: Optional[int] = None,
        n_results: int = 3
    ) -> List[Dict[str, Any]]:
        """
        搜索相似文档
        
        Args:
            query: 查询文本
            knowledge_base_id: 知识库 ID（可选，用于过滤）
            n_results: 返回结果数量
            
        Returns:
            相似文档列表
        """
        try:
            # 生成查询向量
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # 构建过滤条件
            where_filter = None
            if knowledge_base_id is not None:
                where_filter = {"knowledge_base_id": knowledge_base_id}
            
            # 执行搜索
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_filter,
                include=["documents", "metadatas", "distances"]
            )
            
            # 格式化结果
            formatted_results = []
            if results and results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    distance = results['distances'][0][i] if results['distances'] else 0
                    
                    # 将距离转换为相似度分数（ChromaDB 使用 L2 距离）
                    score = 1 / (1 + distance)
                    
                    formatted_results.append({
                        "content": doc,
                        "metadata": metadata,
                        "score": score,
                        "distance": distance
                    })
            
            logger.info(f"搜索完成，找到 {len(formatted_results)} 个相似文档")
            return formatted_results
            
        except Exception as e:
            logger.error(f"搜索失败: {str(e)}")
            return []
    
    def delete_by_knowledge_base(self, knowledge_base_id: int) -> bool:
        """
        删除指定知识库的所有文档
        
        Args:
            knowledge_base_id: 知识库 ID
            
        Returns:
            是否成功
        """
        try:
            # 查询所有相关文档
            results = self.collection.get(
                where={"knowledge_base_id": knowledge_base_id}
            )
            
            if results and results['ids']:
                self.collection.delete(ids=results['ids'])
                logger.info(f"成功删除知识库 {knowledge_base_id} 的 {len(results['ids'])} 个文档")
            
            return True
            
        except Exception as e:
            logger.error(f"删除知识库文档失败: {str(e)}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取向量数据库统计信息
        
        Returns:
            统计信息字典
        """
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": settings.chroma_collection
            }
        except Exception as e:
            logger.error(f"获取统计信息失败: {str(e)}")
            return {"total_documents": 0, "collection_name": settings.chroma_collection}


# 全局向量存储实例
_vector_store_instance = None


def get_vector_store() -> VectorStore:
    """获取向量存储单例"""
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = VectorStore()
    return _vector_store_instance
