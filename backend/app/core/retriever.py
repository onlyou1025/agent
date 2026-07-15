"""
检索器模块
根据用户问题检索相关知识库内容
"""
import logging
from typing import List, Dict, Any, Optional

from app.core.vector_store import get_vector_store

logger = logging.getLogger(__name__)


class Retriever:
    """知识库检索器"""
    
    def __init__(self, n_results: int = 3):
        """
        初始化检索器
        
        Args:
            n_results: 返回的相似文档数量
        """
        self.n_results = n_results
        self.vector_store = get_vector_store()
        logger.info(f"检索器初始化完成，返回 top-{n_results} 结果")
    
    def retrieve(
        self,
        query: str,
        knowledge_base_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        检索与查询相关的知识库内容
        
        Args:
            query: 用户查询
            knowledge_base_id: 知识库 ID（可选）
            
        Returns:
            检索结果列表
        """
        if not query or not query.strip():
            logger.warning("查询为空，跳过检索")
            return []
        
        try:
            logger.info(f"开始检索: query='{query[:50]}...', kb_id={knowledge_base_id}")
            
            # 执行向量搜索
            results = self.vector_store.search(
                query=query,
                knowledge_base_id=knowledge_base_id,
                n_results=self.n_results
            )
            
            if not results:
                logger.info("未找到相关内容")
                return []
            
            # 格式化结果
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "content": result["content"],
                    "source": result["metadata"].get("filename", "未知来源"),
                    "score": result["score"],
                    "metadata": result["metadata"]
                })
            
            logger.info(f"检索完成，找到 {len(formatted_results)} 个相关结果")
            return formatted_results
            
        except Exception as e:
            logger.error(f"检索失败: {str(e)}")
            return []
    
    def format_context(self, retrieval_results: List[Dict[str, Any]]) -> str:
        """
        将检索结果格式化为上下文文本

        Args:
            retrieval_results: 检索结果列表

        Returns:
            格式化后的上下文文本
        """
        if not retrieval_results:
            return ""

        context_parts = []
        seen_sources = set()
        source_idx = 1

        for result in retrieval_results:
            content = result["content"]
            source = result["source"]

            # 对来源进行去重
            if source not in seen_sources:
                seen_sources.add(source)
                context_parts.append(f"[{source_idx}] 来源: {source}\n{content}")
                source_idx += 1
            else:
                # 如果来源已存在，只添加内容
                context_parts.append(content)

        return "\n\n".join(context_parts)


# 全局检索器实例
_retriever_instance = None


def get_retriever(n_results: int = 3) -> Retriever:
    """获取检索器单例"""
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = Retriever(n_results=n_results)
    return _retriever_instance
