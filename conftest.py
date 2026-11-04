"""Pytest fixtures shared by the whole UI suite.

Design notes:
- One fresh Chrome session per test keeps tests independent and repeatable.
- Headless mode is the default so the suite runs on CI without a display.
- ChromeDriver listens on localhost, so the host proxy must never intercept
  that loopback traffic; NO_PROXY is enforced before WebDriver is created.
- A throw-away user-data-dir per session avoids profile locks and stale state.
- Failures automatically store a screenshot under reports/screenshots/.
"""
from __future__ import annotations

import json
import os
import shutil
import uuid
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

PROJECT_ROOT = Path(__file__).resolve().parent
BASE_URL = os.getenv("BASE_URL", "https://www.saucedemo.com")
HEADLESS = os.getenv("HEADLESS", "1").lower() not in {"0", "false", "no"}

# ChromeDriver is reached over http://localhost:<port>; exclude loopback from
# any corporate/sandbox proxy so Selenium's HTTP calls are not intercepted.
_LOOPBACK = ("localhost", "127.0.0.1", "::1")
for _key in ("NO_PROXY", "no_proxy"):
    _parts = [p for p in os.environ.get(_key, "").split(",") if p]
    _parts.extend(h for h in _LOOPBACK if h not in _parts)
    os.environ[_key] = ",".join(_parts)

with (PROJECT_ROOT / "test_data" / "users.json").open(encoding="utf-8") as handle:
    USERS = json.load(handle)


def _build_driver(profile_dir: Path) -> webdriver.Chrome:
    options = Options()
    if HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument(f"--user-data-dir={profile_dir}")
    options.add_argument("--window-size=1440,960")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-component-update")
    options.add_argument("--disable-sync")
    options.add_argument("--remote-allow-origins=*")
    options.add_argument("--lang=en-US")
    return webdriver.Chrome(options=options)


@pytest.fixture(scope="session")
def users() -> dict:
    return USERS


@pytest.fixture()
def driver():
    profile_dir = PROJECT_ROOT / ".profiles" / uuid.uuid4().hex
    profile_dir.mkdir(parents=True, exist_ok=True)
    session = _build_driver(profile_dir)
    try:
        yield session
    finally:
        try:
            session.quit()
        finally:
            shutil.rmtree(profile_dir, ignore_errors=True)


@pytest.fixture()
def login_page(driver):
    from pages.login_page import LoginPage

    return LoginPage(driver, BASE_URL)


@pytest.fixture()
def inventory_page(driver, users):
    from pages.inventory_page import InventoryPage
    from pages.login_page import LoginPage

    account = users["standard"]
    LoginPage(driver, BASE_URL).load().login(account["username"], account["password"])
    page = InventoryPage(driver, BASE_URL)
    page.wait_loaded()
    return page


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Attach a screenshot to the report whenever a test fails."""
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed:
        return
    driver = item.funcargs.get("driver")
    if driver is None:
        return
    try:
        shot_dir = PROJECT_ROOT / "reports" / "screenshots"
        shot_dir.mkdir(parents=True, exist_ok=True)
        driver.save_screenshot(str(shot_dir / f"{item.name}.png"))
    except Exception:  # never let reporting break the run
        pass
