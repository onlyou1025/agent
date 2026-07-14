/**
 * 聊天页面
 */
import { useState, useEffect, useRef } from 'react';
import { Input, Button, Card, List, Typography, Tag, Space, Empty, Spin, message as antMessage } from 'antd';
import { SendOutlined, ClearOutlined, RobotOutlined, UserOutlined } from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import { chatApi, knowledgeApi } from '../services/api';
import type { ChatMessage, KnowledgeBase } from '../types';
import dayjs from 'dayjs';

const { Text } = Typography;
const { TextArea } = Input;

function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId] = useState(() => `session_${Date.now()}`);
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([]);
  const [selectedKbId, setSelectedKbId] = useState<number | undefined>();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 加载知识库列表
  useEffect(() => {
    const loadKnowledgeBases = async () => {
      try {
        const kbs = await knowledgeApi.list();
        setKnowledgeBases(kbs);
        if (kbs.length > 0) {
          setSelectedKbId(kbs[0].id);
        }
      } catch (error) {
        console.error('加载知识库列表失败:', error);
      }
    };
    loadKnowledgeBases();
  }, []);

  // 加载聊天历史
  useEffect(() => {
    const loadHistory = async () => {
      try {
        const history = await chatApi.getHistory(sessionId);
        setMessages(history.messages);
      } catch (error) {
        console.error('加载聊天历史失败:', error);
      }
    };
    loadHistory();
  }, [sessionId]);

  // 滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 发送消息
  const handleSend = async () => {
    if (!inputMessage.trim()) {
      antMessage.warning('请输入消息');
      return;
    }

    if (!selectedKbId) {
      antMessage.warning('请先选择知识库');
      return;
    }

    const userMessage = inputMessage.trim();
    setInputMessage('');
    setLoading(true);

    // 添加用户消息到列表
    const tempUserMsg: ChatMessage = {
      id: Date.now(),
      session_id: sessionId,
      role: 'user',
      content: userMessage,
      created_at: new Date().toISOString()
    };
    setMessages(prev => [...prev, tempUserMsg]);

    try {
      // 发送消息到后端
      const response = await chatApi.send(sessionId, userMessage, selectedKbId);
      setMessages(prev => [...prev, response]);
    } catch (error: any) {
      console.error('发送消息失败:', error);
      antMessage.error('发送消息失败，请重试');
      
      // 添加错误消息
      const errorMsg: ChatMessage = {
        id: Date.now() + 1,
        session_id: sessionId,
        role: 'assistant',
        content: '抱歉，处理您的请求时出现错误，请稍后重试。',
        created_at: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  // 清空聊天
  const handleClear = async () => {
    try {
      await chatApi.clearHistory(sessionId);
      setMessages([]);
      antMessage.success('聊天已清空');
    } catch (error) {
      console.error('清空聊天失败:', error);
      antMessage.error('清空失败');
    }
  };

  // 按 Enter 发送
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 150px)' }}>
      {/* 知识库选择 */}
      <Card size="small" style={{ marginBottom: 16 }}>
        <Space>
          <Text strong>选择知识库：</Text>
          <select
            value={selectedKbId || ''}
            onChange={(e) => setSelectedKbId(e.target.value ? Number(e.target.value) : undefined)}
            style={{ padding: '4px 8px', borderRadius: 4, border: '1px solid #d9d9d9' }}
          >
            <option value="">请选择知识库</option>
            {knowledgeBases.map(kb => (
              <option key={kb.id} value={kb.id}>
                {kb.name} ({kb.document_count} 个文档)
              </option>
            ))}
          </select>
        </Space>
      </Card>

      {/* 消息列表 */}
      <div style={{ flex: 1, overflowY: 'auto', marginBottom: 16, padding: 16, background: '#fafafa', borderRadius: 8 }}>
        {messages.length === 0 ? (
          <Empty description="开始对话吧" />
        ) : (
          <List
            dataSource={messages}
            renderItem={(msg) => (
              <div
                key={msg.id}
                style={{
                  display: 'flex',
                  justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                  marginBottom: 16
                }}
              >
                <div
                  style={{
                    maxWidth: '70%',
                    padding: '12px 16px',
                    borderRadius: 8,
                    background: msg.role === 'user' ? '#1890ff' : '#fff',
                    color: msg.role === 'user' ? '#fff' : '#000',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                  }}
                >
                  <div style={{ marginBottom: 8 }}>
                    <Tag color={msg.role === 'user' ? 'blue' : 'green'} icon={msg.role === 'user' ? <UserOutlined /> : <RobotOutlined />}>
                      {msg.role === 'user' ? '我' : '助手'}
                    </Tag>
                    <Text type="secondary" style={{ fontSize: 12, marginLeft: 8 }}>
                      {dayjs(msg.created_at).format('HH:mm:ss')}
                    </Text>
                  </div>
                  <div style={{ whiteSpace: 'pre-wrap' }}>
                    {msg.role === 'assistant' ? (
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                    ) : (
                      msg.content
                    )}
                  </div>
                  {msg.sources && msg.sources.length > 0 && (
                    <div style={{ marginTop: 12, paddingTop: 12, borderTop: '1px solid #f0f0f0' }}>
                      <Text type="secondary" style={{ fontSize: 12 }}>引用来源：</Text>
                      {msg.sources.map((source, idx) => (
                        <div key={idx} style={{ marginTop: 4, fontSize: 12 }}>
                          <Tag color="default">{source.source}</Tag>
                          <Text type="secondary" style={{ fontSize: 11 }}>
                            相似度: {(source.score * 100).toFixed(1)}%
                          </Text>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
          />
        )}
        {loading && (
          <div style={{ textAlign: 'center', padding: 16 }}>
            <Spin tip="正在思考..." />
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* 输入区域 */}
      <div style={{ display: 'flex', gap: 8 }}>
        <TextArea
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="输入您的问题... (按 Enter 发送，Shift + Enter 换行)"
          autoSize={{ minRows: 2, maxRows: 4 }}
          disabled={loading}
          style={{ flex: 1 }}
        />
        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={handleSend}
          loading={loading}
          disabled={!inputMessage.trim() || !selectedKbId}
          style={{ height: 'auto' }}
        >
          发送
        </Button>
        <Button
          icon={<ClearOutlined />}
          onClick={handleClear}
          disabled={loading || messages.length === 0}
          style={{ height: 'auto' }}
        >
          清空
        </Button>
      </div>
    </div>
  );
}

export default ChatPage;
