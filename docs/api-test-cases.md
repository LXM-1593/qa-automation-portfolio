# 接口测试用例集（api.restful-api.dev）

被测服务：https://api.restful-api.dev
资源：`/objects`（内存对象 CRUD，公开、无需鉴权）
测试类型：接口功能 / 契约 / 异常场景
执行工具：Postman Collection + Newman

## 环境变量

| 变量 | 值 | 说明 |
|------|----|------|
| `baseUrl` | `https://api.restful-api.dev` | 服务地址 |
| `objectId` | 运行时写入 | 创建对象后由测试脚本自动写入 |

## 用例清单

> 「实际」列来自 `scripts/api_smoke.py` 的真实调用记录（`reports/api-smoke.json`）。

| ID | 方法 / 路径 | 前置条件 | 请求要点 | 预期结果 | 实际结果 | 结论 |
|----|-------------|----------|----------|----------|----------|------|
| API-001 | GET `/objects` | 无 | 无参数 | 200，返回非空数组，元素含 `id`/`name` | 200，13 条记录 | 通过 |
| API-002 | GET `/objects?id=3&id=5` | 无 | 两个 id 查询参数 | 200，仅返回 id=3、5 | 200，返回 2 条 | 通过 |
| API-003 | POST `/objects` | 无 | `name` + `data{year,price,CPU,disk}` | 创建成功并返回 `id`、`createdAt` | 200，返回 id 与 createdAt | 通过（状态码语义见 DEF-004） |
| API-004 | GET `/objects/{id}` | API-003 已创建对象 | 路径参数为新建 id | 200，字段与创建时一致 | 200，字段一致 | 通过 |
| API-005 | PUT `/objects/{id}` | 同上 | 全量替换 `name`、`data` | 200，`name`/`data` 被替换，返回 `updatedAt` | 200，替换成功 | 通过 |
| API-006 | PATCH `/objects/{id}` | 同上 | 仅传 `name` | 200，仅 `name` 变化，`data` 保留 | 200，符合预期 | 通过 |
| API-007 | DELETE `/objects/{id}` | 同上 | 路径参数为目标 id | 2xx，返回删除确认 | 200，返回 message | 通过（语义见 DEF-006） |
| API-008 | GET `/objects/{id}` | 已执行 API-007 | 路径参数为已删除 id | 404，错误体说明不存在 | 404，error 含 id | 通过 |
| API-009 | GET `/objects/{unknown}` | 无 | 不存在的 id | 404，错误体说明不存在 | 404 | 通过 |
| API-010 | DELETE `/objects/{unknown}` | 无 | 不存在的 id | 404 | 404 | 通过 |
| API-011 | POST `/objects` | 无 | 请求体为非法 JSON | 400，提示请求体非法 | 400，`Invalid request body` | 通过 |
| DEF-001 | POST `/objects` | 无 | 仅 `data`，缺 `name` | 400，拒绝创建 | 200，创建成功且 `name: null` | **失败（缺陷）** |
| DEF-002 | POST `/objects` | 无 | `name: ""` | 400，拒绝创建 | 200，创建成功并持久化 | **失败（缺陷）** |
| DEF-003 | POST `/objects` | 无 | `name: 12345`（数字） | 400，类型校验失败 | 200，被静默转为 `"12345"` | **失败（缺陷）** |
| DEF-004 | POST `/objects` | 无 | 合法创建请求 | 201 Created | 200 OK | **失败（缺陷）** |
| DEF-005 | GET / DELETE 不存在 id | 无 | 两条 404 路径 | 错误文案风格一致 | 文案与空格不一致 | **失败（缺陷）** |
| DEF-006 | DELETE `/objects/{id}` | 存在对象 | 删除 | 204 No Content | 200 + JSON 响应体 | **失败（缺陷）** |
| DEF-007 | POST / DELETE | 24h 内调用超过 50 次 | 任意写请求 | 429 Too Many Requests | 405 Method Not Allowed + 限额提示 | **失败（缺陷）** |

## 执行方式

```bash
# 全量（含缺陷复现，预期 6 条断言失败）
newman run postman/collection.json -e postman/environment.json

# 仅跑稳定回归（01-03），应全绿
newman run postman/collection.json -e postman/environment.json --folder "01 - Read" --folder "02 - CRUD happy path" --folder "03 - Negative contract"
```

## 说明

- **配额限制**：公开实例每 24 小时最多 50 次请求，超限返回 `405` + 限额提示（见 DEF-007）。若执行时出现大量 405，请等待配额重置或使用免费账号的 API Key；缺陷证据以配额耗尽前的转录为准。
- 服务为公开共享实例，`GET /objects` 的记录数会随时间变化，因此断言只校验「非空数组 + 字段存在」，不写死数量。
- 创建类用例会写入真实数据，集合内已通过 `pm.sendRequest` 在断言后自动删除，避免污染。
- 文件夹 `04` 的失败是**有意设计**：它复现的是已登记缺陷，不代表脚本错误。
