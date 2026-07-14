import { Routes, Route, Navigate } from 'react-router-dom';
import { Layout, Menu } from 'antd';
import { MessageOutlined, UploadOutlined, DatabaseOutlined } from '@ant-design/icons';
import { Link, useLocation } from 'react-router-dom';
import ChatPage from './pages/ChatPage';
import UploadPage from './pages/UploadPage';
import KnowledgePage from './pages/KnowledgePage';
import './App.css';

const { Header, Content, Sider } = Layout;

function App() {
  const location = useLocation();

  const menuItems = [
    {
      key: '/chat',
      icon: <MessageOutlined />,
      label: <Link to="/chat">聊天</Link>
    },
    {
      key: '/upload',
      icon: <UploadOutlined />,
      label: <Link to="/upload">上传文档</Link>
    },
    {
      key: '/knowledge',
      icon: <DatabaseOutlined />,
      label: <Link to="/knowledge">知识库管理</Link>
    }
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider theme="light" width={200}>
        <div style={{ height: 64, display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', fontSize: 18 }}>
          知识库助手
        </div>
        <Menu
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          style={{ height: '100%', borderRight: 0 }}
        />
      </Sider>
      <Layout>
        <Header style={{ background: '#fff', padding: '0 24px', borderBottom: '1px solid #f0f0f0' }}>
          <h2 style={{ margin: 0, fontSize: 18 }}>
            {location.pathname === '/chat' && '智能聊天'}
            {location.pathname === '/upload' && '上传文档'}
            {location.pathname === '/knowledge' && '知识库管理'}
          </h2>
        </Header>
        <Content style={{ margin: 0, padding: 24, background: '#fff' }}>
          <Routes>
            <Route path="/" element={<Navigate to="/chat" replace />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/knowledge" element={<KnowledgePage />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  );
}

export default App;
