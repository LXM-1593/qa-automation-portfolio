# 接口缺陷报告（api.restful-api.dev）

| 项目 | 内容 |
|------|------|
| 被测服务 | https://api.restful-api.dev |
| 测试类型 | 接口功能 / 契约 / 异常场景 |
| 测试环境 | Windows 11 · Python 3.13 · requests 2.34 · Postman Collection v2.1 |
| 执行时间 | 2026-11-04 |
| 证据文件 | `reports/api-smoke.json`（真实响应转录） |
| 缺陷总数 | 7（High 2 / Medium 2 / Low 3），另有 1 条安全观察 |

## 严重程度定义

| 级别 | 判定标准 |
|------|----------|
| High | 破坏数据完整性或核心契约，可导致脏数据/业务错误 |
| Medium | 行为与契约不符但影响可控，存在数据质量隐患 |
| Low | 语义/文案/一致性偏差，不影响主流程 |
| Info | 设计层面的观察项，非缺陷 |

---

## DEF-001 缺少 `name` 仍可创建对象，且落库为 `null`

- **严重程度**：High
- **优先级**：P1
- **状态**：Open
- **接口**：`POST /objects`

**前置条件**：服务可访问，无特殊状态。

**复现步骤**
1. 发送 `POST https://api.restful-api.dev/objects`，`Content-Type: application/json`。
2. 请求体：`{"data": {"year": 2026}}`（不含 `name`）。
3. 观察响应状态码与响应体。

**预期结果**
- 返回 `400 Bad Request`，错误信息说明 `name` 为必填。
- 不创建任何资源。

**实际结果**
- 返回 `200 OK`。
- 响应体：
```json
{
  "id": "ff808181a09d98f701a1a41263d5284d",
  "name": null,
  "createdAt": 1793754031061,
  "data": { "year": 2026 }
}
```
- 该对象可被 `GET /objects/{id}` 再次读取，说明已真实落库。

**影响**：产生 `name` 为空的非法记录；下游列表/详情页若直接渲染 `name` 会出现空白或空指针风险。

**建议**：在服务端增加必填校验，`name` 缺失或为 `null` 时返回 400；补充对应契约测试。

---

## DEF-002 空字符串 `name` 被接受并持久化

- **严重程度**：High
- **优先级**：P1
- **状态**：Open
- **接口**：`POST /objects`

**复现步骤**
1. `POST /objects`，请求体：`{"name": "", "data": {"year": 2026}}`。
2. 记录返回的 `id`。
3. `GET /objects/{id}` 复查。

**预期结果**：返回 `400`，拒绝空名称。

**实际结果**：返回 `200`，`name` 为 `""`；随后 `GET` 仍返回 `200` 且 `name` 为空字符串。

**影响**：与 DEF-001 同类，产生无意义业务数据。

**建议**：对 `name` 做 `trim` 后非空校验。

---

## DEF-003 数字类型 `name` 被静默转换为字符串

- **严重程度**：Medium
- **优先级**：P2
- **状态**：Open
- **接口**：`POST /objects`

**复现步骤**
1. `POST /objects`，请求体：`{"name": 12345, "data": {"year": 2026}}`。
2. 观察响应中的 `name` 字段类型与值。

**预期结果**：返回 `400`，提示 `name` 必须为字符串；或文档明确声明会做类型转换。

**实际结果**：返回 `200`，`name` 变为字符串 `"12345"`。

**影响**：调用方无法感知类型错误，可能在后续按字符串处理的逻辑中产生隐性偏差；契约不明确。

**建议**：严格类型校验并返回 400，或在 API 文档中显式声明转换规则。

---

## DEF-004 创建资源返回 `200 OK` 而非 `201 Created`

- **严重程度**：Low
- **优先级**：P3
- **状态**：Open
- **接口**：`POST /objects`

**复现步骤**
1. `POST /objects`，提交合法对象。
2. 查看响应状态码。

**预期结果**：`201 Created`，并建议携带 `Location` 头指向新资源。

**实际结果**：`200 OK`。

**影响**：语义不严谨；依赖状态码区分「创建」与「查询」的客户端需额外判断。

**建议**：创建成功返回 201。

---

## DEF-005 404 错误文案不一致

- **严重程度**：Low
- **优先级**：P3
- **状态**：Open
- **接口**：`GET /objects/{id}` 与 `DELETE /objects/{id}`

**复现步骤**
1. `GET /objects/does-not-exist-123456`。
2. `DELETE /objects/does-not-exist-123456`。
3. 对比两处 `error` 文案。

**预期结果**：同类错误使用统一文案与格式。

**实际结果**
- GET：`Object with id=does-not-exist-123456 was not found.`
- DELETE：`Object with id = does-not-exist-123456 doesn't exist.`

差异点：`=` 两侧空格不一致；`was not found` 与 `doesn't exist` 措辞不一致。

**影响**：客户端若按文案做匹配或展示，会出现不一致体验；不利于错误码体系规范化。

**建议**：统一为同一模板，并引入稳定的错误码字段（如 `code: NOT_FOUND`）。

---

## DEF-006 删除成功返回 `200 + 响应体` 而非 `204 No Content`

- **严重程度**：Low
- **优先级**：P3
- **状态**：Open
- **接口**：`DELETE /objects/{id}`

**复现步骤**
1. 创建一个对象。
2. `DELETE /objects/{id}`。
3. 查看状态码与响应体。

**预期结果**：`204 No Content`，无响应体。

**实际结果**：`200 OK`，响应体为 `{"message": "Object with id = ... has been deleted."}`。

**影响**：轻微语义偏差；对严格按 204 处理的客户端可能造成解析负担。

**建议**：按 REST 惯例返回 204，或保留 200 但在文档中明确。

> 注：该结论来自配额耗尽前的真实调用（`reports/api-smoke.json` 中 `delete_object`，状态 200）。当每日配额用尽时，同一端点会返回 405，见 DEF-007。

---

## DEF-007 超出每日配额返回 `405` 而非 `429 Too Many Requests`

- **严重程度**：Medium
- **优先级**：P2
- **状态**：Open
- **接口**：任意写接口（如 `POST /objects`、`DELETE /objects/{id}`）

**复现步骤**
1. 在 24 小时内累计调用公开 API 超过 50 次。
2. 再次发送 `POST /objects` 或 `DELETE /objects/{id}`。
3. 观察状态码与响应体。

**预期结果**：返回 `429 Too Many Requests`，并通过 `Retry-After` 头告知重试时间。

**实际结果**：返回 `405 Method Not Allowed`，响应体：
```json
{"error": "You've reached the daily request limit for our public API (50 requests per 24 hours). Create a free account or ..."}
```

**影响**：`405` 通常表示「资源不支持该方法」，会误导客户端以为是路由/方法错误而非限流，导致重试策略失效；监控与告警也难以按 429 归类。

**建议**：限流场景统一返回 429，并补充 `Retry-After`、`X-RateLimit-*` 等响应头。

---

## SEC-001（观察项）接口无鉴权，任意客户端可创建/删除数据

- **严重程度**：Info（设计如此，非缺陷）
- **说明**：`/objects` 全部方法无需认证。任何能访问该服务的人都可以创建、修改、删除对象，且删除他人创建的数据同样返回 200。
- **影响**：作为公开练习 API 可接受；若用于生产需引入认证、授权与租户隔离。
- **建议**：生产化时增加 API Key / OAuth，并对资源做归属校验。

---

## 复现与回归

```bash
# 重新采集真实响应，刷新证据
python scripts/api_smoke.py

# 通过 Postman 集合复现（文件夹 04 预期失败）
newman run postman/collection.json -e postman/environment.json
```

> 说明：`api.restful-api.dev` 为公开共享实例，数据可能被其他使用者改动；本文所有「实际结果」均以 2026-11-04 本次执行的转录为准。
