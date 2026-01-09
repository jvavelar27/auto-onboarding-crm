import pytest
from crm_automation.config import Config
from crm_automation.selectors import Selectors

def test_config_defaults():
    # Test if essential configs are present or defaults work
    assert Config.BASE_URL == "https://crm.infinitegear.app"
    assert Config.DEFAULT_TIMEOUT > 0

def test_selectors_structure():
    # Basic check to ensure selectors are strings and valid css/text
    assert "input" in Selectors.LOGIN_EMAIL_INPUT
    assert "input" in Selectors.PANEL_NAME_INPUT
    assert Selectors.PANELS_URL.startswith("http")
