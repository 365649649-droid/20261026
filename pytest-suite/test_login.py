"""
登录功能测试用例
================
每个 test_ 开头的函数 = 一个用例，pytest 会自动发现并执行。

核心纪律：一个用例只回答一个问题。
    不要把"登录"和"菜单导航"塞进同一个函数，
    否则失败时你分不清是哪块坏了。

关于 Allure 标注（下面那些 @allure.xxx 装饰器）：
    它们不影响测试逻辑，只影响报告的"分组和排版"。
    epic > feature > story 是三层归属，报告左侧就按这个层级折叠展示；
    severity 决定用例被标成 blocker / critical / normal / minor / trivial；
    allure.step() 会在报告里生成"步骤时间线"，失败时能一眼看出卡在第几步。
"""

import re

import allure
import pytest
from playwright.sync_api import expect

BASE_URL = "https://www.saucedemo.com/"


def do_login(page, username, password):
    """
    公共动作抽取。

    三条用例都要"打开页面 + 填账号 + 填密码 + 点登录"，
    抽成一个函数，改一次全生效。

    包上 allure.step 之后，报告里每一步都会单独列出来，
    哪一步慢、哪一步挂，一目了然。
    """
    with allure.step("打开登录页"):
        # wait_until="domcontentloaded" 比默认的 "load" 更快也更稳：
        # 只要 DOM 就绪就能操作，不必等图片等静态资源加载完。
        # timeout 放宽到 60 秒，容忍网络波动。
        page.goto(BASE_URL, wait_until="domcontentloaded", timeout=60_000)

    with allure.step(f"输入用户名：{username or '(空)'}"):
        page.get_by_test_id("username").fill(username)

    # 密码不写进步骤名 —— 报告是对外可分享的，别把凭据漏出去
    with allure.step("输入密码"):
        page.get_by_test_id("password").fill(password)

    with allure.step("点击 Login 按钮"):
        page.get_by_test_id("login-button").click()


# ============================================================
# 用例 1：正常登录（成功路径）
# ============================================================
@allure.epic("SauceDemo 电商网站")
@allure.feature("登录功能")
@allure.story("正常登录")
@allure.severity(allure.severity_level.BLOCKER)
@allure.title("标准用户用正确密码可以登录成功")
def test_standard_user_can_login(page):
    """标准用户用正确密码，应该进入商品列表页。"""
    do_login(page, "standard_user", "secret_sauce")

    # 三层断言：路由 / 语义 / 内容
    with allure.step("校验已跳转到商品列表页（URL）"):
        expect(page).to_have_url(re.compile(r".*inventory\.html.*"))
    with allure.step("校验页面标题是 Products"):
        expect(page.get_by_test_id("title")).to_have_text("Products")
    with allure.step("校验商品列表容器已渲染"):
        expect(page.get_by_test_id("inventory-container")).to_be_visible()


# ============================================================
# 用例 2：密码错误（失败路径）
# ============================================================
@allure.epic("SauceDemo 电商网站")
@allure.feature("登录功能")
@allure.story("密码错误")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("密码错误时被拒绝，并提示不匹配")
def test_wrong_password_is_rejected(page):
    """密码错误，应该停在登录页并提示不匹配。"""
    do_login(page, "standard_user", "wrong_password")

    with allure.step("校验仍停留在登录页"):
        expect(page).to_have_url(BASE_URL)
    with allure.step("校验错误提示可见"):
        error = page.get_by_test_id("error")
        expect(error).to_be_visible()
        expect(error).to_contain_text("Username and password do not match")


# ============================================================
# 用例 3：账号被锁定（边界场景）
# ============================================================
@allure.epic("SauceDemo 电商网站")
@allure.feature("登录功能")
@allure.story("账号锁定")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("被锁定的用户即使密码正确也无法登录")
def test_locked_out_user_is_rejected(page):
    """被锁定的用户，即使密码正确也不能登录。"""
    do_login(page, "locked_out_user", "secret_sauce")

    with allure.step("校验仍停留在登录页"):
        expect(page).to_have_url(BASE_URL)
    with allure.step("校验提示账号被锁定"):
        error = page.get_by_test_id("error")
        expect(error).to_be_visible()
        expect(error).to_contain_text("locked out")


# ============================================================
# 用例 4：参数化 —— 一份代码跑多组数据
# ============================================================
@allure.epic("SauceDemo 电商网站")
@allure.feature("登录功能")
@allure.story("登录失败场景")
@allure.severity(allure.severity_level.NORMAL)
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
    """
    参数化：同一个测试逻辑，喂三组不同数据。

    这是 pytest 最值钱的功能之一 ——
    如果不用参数化，上面三段要复制三遍，改一处要改三处。

    报告标题用 allure.dynamic 动态生成，因为用户名可能是空的，
    写死在装饰器里会出现"用户 "这种半截标题。
    """
    allure.dynamic.title(f"登录失败：用户「{username or '(空用户名)'}」")

    do_login(page, username, password)

    with allure.step("校验仍停留在登录页"):
        expect(page).to_have_url(BASE_URL)
    with allure.step(f"校验提示包含「{expected_error}」"):
        error = page.get_by_test_id("error")
        expect(error).to_be_visible()
        expect(error).to_contain_text(expected_error)
