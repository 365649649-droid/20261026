"""
你录制的【成功登录】脚本 —— 重构版（可直接运行）
=================================================
来源：用 record.bat / codegen 录制后，人工整理。

用例定义：
    用正确的账号密码登录，验证用户能成功进入商品列表页。

运行：
    python my_success_clean.py              # 弹浏览器，看得见过程
    python my_success_clean.py --slow       # 放慢 0.8 秒/步，方便肉眼观察
    python my_success_clean.py --headless   # 静默跑

相比你录制的原版，删掉了这些东西：
    1. [data-test="login-credentials"] + ControlOrMeta+c
       -> 那是你为了复制页面上的账号文本而做的操作，属于"人获取信息"，不是被测功能
    2. [data-test="login-password"] + ControlOrMeta+c
       -> 同上，复制密码文本
    3. fill 之前多余的 click
       -> fill 会自动聚焦，不需要先点
    4. Open Menu / dynamic-catalog-sidebar-link / Close Menu
       -> 属于"菜单导航"，不是登录用例。想测它应该单独写一个用例，
          否则这个用例失败时你分不清是登录坏了还是菜单坏了。
"""

import re
import sys

from playwright.sync_api import expect, sync_playwright

LOGIN_URL = "https://www.saucedemo.com/"

# 这几个练习账号密码是公开印在登录页上的，不涉及真实凭据
USERNAME = "standard_user"
PASSWORD = "secret_sauce"


def open_login_page(page):
    """打开登录页，并确认页面加载正常。"""
    page.goto(LOGIN_URL)
    expect(page.get_by_role("button", name="Login")).to_be_visible()


def submit_login(page, username, password):
    """填写账号密码并提交。

    saucedemo 用的测试属性名是 data-test，
    所以启动时用 set_test_id_attribute("data-test") 声明一次，
    之后就能统一用 get_by_test_id()。
    """
    page.get_by_test_id("username").fill(username)
    page.get_by_test_id("password").fill(password)
    page.get_by_test_id("login-button").click()


def assert_login_succeeded(page):
    """断言：登录成功。这是整个用例的灵魂。

    为什么用三层断言，而不是只看一句文字？
    因为单一信号都可能骗人：
      - 只看文字 "Products"：多语言、文案改版就挂
      - 只看 URL：SPA 可能改了 URL 但内容还是旧的（假跳转）
    三层叠加，才叫"真的进去了"。
    """

    # 第 1 层：URL 跳转到了商品列表页
    # URL 是最硬的信号，因为它代表路由状态真的变了，
    # 而不是页面上碰巧显示了一段文字。
    expect(page).to_have_url(re.compile(r".*inventory\.html.*"))

    # 第 2 层：页面标题变成 Products（业务语义正确）
    expect(page.get_by_test_id("title")).to_have_text("Products")

    # 第 3 层：商品列表容器真的渲染出来了（内容确实加载了）
    expect(page.get_by_test_id("inventory-container")).to_be_visible()


def run(headless: bool, slow_mo: int = 0) -> None:
    with sync_playwright() as p:
        # 声明本站点的测试属性名
        p.selectors.set_test_id_attribute("data-test")

        browser = p.chromium.launch(headless=headless, slow_mo=slow_mo)
        context = browser.new_context()
        page = context.new_page()

        try:
            open_login_page(page)
            submit_login(page, USERNAME, PASSWORD)
            assert_login_succeeded(page)

            page.screenshot(path="my_success_result.png", full_page=True)
            print("通过：standard_user 成功登录并进入商品列表页")

        except AssertionError as e:
            print(f"断言失败，用例不通过：{e}")
            page.screenshot(path="my_success_failure.png", full_page=True)
            raise
        except Exception as e:
            print(f"脚本执行出错：{type(e).__name__}: {e}")
            raise
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    run(
        headless="--headless" in sys.argv,
        slow_mo=800 if "--slow" in sys.argv else 0,
    )
