from crm_automation.pages.base_page import BasePage
from crm_automation.selectors import Selectors
from crm_automation.core.logger import logger

class AdminPage(BasePage):
    def access_account(self, account_name: str):
        # 4. Navigate to Partner URL
        if not self.dry_run:
            self.page.goto("https://crm.infinitegear.app/admin/company/partner")
        logger.info("Navigated to Admin Partner Page")

        # 5. Search Account
        # Use type behavior to ensure Angular inputs trigger change detection
        self.click(Selectors.ADMIN_SEARCH_INPUT, "Search Input")
        if not self.dry_run:
            self.page.type(Selectors.ADMIN_SEARCH_INPUT, account_name, delay=100)
            self.page.keyboard.press("Enter")
            logger.info(f"Typed '{account_name}' into search and pressed Enter")
        
        # Wait for results to filter - expect "1 conta encontrada" or at least checks
        if not self.dry_run:
            self.page.wait_for_timeout(2000) # Initial wait for xhr
            # Ideally wait for the count to change or spinner to stop
            # We can also wait for the specific account name to appear in the list header or body if not there before
        
        # Click "Acessar" button directly
        self.click('text="Acessar"', "Access Button")
        
            # 6. Handle "Acessar conta" Modal
        logger.info("Waiting for Access Modal...")
        if not self.dry_run:
            self.page.wait_for_selector('text="Selecione com qual usuário deseja acessar:"', timeout=10000)
            
            # Use relative selector to find the input near the modal title text
            # This avoids issues with strict role attributes or background elements
            modal_search_selector = 'input:near(:text("Selecione com qual usuário deseja acessar:"))'
            
            # Type the specific profile name
            self.click(modal_search_selector, "Modal Search Input")
            profile_name = "Dr. Daniel Dorta - SuperAdmin" 
            self.page.type(modal_search_selector, profile_name, delay=50)
            self.page.keyboard.press("Enter")
            
            self.page.wait_for_timeout(1000) # Wait for local filter
            
            # Click the "Acessar" button specifically for the SuperAdmin user
            # Using :right-of or :near to ensure we click the button associated with the text
            access_btn_selector = f'button:has-text("Acessar"):near(:text("{profile_name}"))'
            
            self.click(access_btn_selector, "Confirm Access Button")

        # Wait for dashboard switch (URL change or element)
        if not self.dry_run:
             self.page.wait_for_timeout(5000)
             
        logger.info(f"Accessing account '{account_name}' initiated.")
