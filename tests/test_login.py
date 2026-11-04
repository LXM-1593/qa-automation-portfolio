"""Authentication regression tests."""
import pytest

from pages.inventory_page import InventoryPage


@pytest.mark.smoke
def test_login_success(login_page, driver, users):
    account = users["standard"]
    login_page.load().login(account["username"], account["password"])

    InventoryPage(driver, login_page.base_url).wait_loaded()
    assert "inventory.html" in driver.current_url


@pytest.mark.smoke
def test_login_with_invalid_password(login_page, users):
    account = users["invalid"]
    login_page.load().login(account["username"], account["password"])

    assert "do not match" in login_page.error_message()


def test_locked_user_is_rejected(login_page, users):
    account = users["locked"]
    login_page.load().login(account["username"], account["password"])

    assert "locked out" in login_page.error_message()
    assert "inventory.html" not in login_page.current_url


def test_logout_returns_to_login(login_page, driver, users):
    account = users["standard"]
    login_page.load().login(account["username"], account["password"])

    inventory = InventoryPage(driver, login_page.base_url)
    inventory.wait_loaded()
    inventory.logout()

    login_page.wait_url_contains("saucedemo.com")
    assert "inventory.html" not in driver.current_url
    assert login_page.is_visible(login_page.LOGIN_BUTTON)
