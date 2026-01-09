from playwright.sync_api import Page, Locator, TimeoutError as PlaywrightTimeoutError
from crm_automation.core.logger import logger
from crm_automation.core.exceptions import ElementNotFoundError, ActionFailedError

class BasePage:
    def __init__(self, page: Page, dry_run: bool = False):
        self.page = page
        self.dry_run = dry_run

    def navigate(self, url: str):
        logger.info(f"Navigating to {url}")
        if not self.dry_run:
            try:
                self.page.goto(url)
            except Exception as e:
                raise ActionFailedError(f"Failed to navigate to {url}: {e}")

    def click(self, selector: str, description: str = "element"):
        logger.info(f"Clicking {description} ({selector})")
        if not self.dry_run:
            try:
                self.page.click(selector)
            except PlaywrightTimeoutError:
                raise ElementNotFoundError(f"Element not found for click: {selector}")
            except Exception as e:
                raise ActionFailedError(f"Failed to click {description}: {e}")

    def fill(self, selector: str, value: str, description: str = "field"):
        if "password" in description.lower() or "código" in description.lower():
            safe_value = "***"
        else:
            safe_value = value
            
        logger.info(f"Filling {description} with '{safe_value}'")
        if not self.dry_run:
            try:
                self.page.fill(selector, value)
            except PlaywrightTimeoutError:
                raise ElementNotFoundError(f"Element not found for fill: {selector}")
            except Exception as e:
                raise ActionFailedError(f"Failed to fill {description}: {e}")

    def exists(self, selector: str, timeout: int = 5000) -> bool:
        """Checks if element exists. Always checks for real, even in dry-run, if possible, 
        or assumes False/True based on safety. But usually we want to know state."""
        # For idempotency logic, we might need to know if something exists.
        # If dry-run, we might assume it doesn't exist to show the 'Creation' log,
        # OR we just check it properly to show 'Skipping'. 
        # Safest is to actually check if we can (read-only).
        try:
            self.page.wait_for_selector(selector, state="visible", timeout=timeout)
            return True
        except:
            return False

    def wait_for_url(self, url_snippet: str):
        logger.info(f"Waiting for URL to contain: {url_snippet}")
        if not self.dry_run:
            self.page.wait_for_url(f"**/{url_snippet}**")

    def screenshot(self, path: str):
        if not self.dry_run:
            self.page.screenshot(path=path)
            logger.info(f"Screenshot saved to {path}")
