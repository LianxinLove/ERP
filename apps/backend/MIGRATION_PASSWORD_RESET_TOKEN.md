# 数据库迁移：密码重置令牌哈希化

## 迁移说明

此迁移将 `password_resets` 表中的 `token` 列重命名为 `token_hash`，以提高安全性。

## 迁移步骤

### SQLite 迁移 SQL

```sql
-- 1. 备份现有数据
CREATE TABLE password_resets_backup AS SELECT * FROM password_resets;

-- 2. 创建新表结构
CREATE TABLE password_resets_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token_hash VARCHAR(255) NOT NULL,
    expires_at DATETIME NOT NULL,
    is_used BOOLEAN DEFAULT 0 NOT NULL,
    used_at DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

-- 3. 创建索引
CREATE INDEX ix_password_resets_new_user_id ON password_resets_new(user_id);
CREATE INDEX ix_password_resets_new_token_hash ON password_resets_new(token_hash);
CREATE INDEX ix_password_resets_new_expires_at ON password_resets_new(expires_at);
CREATE INDEX ix_password_resets_new_is_used ON password_resets_new(is_used);

-- 4. 迁移数据（注意：现有令牌将被丢弃，需要重新申请）
-- 由于这是安全性升级，现有未使用的重置令牌将失效
INSERT INTO password_resets_new (id, user_id, expires_at, is_used, used_at, created_at)
SELECT id, user_id, expires_at, is_used, used_at, created_at
FROM password_resets;

-- 5. 删除旧表
DROP TABLE password_resets;

-- 6. 重命名新表
ALTER TABLE password_resets_new RENAME TO password_resets;

-- 7. 清理备份（可选，确认迁移成功后执行）
-- DROP TABLE password_resets_backup;
```

## 注意事项

⚠️ **重要**: 此迁移会导致所有现有的密码重置令牌失效。用户需要重新申请密码重置。

## 验证迁移

迁移完成后，验证表结构：

```sql
.schema password_resets
```

应该显示 `token_hash` 而不是 `token`。
