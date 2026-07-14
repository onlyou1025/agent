/**
 * 知识库管理页面
 */
import { useState, useEffect } from 'react';
import { Card, Button, Modal, Form, Input, message as antMessage, List, Tag, Space, Popconfirm, Empty } from 'antd';
import { PlusOutlined, DeleteOutlined, EditOutlined, DatabaseOutlined } from '@ant-design/icons';
import { knowledgeApi } from '../services/api';
import type { KnowledgeBase } from '../types';
import dayjs from 'dayjs';

function KnowledgePage() {
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingKb, setEditingKb] = useState<KnowledgeBase | null>(null);
  const [form] = Form.useForm();

  // 加载知识库列表
  useEffect(() => {
    loadKnowledgeBases();
  }, []);

  const loadKnowledgeBases = async () => {
    setLoading(true);
    try {
      const kbs = await knowledgeApi.list();
      setKnowledgeBases(kbs);
    } catch (error) {
      console.error('加载知识库列表失败:', error);
      antMessage.error('加载知识库列表失败');
    } finally {
      setLoading(false);
    }
  };

  // 创建知识库
  const handleCreate = () => {
    setEditingKb(null);
    form.resetFields();
    setModalVisible(true);
  };

  // 编辑知识库
  const handleEdit = (kb: KnowledgeBase) => {
    setEditingKb(kb);
    form.setFieldsValue({
      name: kb.name,
      description: kb.description
    });
    setModalVisible(true);
  };

  // 删除知识库
  const handleDelete = async (id: number, name: string) => {
    try {
      await knowledgeApi.delete(id);
      antMessage.success(`知识库 "${name}" 已删除`);
      await loadKnowledgeBases();
    } catch (error) {
      console.error('删除失败:', error);
      antMessage.error('删除失败');
    }
  };

  // 提交表单
  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      
      if (editingKb) {
        // 编辑模式（目前 API 不支持编辑，暂时只显示成功消息）
        antMessage.info('编辑功能暂未实现');
      } else {
        // 创建模式
        await knowledgeApi.create(values.name, values.description);
        antMessage.success('知识库创建成功');
      }
      
      setModalVisible(false);
      form.resetFields();
      await loadKnowledgeBases();
    } catch (error: any) {
      if (error.errorFields) {
        // 表单验证错误
        return;
      }
      console.error('提交失败:', error);
      antMessage.error(error.response?.data?.detail || '操作失败');
    }
  };

  return (
    <div>
      <Card
        title={
          <Space>
            <DatabaseOutlined />
            <span>知识库列表</span>
          </Space>
        }
        extra={
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            创建知识库
          </Button>
        }
      >
        {loading ? (
          <div style={{ textAlign: 'center', padding: 40 }}>加载中...</div>
        ) : knowledgeBases.length === 0 ? (
          <Empty description="暂无知识库，请创建一个" />
        ) : (
          <List
            grid={{ gutter: 16, xs: 1, sm: 2, md: 3, lg: 3, xl: 4, xxl: 4 }}
            dataSource={knowledgeBases}
            renderItem={(kb) => (
              <List.Item>
                <Card
                  title={kb.name}
                  actions={[
                    <Button
                      type="text"
                      icon={<EditOutlined />}
                      onClick={() => handleEdit(kb)}
                    >
                      编辑
                    </Button>,
                    <Popconfirm
                      title="确认删除"
                      description={`确定要删除知识库 "${kb.name}" 吗？这将删除所有相关文档和向量数据。`}
                      onConfirm={() => handleDelete(kb.id, kb.name)}
                      okText="确定"
                      cancelText="取消"
                    >
                      <Button type="text" danger icon={<DeleteOutlined />}>
                        删除
                      </Button>
                    </Popconfirm>
                  ]}
                >
                  <div style={{ marginBottom: 12 }}>
                    <Tag color="blue">{kb.document_count} 个文档</Tag>
                  </div>
                  {kb.description && (
                    <div style={{ color: '#666', marginBottom: 12 }}>
                      {kb.description}
                    </div>
                  )}
                  <div style={{ fontSize: 12, color: '#999' }}>
                    创建于 {dayjs(kb.created_at).format('YYYY-MM-DD HH:mm')}
                  </div>
                </Card>
              </List.Item>
            )}
          />
        )}
      </Card>

      {/* 创建/编辑对话框 */}
      <Modal
        title={editingKb ? '编辑知识库' : '创建知识库'}
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => {
          setModalVisible(false);
          form.resetFields();
        }}
        okText="确定"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="name"
            label="知识库名称"
            rules={[
              { required: true, message: '请输入知识库名称' },
              { max: 100, message: '名称不能超过100个字符' }
            ]}
          >
            <Input placeholder="例如：产品文档、技术手册" />
          </Form.Item>
          <Form.Item
            name="description"
            label="描述"
          >
            <Input.TextArea
              rows={3}
              placeholder="简要描述知识库的用途和内容"
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

export default KnowledgePage;
