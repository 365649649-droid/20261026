# 定位方式速查表（Locator Cheatsheet）

> 这是你之后每天都会回来看的一页。
> 脚本 80% 的"不稳定"，都出在定位方式选错了。

---

## 一、优先级从高到低

| 优先级 | 写法 | 什么时候用 | 稳定性 |
|--------|------|-----------|--------|
| 1（最推荐） | `get_by_role()` | 几乎永远先试它 | 最稳，和用户的真实感知一致 |
| 2 | `get_by_test_id()` | 前端加了 `data-testid` 时 | 非常稳，专为测试而生 |
| 3 | `get_by_text()` / `get_by_label()` | 按可见文字/表单标签找 | 稳（但文案改动会挂） |
| 4 | `locator("css选择器")` | 上面都不行时 | 一般，受页面结构影响 |
| 5（最后手段） | XPath `//div[3]/span` | 实在没别的办法 | 脆，页面一动就挂 |

**核心原则：找"用户能感知到的东西"（角色、文字、标签），而不是"HTML 结构里的第几个 div"。**

---

## 二、逐条示例

### 1. get_by_role —— 首选

按元素的"语义角色" + "可访问名称"定位，最接近用户视角。

```python
# 按钮（按名字）
page.get_by_role("button", name="登录").click()
page.get_by_role("button", name="Login").click()

# 链接
page.get_by_role("link", name="忘记密码").click()

# 输入框（按 label 或 placeholder）
page.get_by_role("textbox", name="用户名").fill("admin")

# 复选框
page.get_by_role("checkbox", name="记住我").check()

# 下拉框
page.get_by_role("combobox", name="城市").select_option("上海")
```

常用角色：`button` `link` `textbox` `checkbox` `radio` `combobox` `tab` `heading` `dialog`

### 2. get_by_test_id —— 团队协作用

```python
# 对应页面上 <button data-testid="submit-btn">提交</button>
page.get_by_test_id("submit-btn").click()
```

> 注意：`data-testid` 需要前端配合加。如果你们项目没加，可以跟开发提这个需求——这是现在前端+测试协作的标准做法。
> 如果项目里用的是其它属性名（比如 `data-test`），也能指定：
> ```python
> # 在测试配置里统一设置一次
> playwright.selectors.set_test_id_attribute("data-test")
> ```

### 3. get_by_text / get_by_label —— 按文字找

```python
page.get_by_text("欢迎回来").click()
page.get_by_label("邮箱地址").fill("a@b.com")
page.get_by_placeholder("请输入手机号").fill("13800138000")
page.get_by_title("关闭").click()
```

### 4. locator（CSS）—— 兜底方案

```python
page.locator("#user-name").fill("admin")            # id
page.locator(".login-btn").click()                  # class
page.locator("[data-test='login-button']").click()  # 任意属性
page.locator("input[type='password']").fill("pwd")  # 标签+属性
```

---

## 三、坏写法 vs 好写法，直观对比

同一个"点击登录按钮"，看看差距有多大：

```python
# 坏：绝对路径 XPath，页面只要多包一层 div 就彻底挂掉
page.click("/html/body/div[1]/div[2]/form/div[3]/button")

# 坏：位置索引，前端加一个广告位，第 3 个就不是它了
page.click("div.login-form > button:nth-child(3)")

# 坏：依赖 CSS-in-JS 生成的哈希类名，每次打包都可能变
page.click(".css-1x2y3z4 > span")

# 好：按用户看到的"登录"两个字找，UI 重构也不容易挂
page.get_by_role("button", name="登录").click()

# 也好：用测试专用属性，最稳
page.get_by_test_id("login-button").click()
```

---

## 四、绝对不要做的事：手写等待

```python
# 错误示范 —— 新手最爱写，但这是万恶之源
import time
time.sleep(3)
page.click("button")

# 为什么错？
#   网络快的时候白白等 3 秒；网络慢的时候 3 秒还是不够，照样挂。
#   一百个用例各 sleep 3 秒，整套下来多花好几分钟。
```

**正确做法：直接操作，Playwright 自己会等。**

```python
# Playwright 会自动等到元素出现、可见、可点击、稳定不动了才操作
page.get_by_role("button", name="提交").click()

# 需要等待"结果"而不是"元素"时，用 expect 断言（自带超时重试）
expect(page.get_by_text("保存成功")).to_be_visible()

# 真的非要调整超时（默认 30 秒），用 expect 的 timeout 参数
expect(page.get_by_text("加载完成")).to_be_visible(timeout=10000)
```

---

## 五、写在最后的三句话

1. **定位 = 替用户描述"你要点的那个东西"**，而不是描述"它在 HTML 的第几层"。
2. **每个用例必须有断言**。只是点一遍页面的脚本不是自动化，因为它永远不会告诉你"哪里错了"。
3. **脚本挂了先怀疑定位器**，再怀疑产品有 bug——大概率是前者。
