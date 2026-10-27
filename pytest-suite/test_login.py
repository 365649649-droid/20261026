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
    # wait_until="domcontentloaded" 比默认的 "load" 更快也更稳：
    # 只要 DOM 就绪就能操作，不必等图片等静态资源加载完。
    # timeout 放宽到 60 秒，容忍网络波动。
    page.goto(BASE_URL, wait_until="domcontentloaded", timeout=60_000)
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

    # ------------------------------------------------------------
    # 【故意让 CI 红一次的练习】
    #
    # 位置很重要：这一行必须放在"已经成功登录、title 元素确实存在"的用例里。
    # 因为此时页面上真的有 title，且它的值是 "Products"，
    # 断言 "WRONG" 才能得到一条干净的对比：
    #     Expected string: "WRONG"
    #     Received string: "Products"
    # 这才叫"断言失败"——元素找得到，是值不对。
    #
    # 如果把它放到登录失败的用例里（之前就是这么放的），
    # 那里页面还停在登录页，压根没有 title 元素，
    # 报出来的是 Actual value: None —— 那是"元素不存在"，不是"断言失败"，
    # 看日志时会被误导成"页面结构变了"。
    #
    # 想恢复绿灯：删掉下面这一行。
    # ------------------------------------------------------------
    expect(page.get_by_test_id("title")).to_have_text("WRONG")


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