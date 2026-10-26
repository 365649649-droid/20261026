"""
登录功能测试用例
================
每个 test_ 开头的函数 = 一个用例，pytest 会自动发现并执行。

核心纪律：一个用例只回答一个问题。
    不要把"登录"和"菜单导航"塞进同一个函数，
    否则失败时你分不清是哪块坏了。
"""

import re

import pytest
from playwright.sync_api import expect

BASE_URL = "https://www.saucedemo.com/"


def do_login(page, username, password):
    """
    公共动作抽取。

    三条用例都要"打开页面 + 填账号 + 填密码 + 点登录"，
    抽成一个函数，改一次全生效。
    """
    page.goto(BASE_URL)
    page.get_by_test_id("username").fill(username)
    page.get_by_test_id("password").fill(password)
    page.get_by_test_id("login-button").click()


# ============================================================
# 用例 1：正常登录（成功路径）
# ============================================================
def test_standard_user_can_login(page):
    """标准用户用正确密码，应该进入商品列表页。"""
    do_login(page, "standard_user", "secret_sauce")

    # 三层断言：路由 / 语义 / 内容
    expect(page).to_have_url(re.compile(r".*inventory\.html.*"))
    expect(page.get_by_test_id("title")).to_have_text("Products")
    expect(page.get_by_test_id("inventory-container")).to_be_visible()


# ============================================================
# 用例 2：密码错误（失败路径）
# ============================================================
def test_wrong_password_is_rejected(page):
    """密码错误，应该停在登录页并提示不匹配。"""
    do_login(page, "standard_user", "wrong_password")

    expect(page).to_have_url(BASE_URL)
    error = page.get_by_test_id("error")
    expect(error).to_be_visible()
    expect(error).to_contain_text("Username and password do not match")


# ============================================================
# 用例 3：账号被锁定（边界场景）
# ============================================================
def test_locked_out_user_is_rejected(page):
    """被锁定的用户，即使密码正确也不能登录。"""
    do_login(page, "locked_out_user", "secret_sauce")

    expect(page).to_have_url(BASE_URL)
    error = page.get_by_test_id("error")
    expect(error).to_be_visible()
    expect(error).to_contain_text("locked out")


# ============================================================
# 用例 4：参数化 —— 一份代码跑多组数据
# ============================================================
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
    """
    do_login(page, username, password)

    expect(page).to_have_url(BASE_URL)
    error = page.get_by_test_id("error")
    expect(error).to_be_visible()
    expect(error).to_contain_text(expected_error)
