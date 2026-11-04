"""End-to-end checkout regression tests."""
import pytest

from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage


def _go_to_checkout(inventory_page) -> CheckoutPage:
    inventory_page.add_item("Sauce Labs Backpack")
    inventory_page.go_to_cart()

    cart = CartPage(inventory_page.driver, inventory_page.base_url)
    cart.wait_loaded()
    cart.checkout()

    checkout = CheckoutPage(inventory_page.driver, inventory_page.base_url)
    checkout.wait_step_one()
    return checkout


@pytest.mark.smoke
@pytest.mark.regression
def test_full_purchase_flow(inventory_page):
    checkout = _go_to_checkout(inventory_page)
    checkout.fill_info("Ada", "Lovelace", "12345")
    checkout.continue_checkout()
    checkout.finish()

    assert "Thank you for your order" in checkout.complete_header()


@pytest.mark.regression
def test_checkout_requires_postal_code(inventory_page):
    checkout = _go_to_checkout(inventory_page)
    checkout.fill_info("Ada", "Lovelace", "")
    checkout.continue_checkout()

    assert "Postal Code is required" in checkout.error_message()


@pytest.mark.regression
def test_checkout_shows_order_total(inventory_page):
    checkout = _go_to_checkout(inventory_page)
    checkout.fill_info("Ada", "Lovelace", "12345")
    checkout.continue_checkout()

    assert checkout.summary_total().startswith("Total:")
