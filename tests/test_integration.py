from unittest.mock import MagicMock
from crm_automation.pages.login_page import LoginPage
from crm_automation.pages.base_page import BasePage

def test_login_page_init():
    mock_page = MagicMock()
    page = LoginPage(mock_page, dry_run=True)
    assert isinstance(page, BasePage)
    assert page.dry_run is True
    assert page.page == mock_page
