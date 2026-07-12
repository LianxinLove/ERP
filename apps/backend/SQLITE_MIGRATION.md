# SQLite 数据库迁移完成

## 修改内容

已将后端数据库从 **MySQL** 迁移到 **SQLite**，以下是修改的文件：

### 修改的文件

| 文件 | 修改内容 |
|------|----------|
| `app/core/config.py` | 将数据库配置从 MySQL 参数改为 SQLite 路径 |
| `app/core/database.py` | 移除 MySQL 连接池配置，简化为 SQLite |
| `pyproject.toml` | 将 `aiomysql/pymysql` 改为 `aiosqlite` |
| `.env.example` | 更新环境变量示例 |

### 新的数据库配置

**环境变量 (`.env`):**
```bash
# SQLite 数据库文件路径
DB_PATH=./erp_system.db
```

**数据库 URL:**
```python
# 旧 (MySQL)
mysql+aiomysql://user:pass@localhost:3306/erp_system

# 新 (SQLite)
sqlite+aiosqlite:///./erp_system.db
```

---

## 启动步骤

### 1. 重新安装依赖

```bash
cd apps/backend

# 卸载旧的 MySQL 驱动（可选）
pip uninstall -y aiomysql pymysql

# 安装新的依赖
pip install -e .
```

### 2. 创建环境文件

```bash
# 复制示例配置
cp .env.example .env

# 生成 JWT 密钥
openssl rand -hex 32
```

将生成的密钥填入 `.env` 文件的 `JWT_SECRET_KEY`。

### 3. 启动服务

```bash
# 初始化数据库
python -m app.core.init_db

# 初始化 RBAC 数据
python -m app.core.init_rbac

# 启动服务
python -m app.main
```

---

## SQLite 优点

| 特性 | 说明 |
|------|------|
| ✅ 无需安装 | 不需要单独的数据库服务器 |
| ✅ 零配置 | 开箱即用，无需配置连接参数 |
| ✅ 便携性 | 数据库是单个文件，易于备份和迁移 |
| ✅ 跨平台 | 支持 Windows、Linux、macOS |
| ✅ 适合开发 | 开发和小型项目理想选择 |

---

## 注意事项

### 生产环境建议

SQLite 适合以下场景：
- 小型应用 (< 100 用户)
- 读多写少的场景
- 单服务器部署

如果需要升级到生产级数据库，建议：
- **PostgreSQL** - 功能最全面，推荐用于生产
- **MySQL** - 广泛支持，成熟稳定

### 数据库迁移

如需迁移数据：

```bash
# 导出 SQLite 数据
sqlite3 erp_system.db .dump > backup.sql

# 导入到 PostgreSQL/MySQL
psql -U user -d database < backup.sql
```

---

## API 文档

启动后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

*迁移完成日期：2026-07-11*
