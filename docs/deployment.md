# ERP 系统部署指南

## 目录
- [环境要求](#环境要求)
- [Docker 部署](#docker-部署)
- [手动部署](#手动部署)
- [生产环境配置](#生产环境配置)
- [监控与维护](#监控与维护)

---

## 环境要求

### 最低配置
- CPU: 2 核
- 内存: 4GB
- 硬盘: 20GB
- 系统: Linux (Ubuntu 20.04+ 推荐)

### 推荐配置
- CPU: 4 核
- 内存: 8GB
- 硬盘: 50GB SSD
- 系统: Ubuntu 22.04 LTS

### 软件要求
- Docker 20.10+
- Docker Compose 2.0+
- Git

---

## Docker 部署

### 1. 克隆代码

```bash
git clone https://github.com/your-org/erp-system.git
cd erp-system
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置以下关键参数：

```bash
# 数据库配置
MYSQL_ROOT_PASSWORD=your_secure_root_password
MYSQL_DATABASE=erp_db
MYSQL_USER=erp_user
MYSQL_PASSWORD=your_secure_password

# 应用密钥（使用 openssl rand -hex 32 生成）
SECRET_KEY=your_secret_key_here

# CORS 配置
CORS_ORIGINS=["https://your-domain.com"]
```

### 3. 启动服务

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
```

### 4. 初始化数据库

```bash
# 进入后端容器
docker-compose exec backend bash

# 初始化数据库
python -m app.core.init_db

# 创建管理员账户
python -m app.core.create_admin
```

### 5. 访问系统

- 前端: http://your-server-ip:3000
- API 文档: http://your-server-ip:8000/docs
- 健康检查: http://your-server-ip:8000/health

---

## 手动部署

### 后端部署

#### 1. 安装依赖

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv mysql-server redis-server nginx

# 创建虚拟环境
cd apps/backend
python3.11 -m venv venv
source venv/bin/activate
pip install -e .
```

#### 2. 配置数据库

```bash
# 登录 MySQL
sudo mysql -u root -p

CREATE DATABASE erp_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'erp_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON erp_db.* TO 'erp_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### 3. 配置环境

```bash
cp .env.example .env
# 编辑 .env 文件
```

#### 4. 初始化数据库

```bash
python -m app.core.init_db
python -m app.core.create_admin
```

#### 5. 使用 Systemd 管理

创建 `/etc/systemd/system/erp-backend.service`:

```ini
[Unit]
Description=ERP Backend API
After=network.target mysql.service redis.service

[Service]
Type=notify
User=erp
WorkingDirectory=/var/www/erp/backend
Environment="PATH=/var/www/erp/backend/venv/bin"
ExecStart=/var/www/erp/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable erp-backend
sudo systemctl start erp-backend
```

### 前端部署

#### 1. 安装依赖

```bash
cd apps/frontend
pnpm install
```

#### 2. 构建生产版本

```bash
pnpm build
```

#### 3. 使用 PM2 管理

```bash
# 安装 PM2
npm install -g pm2

# 启动应用
pm2 start npm --name "erp-frontend" -- start

# 保存配置
pm2 save
pm2 startup
```

---

## 生产环境配置

### Nginx 配置

安装 Nginx:
```bash
sudo apt install nginx
```

复制配置文件：
```bash
sudo cp nginx/nginx.conf /etc/nginx/nginx.conf
```

测试并重启：
```bash
sudo nginx -t
sudo systemctl restart nginx
```

### SSL 证书（使用 Let's Encrypt）

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

### 防火墙配置

```bash
# UFW 防火墙
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

---

## 监控与维护

### 日志管理

```bash
# Docker 日志
docker-compose logs --tail=100 -f backend

# 系统日志
sudo journalctl -u erp-backend -f
```

### 数据库备份

```bash
# 备份
docker-compose exec mysql mysqldump -u root -p erp_db > backup_$(date +%Y%m%d).sql

# 恢复
docker-compose exec -T mysql mysql -u root -p erp_db < backup_20240620.sql
```

### 定期任务

设置自动备份（crontab）:
```bash
# 编辑 crontab
crontab -e

# 添加每天 2 点备份
0 2 * * * /path/to/backup-script.sh
```

### 性能监控

推荐使用：
- Prometheus + Grafana
- Sentry（错误追踪）
- New Relic / Datadog（APM）

---

## 更新升级

### Docker 部署升级

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker-compose up -d --build

# 数据库迁移（如需要）
docker-compose exec backend python -m alembic upgrade head
```

### 手动部署升级

```bash
# 后端
cd /var/www/erp/backend
git pull
source venv/bin/activate
pip install -e .
python -m alembic upgrade head
sudo systemctl restart erp-backend

# 前端
cd /var/www/erp/frontend
git pull
pnpm install
pnpm build
pm2 restart erp-frontend
```

---

## 故障排除

### 常见问题

**Q: 数据库连接失败**
```bash
# 检查 MySQL 状态
sudo systemctl status mysql

# 检查连接
docker-compose exec backend mysql -h mysql -u erp_user -p erp_db
```

**Q: 前端无法访问 API**
```bash
# 检查 CORS 配置
# 查看后端日志
docker-compose logs backend | grep -i cors
```

**Q: 内存不足**
```bash
# 增加 Docker 内存限制
# 在 docker-compose.yml 中添加:
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
```

---

## 安全建议

1. 修改默认密码
2. 启用 HTTPS
3. 配置防火墙
4. 定期更新系统
5. 限制数据库远程访问
6. 使用强密码策略
7. 定期备份数据

---

*最后更新时间：2024-06-20*
