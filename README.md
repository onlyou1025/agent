# 知识库聊天机器人

基于 RAG（检索增强生成）技术的本地知识库聊天机器人系统。支持上传 PDF 和 Word 文档作为知识库，通过本地部署的大语言模型进行智能问答。

## 功能特性

- 📚 **知识库管理**：创建、查看、删除知识库
- 📄 **文档上传**：支持 PDF 和 Word 文档批量上传
- 🔍 **智能检索**：基于向量相似度的知识库内容检索
- 💬 **智能对话**：结合知识库内容的智能问答
- 🎯 **引用溯源**：回答附带引用来源和相似度分数
- 🖥️ **本地部署**：使用 Ollama 本地运行大模型，数据安全

## 技术栈

### 后端
- **框架**: FastAPI + Python 3.9+
- **向量数据库**: ChromaDB
- **文档解析**: PyPDF2 + python-docx
- **文本嵌入**: sentence-transformers
- **文本分块**: LangChain Text Splitters
- **大模型**: Ollama (Llama2/Qwen)

### 前端
- **框架**: React 18 + TypeScript
- **UI 组件**: Ant Design
- **构建工具**: Vite
- **路由**: React Router

## 快速开始

### 1. 环境要求

- Python 3.9+
- Node.js 18+
- Ollama

### 2. 安装 Ollama

```bash
# macOS
brew install ollama

# 启动服务
ollama serve

# 下载模型（在新终端窗口）
ollama pull llama2
# 或
ollama pull qwen2
```

### 3. 初始化环境

```bash
# 运行初始化脚本
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### 4. 启动服务

```bash
# 使用启动脚本
chmod +x scripts/start.sh
./scripts/start.sh

# 或手动启动

# 终端 1：启动后端
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 终端 2：启动前端
cd frontend
npm run dev
```

### 5. 访问应用

- 前端界面: http://localhost:5173
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

## 使用流程

1. **创建知识库**
   - 访问"知识库管理"页面
   - 点击"创建知识库"
   - 输入名称和描述

2. **上传文档**
   - 访问"上传文档"页面
   - 选择目标知识库
   - 拖拽或点击上传 PDF/Word 文件
   - 等待文档处理完成

3. **开始对话**
   - 访问"聊天"页面
   - 选择知识库
   - 输入问题
   - 系统会基于知识库内容生成回答

## 项目结构

```
agent/
├── backend/              # 后端代码
│   ├── app/
│   │   ├── api/         # API 路由
│   │   ├── core/        # 核心业务逻辑
│   │   ├── models/      # 数据模型
│   │   ├── utils/       # 工具函数
│   │   └── main.py      # 应用入口
│   ├── data/            # 数据存储
│   └── requirements.txt # Python 依赖
│
├── frontend/            # 前端代码
│   ├── src/
│   │   ├── components/  # 组件
│   │   ├── pages/       # 页面
│   │   ├── services/    # API 服务
│   │   └── types/       # 类型定义
│   └── package.json
│
├── scripts/             # 脚本
│   ├── setup.sh        # 环境初始化
│   ├── start.sh        # 启动服务
│   └── stop.sh         # 停止服务
│
└── docs/               # 文档
    ├── API.md          # API 文档
    └── DEPLOYMENT.md   # 部署文档
```

## 配置说明

### 后端配置 (backend/.env)

```env
# Ollama 配置
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# 数据库配置
DATABASE_URL=sqlite+aiosqlite:///./data/app.db

# ChromaDB 配置
CHROMA_PERSIST_DIR=./data/vector_db
CHROMA_COLLECTION=knowledge_base

# Embedding 模型
EMBEDDING_MODEL=all-MiniLM-L6-v2

# 文件上传配置
UPLOAD_DIR=./data/uploads
MAX_FILE_SIZE=52428800  # 50MB
```

### 前端配置 (frontend/vite.config.ts)

```typescript
export default defineConfig({
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

## 开发指南

### 后端开发

```bash
cd backend
source venv/bin/activate

# 运行开发服务器
python -m uvicorn app.main:app --reload

# 运行测试（待实现）
pytest
```

### 前端开发

```bash
cd frontend

# 开发模式
npm run dev

# 构建生产版本
npm run build

# 代码检查
npm run lint
```

## 常见问题

### 1. Ollama 连接失败
确保 Ollama 服务正在运行：
```bash
ollama serve
```

### 2. 文档处理失败
- 检查文件格式是否正确
- 查看后端日志：`tail -f logs/backend.log`
- 确保文件未损坏

### 3. 向量数据库初始化慢
首次运行会下载 Embedding 模型，可能需要几分钟，请耐心等待。

### 4. 内存不足
大文档会消耗较多内存，建议：
- 限制文件大小（默认 50MB）
- 调整 `chunk_size` 参数（在 `backend/app/config.py`）

## 性能优化

1. **使用 GPU 加速**（如果可用）
   - 安装 CUDA 版本的 PyTorch
   - sentence-transformers 会自动使用 GPU

2. **调整文本分块参数**
   ```python
   # backend/app/config.py
   chunk_size = 1000  # 减小可以提高检索精度
   chunk_overlap = 200  # 增加可以提高上下文连贯性
   ```

3. **更换更快的 Embedding 模型**
   ```env
   # backend/.env
   EMBEDDING_MODEL=all-MiniLM-L6-v2  # 速度快
   # 或
   EMBEDDING_MODEL=all-mpnet-base-v2  # 精度高
   ```

## 路线图

- [ ] 支持更多文件格式（HTML、Markdown、Excel）
- [ ] 多轮对话上下文优化
- [ ] 流式输出支持
- [ ] 对话导出功能
- [ ] 知识库分享功能
- [ ] 用户认证和权限管理
- [ ] 性能监控和日志系统

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题，请通过 GitHub Issues 反馈。
# agent
