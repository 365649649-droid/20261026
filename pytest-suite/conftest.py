"""
pytest 公共配置（conftest.py）
==============================
pytest 会自动加载这个文件，你不需要在任何地方 import 它。

它做四件事：
    1. 注册两个自定义命令行参数：--headed / --slowmo
    2. 提供 browser 和 page 两个 fixture（测试函数用参数名直接取用）
    3. 用例失败时自动截图，并把截图塞进 Allure 报告
    4. 把环境信息（Python / Playwright / 系统版本）写进报告首页
"""

import platform
import re
from pathlib import Path

import allure
import pytest
from playwright.sync_api import sync_playwright

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


def pytest_addoption(parser):
    """注册自定义命令行参数，这样 pytest 才认识 --headed / --slowmo。"""
    parser.addoption(
        "--headed",
        action="store_true",
        default=False,
        help="显示浏览器窗口（默认无头模式，看不见浏览器）",
    )
    parser.addoption(
        "--slowmo",
        action="store",
        default=0,
        type=int,
        help="每步停顿的毫秒数，例如 --slowmo=500",
    )


@pytest.fixture(scope="session")
def browser(pytestconfig):
    """
    整个测试会话只启动一次浏览器，所有用例复用。

    scope="session" 是性能关键：
    每条用例都重启浏览器的话，6 条用例要多花 20 秒以上。
    """
    headless = not pytestconfig.getoption("--headed")
    slow_mo = pytestconfig.getoption("--slowmo")

    with sync_playwright() as p:
        # 注意：selectors 挂在 Playwright 实例 (p) 上，不在 BrowserContext 上。
        # 写 context.selectors 会报 AttributeError，这是个常见坑。
        p.selectors.set_test_id_attribute("data-test")

        browser = p.chromium.launch(headless=headless, slow_mo=slow_mo)
        yield browser          # yield 之前是"准备"，之后是"清理"
        browser.close()


@pytest.fixture
def page(browser):
    """
    每条测试函数拿到一个全新的页面（独立 context）。

    为什么不用同一个页面？
    因为登录状态会互相污染 —— 上一条用例登录了，
    下一条用例打开页面时可能已经是登录态，测试就不可信了。
    """
    context = browser.new_context()
    page = context.new_page()

    # 统一放宽操作超时（默认 30 秒）。访问境外站点时网络抖动很常见，
    # 用例偶发 TimeoutError 大多是这个原因，不是脚本写错了。
    page.set_default_timeout(60_000)
    page.set_default_navigation_timeout(60_000)

    yield page
    context.close()


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item, call):
    """
    用例失败时自动截图存到 screenshots/，并附到 Allure 报告里。

    这是自动化测试的救命功能：
    CI 上跑挂了，你不在现场，只能靠这张图还原"当时页面长什么样"。
    """
    report = yield

    if report.when == "call" and report.failed:
        page = item.funcargs.get("page")
        if page is not None:
            SCREENSHOT_DIR.mkdir(exist_ok=True)
            safe_name = re.sub(r"[^\w\-]", "_", item.name)
            shot = SCREENSHOT_DIR / f"FAILED_{safe_name}.png"
            try:
                page.screenshot(path=str(shot), full_page=True)
                # 存一份到磁盘（给 CI 当 artifact），再附一份到报告里（给报告看）
                with open(shot, "rb") as f:
                    allure.attach(
                        f.read(),
                        name=f"失败截图 - {item.name}",
                        attachment_type=allure.attachment_type.PNG,
                    )
                # 顺手记下失败时的网址，复现时能直接打开
                allure.attach(
                    page.url,
                    name="失败时的页面地址",
                    attachment_type=allure.attachment_type.URI_LIST,
                )
            except Exception:
                # 截图失败不能影响原本的错误信息
                pass

    return report


def pytest_sessionfinish(session, exitstatus):
    """
    Allure 报告的"环境信息"区块。

    报告首页会显示这一块，用来回答"这个结果是什么机器上跑出来的"——
    本地能过、CI 挂了的玄学问题，往往靠它破案（Python 版本不同、
    浏览器版本不同、系统不同）。
    """
    alluredir = session.config.getoption("--alluredir", default=None)
    if not alluredir:
        return

    from importlib.metadata import version

    def safe(pkg):
        try:
            return version(pkg)
        except Exception:
            return "未安装"

    info = {
        "Python": platform.python_version(),
        "pytest": safe("pytest"),
        "playwright": safe("playwright"),
        "allure-pytest": safe("allure-pytest"),
        "操作系统": f"{platform.system()} {platform.release()}",
        "浏览器": "Chromium（headless，可加 --headed 切可见）",
        "被测站点": "https://www.saucedemo.com/",
    }

    target = Path(alluredir)
    target.mkdir(parents=True, exist_ok=True)
    (target / "environment.properties").write_text(
        "\n".join(f"{k}={v}" for k, v in info.items()),
        encoding="utf-8",
    )
