"""
大模型服务模块
与 Ollama 服务交互，生成回答
"""
import logging
from typing import List, Dict, Any, Optional, AsyncGenerator
import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """大模型服务"""
    
    def __init__(self):
        """初始化 LLM 服务"""
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
        logger.info(f"LLM 服务初始化完成: model={self.model}, url={self.base_url}")
    
    def build_prompt(
        self,
        question: str,
        context: str,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        构建 RAG Prompt
        
        Args:
            question: 用户问题
            context: 检索到的知识库上下文
            chat_history: 聊天历史（可选）
            
        Returns:
            构建好的 Prompt
        """
        system_prompt = """你是一个智能助手，基于提供的知识库内容回答用户问题。请遵循以下原则：

1. 如果知识库中有相关信息，请基于知识库内容给出准确、详细的回答
2. 如果知识库中没有相关信息，请明确告知用户"根据现有知识库，我找不到相关信息"
3. 回答时请引用来源，让用户知道信息的出处
4. 保持回答简洁、有条理
5. 不要编造知识库中不存在的信息"""

        prompt_parts = [system_prompt]
        
        # 添加聊天历史
        if chat_history:
            prompt_parts.append("\n\n对话历史：")
            for msg in chat_history[-5:]:  # 只保留最近 5 轮对话
                role = "用户" if msg["role"] == "user" else "助手"
                prompt_parts.append(f"{role}: {msg['content']}")
        
        # 添加知识库上下文
        if context:
            prompt_parts.append(f"\n\n知识库内容：\n{context}")
        
        # 添加用户问题
        prompt_parts.append(f"\n\n用户问题：{question}")
        prompt_parts.append("\n\n请基于以上知识库内容回答用户问题：")
        
        return "\n".join(prompt_parts)
    
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        生成回答（非流式）
        
        Args:
            prompt: 完整的 Prompt
            temperature: 温度参数，控制生成的随机性
            max_tokens: 最大生成 token 数
            
        Returns:
            生成的回答文本
        """
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": temperature,
                            "num_predict": max_tokens
                        }
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    generated_text = result.get("response", "")
                    logger.info(f"生成完成，长度: {len(generated_text)}")
                    return generated_text
                else:
                    logger.error(f"Ollama API 错误: {response.status_code} - {response.text}")
                    return f"生成失败: {response.status_code}"
                    
        except httpx.TimeoutException:
            logger.error("Ollama 请求超时")
            return "抱歉，生成回答超时，请稍后重试。"
        except Exception as e:
            logger.error(f"生成失败: {str(e)}")
            return f"生成失败: {str(e)}"
    
    async def generate_stream(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> AsyncGenerator[str, None]:
        """
        生成回答（流式）
        
        Args:
            prompt: 完整的 Prompt
            temperature: 温度参数
            max_tokens: 最大生成 token 数
            
        Yields:
            生成的文本片段
        """
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": True,
                        "options": {
                            "temperature": temperature,
                            "num_predict": max_tokens
                        }
                    }
                ) as response:
                    if response.status_code == 200:
                        async for line in response.aiter_lines():
                            if line:
                                import json
                                try:
                                    data = json.loads(line)
                                    if "response" in data:
                                        yield data["response"]
                                except json.JSONDecodeError:
                                    continue
                    else:
                        logger.error(f"流式生成失败: {response.status_code}")
                        yield f"生成失败: {response.status_code}"
                        
        except Exception as e:
            logger.error(f"流式生成失败: {str(e)}")
            yield f"生成失败: {str(e)}"
    
    async def check_health(self) -> bool:
        """
        检查 Ollama 服务是否可用
        
        Returns:
            服务是否健康
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama 健康检查失败: {str(e)}")
            return False


# 全局 LLM 服务实例
_llm_service_instance = None


def get_llm_service() -> LLMService:
    """获取 LLM 服务单例"""
    global _llm_service_instance
    if _llm_service_instance is None:
        _llm_service_instance = LLMService()
    return _llm_service_instance
