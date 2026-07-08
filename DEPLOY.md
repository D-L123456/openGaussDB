# OpenGauss知识智能体 — 远程部署指南

## 一、所需文件

| 文件/目录 | 说明 |
|-----------|------|
| `backend/` | 后端代码 |
| `frontend/` | 前端代码 |
| `rebuild_final.py` | 知识树重建脚本（数据更新时用） |
| `opengauss_agent_pg.backup` | 数据库备份（2.6MB，含知识库+向量+题目） |

---

## 二、环境要求

| 组件 | 版本 | 说明 |
|------|------|------|
| Python | 3.10+ | 后端运行 |
| Node.js | 18+ | 前端构建 |
| PostgreSQL + pgvector | 15+ / 0.5+ | RDS或自建均可 |

---

## 三、部署步骤

### 步骤1：准备数据库（RDS）

1. 在华为云RDS创建 PostgreSQL 15+ 实例，勾选 pgvector 扩展
2. 创建数据库 `opengauss_agent`
3. 连接数据库，启用 pgvector：
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
4. 从本地上传备份文件到服务器，然后恢复：
   ```bash
   pg_restore -U 用户名 -h RDS地址 -d opengauss_agent opengauss_agent_pg.backup
   ```
5. 验证：
   ```sql
   SELECT COUNT(*) FROM knowledge_nodes;       -- 287
   SELECT COUNT(*) FROM knowledge_chunks;      -- 1108
   SELECT COUNT(*) FROM sql_questions;         -- 7
   SELECT extname FROM pg_extension WHERE extname='vector';  -- vector
   ```

### 步骤2：部署后端

1. 将 `backend/` 复制到服务器，如 `D:\opengauss-agent\backend\`
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   pip install psycopg2-binary asyncpg
   ```
3. 修改 `backend/.env`：
   ```ini
   APP_NAME=OpenGauss知识智能体
   APP_VERSION=1.0.0
   DEBUG=False

   # RDS数据库连接
   DATABASE_URL=postgresql+asyncpg://用户名:密码@RDS地址:5432/opengauss_agent

   # LLM API
   MODELARTS_API_KEY=你的API密钥
   MODELARTS_BASE_URL=https://api.modelarts-maas.com/v2/chat/completions
   MODELARTS_MODEL=deepseek-v4-flash

   # 文档目录（图片服务用，指向backend/app/data）
   DOCX_DIR=D:\opengauss-agent\backend\app\data

   # JWT密钥（务必更换为随机字符串）
   JWT_SECRET_KEY=你的随机密钥-至少32位
   ```
4. 启动后端：
   ```bash
   cd D:\opengauss-agent\backend
   python run.py
   ```
   或用 uvicorn：
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

### 步骤3：部署前端

1. 将 `frontend/` 复制到服务器
2. 修改 `frontend/vite.config.ts` 中的代理目标地址（如果后端不在同一台机器）
3. 安装依赖并构建：
   ```bash
   npm install
   npm run build
   ```
4. 构建产物在 `dist/` 目录，用 Nginx 托管

### 步骤4：配置 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root D:/opengauss-agent/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端API代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 图片资源代理
    location /images/ {
        proxy_pass http://127.0.0.1:8000/images/;
    }
}
```

---

## 四、验证部署

```bash
# 检查后端API
curl http://localhost:8000/api/knowledge-tree/stats
# 预期：{"total_documents":1108,"chapters":12}

# 检查RAG问答
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"什么是openGauss?\"}"

# 浏览器访问
http://your-domain.com
```

---

## 五、数据更新（如需重新导入教材）

1. 修改 docx 源文件
2. 在本地运行：
   ```bash
   python rebuild_final.py
   ```
3. 重新导出备份并恢复到RDS：
   ```bash
   pg_dump -U postgres -F c -f opengauss_agent_pg.backup opengauss_agent
   pg_restore -U 用户名 -h RDS地址 -d opengauss_agent --clean opengauss_agent_pg.backup
   ```
4. 重启后端
