# QA Automation Portfolio

[![UI Regression](https://github.com/LXM-1593/qa-automation-portfolio/actions/workflows/ui-regression.yml/badge.svg)](https://github.com/LXM-1593/qa-automation-portfolio/actions/workflows/ui-regression.yml)
[![API Regression](https://github.com/LXM-1593/qa-automation-portfolio/actions/workflows/api-regression.yml/badge.svg)](https://github.com/LXM-1593/qa-automation-portfolio/actions/workflows/api-regression.yml)

面向软件测试岗位的端到端作品集：**UI 回归自动化（Pytest + Selenium）+ 接口测试（Postman / Newman）+ 结构化用例与缺陷资产**。

- UI 目标站点：[SauceDemo](https://www.saucedemo.com)（公开电商演示站，覆盖登录 → 浏览 → 购物车 → 结算全链路）
- 接口目标服务：[api.restful-api.dev](https://api.restful-api.dev)（公开对象 CRUD，无需鉴权）
- 当前结果：UI `15 passed`；接口 01–03 稳定回归全绿（11 请求 / 29 断言），缺陷复现文件夹按预期失败

---

## 技术栈

| 领域 | 选型 |
|------|------|
| 语言 | Python 3.10+ |
| UI 自动化 | Selenium 4 + Pytest 8/9 + Page Object Model |
| 报告 | pytest-html（含失败截图） |
| 接口测试 | Postman Collection v2.1 + Newman |
| 数据校验 | requests（缺陷证据采集） |
| 持续集成 | GitHub Actions（UI 与接口拆成两个工作流） |
| 版本控制 | Git（按功能分层提交） |

---

## 目录结构

```text
qa-automation-portfolio/
├── conftest.py                 # 全局夹具：驱动、登录态、失败截图、代理绕过
├── pytest.ini                  # 测试发现规则、标记、HTML 报告
├── requirements.txt
├── README.md
├── .gitignore
├── .github/workflows/
│   ├── ui-regression.yml       # push/PR/定时跑 UI 回归，上传报告与截图
│   └── api-regression.yml      # postman/ 变更或手动触发跑接口集合
├── pages/                      # 页面对象层（Page Object Model）
│   ├── __init__.py
│   ├── base_page.py            # 显式等待、点击、输入等通用能力
│   ├── login_page.py
│   ├── inventory_page.py
│   ├── cart_page.py
│   └── checkout_page.py
├── tests/                      # 测试用例层（只表达业务语义）
│   ├── __init__.py
│   ├── test_login.py
│   ├── test_inventory.py
│   ├── test_cart.py
│   └── test_checkout.py
├── test_data/
│   └── users.json              # 测试账号数据外置
├── postman/
│   ├── collection.json         # 4 个文件夹、16 个请求、内嵌断言
│   └── environment.json        # baseUrl / objectId
├── scripts/
│   ├── api_smoke.py            # 真实调用并转录响应，生成缺陷证据
│   ├── run_tests.ps1           # Windows 一键执行
│   └── run_tests.sh            # macOS / Linux 一键执行
├── docs/
│   ├── test-strategy.md        # 测试策略：范围/分层/设计方法/出入口准则/CI 规则
│   ├── test-cases.md           # UI 用例集（15 条）
│   ├── api-test-cases.md       # 接口用例集（18 条）
│   └── defect-report.md        # 缺陷报告（6 条 + 1 观察项）
└── reports/                    # 运行产物（HTML、截图、证据 JSON）
```

---

## 环境搭建

### 1. 前置条件

- Python 3.10 及以上
- Chrome 浏览器（Selenium 4 自带 Selenium Manager，会自动匹配驱动，无需手动下载 chromedriver）
- Node.js 18+（仅在需要运行 Newman 时）

### 2. 创建虚拟环境并安装依赖

```bash
cd qa-automation-portfolio
python -m venv .venv

# Windows (Git Bash / PowerShell)
.venv/Scripts/python.exe -m pip install -r requirements.txt

# macOS / Linux
.venv/bin/python -m pip install -r requirements.txt
```

### 3. 安装 Newman（可选，用于命令行跑接口集合）

```bash
npm install newman --no-save
```

---

## 运行方式

### UI 回归

```bash
# 默认 headless
.venv/Scripts/python.exe -m pytest

# 有头模式（观察浏览器操作）
HEADLESS=0 .venv/Scripts/python.exe -m pytest

# 只跑冒烟用例
.venv/Scripts/python.exe -m pytest -m smoke

# 指定单文件 / 单用例
.venv/Scripts/python.exe -m pytest tests/test_checkout.py -v
```

Windows 也可直接执行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_tests.ps1
```

产物：
- HTML 报告：`reports/report.html`
- 失败截图：`reports/screenshots/<用例名>.png`

### 接口测试

```bash
# 全量（文件夹 04 为缺陷复现，预期 6 条断言失败）
node_modules/.bin/newman run postman/collection.json -e postman/environment.json

# 仅稳定回归（01-03，应全绿）
node_modules/.bin/newman run postman/collection.json -e postman/environment.json \
  --folder "01 - Read" --folder "02 - CRUD happy path" --folder "03 - Negative contract"

# 也可导入 Postman 桌面端，选择 environment: restful-api.dev
```

### 刷新缺陷证据

```bash
.venv/Scripts/python.exe scripts/api_smoke.py
# 输出 reports/api-smoke.json，供 docs/defect-report.md 引用
```

---

## 持续集成（GitHub Actions）

两个 workflow 分开，是为了**让接口层只在必要时消耗配额**（公开 API 每天仅 50 次请求）。

| Workflow | 触发 | 阻塞 | 产物 |
|---|---|---|---|
| `ui-regression.yml` | push / PR 到 `main`、每周一 09:00、手动 | 是 | `ui-report`（HTML 报告 + 失败截图） |
| `api-regression.yml` | `postman/**` 变更、每周一 09:00、手动 | 稳定层阻塞；缺陷层不阻塞 | `api-report`（Newman JSON） |

**三个刻意设计**：

1. **接口层不做"每次 push 必跑"**——50 次/天的配额会被 CI 瞬间打空，造成假红。改为路径过滤 + 定时 + 手动。
2. **缺陷复现文件夹永不阻塞**——它失败代表"缺陷仍在"，是预期状态；若设为阻塞，红灯会变成噪音。
   手动触发时勾选 `run_defect_suite` 才会执行。
3. **配额预检前置**——若 `GET /objects` 返回 405（配额耗尽）或 5xx，直接 `exit 1` 并明确提示
   "本次结果不可作为回归结论"，避免把环境问题误判为用例失败。

手动全量验证（含缺陷复现）：

```bash
gh workflow run api-regression.yml -f run_defect_suite=true
```

> 注：`[skip ci]` 写进 commit message 可跳过 UI 工作流（纯文档改动时用）。

---

## 用例与缺陷记录说明

### 用例资产

| 文档 | 内容 | 编号规则 |
|------|------|----------|
| `docs/test-cases.md` | UI 功能用例：前置条件、步骤/输入、预期结果、优先级、对应自动化函数 | `UI-xxx` |
| `docs/api-test-cases.md` | 接口用例：方法/路径、请求要点、预期 vs 实际、结论 | `API-xxx` / `DEF-xxx` |

每条 UI 用例都可追溯到 `tests/` 中的具体函数；接口用例的「实际结果」来自真实调用转录，而非推测。

**测试策略**（范围边界、分层依据、设计方法落地位置、环境与数据策略、出入口准则、缺陷分级、CI 规则、度量基线、风险登记）见
`docs/test-strategy.md` —— 用例说明"测了什么"，策略说明"为什么这样测"。

### 缺陷记录

`docs/defect-report.md` 采用标准缺陷单结构：**严重程度 / 优先级 / 状态 / 前置条件 / 复现步骤 / 预期结果 / 实际结果 / 证据 / 影响 / 建议**。

| ID | 摘要 | 级别 |
|----|------|------|
| DEF-001 | 缺少 `name` 仍可创建对象并落库为 `null` | High |
| DEF-002 | 空字符串 `name` 被接受并持久化 | High |
| DEF-003 | 数字 `name` 被静默转为字符串 | Medium |
| DEF-004 | 创建返回 200 而非 201 | Low |
| DEF-005 | 404 错误文案不一致 | Low |
| DEF-006 | 删除返回 200+body 而非 204 | Low |
| DEF-007 | 超配额返回 405 而非 429 | Medium |
| SEC-001 | 接口无鉴权（设计观察项） | Info |

Postman 集合的 `04 - Defect reproduction` 文件夹用断言固化这些期望契约，因此运行时会**有意失败**——失败即缺陷仍存在，修复后会自动转绿。这是把缺陷变成可回归资产的做法。

---

## 设计要点

1. **分层清晰**：`pages/` 只负责定位与页面动作，`tests/` 只表达业务语义；选择器变更不影响用例。
2. **无固定休眠**：全部使用 `WebDriverWait` 显式等待；排序场景额外等待 DOM 顺序稳定，避免竞态。
3. **用例独立**：每个用例新建浏览器会话与临时 `user-data-dir`，结束后清理，可任意顺序重复执行。
4. **失败可诊断**：失败自动截图并写入 HTML 报告，定位问题不依赖日志猜测。
5. **代理兼容**：ChromeDriver 走 `localhost`，`conftest.py` 会自动把回环地址加入 `NO_PROXY`，避免企业/沙箱代理拦截 Selenium 与驱动的通信（这是本项目实际踩到并修复的环境问题）。
6. **缺陷可回归**：缺陷不是一次性文档，而是转化为断言，修复后自动验证。

---

## 已知限制

- SauceDemo 为公开演示站，页面文案或结构若变更，需同步更新页面对象定位器。
- `api.restful-api.dev` 为公开共享实例，数据可能被其他使用者改动；用例只断言结构与契约，不写死记录数量。
- **该公开实例每 24 小时限 50 次请求**，超额返回 `405` + 限额提示（已登记为 DEF-007）。若运行集合时大量请求返回 405，说明配额已耗尽，请等待重置或改用账号 API Key；UI 套件不受影响。
- 缺陷报告基于 2026-11-04 的执行结果；服务升级后应以 `scripts/api_smoke.py` 重新采集为准。

---

## 提交规范

采用 Conventional Commits 前缀：

- `feat(ui):` 新增页面对象或能力
- `test(ui):` 新增/调整测试用例
- `test(api):` 接口集合与脚本
- `docs:` 文档与报告
- `chore:` 工程配置

示例：`test(ui): cover full checkout flow and postal-code validation`
