/**
 * API 服务层
 */
import axios from 'axios';
import type {
  KnowledgeBase,
  Document,
  ChatMessage,
  ChatHistory
} from '../types';

const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 知识库相关 API
export const knowledgeApi = {
  // 创建知识库
  create: async (name: string, description?: string): Promise<KnowledgeBase> => {
    const response = await api.post('/knowledge', { name, description });
    return response.data;
  },

  // 获取知识库列表
  list: async (): Promise<KnowledgeBase[]> => {
    const response = await api.get('/knowledge');
    return response.data.knowledge_bases;
  },

  // 获取知识库详情
  get: async (id: number): Promise<KnowledgeBase> => {
    const response = await api.get(`/knowledge/${id}`);
    return response.data;
  },

  // 删除知识库
  delete: async (id: number): Promise<void> => {
    await api.delete(`/knowledge/${id}`);
  },

  // 获取知识库文档列表
  listDocuments: async (kbId: number): Promise<Document[]> => {
    const response = await api.get(`/knowledge/${kbId}/documents`);
    return response.data.documents;
  }
};

// 文件相关 API
export const fileApi = {
  // 上传文件
  upload: async (kbId: number, file: File): Promise<Document> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post(`/files/upload/${kbId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  },

  // 删除文件
  delete: async (documentId: number): Promise<void> => {
    await api.delete(`/files/${documentId}`);
  }
};

// 聊天相关 API
export const chatApi = {
  // 发送消息
  send: async (
    sessionId: string,
    message: string,
    knowledgeBaseId?: number
  ): Promise<ChatMessage> => {
    const response = await api.post('/chat', {
      session_id: sessionId,
      message,
      knowledge_base_id: knowledgeBaseId
    });
    return response.data;
  },

  // 获取聊天历史
  getHistory: async (sessionId: string): Promise<ChatHistory> => {
    const response = await api.get(`/chat/history/${sessionId}`);
    return response.data;
  },

  // 清空聊天历史
  clearHistory: async (sessionId: string): Promise<void> => {
    await api.delete(`/chat/history/${sessionId}`);
  },

  // 获取所有会话 ID
  listSessions: async (): Promise<string[]> => {
    const response = await api.get('/chat/sessions');
    return response.data;
  }
};

export default api;
