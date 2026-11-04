"""Page object for the product inventory / catalogue screen."""
from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from .base_page import BasePage


class InventoryPage(BasePage):
    LIST = (By.CLASS_NAME, "inventory_list")
    ITEMS = (By.CLASS_NAME, "inventory_item")
    ITEM_NAME = (By.CLASS_NAME, "inventory_item_name")
    ITEM_PRICE = (By.CLASS_NAME, "inventory_item_price")
    SORT_SELECT = (By.CSS_SELECTOR, "select.product_sort_container")
    CART_LINK = (By.CLASS_NAME, "shopping_cart_link")
    CART_BADGE = (By.CLASS_NAME, "shopping_cart_badge")
    MENU_BUTTON = (By.ID, "react-burger-menu-btn")
    LOGOUT_LINK = (By.ID, "logout_sidebar_link")

    def wait_loaded(self) -> "InventoryPage":
        self.find(self.LIST)
        return self

    def item_count(self) -> int:
        return len(self.find_all(self.ITEMS))

    def item_names(self) -> list[str]:
        return [element.text.strip() for element in self.find_all(self.ITEM_NAME)]

    def item_prices(self) -> list[float]:
        return [
            float(element.text.replace("$", "").strip())
            for element in self.find_all(self.ITEM_PRICE)
        ]

    def sort_by(self, value: str) -> "InventoryPage":
        """value: az | za | lohi | hilo"""
        Select(self.find(self.SORT_SELECT)).select_by_value(value)
        return self

    def _item_button(self, name: str, label: str) -> tuple[str, str]:
        return (
            By.XPATH,
            "//div[contains(@class,'inventory_item')]"
            f"[.//div[contains(@class,'inventory_item_name') and normalize-space()='{name}']]"
            f"//button[normalize-space()='{label}']",
        )

    def add_item(self, name: str) -> "InventoryPage":
        self.click(self._item_button(name, "Add to cart"))
        return self

    def remove_item(self, name: str) -> "InventoryPage":
        self.click(self._item_button(name, "Remove"))
        return self

    def cart_count(self) -> int:
        if self.is_visible(self.CART_BADGE, timeout=3):
            return int(self.text_of(self.CART_BADGE))
        return 0

    def go_to_cart(self) -> "InventoryPage":
        self.click_until(self.CART_LINK, EC.url_contains("cart.html"))
        return self

    def logout(self) -> "InventoryPage":
        # 侧边菜单是 JS 展开的，先等菜单项可点击，再以后置条件确认已离开商品页
        self.click(self.MENU_BUTTON)
        self.click_until(
            self.LOGOUT_LINK,
            lambda driver: "inventory.html" not in driver.current_url,
        )
        return self
