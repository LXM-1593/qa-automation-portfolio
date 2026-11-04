"""Shopping-cart regression tests."""
import pytest


@pytest.mark.smoke
def test_add_single_item_updates_badge(inventory_page):
    inventory_page.add_item("Sauce Labs Backpack")
    assert inventory_page.cart_count() == 1


@pytest.mark.regression
def test_add_multiple_items(inventory_page):
    inventory_page.add_item("Sauce Labs Backpack")
    inventory_page.add_item("Sauce Labs Bike Light")
    assert inventory_page.cart_count() == 2


@pytest.mark.regression
def test_remove_item_updates_badge(inventory_page):
    inventory_page.add_item("Sauce Labs Backpack")
    assert inventory_page.cart_count() == 1

    inventory_page.remove_item("Sauce Labs Backpack")
    assert inventory_page.cart_count() == 0


@pytest.mark.regression
def test_added_item_is_present_in_cart(inventory_page):
    from pages.cart_page import CartPage

    inventory_page.add_item("Sauce Labs Onesie")
    inventory_page.go_to_cart()

    cart = CartPage(inventory_page.driver, inventory_page.base_url)
    cart.wait_loaded()
    assert "Sauce Labs Onesie" in cart.item_names()
