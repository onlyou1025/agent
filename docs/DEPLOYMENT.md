# 部署文档

## 环境要求

### 系统要求
- Python 3.9+
- Node.js 18+
- macOS / Linux / Windows

### 软件依赖
- Ollama（本地大模型服务）
- Git（可选，用于版本控制）

## 安装步骤

### 1. 安装 Ollama

#### macOS
```bash
# 使用 Homebrew 安装
brew install ollama

# 启动 Ollama 服务
ollama serve

# 在另一个终端窗口下载模型
ollama pull llama2
# 或
ollama pull qwen2
```

#### Linux
```bash
# 安装 Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 启动服务
ollama serve

# 下载模型
ollama pull llama2
```

#### Windows
从 [Ollama 官网](https://ollama.com/download) 下载安装包

### 2. 后端部署

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 复制环境变量配置文件
cp .env.example .env

# （可选）编辑 .env 文件，修改配置
# 主要配置项：
# - OLLAMA_BASE_URL: Ollama 服务地址（默认 http://localhost:11434）
# - OLLAMA_MODEL: 使用的模型名称（默认 llama2）
# - EMBEDDING_MODEL: Embedding 模型（默认 all-MiniLM-L6-v2）

# 启动后端服务
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端服务将在 `http://localhost:8000` 启动
API 文档访问：`http://localhost:8000/docs`

### 3. 前端部署

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务将在 `http://localhost:5173` 启动

### 4. 验证部署

1. 检查后端健康状态：
   ```bash
   curl http://localhost:8000/health
   ```

2. 访问前端界面：
   打开浏览器访问 `http://localhost:5173`

3. 测试功能：
   - 创建知识库
   - 上传 PDF/Word 文档
   - 在聊天页面提问

## 生产环境部署

### 后端生产部署

```bash
# 不使用 reload 模式
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# 或使用 gunicorn（推荐）
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 前端生产构建

```bash
# 构建生产版本
npm run build

# 构建产物在 dist/ 目录
# 可以使用 nginx 或其他 web 服务器托管
```

### Nginx 配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /path/to/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API 代理
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## 常见问题

### 1. Ollama 连接失败
- 确保 Ollama 服务正在运行：`ollama serve`
- 检查端口是否被占用：`lsof -i :11434`
- 验证模型是否已下载：`ollama list`

### 2. 向量数据库初始化失败
- 删除 `backend/data/vector_db` 目录，让系统重新创建
- 检查磁盘空间是否充足

### 3. 文档解析失败
- 确保 PDF/Word 文件格式正确
- 检查文件是否损坏
- 查看后端日志获取详细错误信息

### 4. 前端无法连接后端
- 检查后端服务是否启动
- 确认 CORS 配置（`backend/app/main.py`）
- 检查 `frontend/vite.config.ts` 中的代理配置

## 性能优化建议

1. **Embedding 模型**：首次运行会下载模型，可能需要几分钟
2. **向量数据库**：定期备份 `backend/data/vector_db` 目录
3. **文件存储**：定期清理 `backend/data/uploads` 中的临时文件
4. **内存使用**：大文档会消耗较多内存，建议限制文件大小

## 安全建议

1. 生产环境使用 HTTPS
2. 配置防火墙规则
3. 定期备份数据
4. 监控服务日志
5. 限制文件大小和上传频率
