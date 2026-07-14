/**
 * 上传页面
 */
import { useState, useEffect } from 'react';
import { Upload, Card, Select, message as antMessage, Progress, List, Tag, Button, Space } from 'antd';
import { InboxOutlined, FileOutlined, DeleteOutlined, CheckCircleOutlined, CloseCircleOutlined, LoadingOutlined } from '@ant-design/icons';
import { knowledgeApi, fileApi } from '../services/api';
import type { KnowledgeBase, Document } from '../types';
import type { UploadFile } from 'antd/es/upload/interface';
import dayjs from 'dayjs';

const { Dragger } = Upload;

function UploadPage() {
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([]);
  const [selectedKbId, setSelectedKbId] = useState<number | undefined>();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [uploading, setUploading] = useState(false);
  const [loadingDocs, setLoadingDocs] = useState(false);

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
        antMessage.error('加载知识库列表失败');
      }
    };
    loadKnowledgeBases();
  }, []);

  // 加载文档列表
  useEffect(() => {
    if (selectedKbId) {
      loadDocuments(selectedKbId);
    }
  }, [selectedKbId]);

  const loadDocuments = async (kbId: number) => {
    setLoadingDocs(true);
    try {
      const docs = await knowledgeApi.listDocuments(kbId);
      setDocuments(docs);
    } catch (error) {
      console.error('加载文档列表失败:', error);
      antMessage.error('加载文档列表失败');
    } finally {
      setLoadingDocs(false);
    }
  };

  // 上传文件
  const handleUpload = async (file: File) => {
    if (!selectedKbId) {
      antMessage.warning('请先选择知识库');
      return;
    }

    setUploading(true);
    try {
      await fileApi.upload(selectedKbId, file);
      antMessage.success(`${file.name} 上传成功，正在处理中...`);
      
      // 刷新文档列表
      await loadDocuments(selectedKbId);
      
      // 定时检查文档状态
      const checkInterval = setInterval(async () => {
        const docs = await knowledgeApi.listDocuments(selectedKbId);
        setDocuments(docs);
        
        const allCompleted = docs.every(doc => doc.status === 'completed' || doc.status === 'failed');
        if (allCompleted) {
          clearInterval(checkInterval);
          const successCount = docs.filter(doc => doc.status === 'completed').length;
          const failedCount = docs.filter(doc => doc.status === 'failed').length;
          
          if (failedCount > 0) {
            antMessage.warning(`${successCount} 个文档处理成功，${failedCount} 个失败`);
          } else {
            antMessage.success(`所有文档处理完成！`);
          }
        }
      }, 3000);
      
    } catch (error: any) {
      console.error('上传失败:', error);
      antMessage.error(error.response?.data?.detail || '上传失败');
    } finally {
      setUploading(false);
    }
  };

  // 删除文档
  const handleDelete = async (docId: number, filename: string) => {
    try {
      await fileApi.delete(docId);
      antMessage.success(`${filename} 已删除`);
      
      if (selectedKbId) {
        await loadDocuments(selectedKbId);
      }
    } catch (error) {
      console.error('删除失败:', error);
      antMessage.error('删除失败');
    }
  };

  // 获取状态标签
  const getStatusTag = (status: Document['status']) => {
    switch (status) {
      case 'pending':
        return <Tag icon={<FileOutlined />} color="default">等待处理</Tag>;
      case 'processing':
        return <Tag icon={<LoadingOutlined />} color="processing">处理中</Tag>;
      case 'completed':
        return <Tag icon={<CheckCircleOutlined />} color="success">已完成</Tag>;
      case 'failed':
        return <Tag icon={<CloseCircleOutlined />} color="error">失败</Tag>;
      default:
        return <Tag>{status}</Tag>;
    }
  };

  // 格式化文件大小
  const formatFileSize = (bytes?: number) => {
    if (!bytes) return '未知';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  return (
    <div style={{ display: 'flex', gap: 24 }}>
      {/* 左侧：上传区域 */}
      <div style={{ flex: 1 }}>
        <Card title="上传文档" style={{ marginBottom: 16 }}>
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            <div>
              <span style={{ marginRight: 8 }}>选择知识库：</span>
              <Select
                value={selectedKbId}
                onChange={setSelectedKbId}
                style={{ width: 300 }}
                placeholder="请选择知识库"
              >
                {knowledgeBases.map(kb => (
                  <Select.Option key={kb.id} value={kb.id}>
                    {kb.name} ({kb.document_count} 个文档)
                  </Select.Option>
                ))}
              </Select>
            </div>

            <Dragger
              accept=".pdf,.docx,.doc"
              multiple={true}
              showUploadList={false}
              beforeUpload={(file) => {
                handleUpload(file);
                return false;
              }}
              disabled={!selectedKbId || uploading}
            >
              <p className="ant-upload-drag-icon">
                <InboxOutlined />
              </p>
              <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
              <p className="ant-upload-hint">
                支持 PDF、Word 文档（.pdf, .docx, .doc），可批量上传
              </p>
            </Dragger>

            {uploading && <Progress percent={100} status="active" />}
          </Space>
        </Card>
      </div>

      {/* 右侧：文档列表 */}
      <div style={{ flex: 1 }}>
        <Card
          title={`文档列表 (${documents.length})`}
          extra={
            selectedKbId && (
              <Button onClick={() => loadDocuments(selectedKbId)} loading={loadingDocs}>
                刷新
              </Button>
            )
          }
        >
          {!selectedKbId ? (
            <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>
              请先选择知识库
            </div>
          ) : loadingDocs ? (
            <div style={{ textAlign: 'center', padding: 40 }}>
              <LoadingOutlined style={{ fontSize: 24 }} />
              <p style={{ marginTop: 16 }}>加载中...</p>
            </div>
          ) : documents.length === 0 ? (
            <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>
              暂无文档
            </div>
          ) : (
            <List
              dataSource={documents}
              renderItem={(doc) => (
                <List.Item
                  actions={[
                    <Button
                      type="text"
                      danger
                      icon={<DeleteOutlined />}
                      onClick={() => handleDelete(doc.id, doc.filename)}
                    >
                      删除
                    </Button>
                  ]}
                >
                  <List.Item.Meta
                    avatar={<FileOutlined style={{ fontSize: 24, color: '#1890ff' }} />}
                    title={doc.filename}
                    description={
                      <Space>
                        {getStatusTag(doc.status)}
                        <span>{formatFileSize(doc.file_size)}</span>
                        <span>{dayjs(doc.created_at).format('YYYY-MM-DD HH:mm')}</span>
                      </Space>
                    }
                  />
                </List.Item>
              )}
            />
          )}
        </Card>
      </div>
    </div>
  );
}

export default UploadPage;
