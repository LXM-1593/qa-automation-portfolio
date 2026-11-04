"""Base page object: shared wait/click/type helpers for all pages."""
from __future__ import annotations

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    """Thin wrapper around WebDriver with explicit-wait helpers.

    Every page object inherits from this class so that locating, waiting and
    interacting with elements stays consistent and free of sleeps.
    """

    def __init__(self, driver: WebDriver, base_url: str, timeout: int = 12) -> None:
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout)

    # ------------------------------------------------------------------ nav
    def open(self, path: str = "") -> "BasePage":
        url = f"{self.base_url}/{path.lstrip('/')}" if path else self.base_url
        self.driver.get(url)
        return self

    # --------------------------------------------------------------- lookups
    def find(self, locator: tuple[str, str]) -> WebElement:
        return self.wait.until(EC.presence_of_element_located(locator))

    def find_all(self, locator: tuple[str, str]) -> list[WebElement]:
        self.wait.until(EC.presence_of_element_located(locator))
        return self.driver.find_elements(*locator)

    def click(self, locator: tuple[str, str]) -> "BasePage":
        self.wait.until(EC.element_to_be_clickable(locator)).click()
        return self

    def click_until(
        self,
        locator: tuple[str, str],
        condition,
        attempts: int = 3,
    ) -> "BasePage":
        """Click until the expected post-condition holds.

        Why this exists: SauceDemo ships static HTML progressively enhanced by
        JS. The button is visible and enabled *before* its handler is bound, so
        on a slow CI runner the first click can land on a dead element — no
        exception, no navigation, just a silent no-op. Local runs almost always
        win the race, which makes this the classic "green locally, red on CI"
        flake.

        The fix is not a sleep: each attempt re-locates the element, clicks,
        and then waits for the *observable consequence* (URL change, new view).
        A genuinely broken button still fails — after N attempts — so this
        stabilises timing without hiding regressions.
        """
        last_error: Exception | None = None
        for _ in range(attempts):
            self.click(locator)
            try:
                self.wait.until(condition)
                return self
            except TimeoutException as exc:
                last_error = exc
        raise TimeoutException(
            f"点击 {locator} 后等待后置条件超时，已重试 {attempts} 次：{last_error}"
        )

    def type(self, locator: tuple[str, str], text: str) -> "BasePage":
        element = self.wait.until(EC.visibility_of_element_located(locator))
        element.clear()
        element.send_keys(text)
        return self

    def text_of(self, locator: tuple[str, str]) -> str:
        return self.find(locator).text.strip()

    def is_visible(self, locator: tuple[str, str], timeout: int | None = None) -> bool:
        try:
            WebDriverWait(self.driver, timeout or self.timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    def wait_url_contains(self, fragment: str) -> "BasePage":
        self.wait.until(EC.url_contains(fragment))
        return self

    @property
    def current_url(self) -> str:
        return self.driver.current_url
