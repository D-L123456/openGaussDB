# 远端Windows服务器 — PostgreSQL 17 + pgvector 安装与数据恢复

## 一、安装 PostgreSQL 17

1. 下载安装包：https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
2. 运行安装程序，安装过程中：
   - 安装路径保持默认 `C:\Program Files\PostgreSQL\17\`
   - 设置超级用户 postgres 的密码（记住此密码，后续连接要用）
   - 端口保持默认 `5432`
   - 区域设置选默认即可
3. 安装完成后，PostgreSQL 服务会自动启动

验证安装：
```bash
"C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -c "SELECT version();"
```

---

## 二、安装 pgvector 扩展

1. 下载 pgvector Windows 预编译包：https://github.com/pgvector/pgvector/releases
   - 选择 `pgvector-0.7.x-windows-pg17.zip`（版本号可能更新，选最新的 pg17 版本）
2. 解压后，将以下文件复制到对应目录：

| 源文件 | 目标目录 |
|--------|----------|
| `vector.dll` | `C:\Program Files\PostgreSQL\17\lib\` |
| `vector.control` | `C:\Program Files\PostgreSQL\17\share\extension\` |
| `vector--0.7.x.sql` | `C:\Program Files\PostgreSQL\17\share\extension\` |

3. 验证安装：
```sql
-- 用 psql 或 pgAdmin 连接后执行
CREATE EXTENSION vector;
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';
-- 预期输出：vector | 0.7.x
```

---

## 三、创建数据库并恢复数据

### 3.1 创建数据库

```bash
"C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -c "CREATE DATABASE opengauss_agent;"
```

或用 pgAdmin 图形界面创建。

### 3.2 启用 pgvector 扩展

```bash
"C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -d opengauss_agent -c "CREATE EXTENSION vector;"
```

### 3.3 恢复备份数据

1. 将 `opengauss_agent_pg.backup` 文件复制到远端服务器（如 `D:\` 根目录）
2. 执行恢复：

```bash
"C:\Program Files\PostgreSQL\17\bin\pg_restore.exe" -U postgres -d opengauss_agent D:\opengauss_agent_pg.backup
```

3. 验证数据：

```bash
"C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -d opengauss_agent -c "SELECT tablename FROM pg_tables WHERE schemaname='public';"
```

预期输出以下表：

| 表名 | 预期行数 |
|------|---------|
| knowledge_nodes | 287 |
| knowledge_chunks | 1108 |
| sql_questions | 7 |
| deposit_types | 45 |
| preset_customers | 10 |
| preset_cards | 10 |
| learning_events | 2 |
| user_profiles | 1 |

```bash
"C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -d opengauss_agent -c "SELECT COUNT(*) FROM knowledge_chunks WHERE embedding IS NOT NULL;"
```

预期输出：1108（向量嵌入数量）