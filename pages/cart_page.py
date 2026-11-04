"""Page object for the shopping cart screen."""
from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .base_page import BasePage


class CartPage(BasePage):
    CART_ITEMS = (By.CLASS_NAME, "cart_item")
    ITEM_NAME = (By.CLASS_NAME, "inventory_item_name")
    CHECKOUT_BUTTON = (By.ID, "checkout")
    CONTINUE_SHOPPING = (By.ID, "continue-shopping")

    def wait_loaded(self) -> "CartPage":
        self.wait_url_contains("cart.html")
        return self

    def item_count(self) -> int:
        return len(self.find_all(self.CART_ITEMS))

    def item_names(self) -> list[str]:
        return [element.text.strip() for element in self.find_all(self.ITEM_NAME)]

    def remove_item(self, name: str) -> "CartPage":
        locator = (
            By.XPATH,
            "//div[contains(@class,'cart_item')]"
            f"[.//div[contains(@class,'inventory_item_name') and normalize-space()='{name}']]"
            "//button",
        )
        self.click(locator)
        return self

    def checkout(self) -> "CartPage":
        # 以后置条件（URL 跳到 checkout-step-one）作为重试判据，兼容 JS 绑定竞态
        self.click_until(self.CHECKOUT_BUTTON, EC.url_contains("checkout-step-one"))
        return self
