"""Page object for https://www.saucedemo.com/ (login screen)."""
from __future__ import annotations

from selenium.webdriver.common.by import By

from .base_page import BasePage


class LoginPage(BasePage):
    USERNAME = (By.ID, "user-name")
    PASSWORD = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-button")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "h3[data-test='error']")

    def load(self) -> "LoginPage":
        self.open("/")
        return self

    def login(self, username: str, password: str) -> "LoginPage":
        self.type(self.USERNAME, username)
        self.type(self.PASSWORD, password)
        self.click(self.LOGIN_BUTTON)
        return self

    def error_message(self) -> str:
        return self.text_of(self.ERROR_MESSAGE)
