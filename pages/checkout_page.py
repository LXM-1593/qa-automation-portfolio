"""Page object covering both checkout steps and the confirmation screen."""
from __future__ import annotations

from selenium.webdriver.common.by import By

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
        self.click(self.CONTINUE_BUTTON)
        return self

    def finish(self) -> "CheckoutPage":
        self.wait_url_contains("checkout-step-two")
        self.click(self.FINISH_BUTTON)
        return self

    def complete_header(self) -> str:
        return self.text_of(self.COMPLETE_HEADER)

    def summary_total(self) -> str:
        return self.text_of(self.SUMMARY_TOTAL)

    def error_message(self) -> str:
        return self.text_of(self.ERROR_MESSAGE)
