# UI 测试用例集（SauceDemo）

被测系统：https://www.saucedemo.com — Swag Labs 电商演示站
测试类型：功能回归 / 端到端（黑盒为主）
自动化框架：pytest + Selenium 4 + Page Object Model

## 约定

- **优先级**：P0 核心主流程；P1 主要功能；P2 次要功能。
- **前置条件**：未特别说明时，默认浏览器已打开站点首页且网络可用。
- **测试账号**：`standard_user / secret_sauce`；锁定账号 `locked_out_user / secret_sauce`。

## 用例清单

| ID | 模块 | 标题 | 前置条件 | 输入 / 操作步骤 | 预期结果 | 优先级 | 自动化用例 |
|----|------|------|----------|------------------|----------|--------|------------|
| UI-001 | 登录 | 标准用户登录成功 | 位于登录页 | 输入 standard_user / secret_sauce，点击 Login | 跳转至 `/inventory.html`，商品列表加载完成 | P0 | `test_login.py::test_login_success` |
| UI-002 | 登录 | 错误密码被拒绝 | 位于登录页 | 输入 standard_user / wrong_password，点击 Login | 停留在登录页，提示 "Username and password do not match" | P1 | `test_login.py::test_login_with_invalid_password` |
| UI-003 | 登录 | 锁定用户被拒绝 | 位于登录页 | 输入 locked_out_user / secret_sauce，点击 Login | 提示 "Sorry, this user has been locked out"，不进入商品页 | P1 | `test_login.py::test_locked_user_is_rejected` |
| UI-004 | 登录 | 登出返回登录页 | 已用标准用户登录 | 打开左上菜单，点击 Logout | 回到首页，URL 不含 `inventory.html`，登录按钮可见 | P2 | `test_login.py::test_logout_returns_to_login` |
| UI-005 | 商品列表 | 默认展示全部商品 | 已登录 | 打开商品列表 | 展示 6 个商品，名称互不重复 | P0 | `test_inventory.py::test_inventory_lists_all_products` |
| UI-006 | 排序 | 价格从低到高 | 已登录 | 排序下拉选择 `Price (low to high)` | 价格序列非递减 | P1 | `test_inventory.py::test_sort_by_price_low_to_high` |
| UI-007 | 排序 | 价格从高到低 | 已登录 | 排序下拉选择 `Price (high to low)` | 价格序列非递增 | P1 | `test_inventory.py::test_sort_by_price_high_to_low` |
| UI-008 | 排序 | 名称 A→Z | 已登录 | 排序下拉选择 `Name (A to Z)` | 名称按字典序升序（忽略大小写） | P1 | `test_inventory.py::test_sort_by_name_a_to_z` |
| UI-009 | 购物车 | 加入单件商品更新角标 | 已登录，购物车为空 | 点击 Sauce Labs Backpack 的 Add to cart | 购物车角标显示 1 | P0 | `test_cart.py::test_add_single_item_updates_badge` |
| UI-010 | 购物车 | 加入多件商品累加角标 | 已登录，购物车为空 | 依次加入 Backpack、Bike Light | 角标显示 2 | P1 | `test_cart.py::test_add_multiple_items` |
| UI-011 | 购物车 | 移除商品更新角标 | 已登录，已加入 1 件 | 点击同一商品的 Remove | 角标消失（计数为 0） | P1 | `test_cart.py::test_remove_item_updates_badge` |
| UI-012 | 购物车 | 已加商品出现在购物车 | 已登录 | 加入 Onesie 后打开购物车 | 购物车列表中包含 "Sauce Labs Onesie" | P1 | `test_cart.py::test_added_item_is_present_in_cart` |
| UI-013 | 结算 | 完整下单成功 | 已登录，购物车含 1 件商品 | 点击 Checkout → 填写 Ada/Lovelace/12345 → Continue → Finish | 出现 "Thank you for your order!" | P0 | `test_checkout.py::test_full_purchase_flow` |
| UI-014 | 结算 | 缺少邮编被拦截 | 已登录，购物车含 1 件商品 | Checkout → 仅填姓名，邮编留空 → Continue | 提示 "Postal Code is required"，停留在第一步 | P1 | `test_checkout.py::test_checkout_requires_postal_code` |
| UI-015 | 结算 | 订单金额展示 | 已登录，购物车含 1 件商品 | 完成信息填写后进入第二步 | 显示以 "Total:" 开头的合计金额 | P2 | `test_checkout.py::test_checkout_shows_order_total` |

## 执行结果

最近一次执行：`15 passed in 160.16s`（Windows 11 / Chrome 156 / Python 3.13，headless）。
HTML 报告：`reports/report.html`。

## 设计说明

1. **页面对象**：`pages/` 下每个页面封装定位器与业务动作，用例只表达业务语义，不出现 CSS/XPath。
2. **显式等待**：`BasePage` 统一使用 `WebDriverWait`，不使用 `time.sleep`；排序用例额外等待 DOM 顺序稳定。
3. **测试隔离**：每个用例独立启动/关闭浏览器，避免状态串扰；失败自动截图到 `reports/screenshots/`。
4. **数据外置**：账号信息存于 `test_data/users.json`，便于切换环境。
