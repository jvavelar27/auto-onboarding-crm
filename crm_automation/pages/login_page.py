from crm_automation.pages.base_page import BasePage
from crm_automation.selectors import Selectors
from crm_automation.core.logger import logger
import time

class LoginPage(BasePage):
    def initiate_login(self, email: str):
        """
        Part 1: Enter email and request 2FA code.
        Returns control once the 2FA input is visible.
        """
        logger.info(f"Initiating login for {email}...")
        
        # 2. Click "Entrar com e-mail" if exists
        if self.exists(Selectors.LOGIN_START_BTN, timeout=5000):
            if not self.dry_run:
                self.page.click(Selectors.LOGIN_START_BTN, force=True) 
            logger.info("Clicking Login with Email Button (forced)")
            
            if not self.dry_run:
                self.page.wait_for_timeout(1000)
                self.page.wait_for_selector(Selectors.LOGIN_EMAIL_INPUT, state="visible", timeout=10000)

        # 3. Fill Email
        self.fill(Selectors.LOGIN_EMAIL_INPUT, email, "Email Input")
        
        # 4. Click Check/Next to send code
        if not self.dry_run:
            self.page.wait_for_timeout(2000)
        
        if not self.dry_run:
             self.page.click(Selectors.LOGIN_SUBMIT_BTN, force=True)
        logger.info("Clicking Send Email Button (Entrar)")
        
        # Wait for the Code Input to appear
        if not self.dry_run:
            try:
                self.page.wait_for_selector(Selectors.LOGIN_CODE_INPUT, timeout=10000)
                logger.info("2FA Code Input is visible. Ready for step 2.")
            except:
                logger.warning("Timed out waiting for Code Input. Check if email was sent.")

    def submit_otp(self, code: str):
        """
        Part 2: Fill OTP code and submit.
        """
        logger.info(f"Submitting OTP code: {code}")
        
        if not code:
            raise ValueError("Verification code is required.")

        # 6. Fill Code using 6 separate inputs with keyboard events
        try:
            self.page.wait_for_selector(Selectors.LOGIN_CODE_INPUT, state="visible", timeout=30000)
            inputs = self.page.query_selector_all(Selectors.LOGIN_CODE_INPUT)
            
            if len(inputs) >= 6 and len(code) == 6:
                logger.info("Filling 6-digit OTP with keyboard events...")
                for i, digit in enumerate(code):
                    inputs[i].focus()
                    self.page.wait_for_timeout(50)
                    inputs[i].type(digit, delay=50)
                    self.page.wait_for_timeout(150) 
            else:
                logger.warning(f"Found {len(inputs)} inputs for {len(code)} digits. Trying standard fill.")
                self.fill(Selectors.LOGIN_CODE_INPUT, code, "Code Input")
        except Exception as e:
            logger.error(f"Error filling OTP: {e}")

        # 7. Click Verify/Login
        if self.exists(Selectors.LOGIN_SUBMIT_OTP_BTN, timeout=2000):
            self.click(Selectors.LOGIN_SUBMIT_OTP_BTN, "Final Login Button (OTP)")
        elif self.exists(Selectors.LOGIN_SUBMIT_BTN, timeout=2000):
             self.click(Selectors.LOGIN_SUBMIT_BTN, "Final Login Button (Fallback)")
        
        logger.info("Login credential submission complete.")
        time.sleep(2) 

    def login(self, email: str):
        """
        Legacy/Interactive Login Flow (Part 1 + Manual Input + Part 2)
        """
        self.initiate_login(email)
        
        # Interactive prompt
        logger.info("WAITING FOR 2FA CODE. Please check your messages.")
        if not self.dry_run:
            code = input(">>> DIGITE O CÓDIGO DE VERIFICAÇÃO (2FA): ").strip()
        else:
            code = "000000"
            logger.info(f"[DRY-RUN] Using dummy code: {code}")
            
        self.submit_otp(code)
