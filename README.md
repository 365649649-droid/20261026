# Playwright 第一天练习包（零基础 · Windows）

> **环境已经装好，开箱即用（2026-10-26 安装）。**
> 本机已安装 Python 3.12.10 + Playwright 1.64.1 + Chromium 内核，
> 新开一个命令行窗口即可直接用 `python` 命令。
> 也可以双击 `.bat` 运行，不用碰命令行。

---

## 三个文件，按顺序双击

| 顺序 | 文件 | 作用 |
|------|------|------|
| ① | **`run.bat`** | 跑示例脚本：自动完成登录、断言、截图 |
| ② | **`record.bat`** | 打开录制器：你用鼠标操作，它自动生成代码 |
| ③ | **`run_mine.bat`** | 回放你自己录的脚本（存成 `my_recorded.py`） |

---

## 第 1 步：双击 `run.bat`

跑起来后它会依次做这些事：

1. 自动找到一个能用的 Python（不需要你配置 PATH）
2. 确认 Playwright 就绪
3. 驱动你电脑上的 Edge 打开练习网站
4. 自动填账号 → 点登录 → 验证结果 → 截图

**你会看到：** Edge 自己弹出来，自己填账号密码，自己点登录。
脚本跑两个场景——正常登录成功、故意输错密码看错误提示。

跑完窗口会停住让你看结果，文件夹里会多出两张图：

- `success_login.png` —— 成功进入商品列表页
- `failed_login.png` —— 被拦在登录页，红色报错提示

**这两张图就是"执行证据"，是自动化测试的核心产出。**

### 为什么 bat 里的提示是英文的？

刻意为之，不是偷懒。批处理文件里混中文极易触发
「`'p' 不是内部或外部命令`」这种诡异报错——cmd.exe 按系统代码页（GBK）
逐字节解析文件，编码不一致时中文字节会把 `python` 拦腰截断成 `p` + `thon`。
所以这里统一纯 ASCII。脚本本体的中文输出是正常的。

### bat 是怎么找到 Python 的？

按这个顺序找，第一个能用的就用：

1. 你自己装的 Python（`%LOCALAPPDATA%\Programs\Python\Python3xx\python.exe`）← **当前就是这一个**
2. 系统级安装（`C:\Python3xx\python.exe`）
3. 备用环境（`%USERPROFILE%\.workbuddy\...`，仅在前面都找不到时兜底）
4. PATH 里的 `python`

> **Windows 有个坑值得知道：** 系统在 `WindowsApps\` 下放了个**假的 `python.exe`**，
> 它只有 121 字节，执行后只会打开微软商店，根本不是 Python。
> 你之前报错 `Python not found` 就是被它挡住的。
> 以后自己装了 Python 却发现 `python` 还弹商店的话，去
> **设置 → 应用 → 高级应用设置 → 应用执行别名**，把 `python.exe` / `python3.exe` 关掉。

---

## 第 2 步：读懂 `01_first_login.py`

用记事本或任意编辑器打开它。**里面的注释比代码还多**，就是给你读的。

对照着看这几个关键部分：

| 代码位置 | 它在干什么 |
|---------|-----------|
| `page.goto(...)` | 打开网页 |
| `page.locator('[data-test="username"]').fill(...)` | 往输入框填字 |
| `.click()` | 点击 |
| `expect(...).to_have_url(...)` | **断言**：验证 URL 确实变了 |
| `expect(...).to_be_visible()` | **断言**：验证元素确实出现了 |
| `page.screenshot(...)` | 截图留证 |

**最关键的一点：没有断言的脚本不算自动化。** 只把页面点一遍，出问题它也不会告诉你。

想用命令行跑（可选）：

```powershell
cd "C:/Users/Admin/WorkBuddy/2026-10-26-17-06-48/playwright-day1"
python 01_first_login.py              # 弹浏览器，看得见过程
python 01_first_login.py --headless   # 静默跑
```

---

## 第 3 步：双击 `record.bat`（零基础最爽的一步）

不用写代码，**鼠标点哪它录哪**。

会弹出两个窗口：

- **左边浏览器**：你正常操作（登录、点商品、加购物车都行）
- **右边 Playwright Inspector**：代码实时自动生成

操作完，从 Inspector 里 **Copy** 生成的代码，
在本文件夹存成 **`my_recorded.py`**，然后双击 **`run_mine.bat`** 回放。

**录出来的代码通常很丑**，比如一堆 `page.locator("div:nth-child(3) > span.css-1x2y3z")`。
别管它，录出来就赢了，下一步交给 AI 收拾。

---

## 第 4 步：把"丑脚本"交给 AI 改

打开 `03_ai_prompt_templates.md`，里面有现成的提示词模板。
把录出来的代码连同模板一起发给我（或 Cursor / 通义灵码 / 元宝），让它：

1. 把脆弱的定位器换成稳定的（`get_by_role` / `data-testid`）
2. 补断言（验证页面到底对不对）
3. 抽函数、加异常分支、删掉 `time.sleep`

**你要做的只是验收**——看它改完能不能跑通，断言是不是真的在验证有意义的东西。

---

## 第 5 步：记住这几条铁律

详细版见 `02_locator_cheatsheet.md`，这里只记结论：

1. **定位优先级**：`get_by_role` > `get_by_test_id` > `get_by_text` > CSS > **XPath（最后手段）**
2. **不要写 `time.sleep(3)`**。Playwright 自带自动等待，用 `expect(...)` 就够了。
3. **一个脚本必须有断言**，否则等于什么都没验证。
4. **选"用户能感知的锚点"**：按钮名、表单 label，比 `div:nth-child(3)` 稳十倍。

---

## 练习用的目标站点

脚本默认访问 **https://www.saucedemo.com/** ——官方专门给自动化练习用的假商店，
不需要注册，也不会有真实交易。

| 账号 | 密码 | 用途 |
|------|------|------|
| `standard_user` | `secret_sauce` | 正常登录 |
| `locked_out_user` | `secret_sauce` | 被锁定用户（失败路径） |

---

## 常见问题

| 现象 | 原因 | 怎么修 |
|------|------|--------|
| `Python not found` | 窗口没读到新 PATH，或误删了 Python | 关掉窗口重新开一个；再不行重跑 winget 安装命令 |
| `'p' 不是内部或外部命令` | bat 文件编码问题 | 已修复（纯 ASCII + CRLF） |
| 浏览器下载卡住 | `cdn.playwright.dev` 国内不可达 | 内核已装好；重装时用 npmmirror 镜像（见下方命令） |
| 浏览器没弹出来 | 用了 `--headless` | 去掉该参数 |
| 找不到你录的脚本 | 没存成 `my_recorded.py` | 文件名要对 |

---

## 本机环境清单（2026-10-26 安装）

| 组件 | 版本 | 位置 |
|------|------|------|
| Python | 3.12.10 | `%LOCALAPPDATA%\Programs\Python\Python312\` |
| pip | 25.0.1 | 随 Python 安装 |
| Playwright | 1.64.1 | 上述 Python 的 site-packages |
| Chromium | 156.0.8078.4 | `%LOCALAPPDATA%\ms-playwright\chromium-1248\` |
| Chromium Headless Shell | 同上 | `%LOCALAPPDATA%\ms-playwright\chromium_headless_shell-1248\` |
| FFmpeg | 1013 | `%LOCALAPPDATA%\ms-playwright\ffmpeg-1013\` |

**PATH 顺序已确认**：Python 路径排在 `WindowsApps` **之前**，
所以 `python` 命令会命中真 Python，不会被微软商店的占位存根拦截。

### 如果以后 `python` 又提示找不到

多半是新开的窗口还没读到新 PATH。**关掉窗口重新开一个**即可。
如果重启后仍然不行，检查：

```powershell
where python
```

正常应该第一行就指向 `...\Python312\python.exe`。

### 如果以后想升级或重装

```powershell
winget install --id Python.Python.3.12 --source winget --exact --scope user
python -m pip install --upgrade playwright -i https://pypi.tuna.tsinghua.edu.cn/simple
```

> 装 Playwright 内核时如果官方源不通，用国内镜像：
> ```powershell
> $env:PLAYWRIGHT_DOWNLOAD_HOST="https://cdn.npmmirror.com/binaries/playwright"
> python -m playwright install chromium
> ```

---

## 下一步

等你跑熟这套，往下接的是：

1. 多浏览器跑同一套脚本
2. 用 `pytest-playwright` 组织成规范的测试用例
3. 接 CI（GitHub Actions / Jenkins）自动跑

到时候再让我给你出第二份练习包。
