#!/bin/bash
set -e

# ============================================================
# openGauss知识智能体 — 华为云ECS一键部署脚本
# 适用系统：Ubuntu 22.04 LTS
# 使用方法：sudo bash deploy.sh
# ============================================================

# ---------- 颜色输出 ----------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# ---------- 配置区（按需修改） ----------
APP_DIR="/opt/opengauss-agent"
PG_USER="opengauss_app"
PG_PASS="Opengauss@2026"
PG_DB="opengauss_agent"
PG_PORT=5432
BACKEND_PORT=8000
FRONTEND_PORT=80
LLM_API_KEY=""
LLM_BASE_URL="https://api.modelarts-maas.com/v2/chat/completions"
LLM_MODEL="deepseek-v4-flash"

# ---------- 交互式获取配置 ----------
echo ""
echo "=========================================="
echo "  openGauss知识智能体 — 一键部署"
echo "=========================================="
echo ""

read -p "请输入华为云ECS公网IP（回车跳过则用本机IP）: " SERVER_IP
SERVER_IP=${SERVER_IP:-$(hostname -I | awk '{print $1}')}

read -p "请输入ModelArts API Key（必填）: " LLM_API_KEY
if [ -z "$LLM_API_KEY" ]; then
    error "API Key不能为空，请到华为云ModelArts控制台获取"
fi

read -p "请输入PostgreSQL数据库密码（默认: Opengauss@2026）: " INPUT_PG_PASS
PG_PASS=${INPUT_PG_PASS:-$PG_PASS}

info "部署配置："
info "  服务器IP: $SERVER_IP"
info "  应用目录: $APP_DIR"
info "  数据库: ${PG_DB} (用户: ${PG_USER})"
info "  LLM模型: ${LLM_MODEL}"
echo ""

read -p "确认开始部署？(y/n): " CONFIRM
if [ "$CONFIRM" != "y" ]; then
    info "已取消部署"; exit 0
fi

# ---------- 0. 检查系统 ----------
info "检查系统环境..."
if [ ! -f /etc/lsb-release ]; then
    warn "非Ubuntu系统，脚本可能不兼容，继续执行..."
fi

# ---------- 1. 安装系统依赖 ----------
info "[1/8] 安装系统依赖..."
apt-get update -qq
apt-get install -y -qq \
    curl wget git unzip \
    build-essential libpq-dev \
    postgresql-14 postgresql-server-dev-14 \
    nginx \
    python3.11 python3.11-venv python3.11-dev \
    > /dev/null 2>&1

# 检查Python 3.11
if ! command -v python3.11 &> /dev/null; then
    info "添加Python 3.11 PPA..."
    apt-get install -y -qq software-properties-common
    add-apt-repository -y ppa:deadsnakes/ppa
    apt-get update -qq
    apt-get install -y -qq python3.11 python3.11-venv python3.11-dev
fi

# 安装Node.js 18
if ! command -v node &> /dev/null || [ "$(node -v | cut -d. -f1)" != "v18" ]; then
    info "安装Node.js 18..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - > /dev/null 2>&1
    apt-get install -y -qq nodejs
fi

info "  Python: $(python3.11 --version)"
info "  Node.js: $(node --version)"
info "  PostgreSQL: $(psql --version | head -1)"
info "  Nginx: $(nginx -v 2>&1)"

# ---------- 2. 安装pgvector ----------
info "[2/8] 安装pgvector扩展..."
if ! psql -U postgres -c "SELECT * FROM pg_available_extensions WHERE name='vector'" -t | grep -q vector; then
    if [ ! -d /tmp/pgvector ]; then
        git clone --depth 1 https://github.com/pgvector/pgvector.git /tmp/pgvector
    fi
    cd /tmp/pgvector
    make -j$(nproc) > /dev/null 2>&1
    make install > /dev/null 2>&1
    info "  pgvector安装完成"
else
    info "  pgvector已安装，跳过"
fi

# ---------- 3. 配置PostgreSQL ----------
info "[3/8] 配置PostgreSQL..."

# 创建数据库用户和数据库
sudo -u postgres psql -c "SELECT 1 FROM pg_roles WHERE rolname='${PG_USER}'" -t | grep -q 1 || \
    sudo -u postgres psql -c "CREATE USER ${PG_USER} WITH PASSWORD '${PG_PASS}' SUPERUSER;"

sudo -u postgres psql -c "SELECT 1 FROM pg_database WHERE datname='${PG_DB}'" -t | grep -q 1 || \
    sudo -u postgres psql -c "CREATE DATABASE ${PG_DB} OWNER ${PG_USER};"

# 启用pgvector扩展
sudo -u postgres psql -d ${PG_DB} -c "CREATE EXTENSION IF NOT EXISTS vector;"

# 配置pg_hba.conf允许密码认证
PG_HBA="/etc/postgresql/14/main/pg_hba.conf"
if ! grep -q "host.*all.*all.*0.0.0.0/0.*md5" "$PG_HBA" 2>/dev/null; then
    echo "host  all  all  0.0.0.0/0  md5" | sudo tee -a "$PG_HBA" > /dev/null
fi

# 配置postgresql.conf监听地址
PG_CONF="/etc/postgresql/14/main/postgresql.conf"
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" "$PG_CONF"

sudo systemctl restart postgresql
info "  数据库 ${PG_DB} 已创建，pgvector扩展已启用"

# ---------- 4. 上传/准备项目文件 ----------
info "[4/8] 准备项目文件..."

if [ -d "$APP_DIR" ]; then
    warn "  ${APP_DIR} 已存在，备份为 ${APP_DIR}.bak.$(date +%s)"
    mv "$APP_DIR" "${APP_DIR}.bak.$(date +%s)"
fi

mkdir -p "$APP_DIR"

# 检查是否有上传的项目包
if [ -f "/root/opengauss-agent.zip" ] || [ -f "/tmp/opengauss-agent.zip" ]; then
    ZIP_FILE=$([ -f "/root/opengauss-agent.zip" ] && echo "/root/opengauss-agent.zip" || echo "/tmp/opengauss-agent.zip")
    info "  从 ${ZIP_FILE} 解压项目..."
    unzip -q -o "$ZIP_FILE" -d "$APP_DIR"
    # 处理可能的嵌套目录
    if [ -d "$APP_DIR/opengauss-agent" ] && [ ! -f "$APP_DIR/backend/main.py" ]; then
        cp -r "$APP_DIR/opengauss-agent/"* "$APP_DIR/"
        rm -rf "$APP_DIR/opengauss-agent"
    fi
elif [ -d "/root/opengauss-agent" ]; then
    info "  从 /root/opengauss-agent 复制项目..."
    cp -r /root/opengauss-agent/* "$APP_DIR/"
else
    error "  未找到项目文件！请将项目zip上传到 /root/opengauss-agent.zip 或将项目目录放在 /root/opengauss-agent"
fi

# ---------- 5. 恢复数据库 ----------
info "[5/8] 恢复数据库数据..."

SQL_FILE="$APP_DIR/opengauss_agent.sql"
BACKUP_FILE="$APP_DIR/opengauss_agent_pg.backup"

if [ -f "$SQL_FILE" ]; then
    info "  从SQL文件恢复..."
    PGPASSWORD="$PG_PASS" psql -U "$PG_USER" -d "$PG_DB" -h localhost -f "$SQL_FILE" > /dev/null 2>&1 || true
    info "  数据库恢复完成"
elif [ -f "$BACKUP_FILE" ]; then
    info "  从备份文件恢复..."
    PGPASSWORD="$PG_PASS" pg_restore -U "$PG_USER" -d "$PG_DB" -h localhost -c "$BACKUP_FILE" > /dev/null 2>&1 || true
    info "  数据库恢复完成"
else
    warn "  未找到数据库备份文件，将使用空数据库"
fi

# ---------- 6. 配置后端 ----------
info "[6/8] 配置后端..."

cd "$APP_DIR/backend"

# 创建虚拟环境
python3.11 -m venv venv
source venv/bin/activate

# 精简安装（跳过chromadb等不需要的包）
info "  安装Python依赖..."
pip install --upgrade pip -q
pip install -q \
    fastapi==0.115.6 \
    uvicorn[standard]==0.34.0 \
    sqlalchemy[asyncio]==2.0.36 \
    asyncpg==0.30.0 \
    alembic==1.14.0 \
    pydantic==2.10.3 \
    pydantic-settings==2.7.0 \
    python-docx==1.1.2 \
    httpx==0.28.1 \
    python-jose[cryptography]==3.3.0 \
    bcrypt==4.2.1 \
    python-multipart==0.0.20 \
    sse-starlette==2.2.1 \
    pgvector==0.3.6

# 写入.env配置
cat > .env << ENVEOF
APP_NAME=OpenGauss知识智能体
APP_VERSION=1.0.0
DEBUG=False
DATABASE_URL=postgresql+asyncpg://${PG_USER}:${PG_PASS}@localhost:${PG_PORT}/${PG_DB}
MODELARTS_API_KEY=${LLM_API_KEY}
MODELARTS_BASE_URL=${LLM_BASE_URL}
MODELARTS_MODEL=${LLM_MODEL}
ENVEOF

info "  后端配置完成"

# ---------- 7. 构建前端 ----------
info "[7/8] 构建前端..."

cd "$APP_DIR/frontend"
npm install --legacy-peer-deps > /dev/null 2>&1
npm run build > /dev/null 2>&1

if [ ! -d "$APP_DIR/frontend/dist" ]; then
    error "  前端构建失败！请检查 npm run build 的输出"
fi

info "  前端构建完成，输出到 dist/"

# ---------- 8. 配置Nginx + Systemd ----------
info "[8/8] 配置Nginx和系统服务..."

# Nginx配置
cat > /etc/nginx/sites-available/opengauss-agent << NGXEOF
server {
    listen ${FRONTEND_PORT};
    server_name ${SERVER_IP};

    client_max_body_size 50M;

    location / {
        root ${APP_DIR}/frontend/dist;
        index index.html;
        try_files \$uri \$uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:${BACKEND_PORT}/api/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_read_timeout 120s;
        proxy_send_timeout 120s;
    }

    location /images/ {
        proxy_pass http://127.0.0.1:${BACKEND_PORT}/images/;
    }
}
NGXEOF

ln -sf /etc/nginx/sites-available/opengauss-agent /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t > /dev/null 2>&1 || error "Nginx配置有误"
systemctl restart nginx

# Systemd服务配置
cat > /etc/systemd/system/opengauss-backend.service << SVCEOF
[Unit]
Description=openGauss Agent Backend
After=network.target postgresql.service

[Service]
Type=simple
User=root
WorkingDirectory=${APP_DIR}/backend
ExecStart=${APP_DIR}/backend/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port ${BACKEND_PORT}
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
SVCEOF

systemctl daemon-reload
systemctl enable opengauss-backend
systemctl start opengauss-backend

# 等待后端启动
info "  等待后端启动..."
sleep 3

# 检查后端是否正常
if curl -s -o /dev/null -w "%{http_code}" "http://localhost:${BACKEND_PORT}/api/knowledge-tree/stats" | grep -q "200"; then
    info "  后端启动成功！"
else
    warn "  后端可能还在启动中，请稍后检查: systemctl status opengauss-backend"
fi

# ---------- 完成 ----------
echo ""
echo "=========================================="
echo -e "  ${GREEN}部署完成！${NC}"
echo "=========================================="
echo ""
echo "  访问地址: http://${SERVER_IP}"
echo ""
echo "  常用命令："
echo "    查看后端状态:  systemctl status opengauss-backend"
echo "    查看后端日志:  journalctl -u opengauss-backend -f"
echo "    重启后端:      systemctl restart opengauss-backend"
echo "    重启Nginx:     systemctl restart nginx"
echo "    停止所有服务:  systemctl stop opengauss-backend nginx"
echo ""
echo "  安全组请确认已开放端口: 80(HTTP), 22(SSH)"
echo ""