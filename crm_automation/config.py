import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    CRM_EMAIL = os.getenv("CRM_EMAIL")
    DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", 30000))
    BASE_URL = "https://crm.infinitegear.app"
    
    # URLs
    URL_LOGIN = "https://crm.infinitegear.app/login" # Assumindo
    URL_PARTNER = "https://crm.infinitegear.app/admin/company/partner"
    URL_PANELS = "https://crm.infinitegear.app/panels"
    URL_CONTACTS = "https://crm.infinitegear.app/contacts"

    @staticmethod
    def get_email(cli_email=None):
        return cli_email or Config.CRM_EMAIL
