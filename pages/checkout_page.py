"""Page object covering both checkout steps and the confirmation screen."""
from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .base_page import BasePage


class CheckoutPage(BasePage):
    FIRST_NAME = (By.ID, "first-name")
    LAST_NAME = (By.ID, "last-name")
    POSTAL_CODE = (By.ID, "postal-code")
    CONTINUE_BUTTON = (By.ID, "continue")
    FINISH_BUTTON = (By.ID, "finish")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "h3[data-test='error']")
    COMPLETE_HEADER = (By.CLASS_NAME, "complete-header")
    SUMMARY_TOTAL = (By.CLASS_NAME, "summary_total_label")

    def wait_step_one(self) -> "CheckoutPage":
        self.wait_url_contains("checkout-step-one")
        return self

    def fill_info(self, first_name: str, last_name: str, postal_code: str) -> "CheckoutPage":
        self.type(self.FIRST_NAME, first_name)
        self.type(self.LAST_NAME, last_name)
        self.type(self.POSTAL_CODE, postal_code)
        return self

    def continue_checkout(self) -> "CheckoutPage":
        # 两条合法分支：字段齐全 → step-two；字段缺失 → 原地显示错误提示。
        # 两者都不出现，说明点击落空（JS 未绑定），此时才重试。
        self.click_until(
            self.CONTINUE_BUTTON,
            lambda driver: "checkout-step-two" in driver.current_url
            or bool(driver.find_elements(*self.ERROR_MESSAGE)),
        )
        return self

    def finish(self) -> "CheckoutPage":
        self.wait_url_contains("checkout-step-two")
        self.click_until(
            self.FINISH_BUTTON,
            EC.presence_of_element_located(self.COMPLETE_HEADER),
        )
        return self

    def complete_header(self) -> str:
        return self.text_of(self.COMPLETE_HEADER)

    def summary_total(self) -> str:
        return self.text_of(self.SUMMARY_TOTAL)

    def error_message(self) -> str:
        return self.text_of(self.ERROR_MESSAGE)
