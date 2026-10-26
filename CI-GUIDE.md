# 第三课：接入 CI（GitHub Actions）

> 目标：**每次提交代码，测试自动跑一遍。**
> 这是"会写脚本"和"会做测试工程"的分界线。

---

## 这一步到底解决什么问题

现在你是手动跑测试。缺点很明显：

- 忘了跑 → 代码带着 bug 合进主分支
- 只在自己机器上跑 → 换台电脑/换个系统就挂（环境差异）
- 没有历史记录 → 说不清"上周三那次到底是好的还是坏的"

接了 CI 之后：**每次 push 自动跑，结果留痕，挂了自动截图。**

---

## 我给你的文件

```
playwright-day1/
├── .github/workflows/ui-tests.yml    # CI 流水线定义
├── .gitignore                        # 哪些文件不进仓库
└── .gitattributes                    # 换行符规则（保护 .bat）
```

`ui-tests.yml` 一共 7 步：

| 步骤 | 作用 |
|------|------|
| Checkout | 把仓库代码拉到 CI 机器 |
| Setup Python | 装 Python 3.12 + 开 pip 缓存 |
| Install dependencies | 装 pytest、playwright |
| Install Chromium | 装浏览器内核（CI 机器是干净的，必须装） |
| Run tests | 跑测试，产出 `report.xml` |
| Upload failure screenshots | **挂了才上传截图** |
| Upload test report | 无论成败都留档 |

**注意第 6 步**：`if: failure()`。成功的截图没人看，还占存储——这是标准做法。

---

## 怎么让它跑起来（3 步）

### 第 1 步：在 GitHub 建一个空仓库

1. 打开 https://github.com/new
2. Repository name 填 `playwright-ui-tests`（名字随意）
3. **不要**勾选 "Add a README file"（勾了会和你本地的冲突）
4. 点 Create repository
5. 建好后页面上会给你一个地址，形如：
   `https://github.com/你的用户名/playwright-ui-tests.git`

### 第 2 步：配置 git 身份并提交

打开 PowerShell，**逐行执行**（把尖括号里的内容换成你自己的）：

```powershell
cd "C:/Users/Admin/WorkBuddy/2026-10-26-17-06-48/playwright-day1"

git config user.name "你的名字"
git config user.email "你的邮箱@example.com"

git commit -m "feat: Playwright UI 自动化测试套件 + CI 流水线"
```

> `user.name` / `user.email` 建议和你的 GitHub 账号一致，
> 否则 commit 在 GitHub 上不会关联到你的头像。

### 第 3 步：关联远程仓库并推送

```powershell
# 换成第 1 步给你的仓库地址
git remote add origin https://github.com/你的用户名/playwright-ui-tests.git

# GitHub 在国内直连不稳，先给这个仓库配代理（换成你自己梯子的端口）
git config http.proxy http://127.0.0.1:10808

git push -u origin main
```

> **代理端口怎么确认**：你之前系统代理是 `127.0.0.1:10808`，
> 如果 push 超时就换这个。不需要时代码里删掉：
> `git config --unset http.proxy`

---

## 怎么知道成功了

1. 推送成功后打开你的仓库页面
2. 点顶部 **Actions** 标签
3. 会看到一条正在跑的 workflow（黄色圆点 → 转圈）
4. 等 1~3 分钟，变成 **绿色对勾** 就是全过了

点进去能看到每一步的耗时和完整日志，和我们本地跑的输出一样：

```
6 passed in 7.86s
```

---

## 强烈建议：故意弄坏一次，看它变红

这是最有价值的一步——**你得亲眼见过 CI 挂掉的样子，才知道它真的在保护你。**

随便找个用例改错一个断言，比如 `test_login.py` 里：

```python
expect(page.get_by_test_id("title")).to_have_text("Products")
# 改成
expect(page.get_by_test_id("title")).to_have_text("WRONG_TEXT")
```

然后：

```powershell
git add -A
git commit -m "test: 故意让 CI 红一次"
git push
```

去 Actions 页面看，你会看到：
- 红色叉号
- 失败用例的名字和断言错误详情
- **Artifacts 区域多了一个 `failure-screenshots`** ← 点进去下载，就是失败那一刻的页面截图

看完记得改回来再推一次。

---

## 如果要给国内公司用：Jenkins 版

GitHub Actions 是 SaaS，国内公司很多用 Jenkins。逻辑完全一样，只是写法不同：

```groovy
pipeline {
    agent { label 'windows' }
    stages {
        stage('Setup') {
            steps {
                bat 'python -m pip install pytest playwright'
                bat 'python -m playwright install chromium'
            }
        }
        stage('Test') {
            steps {
                dir('pytest-suite') {
                    bat 'python -m pytest --junitxml=report.xml'
                }
            }
            post {
                always {
                    junit 'pytest-suite/report.xml'
                }
                failure {
                    archiveArtifacts artifacts: 'pytest-suite/screenshots/**', allowEmptyArchive: true
                }
            }
        }
    }
}
```

**共同的三个要素，记住就够了：**
1. 装依赖（含浏览器内核）
2. 跑测试并产出 JUnit XML
3. 失败时归档截图

换任何 CI 平台（GitLab CI、Azure DevOps、Coding）都是这三件事，只是语法不同。

---

## 常见问题

| 现象 | 原因 | 怎么办 |
|------|------|--------|
| `push` 卡住/超时 | 连不上 GitHub | 配代理 `git config http.proxy http://127.0.0.1:10808` |
| `Authentication failed` | 密码不能用，要用 Token | 用 Personal Access Token 当密码（Settings → Developer settings → Tokens） |
| Actions 里没有 workflow | 文件路径不对 | 必须是 `.github/workflows/*.yml`，注意 `.github` 前面的点 |
| CI 里测试红了，本地是绿的 | 环境差异（时区/语言/网络） | 看日志定位，这类问题正是 CI 的价值 |
| `Playwright install` 超时 | CI 访问 CDN 慢 | 加镜像：`PLAYWRIGHT_DOWNLOAD_HOST` 环境变量 |

---

## 这一课你真正学到的东西

不是"怎么写 YAML"，而是这三个认知：

1. **测试必须自动化执行，不能靠人记得跑**
2. **失败必须留下现场**（截图 + 日志 + 报告），否则等于没测
3. **环境差异是隐性 bug 的最大来源**，CI 帮你提前暴露
