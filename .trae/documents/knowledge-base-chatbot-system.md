# 基于知识库的聊天机器人系统设计方案

## 一、系统概述

### 1.1 项目目标
构建一个支持知识库上传的本地化聊天机器人系统，用户可以上传 PDF 和 Word 文档作为知识库，系统通过 RAG（检索增强生成）技术，让大模型能够基于知识库内容进行智能问答。

### 1.2 核心功能
- **知识库管理**：上传、查看、删除知识库文档
- **文档处理**：自动解析 PDF 和 Word 文档，提取文本内容
- **向量化存储**：将文档内容转换为向量并存储到向量数据库
- **智能检索**：根据用户问题检索相关知识库内容
- **对话生成**：结合检索内容和用户问题，调用大模型生成回答
- **对话历史**：保存用户对话记录，支持上下文理解

## 二、技术架构

### 2.1 技术栈选型

| 组件 | 技术选型 | 说明 |
|------|---------|------|
| **前端** | React + TypeScript | 现代化前端框架，组件化开发 |
| **UI 组件库** | Ant Design | 丰富的企业级 UI 组件 |
| **后端框架** | Python + FastAPI | 高性能异步框架，适合 AI 应用 |
| **大模型部署** | Ollama | 本地部署 Llama2/Qwen 等开源模型 |
| **向量数据库** | ChromaDB | 轻量级向量数据库，易于集成 |
| **文档解析** | PyPDF2 + python-docx | 解析 PDF 和 Word 文档 |
| **文本嵌入** | sentence-transformers | 本地 Embedding 模型 |
| **文本分块** | LangChain Text Splitter | 智能文本分块 |

### 2.2 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        前端 (React)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  文件上传组件  │  │  聊天界面组件  │  │  知识库管理   │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP/WebSocket
┌─────────────────────────▼───────────────────────────────────┐
│                     后端 (FastAPI)                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  文件上传 API │  │  聊天 API    │  │  知识库 API   │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              RAG 核心处理流程                          │   │
│  │  文档解析 → 文本分块 → 向量化 → 检索 → 生成回答        │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────┬──────────────────┬──────────────────┬────────────┘
           │                  │                  │
    ┌──────▼──────┐    ┌──────▼──────┐    ┌──────▼──────┐
    │  ChromaDB   │    │   Ollama    │    │  SQLite/    │
    │  向量数据库  │    │  大模型服务  │    │  PostgreSQL │
    └─────────────┘    └─────────────┘    └─────────────┘
```

### 2.3 数据流程

#### 知识库上传流程
```
用户上传文件 → 文件保存到本地 → 解析文档内容 → 文本分块 → 
生成向量 → 存储到 ChromaDB → 更新知识库元数据
```

#### 聊天问答流程
```
用户提问 → 问题向量化 → ChromaDB 检索相似内容 → 
构建 Prompt（问题 + 检索内容）→ 调用 Ollama 生成回答 → 
返回结果并保存对话记录
```

## 三、项目结构

```
agent/
├── backend/                    # 后端代码
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI 入口
│   │   ├── config.py          # 配置文件
│   │   ├── api/               # API 路由
│   │   │   ├── __init__.py
│   │   │   ├── chat.py        # 聊天相关 API
│   │   │   ├── knowledge.py   # 知识库管理 API
│   │   │   └── files.py       # 文件上传 API
│   │   ├── core/              # 核心业务逻辑
│   │   │   ├── __init__.py
│   │   │   ├── document_parser.py    # 文档解析
│   │   │   ├── text_splitter.py      # 文本分块
│   │   │   ├── vector_store.py       # 向量存储
│   │   │   ├── retriever.py          # 检索器
│   │   │   └── llm_service.py        # 大模型服务
│   │   ├── models/            # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── database.py    # 数据库连接
│   │   │   └── schemas.py     # Pydantic 模型
│   │   └── utils/             # 工具函数
│   │       ├── __init__.py
│   │       └── file_utils.py
│   ├── data/                  # 数据存储
│   │   ├── uploads/           # 上传的文件
│   │   ├── vector_db/         # ChromaDB 数据
│   │   └── chat_history/      # 对话历史
│   ├── requirements.txt       # Python 依赖
│   └── .env.example          # 环境变量示例
│
├── frontend/                   # 前端代码
│   ├── public/
│   ├── src/
│   │   ├── components/        # 组件
│   │   │   ├── Chat/          # 聊天组件
│   │   │   ├── Upload/        # 上传组件
│   │   │   └── Knowledge/     # 知识库管理组件
│   │   ├── pages/             # 页面
│   │   │   ├── ChatPage.tsx
│   │   │   ├── UploadPage.tsx
│   │   │   └── KnowledgePage.tsx
│   │   ├── services/          # API 服务
│   │   │   └── api.ts
│   │   ├── types/             # 类型定义
│   │   │   └── index.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── scripts/                    # 脚本
│   ├── setup.sh              # 环境初始化脚本
│   └── start.sh              # 启动脚本
│
├── docs/                       # 文档
│   ├── API.md                 # API 文档
│   └── DEPLOYMENT.md          # 部署文档
│
└── README.md                   # 项目说明
```

## 四、核心模块设计

### 4.1 文档解析模块 (document_parser.py)

**功能**：解析 PDF 和 Word 文档，提取纯文本内容

**关键实现**：
- 使用 PyPDF2 解析 PDF 文件
- 使用 python-docx 解析 Word 文档
- 支持批量解析
- 错误处理和日志记录

### 4.2 文本分块模块 (text_splitter.py)

**功能**：将长文档分割成适合向量化的文本块

**关键实现**：
- 使用 LangChain 的 RecursiveCharacterTextSplitter
- 支持自定义 chunk_size（默认 1000 字符）和 chunk_overlap（默认 200 字符）
- 保留文档元数据（来源文件名、页码等）

### 4.3 向量存储模块 (vector_store.py)

**功能**：管理 ChromaDB 向量数据库

**关键实现**：
- 初始化 ChromaDB 客户端
- 创建和管理集合（Collection）
- 文本向量化（使用 sentence-transformers）
- 向量存储和检索
- 支持按知识库 ID 过滤

### 4.4 检索器模块 (retriever.py)

**功能**：根据用户问题检索相关知识库内容

**关键实现**：
- 问题向量化
- 相似度检索（默认返回 top-3 相关文档块）
- 结果重排序和过滤
- 返回格式化的上下文

### 4.5 大模型服务模块 (llm_service.py)

**功能**：与 Ollama 服务交互，生成回答

**关键实现**：
- 调用 Ollama API
- 构建 RAG Prompt（系统提示 + 检索内容 + 用户问题）
- 支持流式输出
- 错误处理和重试机制

### 4.6 API 设计

#### 知识库管理 API
```
POST   /api/knowledge          # 创建知识库
GET    /api/knowledge          # 获取知识库列表
GET    /api/knowledge/{id}     # 获取知识库详情
DELETE /api/knowledge/{id}     # 删除知识库
POST   /api/knowledge/{id}/upload  # 上传文档到知识库
```

#### 聊天 API
```
POST   /api/chat               # 发送消息（支持流式响应）
GET    /api/chat/history       # 获取对话历史
DELETE /api/chat/history       # 清空对话历史
```

#### 文件管理 API
```
POST   /api/files/upload       # 上传文件
GET    /api/files              # 获取文件列表
DELETE /api/files/{id}         # 删除文件
```

## 五、数据库设计

### 5.1 SQLite 表结构

#### knowledge_bases 表（知识库）
```sql
CREATE TABLE knowledge_bases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### documents 表（文档）
```sql
CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    knowledge_base_id INTEGER NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(10) NOT NULL,
    file_size INTEGER,
    status VARCHAR(20) DEFAULT 'pending',  -- pending/processing/completed/failed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (knowledge_base_id) REFERENCES knowledge_bases(id)
);
```

#### chat_messages 表（对话消息）
```sql
CREATE TABLE chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL,  -- user/assistant/system
    content TEXT NOT NULL,
    sources TEXT,  -- JSON 格式，存储引用的知识库内容
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 六、前端页面设计

### 6.1 页面结构

1. **聊天页面 (ChatPage)**
   - 左侧：对话历史列表
   - 右侧：聊天窗口（消息列表 + 输入框）
   - 支持显示引用来源

2. **上传页面 (UploadPage)**
   - 文件拖拽上传区域
   - 上传进度显示
   - 选择目标知识库

3. **知识库管理页面 (KnowledgePage)**
   - 知识库列表（卡片式展示）
   - 创建新知识库
   - 查看知识库详情和文档列表

### 6.2 组件设计

- `ChatMessage`: 单条消息组件，支持 Markdown 渲染
- `FileUploader`: 文件上传组件，支持拖拽
- `KnowledgeCard`: 知识库卡片组件
- `SourceReference`: 引用来源展示组件

## 七、部署方案

### 7.1 环境要求
- Python 3.9+
- Node.js 18+
- Ollama（已安装并运行）

### 7.2 安装步骤

1. **安装 Ollama 并下载模型**
```bash
# 安装 Ollama（macOS）
brew install ollama

# 启动 Ollama 服务
ollama serve

# 下载模型（在新终端窗口）
ollama pull llama2
# 或
ollama pull qwen2
```

2. **后端安装**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **前端安装**
```bash
cd frontend
npm install
```

4. **启动服务**
```bash
# 启动后端（终端 1）
cd backend
uvicorn app.main:app --reload --port 8000

# 启动前端（终端 2）
cd frontend
npm run dev
```

## 八、开发计划

### 阶段一：基础架构搭建（1-2 天）
- [ ] 初始化项目结构
- [ ] 配置 FastAPI 后端
- [ ] 配置 React 前端
- [ ] 设置数据库和向量数据库

### 阶段二：核心功能开发（3-4 天）
- [ ] 实现文档解析模块
- [ ] 实现文本分块和向量化
- [ ] 实现知识库管理 API
- [ ] 实现文件上传功能

### 阶段三：RAG 功能实现（2-3 天）
- [ ] 实现向量检索
- [ ] 集成 Ollama 大模型
- [ ] 实现聊天 API
- [ ] 构建 RAG Prompt

### 阶段四：前端开发（2-3 天）
- [ ] 开发聊天界面
- [ ] 开发文件上传界面
- [ ] 开发知识库管理界面
- [ ] 实现 API 对接

### 阶段五：测试和优化（1-2 天）
- [ ] 功能测试
- [ ] 性能优化
- [ ] 错误处理完善
- [ ] 文档编写

## 九、关键配置文件

### 9.1 后端环境变量 (.env)
```env
# Ollama 配置
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# 数据库配置
DATABASE_URL=sqlite:///./data/app.db

# ChromaDB 配置
CHROMA_HOST=localhost
CHROMA_PORT=8000
CHROMA_COLLECTION=knowledge_base

# Embedding 模型
EMBEDDING_MODEL=all-MiniLM-L6-v2

# 文件上传配置
UPLOAD_DIR=./data/uploads
MAX_FILE_SIZE=52428800  # 50MB
```

### 9.2 Python 依赖 (requirements.txt)
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6
pydantic==2.5.3
pydantic-settings==2.1.0
chromadb==0.4.22
sentence-transformers==2.3.1
PyPDF2==3.0.1
python-docx==1.1.0
langchain==0.1.5
langchain-text-splitters==0.0.1
httpx==0.26.0
python-dotenv==1.0.0
sqlalchemy==2.0.25
aiosqlite==0.19.0
```

## 十、验证方案

### 10.1 功能验证
1. **知识库上传验证**
   - 上传 PDF 文件，确认解析成功
   - 上传 Word 文件，确认解析成功
   - 查看知识库列表，确认文档已添加

2. **聊天功能验证**
   - 提问知识库中的内容，确认能正确回答
   - 提问知识库外的问题，确认不会编造答案
   - 查看回答的引用来源，确认来源准确

3. **性能验证**
   - 上传大文件（>10MB），确认处理时间合理
   - 并发聊天请求，确认响应时间 < 5 秒

### 10.2 测试用例
- 上传空文件，确认错误提示
- 上传不支持的文件格式，确认拒绝
- 删除正在使用的知识库，确认提示
- 网络中断时调用大模型，确认错误处理

## 十一、后续优化方向

1. **功能增强**
   - 支持更多文件格式（HTML、Markdown、Excel）
   - 支持多轮对话上下文
   - 支持对话导出
   - 支持知识库分享

2. **性能优化**
   - 使用 GPU 加速向量化
   - 实现向量缓存
   - 异步处理大文件

3. **体验优化**
   - 添加加载动画
   - 支持流式输出
   - 添加对话搜索功能

---

**下一步**：确认本方案后，将按照开发计划逐步实现各个功能模块。
