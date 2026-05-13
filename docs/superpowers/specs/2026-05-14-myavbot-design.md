# MyAVBot 设计文档

## 概述

基于 Telegram Bot 的欧美成人女优资料查询、最新作品浏览、磁力搜索工具。面向中文用户。

## 架构

### 微服务模式（Docker Compose）

```
┌─────────────┐     ┌─────────────────┐
│  Telegram    │────▶│  Bot Service    │
│  User        │     │  (:8080)        │
└─────────────┘     └────────┬─────────┘
                             │ HTTP REST
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
   │ Crawler      │  │ Magnet       │  │ MySQL        │
   │ Service      │  │ Search       │  │ (:3306)      │
   │ (:8081)      │  │ Service      │  │              │
   └──────────────┘  │ (:8082)      │  └──────────────┘
                      └──────────────┘
```

### 服务间通信

- **查询类**（查女优资料、查作品）：HTTP REST 同步调用
- **耗时操作**（爬取新数据、磁力搜索）：Redis 任务队列异步处理，bot 先返回 "搜索中"，完成后主动推送

## 数据模型

### actresses（女优资料）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK AUTO | 主键 |
| name | VARCHAR(100) | 艺名 |
| aliases | TEXT JSON | 别名列表 |
| birthday | DATE | 出生日期 |
| birthplace | VARCHAR(100) | 出生地 |
| height | SMALLINT | 身高 cm |
| measurements | VARCHAR(50) | 三围 |
| bust | VARCHAR(20) | 罩杯 |
| country | VARCHAR(50) | 国籍 |
| career_start | YEAR | 出道年份 |
| bio_text | TEXT | 简介 |
| profile_image | VARCHAR(500) | 头像 URL |
| social_links | TEXT JSON | 社交链接 |
| status | ENUM('active','retired','unknown') | 状态 |
| source_url | VARCHAR(500) | 数据来源 |
| updated_at | DATETIME | 更新时间 |
| created_at | DATETIME | 创建时间 |

### works（作品）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK AUTO | 主键 |
| title | VARCHAR(300) | 作品标题 |
| work_id | VARCHAR(50) | 作品编号 |
| studio_id | INT FK | 关联片商 |
| release_date | DATE | 发行日期 |
| duration | SMALLINT | 时长（分钟）|
| cover_image | VARCHAR(500) | 封面 URL |
| description | TEXT | 描述 |
| genres | TEXT JSON | 标签列表 |
| cast_ids | TEXT JSON | 参演女优 ID 列表 |
| rating | DECIMAL(2,1) | 评分 |
| source_url | VARCHAR(500) | 来源 |
| updated_at | DATETIME | 更新时间 |
| created_at | DATETIME | 创建时间 |

### studios（片商）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK AUTO | 主键 |
| name | VARCHAR(200) | 名称 |
| country | VARCHAR(50) | 国家 |
| website | VARCHAR(500) | 官网 |
| logo | VARCHAR(500) | Logo |
| description | TEXT | 简介 |

### magnet_links（磁力链接）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK AUTO | 主键 |
| info_hash | VARCHAR(40) UNIQUE | BT Hash |
| title | VARCHAR(500) | 种子标题 |
| file_size | BIGINT | 文件大小 |
| file_count | INT | 文件数 |
| source_site | VARCHAR(100) | 来源站 |
| work_id | VARCHAR(50) | 关联作品(nullable)|
| category | ENUM('adult_eu','general') | 分类 |
| seeders | INT | 做种数 |
| leechers | INT | 下载数 |
| scraped_at | DATETIME | 采集时间 |
| created_at | DATETIME | 创建时间 |

### search_cache（搜索缓存）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK AUTO | 主键 |
| query_hash | VARCHAR(64) UNIQUE | 搜索词 SHA256 |
| query_type | ENUM('actress','work','magnet')| 类型 |
| result_json | JSON | 缓存结果 |
| expires_at | DATETIME | 过期时间 |
| created_at | DATETIME | 创建时间 |

### bot_users（用户）

| 字段 | 类型 | 说明 |
|------|------|------|
| user_id | BIGINT PK | Telegram User ID |
| username | VARCHAR(100) | 用户名 |
| first_name | VARCHAR(100) | 名 |
| last_name | VARCHAR(100) | 姓 |
| language | VARCHAR(10) | 语言偏好 |
| is_admin | BOOLEAN | 管理员标记 |
| is_banned | BOOLEAN | 封禁标记 |
| usage_count | INT | 使用次数 |
| last_active | DATETIME | 最后活跃 |
| created_at | DATETIME | 创建时间 |

## 服务 API 设计

### Crawler Service (:8081)

```
GET  /api/v1/actress/search?q={name}&page={n}
GET  /api/v1/actress/{id}
POST /api/v1/actress/refresh/{id}
GET  /api/v1/actress/new?since={days}
GET  /api/v1/work/search?q={title}&page={n}
GET  /api/v1/work/{id}
GET  /api/v1/work/latest?studio={id}&page={n}
GET  /api/v1/work/by-actress/{actress_id}
GET  /api/v1/studio/list
GET  /api/v1/studio/{id}
```

### Magnet Service (:8082)

```
GET  /api/v1/magnet/search?q={keyword}&category={eu|general}&page={n}
GET  /api/v1/magnet/{id}
POST /api/v1/magnet/batch-search
GET  /api/v1/magnet/task/{task_id}
```

## Bot 命令

| 命令 | 功能 | 参数 |
|------|------|------|
| /start | 欢迎 + 使用说明 | - |
| /help | 帮助菜单 | - |
| /actress \<name\> | 搜索女优 | 姓名 |
| /work \<title/id\> | 搜索作品 | 作品名/编号 |
| /latest [studio] | 最新作品 | 可选：片商 |
| /magnet \<keyword\> | 磁力搜索 | 关键词 |
| /new | 近期新人 | - |
| /studio \<name\> | 片商信息 | 片商名 |
| /trending | 热门 | - |

## 数据源

- **女优资料 + 作品**：爬虫采集（iafd, adultdvdempire, data18 等）
- **磁力链接**：爬取磁力索引站（默认过滤欧美成人内容，支持通用搜索开关）
- **缓存策略**：热门搜索缓存 1 小时，女优资料缓存 24 小时

## 反爬策略

### 爬虫执行器分层

```
目标网站请求
    │
    ├── 无反爬 / 简单反爬 ──→ HTTP Executor (httpx)
    │                         快速、轻量、无头
    │
    └── 有反爬检测 ──→ CloakBrowser Executor
                       Playwright API 兼容
                       源码级 Chromium 指纹修补
                       30/30 反检测全过
                           │
                           └── 代理轮换（可选）
```

### CloakBrowser 整合方式

- **定位**：专项解决反爬检测，不是在所有场景使用
- **集成**：Crawler Service 内部抽象 `CrawlerExecutor` 接口，`HttpExecutor` 和 `CloakBrowserExecutor` 两个实现
- **自动降级**：HTTP 层发现 403/429 或明显反爬页面时，自动降级到 CloakBrowser 重试
- **资源管理**：CloakBrowser 启动 Chromium 进程较重，使用连接池 + 空闲超时管理
- **Docker**：Chromium 运行在 crawler 容器内，无需额外服务

## 技术栈

- **语言**：Python 3.11+
- **Bot 框架**：python-telegram-bot
- **Web 框架**：FastAPI（各服务 HTTP API）
- **ORM**：SQLAlchemy 2.0 + PyMySQL
- **数据库**：MySQL 8.0
- **任务队列**：Redis + RQ
- **爬虫**：httpx + BeautifulSoup4 / parsel + CloakBrowser（Playwright API）
- **部署**：Docker Compose
