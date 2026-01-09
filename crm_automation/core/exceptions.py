class CRMAutomationError(Exception):
    """Base class for exceptions in this module."""
    pass

class ElementNotFoundError(CRMAutomationError):
    """Raised when an expected element is not found."""
    pass

class ActionFailedError(CRMAutomationError):
    """Raised when an action (click, type) fails."""
    pass

class LoginFailedError(CRMAutomationError):
    """Raised when 2FA or Login fails."""
    pass
