# API 文档

## 基础信息

- **基础 URL**: `http://localhost:8000`
- **API 版本**: v0.1.0
- **交互式文档**: 访问 `http://localhost:8000/docs` 查看 Swagger UI

## 通用响应格式

### 成功响应
```json
{
  "data": {...},
  "message": "操作成功",
  "success": true
}
```

### 错误响应
```json
{
  "error": "错误类型",
  "detail": "详细错误信息",
  "success": false
}
```

---

## 知识库管理 API

### 1. 创建知识库

**POST** `/api/knowledge`

**请求体**:
```json
{
  "name": "产品文档",
  "description": "包含所有产品相关文档"
}
```

**响应**:
```json
{
  "id": 1,
  "name": "产品文档",
  "description": "包含所有产品相关文档",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00",
  "document_count": 0
}
```

**字段说明**:
- `name`: 知识库名称（必填，1-100字符）
- `description`: 知识库描述（可选）

---

### 2. 获取知识库列表

**GET** `/api/knowledge`

**响应**:
```json
{
  "knowledge_bases": [
    {
      "id": 1,
      "name": "产品文档",
      "description": "包含所有产品相关文档",
      "created_at": "2024-01-15T10:30:00",
      "updated_at": "2024-01-15T10:30:00",
      "document_count": 5
    }
  ],
  "total": 1
}
```

---

### 3. 获取知识库详情

**GET** `/api/knowledge/{kb_id}`

**路径参数**:
- `kb_id`: 知识库 ID

**响应**:
```json
{
  "id": 1,
  "name": "产品文档",
  "description": "包含所有产品相关文档",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00",
  "document_count": 5
}
```

---

### 4. 删除知识库

**DELETE** `/api/knowledge/{kb_id}`

**路径参数**:
- `kb_id`: 知识库 ID

**响应**:
```json
{
  "message": "知识库 '产品文档' 已成功删除",
  "success": true
}
```

**注意**: 删除知识库会同时删除所有相关文档和向量数据

---

### 5. 获取知识库文档列表

**GET** `/api/knowledge/{kb_id}/documents`

**路径参数**:
- `kb_id`: 知识库 ID

**响应**:
```json
{
  "documents": [
    {
      "id": 1,
      "knowledge_base_id": 1,
      "filename": "product_manual.pdf",
      "file_type": "pdf",
      "file_size": 1048576,
      "status": "completed",
      "created_at": "2024-01-15T10:35:00"
    }
  ],
  "total": 1
}
```

**文档状态说明**:
- `pending`: 等待处理
- `processing`: 正在处理
- `completed`: 处理完成
- `failed`: 处理失败

---

## 文件管理 API

### 1. 上传文件

**POST** `/api/files/upload/{kb_id}`

**路径参数**:
- `kb_id`: 知识库 ID

**请求体**: `multipart/form-data`
- `file`: 文件（支持 PDF、DOCX、DOC 格式）

**响应**:
```json
{
  "id": 1,
  "knowledge_base_id": 1,
  "filename": "product_manual.pdf",
  "file_type": "pdf",
  "file_size": 1048576,
  "status": "pending",
  "created_at": "2024-01-15T10:35:00"
}
```

**限制**:
- 文件大小：最大 50MB
- 支持格式：PDF、DOCX、DOC

**处理流程**:
1. 文件上传后立即返回（状态为 `pending`）
2. 后台异步处理文档（解析、分块、向量化）
3. 状态变为 `processing`
4. 处理完成后状态变为 `completed`

---

### 2. 删除文件

**DELETE** `/api/files/{document_id}`

**路径参数**:
- `document_id`: 文档 ID

**响应**:
```json
{
  "message": "文档 'product_manual.pdf' 已成功删除",
  "success": true
}
```

---

## 聊天 API

### 1. 发送消息

**POST** `/api/chat`

**请求体**:
```json
{
  "session_id": "session_123456",
  "message": "这个产品的特点是什么？",
  "knowledge_base_id": 1
}
```

**字段说明**:
- `session_id`: 会话 ID（客户端生成，用于标识对话）
- `message`: 用户消息（必填）
- `knowledge_base_id`: 知识库 ID（可选，指定从哪个知识库检索）

**响应**:
```json
{
  "id": 1,
  "session_id": "session_123456",
  "role": "assistant",
  "content": "根据知识库内容，这个产品有以下特点：\n\n1. **高性能**：采用最新技术...\n2. **易用性**：界面简洁直观...",
  "sources": [
    {
      "content": "产品特点包括高性能、易用性和可靠性...",
      "source": "product_manual.pdf",
      "score": 0.85
    }
  ],
  "created_at": "2024-01-15T10:40:00"
}
```

**字段说明**:
- `role`: 消息角色（`user` 或 `assistant`）
- `content`: 消息内容（支持 Markdown 格式）
- `sources`: 引用来源列表
  - `content`: 引用内容片段
  - `source`: 来源文件名
  - `score`: 相似度分数（0-1）

---

### 2. 获取聊天历史

**GET** `/api/chat/history/{session_id}`

**路径参数**:
- `session_id`: 会话 ID

**响应**:
```json
{
  "session_id": "session_123456",
  "messages": [
    {
      "id": 1,
      "session_id": "session_123456",
      "role": "user",
      "content": "这个产品的特点是什么？",
      "sources": null,
      "created_at": "2024-01-15T10:40:00"
    },
    {
      "id": 2,
      "session_id": "session_123456",
      "role": "assistant",
      "content": "根据知识库内容...",
      "sources": [...],
      "created_at": "2024-01-15T10:40:05"
    }
  ],
  "total": 2
}
```

---

### 3. 清空聊天历史

**DELETE** `/api/chat/history/{session_id}`

**路径参数**:
- `session_id`: 会话 ID

**响应**:
```json
{
  "message": "已清空 2 条聊天记录",
  "success": true
}
```

---

### 4. 获取所有会话 ID

**GET** `/api/chat/sessions`

**响应**:
```json
[
  "session_123456",
  "session_789012"
]
```

---

## 系统 API

### 1. 健康检查

**GET** `/health`

**响应**:
```json
{
  "status": "healthy",
  "service": "knowledge-base-chatbot"
}
```

---

### 2. 根路径

**GET** `/`

**响应**:
```json
{
  "message": "知识库聊天机器人 API",
  "version": "0.1.0",
  "docs": "/docs"
}
```

---

## 错误码说明

| HTTP 状态码 | 说明 |
|------------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 413 | 文件过大 |
| 500 | 服务器内部错误 |

---

## 使用示例

### Python 示例

```python
import requests

# 创建知识库
response = requests.post('http://localhost:8000/api/knowledge', json={
    'name': '测试知识库',
    'description': '用于测试'
})
kb_id = response.json()['id']

# 上传文件
with open('test.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.post(
        f'http://localhost:8000/api/files/upload/{kb_id}',
        files=files
    )

# 发送消息
response = requests.post('http://localhost:8000/api/chat', json={
    'session_id': 'test_session',
    'message': '文档中说了什么？',
    'knowledge_base_id': kb_id
})
print(response.json()['content'])
```

### JavaScript 示例

```javascript
// 创建知识库
const response = await fetch('/api/knowledge', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ name: '测试知识库' })
});
const kb = await response.json();

// 上传文件
const formData = new FormData();
formData.append('file', fileInput.files[0]);
await fetch(`/api/files/upload/${kb.id}`, {
  method: 'POST',
  body: formData
});

// 发送消息
const chatResponse = await fetch('/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    session_id: 'test_session',
    message: '文档中说了什么？',
    knowledge_base_id: kb.id
  })
});
const chatData = await chatResponse.json();
console.log(chatData.content);
```
