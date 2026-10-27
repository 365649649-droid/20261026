# 第五课：Allure 测试报告

> 之前跑完 pytest，你看到的是终端里 6 行 `PASSED`。
> 一旦挂了 20 条用例，这个输出就没法看了 —— 你需要一个能点开、能筛选、能看图、能发给别人的报告。这就是 Allure。

---

## 一、先搞清楚它由两块组成

很多人卡在这一步：以为 `pip install allure-pytest` 就完事了，结果找不到 `allure` 命令。

| 组件 | 作用 | 怎么装 |
|---|---|---|
| `allure-pytest`（Python 包） | pytest 插件，跑测试时把结果写成 JSON 数据到 `allure-results/` | `pip install allure-pytest` |
| `allure`（命令行工具） | 把 `allure-results/` 渲染成能点的 HTML 网站 | `npm install -g allure` |
| **Node.js** | 上面那个 CLI 本身是 Node 程序，没有 node 就跑不起来 | 从 nodejs.org 装，或用 winget |

**`allure-pytest` 只管产出数据，`allure` 只管画图。** 少装任何一个，报告都出不来。

> 老教程会让你装 `allure-commandline`（Java 版）+ JDK。**本项目不用那一套** —— Allure 3 的 npm 包是 Node 实现的，直接跑，省掉 200MB 的 Java。

---

## 二、本机已经装好的东西（不用再装）

| 项目 | 版本 / 位置 |
|---|---|
| allure-pytest | 2.16.2（装在 `%LOCALAPPDATA%\Programs\Python\Python312`） |
| allure CLI | 3.22.1，`%LOCALAPPDATA%\allure-cli\allure.cmd`，已加入用户 PATH |
| Node.js | 24.20.0，winget 用户级安装，已加入用户 PATH |

新开一个终端敲这两条，应该都有版本号回来：

```
node --version      → v24.20.0
allure --version    → 3.22.1
```

> **已经开着的旧终端认不到新 PATH**，重开一个就行。
>
> 为什么专门装 Node？你机器上原本的 node 只存在于工具内部环境，自己的 cmd/PowerShell 里是找不到的 —— 而 `allure` 命令恰恰需要它。这就是"我这边能跑、你那边不行"的典型来源，所以这次直接装了系统级的。

---

## 三、怎么跑

### 最省事：双击 `report.bat`

在项目根目录（`playwright-day1\`），双击它，它做四件事：

1. 找到可用的 Python
2. 跑 `pytest`（可以在 bat 后面追加参数，比如 `report.bat -k wrong`）
3. 用 `allure generate` 生成报告
4. 用 `allure open` 起一个本地服务并自动打开浏览器

看完了直接把那个黑窗口关掉，服务就停了。

### 手动跑（面试常问的三条命令）

```bash
cd pytest-suite
python -m pytest                                                  # 结果自动写进 allure-results/
allure generate allure-results -o allure-report                    # 渲染成网页
allure open allure-report                                          # 起服务 + 打开浏览器
```

`--alluredir` 不用写，它已经在 `pytest.ini` 里配好了：

```ini
addopts = -v --tb=short -p no:cacheprovider --alluredir=allure-results --clean-alluredir
```

`--clean-alluredir` 的作用是每次先清空**原始结果**，否则上一次的旧数据会混进这一次的报告里。

> `allure generate` 一般还会带一个 `--clean`（先删掉旧报告目录）。`report.bat` 里**故意没加**：报告目录被别人占用时（比如上一个 `allure open` 窗口还没关），删目录会失败，反而报错；不加它只会多打一行"目录非空"的提示，生成照样成功。旧文件留着不影响查看。
>
> **别双击 `allure-report\index.html`。** 报告是前端页面，要 fetch 一堆 JSON，用 `file://` 打开会被浏览器安全策略拦掉，表现为白屏。必须经由 HTTP（`allure open` 就是帮你起这个服务）。

---

## 四、报告里有什么（按重要性排）

| 区块 | 看什么 |
|---|---|
| **概览页**右上角圆环 | 通过率。100% 是绿的，有失败就变红并显示 `Failed N` |
| **Metadata** | 环境信息：Python / pytest / playwright 版本、操作系统、被测站点。**"本地能过、CI 挂了"这类问题，先来这里比对版本** |
| **测试树** | 按 `test_xxx.py` 文件分组，点套件名展开，点用例名看详情 |
| **用例详情** | 顶部是标签（epic/feature/story/severity），中间是 Error 堆栈，下面是 **Set up + Test body 步骤时间线**，每步单独计时 |
| **Attachments** | 失败时自动附上的截图 + 当时的页面 URL（本项目已配好） |
| **History / Retries** | 历史趋势和重试记录。本地单次跑没有意义，接上 CI 之后才有数据 |

**步骤时间线是本项目最实用的一块。** 它能告诉你"23 秒里 23.8 秒都花在打开登录页上"，从而一眼看出是网络慢还是脚本写错 —— 终端输出永远给不了这个信息。

---

## 五、代码里加了什么

### 1. 用例上贴标签（只影响报告排版，不影响逻辑）

```python
@allure.epic("SauceDemo 电商网站")        # 最上层：业务线
@allure.feature("登录功能")                # 中间层：功能模块
@allure.story("正常登录")                  # 最下层：具体场景
@allure.severity(allure.severity_level.BLOCKER)   # 严重级别
@allure.title("标准用户用正确密码可以登录成功")     # 报告里显示的名字（覆盖函数名）
def test_standard_user_can_login(page):
    ...
```

`epic > feature > story` 三层会在报告左侧形成可折叠的树，**这是把几十条用例组织清楚的关键**。

### 2. 把动作包成步骤

```python
with allure.step("打开登录页"):
    page.goto(BASE_URL, ...)
```

没包 step 的用例，报告里只有一条"测试体 23 秒"；包了之后会拆成：

```
1 打开登录页            23s 839ms
2 输入用户名：standard_user    35ms
3 输入密码                    4ms
4 点击 Login 按钮            28ms
```

一眼看出瓶颈在哪。

### 3. 失败截图自动进报告（`conftest.py` 里）

`pytest_runtest_makereport` 钩子里，截图存盘之后多做一步 `allure.attach`：

```python
with open(shot, "rb") as f:
    allure.attach(f.read(), name=f"失败截图 - {item.name}",
                  attachment_type=allure.attachment_type.PNG)
allure.attach(page.url, name="失败时的页面地址",
              attachment_type=allure.attachment_type.URI_LIST)
```

这样报告里点 `Attachments` 就能看到失败现场，不用再去翻 `screenshots/` 目录。

### 4. 环境信息（`pytest_sessionfinish` 钩子）

每次跑完往 `allure-results/environment.properties` 写一份版本清单，报告首页的 Metadata 就是它。

---

## 六、CI 里的用法

`.github/workflows/ui-tests.yml` 新增了三步：

```yaml
- name: Install Allure CLI
  run: |
    npm install -g allure
    echo "$(npm prefix -g)" >> $env:GITHUB_PATH

- name: Generate Allure report
  if: always()          # 失败时更需要报告
  working-directory: pytest-suite
  run: allure generate allure-results -o allure-report --clean

- name: Upload Allure report
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: allure-report
    path: pytest-suite/allure-report/
```

跑完在 run 详情页底部 `Artifacts` 区下载 `allure-report.zip`，解压后**用 `allure open` 打开解压目录**（同样不能双击 index.html）。CI 机器是干净的，所以那一步必须重新装一遍 CLI —— 你本地装的不会跟着代码上传。

---

## 七、实测踩过的坑

1. **`allure generate --single-file` 在 v3 里没有了。** 网上 2.x 时代的教程还在用这个参数导单文件 HTML，v3 直接报参数不存在。要分享报告就打包整个 `allure-report/` 目录。
2. **npmmirror 镜像缺包。** `npm i -g allure` 走镜像报 `No matching version found for @allurereport/aql@3.22.1`（镜像同步滞后）。走官方源 + 代理秒装：`--registry=https://registry.npmjs.org --proxy=http://127.0.0.1:10808`。
3. **Temurin JRE 装不上。** `winget install EclipseAdoptium.Temurin.21.JRE --scope user` 报"找不到适用的安装程序"（该包只支持机器级）。这也正好说明：走 Node 版 Allure 就绕开了 Java 这个坑。
4. **`allure open` 会占用终端。** 它是个前台服务，按 Ctrl+C 或直接关窗口才退出。写脚本时别把它和后续命令串在一起。
5. **报告目录不要提交。** `allure-results/`（原始 JSON）和 `allure-report/`（生成物）都已加进 `.gitignore`，随时可重建，进仓库只会把 diff 撑爆。
6. **本地跑一次要多久，取决于网络，波动能有 10 倍。** 同一套 6 条用例，实测过两个极端：**16 秒**（网络顺畅，单条 1.4~4.5 秒）和 **156 秒**（saucedemo 慢，单条 20 秒以上，报告里"打开登录页 23 秒"就是证据）。所以别拿一次耗时当基线，也别急着调超时——慢的时候加 `--headed` 就能看到浏览器在干等网络。想真正稳住，得靠复用登录态（`storage_state`）减少页面加载次数。
7. **偶发的 `Page.goto: net::ERR_TIMED_OUT` 不是脚本 bug。** 本地网络抖动（尤其是挂代理时）会让某条用例直接超时，重跑一次通常就好 —— 这也是为什么 CI 上更稳：机房访问境外站点比家里稳定。判断依据：报错是 `net::ERR_TIMED_OUT` 而不是断言失败，且换一次就能过，就是环境问题。
8. **报告页面会缓存数据。** 重新生成后如果浏览器里还是旧数字（比如用例数没变），强制刷新一下（Ctrl+F5）即可，不是生成失败。
9. **`The output directory ... is not empty` 这条黄字警告要当回事。** 提示原文是：

    ```
    The output directory "...\allure-report" is not empty.
    Files of a previous report may break the layout of the new one.
    Use the --clean option to remove the directory before generating.
    ```

    意思不是"生成失败"，而是**报告里可能混进上一次的旧用例**——现象是明明只跑了一条，报告里却还显示 6 条。两种解法：

    ```bat
    allure generate allure-results -o allure-report --clean   :: 方案一
    if exist allure-report rmdir /s /q allure-report          :: 方案二（本项目采用）
    ```

    `report.bat` 里用的是方案二，因为它在 Windows 上更彻底，也不依赖 Allure 版本的参数行为。注意：这个警告每次跑都会出现、只影响"新旧混在一起"的情况，**不是**每次都必须删——但只要你想看的是"这一次"的结果，就必须删。
