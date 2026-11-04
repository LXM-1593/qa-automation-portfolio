"""Product catalogue and sorting regression tests."""
import pytest
from selenium.webdriver.support.ui import WebDriverWait

from pages.inventory_page import InventoryPage


def _wait_until_sorted(page: InventoryPage, reverse: bool = False) -> list[float]:
    """Sorting is client-side; wait until the DOM reflects the new order."""

    def condition(_driver):
        prices = page.item_prices()
        return len(prices) > 1 and prices == sorted(prices, reverse=reverse)

    WebDriverWait(page.driver, 5).until(condition)
    return page.item_prices()


@pytest.mark.smoke
def test_inventory_lists_all_products(inventory_page):
    assert inventory_page.item_count() == 6
    assert len(set(inventory_page.item_names())) == 6


@pytest.mark.regression
def test_sort_by_price_low_to_high(inventory_page):
    inventory_page.sort_by("lohi")
    prices = _wait_until_sorted(inventory_page)
    assert prices == sorted(prices)


@pytest.mark.regression
def test_sort_by_price_high_to_low(inventory_page):
    inventory_page.sort_by("hilo")
    prices = _wait_until_sorted(inventory_page, reverse=True)
    assert prices == sorted(prices, reverse=True)


@pytest.mark.regression
def test_sort_by_name_a_to_z(inventory_page):
    inventory_page.sort_by("az")
    names = inventory_page.item_names()
    assert names == sorted(names, key=str.casefold)
