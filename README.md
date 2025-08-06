# Multi-User SQL Agent Web Application

## 概述 (Overview)

基于 LangGraph 的多用户 SQL 代理 Web 应用程序。允许不同用户通过自然语言独立操作各自的数据库，实现完全的用户隔离。

This application demonstrates how to build a multi-user web app using LangGraph's SQL agent functionality. It allows different users to independently operate their own databases through natural language queries, with complete isolation between users.

![Multi-User SQL Agent Interface](https://github.com/user-attachments/assets/f871ed4d-2196-4ff5-9336-5d519bbfc7fc)

## 核心特性 (Key Features)

- **多用户支持**: 每个用户拥有独立的数据库环境
- **自然语言接口**: 所有数据库操作均通过自然语言实现  
- **用户认证**: 基于会话的身份验证系统
- **RESTful API**: 清晰的 HTTP API 接口
- **实时聊天界面**: 交互式 Web UI 支持自然语言查询
- **安全隔离**: 用户之间无法访问彼此的数据

## 系统架构 (Architecture)

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Frontend  │    │   FastAPI       │    │   SQL Agent     │
│   (HTML/JS)     │───▶│   Backend       │───▶│   (LangGraph)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                               │                        │
                               ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Session Store  │    │   User DBs      │
                       │  (In-memory)    │    │   (SQLite)      │
                       └─────────────────┘    └─────────────────┘
```

## 快速开始 (Quick Start)

### 1. 安装依赖 (Install Dependencies)
```bash
chmod +x setup.sh
./setup.sh
```

### 2. 启动应用 (Start Application)
```bash
source venv/bin/activate  # if using virtual environment
python app.py
```

### 3. 访问应用 (Access Application)
打开浏览器访问: `http://localhost:8000`

## 使用示例 (Usage Examples)

### 用户 A 的会话:
```
用户: "我的数据库中有哪些表？"
代理: "您的数据库包含以下表: customers, orders"

用户: "显示销售额最高的前3个客户"
代理: "以下是您销售额最高的3个客户:
1. Alice Johnson - $1,079.98
2. Bob Smith - $89.98  
3. Carol Davis - $299.99"
```

### 用户 B 的会话 (完全隔离):
```
用户: "我有哪些表？"
代理: "您的数据库包含: employees, departments, projects"

用户: "哪个部门员工最多？"
代理: "工程部有45名员工，是您组织中人数最多的部门。"
```

## API 接口 (API Endpoints)

- `POST /auth/login` - 创建或恢复用户会话
- `GET /auth/logout` - 结束用户会话
- `POST /database/upload` - 上传 CSV 数据创建数据库
- `POST /database/sample-data` - 创建示例数据
- `POST /chat` - 发送自然语言查询
- `GET /database/info` - 获取数据库信息
- `GET /health` - 健康检查

## 安全特性 (Security Features)

- **数据库隔离**: 每个用户拥有独立的 SQLite 数据库文件
- **会话管理**: 安全的用户会话管理机制
- **输入验证**: 所有输入在处理前进行验证
- **SQL 注入防护**: 使用参数化查询和 LangChain 内置保护
- **访问控制**: 用户只能访问自己的数据

## 测试 (Testing)

运行基础功能测试:
```bash
python test_app.py
```

测试 API 接口:
```bash
pip install pytest httpx
python -m pytest test_app.py -v
```