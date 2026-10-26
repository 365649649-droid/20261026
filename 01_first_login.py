"""
Playwright 第一天 —— 第一个登录自动化脚本
=========================================
目标站点: https://www.saucedemo.com/  (官方公开的练习用假商店, 无需注册)
练习账号: standard_user / secret_sauce

本脚本演示一个完整用例的两个场景:
    场景A: 账号密码正确 -> 应该登录成功, 进入商品列表页
    场景B: 密码错误     -> 应该登录失败, 页面给出错误提示

运行方式:
    python 01_first_login.py              # 弹浏览器, 看得见过程(推荐第一次这么跑)
    python 01_first_login.py --headless   # 不弹浏览器, 静默跑

跑完后本目录下会生成几张 .png 截图, 那是脚本执行的证据。
"""

import argparse
import re
import sys

from playwright.sync_api import expect, sync_playwright

# 让控制台输出跟随系统编码(中文 Windows 是 GBK), 只把无法编码的字符替换成 ? 而不是抛异常。
# 注意: 不要强行改成 utf-8, 否则在 GBK 的 cmd 窗口里中文会变乱码。
try:
    sys.stdout.reconfigure(errors="replace")
except Exception:
    pass

LOGIN_URL = "https://www.saucedemo.com/"
BASE_URL = "https://www.saucedemo.com"

# 练习站点的公开账号, 不需要自己注册
NORMAL_USER = "standard_user"
CORRECT_PASSWORD = "secret_sauce"
WRONG_PASSWORD = "wrong_password_123"


def open_login_page(page):
    """打开登录页, 并确认确实到了登录页."""
    # goto 会自动等待页面加载完成, 不用自己 sleep
    page.goto(LOGIN_URL)

    # 断言: 确认登录按钮真的在页面上, 说明没进错页面
    expect(page.get_by_role("button", name="Login")).to_be_visible()


def fill_login_form(page, username, password):
    """填写登录表单并提交."""
    # 定位方式优先用 data-test 属性 —— 这是前端专门留给测试用的标记,
    # 不会因为样式改动、div 层级变化而失效。
    # saucedemo 这个练习站的 data-test 属性是官方提供的, 很适合练手。
    page.locator('[data-test="username"]').fill(username)
    page.locator('[data-test="password"]').fill(password)
    page.locator('[data-test="login-button"]').click()


def scenario_login_success(page):
    """场景A: 正确账号密码, 预期登录成功."""
    print("\n[场景A] 开始: 用正确密码登录")

    open_login_page(page)
    fill_login_form(page, NORMAL_USER, CORRECT_PASSWORD)

    # ===== 断言: 怎么才算"登录成功"? =====

    # 1) URL 应该跳到商品列表页
    expect(page).to_have_url(re.compile(r".*inventory\.html.*"))

    # 2) 页面标题应该是 Products
    expect(page.locator('[data-test="title"]')).to_have_text("Products")

    # 3) 商品列表容器应该可见
    expect(page.locator('[data-test="inventory-container"]')).to_be_visible()

    # 留一张成功截图作为证据
    page.screenshot(path="success_login.png", full_page=True)
    print("[场景A] 通过: 登录成功, 已进入商品列表页, 截图 success_login.png")


def scenario_login_failed(page):
    """场景B: 错误密码, 预期登录失败并给出错误提示."""
    print("\n[场景B] 开始: 故意输错密码")

    open_login_page(page)
    fill_login_form(page, NORMAL_USER, WRONG_PASSWORD)

    # ===== 断言: 怎么才算"正确地失败了"? =====

    # 1) 不应该跳转, 还在登录页
    expect(page).to_have_url(BASE_URL + "/")

    # 2) 页面上应该弹出错误提示
    error_box = page.locator('[data-test="error"]')
    expect(error_box).to_be_visible()
    expect(error_box).to_contain_text("Username and password do not match")

    # 留一张失败截图作为证据
    page.screenshot(path="failed_login.png", full_page=True)
    print("[场景B] 通过: 正确拦截了错误密码, 截图 failed_login.png")


def launch_browser(p, headless, browser_name):
    """
    启动浏览器, 带自动降级。

    为什么要降级?
      Playwright 自带的 chromium 需要额外下载约 150MB 内核,
      国内网络经常下载不动。而 Windows 自带 Edge、很多人也装了 Chrome,
      它们都是 Chromium 内核, Playwright 可以直接驱动, 不用下载任何东西。

    browser_name 说明:
      auto     -> 依次尝试: 自带chromium > 本机Edge > 本机Chrome  (默认)
      chromium -> 只用 Playwright 自带内核
      msedge   -> 只用本机 Microsoft Edge
      chrome   -> 只用本机 Google Chrome
      firefox  -> 只用 Playwright 自带的 Firefox 内核
    """
    slow = 400 if not headless else 0

    candidates = {
        "chromium": lambda: (p.chromium.launch(headless=headless, slow_mo=slow),
                             "Playwright 自带 Chromium 内核"),
        "msedge": lambda: (p.chromium.launch(channel="msedge", headless=headless, slow_mo=slow),
                           "本机 Microsoft Edge"),
        "chrome": lambda: (p.chromium.launch(channel="chrome", headless=headless, slow_mo=slow),
                           "本机 Google Chrome"),
        "firefox": lambda: (p.firefox.launch(headless=headless, slow_mo=slow),
                            "Playwright 自带 Firefox 内核"),
    }

    order = list(candidates.keys())[:-1] if browser_name == "auto" else [browser_name]
    errors = []

    for name in order:
        try:
            browser, desc = candidates[name]()
            print(f"[启动] 正在使用: {desc}")
            return browser
        except Exception as e:
            errors.append(f"  - {name} 启动失败: {str(e).splitlines()[0][:100] if str(e) else type(e).__name__}")

    raise RuntimeError(
        "所有浏览器都启动失败了, 原因如下:\n"
        + "\n".join(errors)
        + "\n\n解决建议:\n"
        "  1. 试试 python 01_first_login.py --browser msedge  (用本机 Edge)\n"
        "  2. 或者补装内核: python -m playwright install chromium\n"
        "     国内下载慢的话用镜像:\n"
        "     set PLAYWRIGHT_DOWNLOAD_HOST=https://cdn.npmmirror.com/binaries/playwright\n"
        "     python -m playwright install chromium"
    )


def main():
    # --headless 决定是否弹浏览器窗口
    parser = argparse.ArgumentParser(description="Playwright 第一天练习脚本")
    parser.add_argument(
        "--headless",
        action="store_true",
        help="不弹出浏览器窗口, 后台静默执行",
    )
    parser.add_argument(
        "--browser",
        default="auto",
        choices=["auto", "chromium", "msedge", "chrome", "firefox"],
        help="指定用哪个浏览器跑, 默认 auto(自带内核优先, 失败自动降级到本机Edge/Chrome)",
    )
    args = parser.parse_args()

    with sync_playwright() as p:
        # headless=False 时会真的弹出浏览器窗口, 第一次建议用这个, 能看清它怎么操作
        # slow_mo 是每一步之间故意停顿的毫秒数, 纯粹为了让你看得清楚
        browser = launch_browser(p, args.headless, args.browser)
        page = browser.new_page()

        try:
            scenario_login_success(page)
            scenario_login_failed(page)
            print("\n" + "=" * 46)
            print("全部通过: 两个场景的断言都成立了")
            print("=" * 46)
        except AssertionError as e:
            # 断言失败 = 发现了 bug(或者你的选择器写错了)
            print(f"\n断言失败, 用例不通过: {e}")
        except Exception as e:
            print(f"\n脚本执行出错了: {e}")
        finally:
            # 不管成功失败都要关掉浏览器, 否则进程会挂住
            browser.close()
            print("浏览器已关闭")


if __name__ == "__main__":
    main()
