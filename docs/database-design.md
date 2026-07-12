# ERP系统数据库设计

## 数据库概述

- **数据库类型**：MySQL 8.0+
- **字符集**：utf8mb4
- **排序规则**：utf8mb4_unicode_ci
- **时区**：UTC

---

## 命名规范

### 表名
- 使用蛇形命名法 (snake_case)
- 使用复数形式
- 示例：`users`, `user_sessions`, `role_permissions`

### 字段名
- 使用蛇形命名法
- 示例：`created_at`, `updated_at`, `is_deleted`

### 索引名
- 主键索引：`PRIMARY`
- 普通索引：`idx_表名_字段名`
- 唯一索引：`uk_表名_字段名`
- 全文索引：`ft_表名_字段名`

### 外键名
- `fk_表名_字段名`

---

## 通用字段规范

所有表都应包含以下基础字段：

```sql
CREATE TABLE table_name (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by BIGINT UNSIGNED COMMENT '创建人ID',
    updated_by BIGINT UNSIGNED COMMENT '更新人ID',
    is_deleted TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否删除：0-否，1-是',
    deleted_at DATETIME COMMENT '删除时间',

    PRIMARY KEY (id),
    INDEX idx_created_at (created_at),
    INDEX idx_is_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='表说明';
```

---

## 核心表结构

### 1. 用户相关表 (阶段2)

#### 1.1 users - 用户表
```sql
CREATE TABLE users (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    username VARCHAR(50) NOT NULL COMMENT '用户名',
    email VARCHAR(100) NOT NULL COMMENT '邮箱',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    full_name VARCHAR(100) COMMENT '全名',
    phone VARCHAR(20) COMMENT '手机号',
    avatar_url VARCHAR(500) COMMENT '头像URL',
    is_active TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否激活',
    is_superuser TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否超级管理员',
    last_login_at DATETIME COMMENT '最后登录时间',
    last_login_ip VARCHAR(45) COMMENT '最后登录IP',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by BIGINT UNSIGNED,
    updated_by BIGINT UNSIGNED,
    is_deleted TINYINT(1) NOT NULL DEFAULT 0,
    deleted_at DATETIME,

    PRIMARY KEY (id),
    UNIQUE KEY uk_username (username),
    UNIQUE KEY uk_email (email),
    INDEX idx_is_active (is_active),
    INDEX idx_is_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';
```

#### 1.2 user_sessions - 用户会话表
```sql
CREATE TABLE user_sessions (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    token_hash VARCHAR(255) NOT NULL COMMENT 'Token哈希',
    refresh_token_hash VARCHAR(255) NOT NULL COMMENT '刷新Token哈希',
    user_agent VARCHAR(500) COMMENT '用户代理',
    ip_address VARCHAR(45) COMMENT 'IP地址',
    expires_at DATETIME NOT NULL COMMENT '过期时间',
    is_revoked TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否已撤销',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_user_id (user_id),
    INDEX idx_token_hash (token_hash),
    INDEX idx_expires_at (expires_at),
    INDEX idx_is_revoked (is_revoked),
    FOREIGN KEY fk_user_id (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户会话表';
```

#### 1.3 password_resets - 密码重置表
```sql
CREATE TABLE password_resets (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    token VARCHAR(255) NOT NULL COMMENT '重置Token',
    expires_at DATETIME NOT NULL COMMENT '过期时间',
    is_used TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否已使用',
    used_at DATETIME COMMENT '使用时间',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_user_id (user_id),
    INDEX idx_token (token),
    INDEX idx_expires_at (expires_at),
    INDEX idx_is_used (is_used),
    FOREIGN KEY fk_user_id (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='密码重置表';
```

---

### 2. 角色权限表 (阶段3)

#### 2.1 roles - 角色表
```sql
CREATE TABLE roles (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    name VARCHAR(50) NOT NULL COMMENT '角色名称',
    code VARCHAR(50) NOT NULL COMMENT '角色编码',
    description VARCHAR(500) COMMENT '角色描述',
    is_system TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否系统角色',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by BIGINT UNSIGNED,
    updated_by BIGINT UNSIGNED,
    is_deleted TINYINT(1) NOT NULL DEFAULT 0,
    deleted_at DATETIME,

    PRIMARY KEY (id),
    UNIQUE KEY uk_code (code),
    INDEX idx_is_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色表';
```

#### 2.2 permissions - 权限表
```sql
CREATE TABLE permissions (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    name VARCHAR(50) NOT NULL COMMENT '权限名称',
    code VARCHAR(100) NOT NULL COMMENT '权限编码',
    module VARCHAR(50) NOT NULL COMMENT '所属模块',
    description VARCHAR(500) COMMENT '权限描述',
    parent_id BIGINT UNSIGNED COMMENT '父权限ID',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted TINYINT(1) NOT NULL DEFAULT 0,
    deleted_at DATETIME,

    PRIMARY KEY (id),
    UNIQUE KEY uk_code (code),
    INDEX idx_module (module),
    INDEX idx_parent_id (parent_id),
    INDEX idx_is_deleted (is_deleted),
    FOREIGN KEY fk_parent_id (parent_id) REFERENCES permissions(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='权限表';
```

#### 2.3 role_permissions - 角色权限关联表
```sql
CREATE TABLE role_permissions (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    role_id BIGINT UNSIGNED NOT NULL COMMENT '角色ID',
    permission_id BIGINT UNSIGNED NOT NULL COMMENT '权限ID',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uk_role_permission (role_id, permission_id),
    INDEX idx_role_id (role_id),
    INDEX idx_permission_id (permission_id),
    FOREIGN KEY fk_role_id (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY fk_permission_id (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色权限关联表';
```

#### 2.4 user_roles - 用户角色关联表
```sql
CREATE TABLE user_roles (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    role_id BIGINT UNSIGNED NOT NULL COMMENT '角色ID',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by BIGINT UNSIGNED COMMENT '分配人ID',

    PRIMARY KEY (id),
    UNIQUE KEY uk_user_role (user_id, role_id),
    INDEX idx_user_id (user_id),
    INDEX idx_role_id (role_id),
    FOREIGN KEY fk_user_id (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY fk_role_id (role_id) REFERENCES roles(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户角色关联表';
```

---

### 3. 组织架构表 (阶段4)

#### 3.1 departments - 部门表
```sql
CREATE TABLE departments (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    name VARCHAR(100) NOT NULL COMMENT '部门名称',
    code VARCHAR(50) NOT NULL COMMENT '部门编码',
    parent_id BIGINT UNSIGNED COMMENT '父部门ID',
    level TINYINT NOT NULL DEFAULT 1 COMMENT '层级',
    sort_order INT NOT NULL DEFAULT 0 COMMENT '排序',
    leader_id BIGINT UNSIGNED COMMENT '部门负责人ID',
    description VARCHAR(500) COMMENT '部门描述',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by BIGINT UNSIGNED,
    updated_by BIGINT UNSIGNED,
    is_deleted TINYINT(1) NOT NULL DEFAULT 0,
    deleted_at DATETIME,

    PRIMARY KEY (id),
    UNIQUE KEY uk_code (code),
    INDEX idx_parent_id (parent_id),
    INDEX idx_level (level),
    INDEX idx_sort_order (sort_order),
    INDEX idx_is_deleted (is_deleted),
    FOREIGN KEY fk_parent_id (parent_id) REFERENCES departments(id) ON DELETE SET NULL,
    FOREIGN KEY fk_leader_id (leader_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='部门表';
```

#### 3.2 positions - 职位表
```sql
CREATE TABLE positions (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    name VARCHAR(100) NOT NULL COMMENT '职位名称',
    code VARCHAR(50) NOT NULL COMMENT '职位编码',
    level TINYINT NOT NULL COMMENT '职级',
    description VARCHAR(500) COMMENT '职位描述',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted TINYINT(1) NOT NULL DEFAULT 0,
    deleted_at DATETIME,

    PRIMARY KEY (id),
    UNIQUE KEY uk_code (code),
    INDEX idx_is_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='职位表';
```

#### 3.3 employee_profiles - 员工档案表
```sql
CREATE TABLE employee_profiles (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    employee_no VARCHAR(50) NOT NULL COMMENT '员工编号',
    department_id BIGINT UNSIGNED COMMENT '部门ID',
    position_id BIGINT UNSIGNED COMMENT '职位ID',
    entry_date DATE COMMENT '入职日期',
    status VARCHAR(20) NOT NULL DEFAULT 'active' COMMENT '状态：active-在职，resigned-离职',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted TINYINT(1) NOT NULL DEFAULT 0,
    deleted_at DATETIME,

    PRIMARY KEY (id),
    UNIQUE KEY uk_employee_no (employee_no),
    UNIQUE KEY uk_user_id (user_id),
    INDEX idx_department_id (department_id),
    INDEX idx_position_id (position_id),
    INDEX idx_status (status),
    INDEX idx_is_deleted (is_deleted),
    FOREIGN KEY fk_user_id (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY fk_department_id (department_id) REFERENCES departments(id) ON DELETE SET NULL,
    FOREIGN KEY fk_position_id (position_id) REFERENCES positions(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='员工档案表';
```

---

### 4. 审批流程表 (阶段5)

#### 4.1 workflow_definitions - 流程定义表
```sql
CREATE TABLE workflow_definitions (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    name VARCHAR(100) NOT NULL COMMENT '流程名称',
    code VARCHAR(50) NOT NULL COMMENT '流程编码',
    category VARCHAR(50) COMMENT '流程分类',
    description VARCHAR(500) COMMENT '流程描述',
    form_config JSON COMMENT '表单配置',
    is_active TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否启用',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by BIGINT UNSIGNED,
    updated_by BIGINT UNSIGNED,
    is_deleted TINYINT(1) NOT NULL DEFAULT 0,
    deleted_at DATETIME,

    PRIMARY KEY (id),
    UNIQUE KEY uk_code (code),
    INDEX idx_category (category),
    INDEX idx_is_active (is_active),
    INDEX idx_is_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='流程定义表';
```

#### 4.2 workflow_nodes - 流程节点表
```sql
CREATE TABLE workflow_nodes (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    workflow_id BIGINT UNSIGNED NOT NULL COMMENT '流程定义ID',
    node_key VARCHAR(50) NOT NULL COMMENT '节点标识',
    node_type VARCHAR(20) NOT NULL COMMENT '节点类型：start-开始，end-结束，approval-审批，condition-条件，parallel-并行',
    name VARCHAR(100) NOT NULL COMMENT '节点名称',
    config JSON COMMENT '节点配置',
    sort_order INT NOT NULL DEFAULT 0 COMMENT '排序',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uk_workflow_node (workflow_id, node_key),
    INDEX idx_workflow_id (workflow_id),
    INDEX idx_node_type (node_type),
    FOREIGN KEY fk_workflow_id (workflow_id) REFERENCES workflow_definitions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='流程节点表';
```

#### 4.3 workflow_edges - 流程连线表
```sql
CREATE TABLE workflow_edges (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    workflow_id BIGINT UNSIGNED NOT NULL COMMENT '流程定义ID',
    source_node VARCHAR(50) NOT NULL COMMENT '源节点标识',
    target_node VARCHAR(50) NOT NULL COMMENT '目标节点标识',
    condition JSON COMMENT '流转条件',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_workflow_id (workflow_id),
    INDEX idx_source_node (source_node),
    INDEX idx_target_node (target_node),
    FOREIGN KEY fk_workflow_id (workflow_id) REFERENCES workflow_definitions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='流程连线表';
```

#### 4.4 workflow_instances - 流程实例表
```sql
CREATE TABLE workflow_instances (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    workflow_id BIGINT UNSIGNED NOT NULL COMMENT '流程定义ID',
    instance_no VARCHAR(50) NOT NULL COMMENT '实例编号',
    title VARCHAR(200) NOT NULL COMMENT '实例标题',
    status VARCHAR(20) NOT NULL COMMENT '状态：running-进行中，completed-已完成，rejected-已拒绝，cancelled-已取消',
    current_node VARCHAR(50) COMMENT '当前节点',
    business_key VARCHAR(100) COMMENT '业务键',
    form_data JSON COMMENT '表单数据',
    initiator_id BIGINT UNSIGNED NOT NULL COMMENT '发起人ID',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    completed_at DATETIME COMMENT '完成时间',

    PRIMARY KEY (id),
    UNIQUE KEY uk_instance_no (instance_no),
    INDEX idx_workflow_id (workflow_id),
    INDEX idx_status (status),
    INDEX idx_business_key (business_key),
    INDEX idx_initiator_id (initiator_id),
    FOREIGN KEY fk_workflow_id (workflow_id) REFERENCES workflow_definitions(id),
    FOREIGN KEY fk_initiator_id (initiator_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='流程实例表';
```

#### 4.5 workflow_tasks - 审批任务表
```sql
CREATE TABLE workflow_tasks (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    instance_id BIGINT UNSIGNED NOT NULL COMMENT '流程实例ID',
    node_key VARCHAR(50) NOT NULL COMMENT '节点标识',
    node_name VARCHAR(100) NOT NULL COMMENT '节点名称',
    assignee_id BIGINT UNSIGNED COMMENT '审批人ID',
    status VARCHAR(20) NOT NULL COMMENT '状态：pending-待处理，approved-已通过，rejected-已拒绝，returned-已退回，cancelled-已取消',
    comment VARCHAR(1000) COMMENT '审批意见',
    due_date DATETIME COMMENT '到期时间',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    completed_at DATETIME COMMENT '完成时间',

    PRIMARY KEY (id),
    INDEX idx_instance_id (instance_id),
    INDEX idx_assignee_id (assignee_id),
    INDEX idx_status (status),
    INDEX idx_node_key (node_key),
    FOREIGN KEY fk_instance_id (instance_id) REFERENCES workflow_instances(id) ON DELETE CASCADE,
    FOREIGN KEY fk_assignee_id (assignee_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='审批任务表';
```

#### 4.6 workflow_approvals - 审批记录表
```sql
CREATE TABLE workflow_approvals (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    task_id BIGINT UNSIGNED NOT NULL COMMENT '任务ID',
    instance_id BIGINT UNSIGNED NOT NULL COMMENT '流程实例ID',
    approver_id BIGINT UNSIGNED NOT NULL COMMENT '审批人ID',
    action VARCHAR(20) NOT NULL COMMENT '操作：approve-通过，reject-拒绝，return-退回',
    comment VARCHAR(1000) COMMENT '审批意见',
    attachments JSON COMMENT '附件',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_task_id (task_id),
    INDEX idx_instance_id (instance_id),
    INDEX idx_approver_id (approver_id),
    INDEX idx_action (action),
    FOREIGN KEY fk_task_id (task_id) REFERENCES workflow_tasks(id) ON DELETE CASCADE,
    FOREIGN KEY fk_instance_id (instance_id) REFERENCES workflow_instances(id) ON DELETE CASCADE,
    FOREIGN KEY fk_approver_id (approver_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='审批记录表';
```

---

### 5. 采购管理表 (阶段6)

#### 5.1 suppliers - 供应商表
```sql
CREATE TABLE suppliers (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    name VARCHAR(200) NOT NULL COMMENT '供应商名称',
    code VARCHAR(50) NOT NULL COMMENT '供应商编码',
    contact_person VARCHAR(100) COMMENT '联系人',
    contact_phone VARCHAR(20) COMMENT '联系电话',
    email VARCHAR(100) COMMENT '邮箱',
    address VARCHAR(500) COMMENT '地址',
    tax_no VARCHAR(50) COMMENT '税号',
    bank_name VARCHAR(100) COMMENT '开户行',
    bank_account VARCHAR(50) COMMENT '银行账号',
    credit_level VARCHAR(20) COMMENT '信用等级',
    status VARCHAR(20) NOT NULL DEFAULT 'active' COMMENT '状态',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by BIGINT UNSIGNED,
    updated_by BIGINT UNSIGNED,
    is_deleted TINYINT(1) NOT NULL DEFAULT 0,
    deleted_at DATETIME,

    PRIMARY KEY (id),
    UNIQUE KEY uk_code (code),
    INDEX idx_status (status),
    INDEX idx_is_deleted (is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='供应商表';
```

---

## 索引设计原则

1. **主键索引**：所有表必须有主键，使用自增BIGINT
2. **外键索引**：所有外键字段创建索引
3. **查询索引**：根据查询频率创建合适索引
4. **联合索引**：遵循最左前缀原则
5. **避免过度索引**：索引会增加写入开销

---

## 数据迁移

使用 Alembic 进行数据库版本管理：

```bash
# 创建迁移
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

---

*最后更新：2024-06-20*
