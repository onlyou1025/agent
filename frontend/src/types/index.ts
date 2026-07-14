/**
 * 类型定义
 */

// 知识库相关类型
export interface KnowledgeBase {
  id: number;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
  document_count: number;
}

export interface Document {
  id: number;
  knowledge_base_id: number;
  filename: string;
  file_type: string;
  file_size?: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  created_at: string;
}

// 聊天相关类型
export interface SourceReference {
  content: string;
  source: string;
  score: number;
}

export interface ChatMessage {
  id: number;
  session_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  sources?: SourceReference[];
  created_at: string;
}

export interface ChatHistory {
  session_id: string;
  messages: ChatMessage[];
  total: number;
}

// API 响应类型
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface ErrorResponse {
  error: string;
  detail?: string;
  success: false;
}
