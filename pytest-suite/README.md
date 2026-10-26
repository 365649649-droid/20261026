# pytest 测试套件（第二课）

> 把之前的三个独立脚本，变成一个**能一键跑全部、自动统计结果、失败自动截图**的测试项目。
> 这就是岗位里实际在用的形态。

---

## 怎么跑

**最简单：双击 `run_tests.bat`**

或者命令行：

```powershell
cd "C:/Users/Admin/WorkBuddy/2026-10-26-17-06-48/playwright-day1/pytest-suite"
python -m pytest                      # 全部跑一遍（无头模式，不弹浏览器）
python -m pytest --headed             # 弹浏览器，看得见过程
python -m pytest --headed --slowmo=500  # 再慢一点
python -m pytest -k "login"           # 只跑名字含 login 的用例
python -m pytest test_login.py::test_standard_user_can_login   # 只跑单条
```

---

## 目录结构

```
pytest-suite/
├── conftest.py          # 公共配置：fixture + 命令行参数 + 失败截图
├── test_login.py        # 测试用例（pytest 自动发现 test_*.py）
├── pytest.ini           # pytest 运行配置
├── run_tests.bat        # 双击启动
└── screenshots/         # 用例失败时自动截图存这里
```

**关键：文件名必须是 `test_*.py`，函数名必须是 `test_*`，否则 pytest 找不到。**

---

## 这个套件里有 6 条用例

| 用例 | 场景 | 类型 |
|------|------|------|
| `test_standard_user_can_login` | 正确密码 → 进入商品页 | 成功路径 |
| `test_wrong_password_is_rejected` | 密码错误 → 提示不匹配 | 失败路径 |
| `test_locked_out_user_is_rejected` | 账号被锁 → 拒绝登录 | 边界 |
| `test_login_failures[wrong_password]` | 参数化第 1 组 | 失败路径 |
| `test_login_failures[locked_out]` | 参数化第 2 组 | 边界 |
| `test_login_failures[empty_username]` | 参数化第 3 组 | 边界 |

注意最后三条：**它们共用同一个函数**，只是数据不同。这就是参数化。

---

## 三个必须理解的概念

### 1. fixture —— "自动准备好、自动清理掉"

```python
def test_xxx(page):     # 只要参数名写 page，pytest 就会自动把页面递给你
    ...
```

`page` 是 `conftest.py` 里定义的 fixture。你不需要 `page = browser.new_page()`，pytest 自己会做，用完自动关闭。

**为什么 `browser` 是 `scope="session"`？**
整个测试只启动一次浏览器，6 条用例复用。如果每条都重启浏览器，要多花 20 秒以上。

**为什么 `page` 不是 session 级？**
每条用例要一个全新页面，否则登录状态会互相污染——上一条登录了，下一条默认就是登录态，测试结果不可信。

### 2. 参数化 —— 一份代码跑多组数据

```python
@pytest.mark.parametrize(
    "username,password,expected_error",
    [
        ("standard_user", "wrong_password", "do not match"),
        ("locked_out_user", "secret_sauce", "locked out"),
        ("", "secret_sauce", "Username is required"),
    ],
    ids=["wrong_password", "locked_out", "empty_username"],
)
def test_login_failures(page, username, password, expected_error):
    ...
```

`ids` 就是报告里方括号中显示的名字。

> **为什么用英文而不是中文？**
> pytest 会把输出里 nodeid 的非 ASCII 字符转义成 `\u5bc6\u7801` 这样的形式
> （为了跨平台兼容），中文 ids 在日志里反而看不懂。
> 另外 CI 日志、Jenkins、以及各种测试报告工具对英文标识的兼容性都更好。
> 中文说明放 `docstring` 里即可，一样能看。

### 3. 失败自动截图 —— CI 上的救命功能

`conftest.py` 里有：

```python
@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item, call):
    ...
    if report.when == "call" and report.failed:
        page.screenshot(path=f"screenshots/FAILED_{...}.png")
```

用例一挂，页面快照就存进 `screenshots/`。
**CI 上跑挂了，你人不在现场，只能靠这张图还原"当时页面长什么样"。**

---

## 踩过的坑（真实记录）

**1. `context.selectors` 不存在**

```python
# 错：
context.selectors.set_test_id_attribute("data-test")
# AttributeError: 'BrowserContext' object has no attribute 'selectors'

# 对：
p.selectors.set_test_id_attribute("data-test")   # 挂在 Playwright 实例上
```

**2. 只在一个地方能生效**

`set_test_id_attribute` 是 Playwright 全局设置，在 `browser` fixture 里设一次，
之后所有 context / page 都生效，不用每个页面重复设。

**3. `pytest.ini` 里加了 `-p no:cacheprovider`**

因为某些目录有权限限制，pytest 写 `.pytest_cache` 会报 warning。关掉缓存插件更干净。

---

## 从这个套件开始，你该养成的四个习惯

1. **一个用例一个断言主题**。别把"登录"和"菜单导航"塞一起。
2. **用例名字要能当说明书读**。`test_locked_out_user_is_rejected` 比 `test_login3` 有用一万倍。
3. **公共动作抽函数**（如 `do_login`），改一次全生效。
4. **断言三層叠加**：路由（URL）+ 语义（标题文字）+ 内容（列表渲染）。

---

## 下一步：接 CI

本地跑通了，接下来是让它**每次代码提交自动跑**。典型形态：

```yaml
# .github/workflows/ui-test.yml（示意）
name: UI Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install pytest playwright
      - run: playwright install chromium
      - run: python -m pytest
      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: failed-screenshots
          path: screenshots/
```

注意最后一段：**只有失败时才上传截图**。这是标准做法——成功的截图没人看，还占存储。
