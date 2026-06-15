# 尚硅谷租房平台 — 智能客服集成方案

> 基于 Spring Boot + Vue 3 + Python AI 的全栈租房管理平台，集成 ReAct Agent 智能客服与 RAG 知识库问答系统。

[![Vue](https://img.shields.io/badge/Vue-3.3-4FC08D?logo=vue.js)](https://vuejs.org/)
[![Vite](https://img.shields.io/badge/Vite-4.3-646CFF?logo=vite)](https://vitejs.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-4.9-3178C6?logo=typescript)](https://www.typescriptlang.org/)
[![Spring Boot](https://img.shields.io/badge/Spring%20Boot-3.0.5-6DB33F?logo=springboot)](https://spring.io/projects/spring-boot)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)

---

## 目录

- [核心功能](#-核心功能)
- [系统架构](#-系统架构)
- [技术栈](#-技术栈)
- [快速开始](#-快速开始)
- [项目结构](#-项目结构)
- [API 文档](#-api-文档)
- [智能客服](#-智能客服)
- [配置说明](#-配置说明)
- [测试](#-测试)
- [界面预览](#-界面预览)
- [常见问题](#-常见问题)
- [贡献指南](#-贡献指南)

---

## 核心功能

### 后端能力 (Java + Python)

| 功能模块 | 描述 | 状态 |
|---------|------|:----:|
| 公寓管理 | 公寓信息、房间、图片、设施管理 | ✅ |
| 租赁管理 | 看房预约、合同签约、退租流程 | ✅ |
| 用户管理 | 注册登录、JWT认证、个人信息 | ✅ |
| 智能客服 | ReAct Agent + RAG知识库问答 | ✅ |
| 知识库管理 | 文档上传、向量检索、知识库构建 | ✅ |
| 流式响应 | SSE 实时流式对话推送 | ✅ |
| 对话历史 | 会话持久化、历史查询、清空管理 | ✅ |
| 工具调用 | 天气查询、用户信息、报告生成 | ✅ |
| 文件存储 | MinIO 对象存储（图片/文档） | ✅ |
| 短信服务 | 阿里云短信验证码 | ✅ |

### 前端能力

| 功能模块 | 描述 | 状态 |
|---------|------|:----:|
| 管理后台 | 公寓/房间/租赁/用户管理 | ✅ |
| H5 用户端 | 移动端租房浏览、预约、个人中心 | ✅ |
| 智能客服 | H5 端内嵌 AI 对话界面 | ✅ |
| 高德地图 | 公寓位置地图展示 | ✅ |
| 数据统计 | ECharts 可视化统计面板 | ✅ |
| 深色模式 | 支持明/暗主题切换 | ✅ |

---

## 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         Vue 3 Frontend                           │
│  ┌──────────────────────────┐  ┌──────────────────────────────┐ │
│  │      管理后台 (Admin)     │  │         H5 用户端             │ │
│  │    Element Plus + Vite   │  │      Vant + TailwindCSS      │ │
│  │                          │  │                              │ │
│  │  * 公寓/房间管理         │  │  * 公寓浏览与搜索           │ │
│  │  * 租赁/合同管理         │  │  * 看房预约                 │ │
│  │  * 用户管理              │  │  * 智能客服对话             │ │
│  │  * 数据统计面板          │  │  * 个人中心                 │ │
│  └────────────┬─────────────┘  └──────────────┬───────────────┘ │
└───────────────┼────────────────────────────────┼────────────────┘
                │                                │
                ▼                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Spring Boot 3 Backend (Java 17)               │
│                                                                  │
│  ┌──────────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │    Admin API     │  │   App API    │  │   Agent Proxy    │  │
│  │  (管理端接口)     │  │  (H5端接口)   │  │  (AI 代理转发)   │  │
│  └────────┬─────────┘  └──────┬───────┘  └────────┬─────────┘  │
│           │                   │                    │             │
│     ┌─────┴─────┬─────────────┴────────────────────┘            │
│     ▼           ▼             ▼                                  │
│  ┌──────┐  ┌────────┐   ┌──────────┐                           │
│  │MySQL │  │ MinIO  │   │   JWT    │                           │
│  │(业务)│  │(图片)  │   │  (认证)   │                           │
│  └──────┘  └────────┘   └──────────┘                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                Python AI Engine (FastAPI :8000)                  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    ReAct Agent                             │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐   │   │
│  │  │  思考    │→ │ 工具调用  │→ │       观察           │   │   │
│  │  │(Thought) │  │ (Action) │  │   (Observation)      │   │   │
│  │  └──────────┘  └──────────┘  └──────────────────────┘   │   │
│  │                         ↓ 循环                            │   │
│  └────────┬─────────────────────────────────────────────────┘   │
│           │                                                      │
│     ┌─────┴─────┬─────────────┬─────────────┐                  │
│     ▼           ▼             ▼             ▼                  │
│  ┌──────┐  ┌────────┐   ┌──────────┐  ┌──────────┐           │
│  │ RAG  │  │ 天气   │   │ 用户信息  │  │  报告    │           │
│  │检索  │  │ 查询   │   │  获取     │  │  生成    │           │
│  └──┬───┘  └────────┘   └──────────┘  └──────────┘           │
│     │                                                           │
│     ▼                                                           │
│  ┌──────────┐                                                   │
│  │ChromaDB  │  向量数据库                                       │
│  │(Vector)  │                                                   │
│  └──────────┘                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 技术栈

### 后端

| 技术 | 版本 | 用途 |
|------|------|------|
| Java | 17 | 运行环境 |
| Spring Boot | 3.0.5 | 业务后端框架 |
| MyBatis-Plus | 3.5.3 | ORM 持久层 |
| MySQL | 8.0 | 关系型数据库 |
| MinIO | 8.2 | 对象存储（图片/文件） |
| JWT (jjwt) | 0.11 | 无状态认证 |
| Knife4j | 4.1 | API 文档生成 |
| Python | 3.10+ | AI 引擎运行环境 |
| FastAPI | 0.109 | AI 引擎 Web 框架 |
| LangChain | - | Agent 编排框架 |
| ChromaDB | - | 向量数据库 |
| 通义千问 (qwen3-max) | - | LLM 大模型 |
| text-embedding-v3 | - | Embedding 模型 |

### 前端

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue | 3.3 | 前端框架 |
| TypeScript | ~4.7.4 | 类型安全 |
| Vite | 4.3 | 构建工具 |
| Pinia | 2.1 | 状态管理 |
| Element Plus | 2.3 | 管理后台 UI 组件库 |
| Vant | 4.6 | H5 移动端 UI 组件库 |
| TailwindCSS | 3.3 | H5 原子化 CSS |
| ECharts | 5.4 | 数据可视化 |
| 高德地图 JSAPI | - | 地图展示 |
| Axios | 1.4 | HTTP 客户端 |

---

## 快速开始

### 环境要求

| 工具 | 最低版本 | 说明 |
|------|:------:|------|
| Python | 3.10+ | AI 引擎运行环境 |
| Java JDK | 17+ | 后端运行环境 |
| Node.js | 16+ | 前端运行环境 |
| Maven | 3.8+ | Java 项目构建 |
| MySQL | 8.0+ | 业务数据库 |
| MinIO | - | 对象存储服务 |

### 1. 克隆仓库

```bash
git clone <your-repo-url>
cd gongyuzuping
```

### 2. 配置环境变量

**Python Agent 配置：**

| 配置文件 | 说明 |
|---------|------|
| `agent_project/config/agent.yml` | Agent 外部数据路径 |
| `agent_project/config/rag.yml` | LLM 模型配置（API Key 等） |
| `agent_project/config/chroma.yml` | 向量库配置 |
| `agent_project/config/prompt.yml` | 提示词配置 |

**Java 后端配置：**

| 配置文件 | 说明 |
|---------|------|
| `lease/web/web-admin/src/main/resources/application.yml` | 管理端数据库/端口配置 |
| `lease/web/web-app/src/main/resources/application.yml` | 移动端数据库/端口配置 |

**前端环境变量：**

| 配置文件 | 说明 |
|---------|------|
| `rentHouseAdmin/.env.development` | 管理后台开发环境变量 |
| `rentHouseAdmin/.env.production` | 管理后台生产环境变量 |
| `rentHouseH5/.env.development` | H5 端开发环境变量 |
| `rentHouseH5/.env.production` | H5 端生产环境变量 |

### 3. 安装依赖

```bash
# 安装 Python 依赖
cd agent_project
pip install -r requirements_api.txt

# 安装前端依赖 - 管理后台
cd ../rentHouseAdmin
npm install

# 安装前端依赖 - H5 用户端
cd ../rentHouseH5
npm install
```

### 4. 启动服务

> **注意：** 请确保 MySQL 和 MinIO 服务已启动。

**方式一：一键启动（Windows）**

```bash
start_agent_services.bat
```

**方式二：一键启动（Linux/Mac）**

```bash
bash start_agent_services.sh
```

**方式三：手动启动（各服务独立启动）**

```bash
# 1. 启动 Python Agent 服务（端口 8000）
cd agent_project
python api_server.py

# 2. 启动 Java Web-App 服务（端口 8081）
cd lease/web/web-app
mvn spring-boot:run

# 3. 启动 H5 前端（端口 5173）
cd rentHouseH5
npm run dev

# 4. 启动管理后台（端口 5174，可选）
cd rentHouseAdmin
npm run dev
```

### 5. 访问服务

| 服务 | 地址 | 说明 |
|------|------|------|
| Agent API 文档 | http://localhost:8000/docs | Swagger 文档 |
| Java 后端 (App) | http://localhost:8081 | H5 端 API |
| H5 用户端 | http://localhost:5173 | 移动端页面 |
| 管理后台 | http://localhost:5174 | 后台管理页面 |

---

## 项目结构

```
gongyuzuping/
├── agent_project/                  # Python AI 引擎
│   ├── agent/                      # Agent 模块
│   │   ├── react_agent.py          # ReAct Agent 主控制器
│   │   └── tools/                  # 工具模块
│   │       ├── agent_tools.py      # RAG/天气/用户信息/报告工具
│   │       └── middleware.py       # 中间件（监控/日志/提示词切换）
│   ├── api_server.py               # FastAPI 服务入口
│   ├── app.py                      # Streamlit 调试界面
│   ├── config/                     # 配置文件
│   │   ├── agent.yml               # Agent 外部数据配置
│   │   ├── rag.yml                 # RAG 模型配置
│   │   ├── chroma.yml              # 向量库配置
│   │   └── prompt.yml              # 提示词配置
│   ├── data/                       # 知识库数据目录
│   │   └── external/               # 外部数据 (CSV)
│   ├── model/                      # LLM 模型工厂
│   │   └── factory.py
│   ├── prompts/                    # 提示词模板
│   │   ├── main_prompt.txt         # ReAct Agent 系统提示词
│   │   ├── rag_summarize.txt       # RAG 总结提示词
│   │   └── report_prompt.txt       # 报告生成提示词
│   ├── rag/                        # RAG 系统
│   │   ├── rag_service.py          # RAG 总结服务
│   │   └── vector_store.py         # ChromaDB 向量存储
│   ├── utils/                      # 工具模块
│   │   ├── config_handler.py       # 配置加载器
│   │   ├── file_handler.py         # 文件处理器
│   │   ├── logger_handler.py       # 日志处理器
│   │   ├── path_tool.py            # 路径工具
│   │   └── prompt_looader.py       # 提示词加载器
│   ├── chroma_db/                  # 向量数据库持久化目录
│   ├── uploads/                    # 文件上传目录
│   ├── logs/                       # 日志目录
│   ├── requirements_api.txt        # API 服务依赖
│   └── test_api.py                 # API 测试脚本
│
├── lease/                          # Java Spring Boot 后端
│   ├── common/                     # 公共模块
│   │   └── src/                    # 工具类、异常、配置
│   ├── model/                      # 数据模型模块
│   │   └── src/                    # 实体类、Mapper、VO
│   └── web/                        # Web 模块
│       ├── web-admin/              # 管理端 API
│       │   └── src/                # Controller、Service
│       └── web-app/                # 移动端 API
│           └── src/                # Controller、Service
│
├── rentHouseAdmin/                 # Vue 3 管理后台
│   ├── src/
│   │   ├── api/                    # API 接口封装
│   │   ├── components/             # 公共组件
│   │   ├── views/                  # 页面视图
│   │   │   ├── apartmentManagement/# 公寓管理
│   │   │   ├── rentManagement/     # 租赁管理
│   │   │   ├── userManagement/     # 用户管理
│   │   │   ├── system/             # 系统配置
│   │   │   └── home/               # 首页/数据统计
│   │   ├── router/                 # 路由配置
│   │   ├── store/                  # Pinia 状态管理
│   │   └── utils/                  # 工具函数
│   └── vite.config.ts
│
├── rentHouseH5/                    # Vue 3 H5 用户端
│   ├── src/
│   │   ├── api/                    # API 接口封装
│   │   │   ├── agent/              # 智能客服 API
│   │   │   ├── search/             # 搜索 API
│   │   │   ├── template/           # 字典/模板 API
│   │   │   └── user/               # 用户 API
│   │   ├── assets/                 # 静态资源
│   │   ├── components/             # 公共组件
│   │   │   ├── ApartmentCard/      # 公寓卡片
│   │   │   ├── LoadingButton/      # 加载按钮
│   │   │   ├── NavBar/             # 导航栏
│   │   │   ├── PullDownRefreshContainer/ # 下拉刷新容器
│   │   │   ├── RoomCard/           # 房间卡片
│   │   │   ├── SearchBar/          # 搜索栏
│   │   │   ├── SvgIcon/            # SVG 图标
│   │   │   └── Tabbar/             # 底部导航栏
│   │   ├── views/                  # 页面视图
│   │   │   ├── agentChat/          # 智能客服对话
│   │   │   ├── agreement/          # 租约详情
│   │   │   ├── apartmentDetail/    # 公寓详情
│   │   │   ├── appointment/        # 看房预约
│   │   │   ├── browsingHistory/    # 浏览历史
│   │   │   ├── group/              # 团购
│   │   │   ├── login/              # 登录
│   │   │   ├── message/            # 消息
│   │   │   ├── myAgreement/        # 我的租约
│   │   │   ├── myAppointment/      # 我的预约
│   │   │   ├── myRoom/             # 我的房间
│   │   │   ├── roomDetail/         # 房间详情
│   │   │   ├── search/             # 搜索
│   │   │   └── userCenter/         # 个人中心
│   │   ├── router/                 # 路由配置
│   │   ├── store/                  # Pinia 状态管理
│   │   │   └── modules/            # user / darkMode / cachedView
│   │   ├── hooks/                  # 组合式函数
│   │   ├── directives/             # 自定义指令
│   │   ├── icons/                  # SVG 图标资源
│   │   ├── styles/                 # 全局样式
│   │   ├── utils/                  # 工具函数
│   │   │   └── http/               # Axios 封装
│   │   ├── enums/                  # 枚举常量
│   │   ├── config/                 # 全局配置（高德地图等）
│   │   ├── App.vue                 # 根组件
│   │   └── main.ts                 # 入口文件
│   ├── .env.development            # 开发环境变量
│   ├── .env.production             # 生产环境变量
│   ├── vite.config.ts              # Vite 配置
│   ├── tailwind.config.js          # TailwindCSS 配置
│   ├── postcss.config.js           # PostCSS 配置（vw 适配）
│   └── package.json
│
├── images/                         # 公寓/房间图片资源
├── start_agent_services.bat        # Windows 一键启动脚本
├── start_agent_services.sh         # Linux/Mac 一键启动脚本
└── README.md
```

---

## API 文档

### Agent 智能客服 API（Python FastAPI）

**发送消息：**

```http
POST /api/chat
Content-Type: application/json

{
  "message": "租房押金一般是多少？",
  "user_id": "user_001",
  "session_id": "optional-session-id"
}
```

**响应：**

```json
{
  "response": "租房押金通常为1-3个月租金...",
  "success": true
}
```

### Agent API 端点一览

| 端点 | 方法 | 描述 |
|------|:----:|------|
| `/api/chat` | POST | 发送消息获取回复 |
| `/api/chat/stream` | POST | 流式对话 (SSE) |
| `/api/chat/history` | POST | 获取对话历史 |
| `/api/chat/history` | DELETE | 清空对话历史 |
| `/api/upload` | POST | 上传知识库文档 |
| `/api/health` | GET | 健康检查 |

> 完整 Agent API 文档请访问：http://localhost:8000/docs

### 管理后台 API（Java Spring Boot）

| 端点 | 方法 | 描述 |
|------|:----:|------|
| `/admin/apartment/*` | CRUD | 公寓信息管理 |
| `/admin/room/*` | CRUD | 房间信息管理 |
| `/admin/lease/*` | CRUD | 租赁合同管理 |
| `/admin/user/*` | CRUD | 用户信息管理 |
| `/admin/file/upload` | POST | 图片上传 (MinIO) |

### H5 用户端 API（Java Spring Boot）

| 端点 | 方法 | 描述 |
|------|:----:|------|
| `/app/apartment/list` | GET | 公寓列表 |
| `/app/apartment/detail` | GET | 公寓详情 |
| `/app/room/detail` | GET | 房间详情 |
| `/app/appointment/*` | CRUD | 看房预约 |
| `/app/user/login` | POST | 用户登录 |
| `/app/agent/**` | POST | AI 客服代理转发 |

---

## 智能客服

### ReAct Agent 工作流程

```
用户提问
    │
    ▼
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  思考    │ --> │  行动    │ --> │  观察    │ --> │ 最终回答 │
│(Thought) │     │(Action)  │     │(Observe) │     │(Answer)  │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
    ^                  │                 │
    └──────────────────┴─────────────────┘
             循环直到信息充足
```

Agent 采用 **ReAct (Reasoning + Acting)** 模式，在思考、行动、观察之间循环迭代，直到收集到足够的信息生成最终回答。

### 可用工具列表

| 工具名称 | 功能描述 | 参数 |
|---------|---------|------|
| `rag_summarize` | 从向量知识库检索租房相关资料 | `query: str` |
| `get_weather` | 获取指定城市天气信息 | `city: str` |
| `get_user_location` | 获取当前用户所在城市 | 无 |
| `get_user_id` | 获取当前用户唯一标识 | 无 |
| `get_current_month` | 获取系统当前月份 | 无 |
| `fetch_external_data` | 检索用户租房使用记录 | `user_id, month` |
| `fill_context_for_report` | 触发报告生成上下文注入 | 无 |

### RAG 知识库配置

```yaml
# agent_project/config/chroma.yml
collection_name: agent
persist_directory: chroma_db
k: 3                         # 检索返回数量
chunk_size: 200              # 文档分块大小
chunk_overlap: 20            # 分块重叠大小
separators: ["\n", "\n\n", " ", "  ", "\t", ".", "?"]
allow_knowledge_file_type: ["pdf", "txt"]
```

---

## 配置说明

### Agent 配置 (`agent_project/config/agent.yml`)

```yaml
external_data_path: data/external/records.csv
```

### RAG 模型配置 (`agent_project/config/rag.yml`)

```yaml
chat_model_name: qwen3-max
embedding_model_name: text-embedding-v3
```

### H5 端 Vite 代理配置

开发环境下通过 Vite 代理转发 API 请求：

```typescript
// rentHouseH5/vite.config.ts
server: {
  proxy: {
    "/app": {
      target: env.VITE_APP_BASE_URL      // Java 后端
    },
    "/api": {
      target: "http://localhost:8000",    // Python Agent
      changeOrigin: true
    },
    "/minio": {
      target: "http://localhost:9000",    // MinIO 对象存储
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/minio/, "")
    }
  }
}
```

### 知识库文档管理

- **支持的文档格式：** PDF、TXT
- **上传方式：** 通过 API `/api/upload` 上传后自动加载到向量库
- **知识库内容：** 租房常见问题、合同签约、费用说明、维修责任、退租指南等

---

## 测试

```bash
# 测试 Agent API
cd agent_project
python test_api.py

# 测试文件上传
python test_upload.py

# 测试 Java 后端
cd lease
mvn test
```

---

## 界面预览

### H5 用户端 - 首页浏览

```
┌──────────────────────────────────────┐
│  🏠 租房系统                    🔍 │
├──────────────────────────────────────┤
│                                      │
│  ┌──────────────────────────────┐   │
│  │     公寓封面大图轮播          │   │
│  └──────────────────────────────┘   │
│                                      │
│  ┌─────────┐ ┌─────────┐           │
│  │ 公寓A   │ │ 公寓B   │  ...      │
│  │ ¥3000  │ │ ¥2500  │           │
│  └─────────┘ └─────────┘           │
├──────────────────────────────────────┤
│  🏠 找房  🤖 客服  🏠 我的  💬 消息  👤 我的  │
└──────────────────────────────────────┘
```

### H5 智能客服对话

```
┌──────────────────────────────────────┐
│  ← 智能客服                          │
├──────────────────────────────────────┤
│                                      │
│  🤖：您好！有什么可以帮助您？          │
│                                      │
│  👤：租房押金一般是多少？              │
│                                      │
│  🤖：租房押金通常为1-3个月租金...      │
│     根据相关资料，押金在退租时         │
│     若无损坏会全额退还...              │
│                                      │
│  ┌──────────────────────────────┐   │
│  │  输入您的问题...           📎  │   │
│  └──────────────────────────────┘   │
└──────────────────────────────────────┘
```

### 管理后台 - 数据面板

```
┌─────────────────────────────────────────────────────────┐
│  租房管理后台            [通知] [用户] [退出]    		      │
├──────────┬──────────────────────────────────────────────┤
│          │  数据概览                                      │
│  仪表盘   │  ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│  公寓管理 │  │ 公寓数  │ │ 房间数  │ │ 用户数  │       │
│  房间管理 │  │   12    │ │  156   │ │  328   │       │
│  租赁管理 │  └─────────┘ └─────────┘ └─────────┘       │
│  用户管理 │                                              │
│  系统配置 │  ┌──────────────────────────────────────┐   │
└──────────┴──────────────────────────────────────────────┘
```

---

## 常见问题

<details>
<summary><b>Q: 启动 Python Agent 时提示找不到模块？</b></summary>

请确保已安装所有依赖：

```bash
cd agent_project
pip install -r requirements_api.txt
```

如果仍然缺少 LangChain 等依赖，可能需要安装完整依赖包。
</details>

<details>
<summary><b>Q: H5 页面请求 API 报 404？</b></summary>

1. 确认 Java 后端已启动（端口 8081）
2. 确认 Python Agent 已启动（端口 8000）
3. 确认 Vite 代理配置正确（见 `vite.config.ts`）
4. 确认 `.env.development` 中 `VITE_APP_BASE_URL` 配置正确
</details>

<details>
<summary><b>Q: 如何添加新的知识库文档？</b></summary>

通过 API 上传：

```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@your-document.pdf"
```

支持的格式：PDF、TXT
</details>

<details>
<summary><b>Q: Node.js 版本不兼容怎么办？</b></summary>

项目要求 Node.js 16+。建议使用 [nvm](https://github.com/nvm-sh/nvm) 管理 Node 版本：

```bash
nvm install 16
nvm use 16
```
</details>

---

## 贡献指南

### Git 提交规范

本项目使用 `husky` + `commitlint` 规范 Git 提交信息，遵循 [Angular](https://github.com/conventional-changelog/conventional-changelog/tree/master/packages/conventional-changelog-angular) 规范。

**提交类型：**

| 类型 | 说明 |
|:-----|------|
| `feat` | 新功能 |
| `fix` | 修复 Bug |
| `perf` | 性能优化 |
| `style` | 代码风格调整 |
| `refactor` | 代码重构 |
| `test` | 测试相关 |
| `docs` | 文档更新 |
| `chore` | 构建/工具/依赖更新 |
| `revert` | 撤销修改 |
| `ci` | CI 配置 |

**提交格式：**

```bash
<type>(<scope>): <subject>

# 示例
feat(agent): 添加天气查询工具
fix(h5): 修复预约页面日期选择问题
docs(readme): 更新快速开始指南
```

### 分支管理

- `main` - 主分支，保持稳定
- `develop` - 开发分支
- `feature/*` - 功能分支
- `fix/*` - 修复分支

