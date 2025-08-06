
# Multi-User SQL Agent 💬🔐

一个基于 LangGraph 的多用户 SQL 代理 Web 应用程序。它允许不同用户通过自然语言独立、安全地操作各自的数据库，实现了完全的用户和数据隔离。

This application demonstrates how to build a multi-user web app using LangGraph's SQL agent functionality. It allows different users to independently operate their own databases through natural language queries, with complete isolation between users.

## 🌟 核心特性 (Key Features)

* **👤 多用户支持** : 每个用户拥有完全独立的数据库会话和环境。
* **💬 自然语言接口** : 所有数据库操作（查询、分析）均通过自然语言对话完成。
* **🔐 用户认证** : 基于会话的身份验证系统，确保用户身份安全。
* ** izolasyon (隔离)**: 强化的安全隔离机制，用户之间无法访问彼此的数据或数据库文件。
* **📊 数据上传** : 支持用户上传自己的 CSV 文件，并立即开始通过自然语言进行查询。
* **🌐 RESTful API** : 提供清晰、标准的 HTTP API 接口，易于集成和扩展。
* **🖥️ 实时聊天界面** : 提供交互式 Web UI，支持流畅的自然语言查询体验。

## 🛠️ 技术栈 (Technology Stack)

* **后端** : FastAPI
* **AI Agent** : LangChain & LangGraph
* **数据库** : SQLite (每个用户一个独立数据库)
* **前端** : HTML, CSS, JavaScript (Vanilla)
* **会话管理** : 内存存储

## 🏗️ 系统架构 (Architecture)

**代码段**

```
graph TD
    subgraph User Interface
        A[🌐 Web Frontend (HTML/JS)]
    end

    subgraph Backend Services
        B[🚀 FastAPI Backend]
        C[🧠 SQL Agent (LangGraph)]
    end

    subgraph Data & Session Layer
        D[(🗄️ Session Store<br>In-memory)]
        E[(💾 User Databases<br>SQLite Files)]
    end

    A -- HTTP Requests --> B
    B -- Authenticates via --> D
    B -- Forwards query to --> C
    C -- Executes SQL on --> E
    E -- Returns data to --> C
    C -- Returns answer to --> B
    B -- Streams response to --> A
```

## 🚀 快速开始 (Quick Start)

### 1. 环境准备 (Prerequisites)

* Python 3.9+
* 一个 OpenAI API 密钥 (或其他 LangChain 支持的 LLM)

### 2. 安装依赖 (Install Dependencies)

克隆本仓库，然后运行安装脚本。该脚本会创建一个虚拟环境并安装所有必需的包。

**Bash**

```
git clone https://github.com/your-username/your-repo.git
cd your-repo

chmod +x setup.sh
./setup.sh
```

### 3. 配置环境变量 (Configure Environment)

创建一个 `.env` 文件，用于存放您的 API 密钥。

**Bash**

```
# 在项目根目录创建一个 .env 文件
cp .env.example .env
```

然后编辑 `.env` 文件，填入您的 OpenAI API Key。

**代码段**

```
# .env
OPENAI_API_KEY="sk-YourSecretApiKey"
```

### 4. 启动应用 (Start Application)

激活虚拟环境并启动 FastAPI 应用。

**Bash**

```
# 激活虚拟环境
source venv/bin/activate

# 启动服务
python app.py
```

### 5. 访问应用 (Access Application)

应用启动后，在浏览器中打开以下地址：

[http://localhost:8000](https://www.google.com/search?q=http://localhost:8000)

## 💡 使用示例 (Usage Examples)

系统为每个新用户会话自动创建隔离的数据库环境。

#### 会话 A (用户 Alice)

1. **上传数据** : Alice 上传一个 `sales.csv` 文件。
2. **开始对话** :

> **Alice** : "我的数据库里有哪些表？"
> **AI 代理** : "您的数据库包含以下表: `sales`"
> **Alice** : "显示销售额最高的前3个客户是谁？"
> **AI 代理** : "好的，以下是销售额最高的3位客户:
>
> 1. Alice Johnson - $1,079.98
> 2. Bob Smith - $899.98
> 3. Carol Davis - $299.99"

---

#### 会话 B (用户 Bob - 完全隔离)

1. **加载示例数据** : Bob 点击 "加载示例数据"，系统为其创建了一个关于公司员工的数据库。
2. **开始对话** :

> **Bob** : "我有哪些表？"
> **AI 代理** : "您的数据库包含: `employees`, `departments`, `projects`"
> **Bob** : "哪个部门的员工最多？"
> **AI 代理** : "工程部拥有45名员工，是您组织中人数最多的部门。"

## 🔌 API 接口 (API Endpoints)

| 方法     | 路径                      | 描述                                   |
| -------- | ------------------------- | -------------------------------------- |
| `POST` | `/auth/login`           | 创建或恢复一个用户会话，返回会话ID。   |
| `GET`  | `/auth/logout`          | 结束当前用户会话。                     |
| `POST` | `/database/upload`      | 上传 CSV 文件，为当前用户创建数据库。  |
| `POST` | `/database/sample-data` | 为当前用户加载内置的示例数据集。       |
| `GET`  | `/database/info`        | 获取当前用户数据库的元信息（如表名）。 |
| `POST` | `/chat`                 | 发送自然语言查询并获取流式响应。       |
| `GET`  | `/health`               | 应用健康检查接口。                     |

导出到 Google 表格

## 🔒 安全特性 (Security Features)

* **数据库隔离** : 每个用户会话都与一个独立的 SQLite 数据库文件绑定，从物理层面防止数据交叉访问。
* **会话管理** : 通过安全的会话 ID 管理用户状态，确保每个请求都与正确的数据库关联。
* **输入验证** : 后端对所有传入的请求和文件进行严格的验证。
* **SQL 注入防护** : 利用 LangChain Agent 和参数化查询的内置机制，有效防范 SQL 注入风险。
* **访问控制** : 强制执行访问控制，确保用户只能通过授权的 API 与自己的数据进行交互。

## ✅ 测试 (Testing)

项目包含一套测试用例，用于验证核心功能和 API 接口。

**Bash**

```
# 安装测试依赖
pip install pytest httpx

# 激活虚拟环境
source venv/bin/activate

# 运行测试
python -m pytest test_app.py -v
```

## 🤝 贡献与支持 (Contributing & Support)

如果您觉得这个项目对您有帮助，或者您喜欢我们的工作，请点亮一颗 ⭐  **Star** ！您的支持是我们持续改进和贡献更多开源项目的最大动力！

我们欢迎任何形式的贡献，无论是提交 issue、创建 pull request 还是提供新的想法。

## 📜 许可证 (License)

本项目基于 [MIT License](https://www.google.com/search?q=LICENSE) 开源。

---
