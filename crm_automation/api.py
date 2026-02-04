from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from playwright.sync_api import sync_playwright
import logging
import os

from crm_automation.config import Config
from crm_automation.core.logger import setup_logger, logger
from crm_automation.pages.login_page import LoginPage
from crm_automation.pages.admin_page import AdminPage
from crm_automation.pages.panels_page import PanelsPage
from crm_automation.pages.contacts_page import ContactsPage

# Setup Logger
setup_logger(level=logging.INFO)

app = FastAPI(title="CRM Automation API", version="1.0.0")

class InitAuthRequest(BaseModel):
    email: str

class InitAuthResponse(BaseModel):
    status: str
    message: str
    session_state: Dict[str, Any]

class CompleteAuthRequest(BaseModel):
    email: str
    code: str
    account_name: str
    session_state: Dict[str, Any]

class CompleteAuthResponse(BaseModel):
    status: str
    message: str
    logs: Optional[list] = None

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/v1/auth/init", response_model=InitAuthResponse)
def init_auth(request: InitAuthRequest):
    """
    Phase 1: Opens browser, enters email, waits for 2FA code input.
    Returns the session state (cookies/local storage) to be saved by the client (n8n).
    """
    logger.info(f"API: Initiating auth for {request.email}")
    
    try:
        with sync_playwright() as p:
            # Helper to find executable
            executable_path = None
            try:
                # Search inside api/ folder as well since we moved it there
                search_roots = [
                    "api/playwright_browsers", 
                    "playwright_browsers", 
                    os.path.join(os.path.dirname(__file__), "../api/playwright_browsers"),
                    "/var/task/api/playwright_browsers"
                ]
                # logger.info(f"Searching for chromium binary in: {search_roots}")
                # Removed detailed manual search to rely on PLAYWRIGHT_BROWSERS_PATH=0 behavior first
                pass
            except Exception as e:
                logger.error(f"Debug inspect error: {e}")

            # Launch args
            launch_args = {
                "headless": True,
                "args": [
                    "--no-sandbox", 
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--single-process"
                ]
            }
            
            # Note: We rely on PLAYWRIGHT_BROWSERS_PATH=0 handling executable_path automatically
            # If manual search was successful in previous iterations we could add it back, 
            # but for now we trust the bundling.

            logger.info(f"Launching browser with args: {launch_args}")
            browser = p.chromium.launch(**launch_args)
            context = browser.new_context()
            page = context.new_page()
            
            try:
                login_page = LoginPage(page)
                
                # Navigate to Login - Relaxed wait condition and increased timeout
                page.goto(
                    Config.URL_LOGIN if hasattr(Config, 'URL_LOGIN') else "https://crm.infinitegear.app/login",
                    timeout=60000, 
                    wait_until='domcontentloaded'
                )
                
                # Execute Phase 1
                login_page.initiate_login(request.email)
                
                # Extract State
                state = context.storage_state()
                
                browser.close()
                
                return {
                    "status": "waiting_code",
                    "message": "Auth initiated. Please provide the 2FA code sent to email.",
                    "session_state": state
                }
                
            except Exception as e:
                logger.error(f"API Init Page Error: {e}")
                import traceback
                traceback.print_exc()
                try:
                    logger.error(f"Page Title on Error: {page.title()}")
                except:
                    pass
                browser.close()
                raise e

    except Exception as e:
        logger.error(f"API Critical Error (Playwright Launch?): {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/auth/complete", response_model=CompleteAuthResponse)
def complete_auth(request: CompleteAuthRequest):
    """
    Phase 2: Restores session, enters code, executes full automation.
    """
    logger.info(f"API: Completing auth for {request.account_name} with code {request.code}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        # Restore State
        try:
            context = browser.new_context(storage_state=request.session_state)
            logger.info("Session state restored.")
        except Exception as e:
            logger.error(f"Failed to restore state: {e}")
            raise HTTPException(status_code=400, detail="Invalid session state provided.")
            
        page = context.new_page()
        
        try:
            # Instantiate Pages
            login_page = LoginPage(page)
            admin_page = AdminPage(page)
            panels_page = PanelsPage(page)
            contacts_page = ContactsPage(page)
            
            # Navigate to Login - Relaxed wait condition and increased timeout
            page.goto(
                Config.URL_LOGIN if hasattr(Config, 'URL_LOGIN') else "https://crm.infinitegear.app/login",
                timeout=60000, 
                wait_until='domcontentloaded'
            )
            
            # Re-enter email to trigger code screen (Idempotency fix)
            login_page.initiate_login(request.email)
            
            # Submit Code
            login_page.submit_otp(request.code)
            
            # --- Continue Automation ---
            admin_page.access_account(request.account_name)
            panels_page.go_to_panels()
            panels_page.create_all_panels()
            contacts_page.go_to_contacts()
            contacts_page.create_tags()
            
            browser.close()
            
            return {
                "status": "success",
                "message": f"Automation completed successfully for {request.account_name}"
            }
            
        except Exception as e:
            logger.error(f"API Complete Error: {e}")
            # Try to grab screenshot if possible, though returning binary in JSON is tricky.
            # For now just error out.
            browser.close()
            raise HTTPException(status_code=500, detail=str(e))
