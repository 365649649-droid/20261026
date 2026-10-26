"""
你录制的脚本 —— 重构版（可直接运行）
=====================================
来源：用 record.bat / codegen 录制后，人工 + AI 整理。

录制时的真实意图：
    输入一组错误的账号密码，验证网站会正确拦截并给出错误提示。

所以这是一个【失败路径】用例，不是登录成功的用例。

运行：
    python my_recorded_clean.py              # 弹浏览器，看得见过程
    python my_recorded_clean.py --headless   # 静默跑

对比你原来录制的版本，改了这几件事：
    1. 删掉误点击（原来点了 .error-message-container，那一步没有意义）
    2. 去掉 fill 之前多余的 click（fill 自己会聚焦）
    3. 定位方式升级成 get_by_test_id，不再手写 [data-test="..."] 字符串
    4. 补上断言 —— 这才是"验证"，不然只是"点了一遍"
    5. 抽成小函数 + 加注释 + 加异常处理 + 失败时截图
"""

import sys

from playwright.sync_api import expect, sync_playwright

LOGIN_URL = "https://www.saucedemo.com/"

# 你录制时用的就是这组错误凭据，保留原样
USERNAME = "123"
PASSWORD = "123"

# 网站对错误凭据的提示文案（断言时只匹配关键片段，避免整句变化就挂）
EXPECTED_ERROR = "Username and password do not match"


def open_login_page(page):
    """打开登录页，并确认页面确实加载出来了。"""
    page.goto(LOGIN_URL)

    # 断言：登录按钮存在 = 页面正常渲染了，没进错页面/没白屏
    expect(page.get_by_role("button", name="Login")).to_be_visible()


def submit_login(page, username, password):
    """填写账号密码并提交。

    定位说明：
        saucedemo 用的是 data-test 属性（不是默认的 data-testid），
        所以下面在启动时调用了 set_test_id_attribute("data-test")，
        之后就能统一用 get_by_test_id() 来定位，比手写选择器干净得多。
    """
    # 不需要先 click 再 fill，fill 会自动聚焦到元素
    page.get_by_test_id("username").fill(username)
    page.get_by_test_id("password").fill(password)
    page.get_by_test_id("login-button").click()


def assert_login_rejected(page):
    """断言：错误凭据应该被拒绝。这是整个用例的核心。"""

    # 1) 不应该跳转，还停在登录页
    expect(page).to_have_url(LOGIN_URL)

    # 2) 应该出现错误提示，且文案匹配
    error_box = page.get_by_test_id("error")
    expect(error_box).to_be_visible()
    expect(error_box).to_contain_text(EXPECTED_ERROR)


def run(headless: bool, slow_mo: int = 0) -> None:
    with sync_playwright() as p:
        # 告诉 Playwright：这个站点的测试属性叫 data-test
        # 之后 get_by_test_id("username") 就等价于 [data-test="username"]
        p.selectors.set_test_id_attribute("data-test")

        # slow_mo 是每一步之间的停顿毫秒数，纯粹为了让人看清过程
        browser = p.chromium.launch(headless=headless, slow_mo=slow_mo)
        context = browser.new_context()
        page = context.new_page()

        try:
            open_login_page(page)
            submit_login(page, USERNAME, PASSWORD)
            assert_login_rejected(page)

            # 留一张证据截图
            page.screenshot(path="my_recorded_result.png", full_page=True)
            print("通过：错误凭据被正确拦截，错误提示文案匹配")

        except AssertionError as e:
            # 断言失败 = 要么产品有 bug，要么你的定位器写错了
            print(f"断言失败，用例不通过：{e}")
            page.screenshot(path="my_recorded_failure.png", full_page=True)
            raise
        except Exception as e:
            print(f"脚本执行出错：{type(e).__name__}: {e}")
            raise
        finally:
            # 无论成功失败都要清理，否则进程会挂住
            context.close()
            browser.close()


if __name__ == "__main__":
    # 支持 --headless（静默）和 --slow（放慢，方便肉眼观察）
    run(
        headless="--headless" in sys.argv,
        slow_mo=800 if "--slow" in sys.argv else 0,
    )
