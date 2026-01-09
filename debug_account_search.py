from playwright.sync_api import sync_playwright
import time

def debug_account_search():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://crm.infinitegear.app/login")
        
        # Login flow
        try:
            page.click('text="Entrar com e-mail"', timeout=5000)
            time.sleep(1)
            page.fill('[data-cy="input-email"]', "avelarmarcaljoaovitor@gmail.com")
            time.sleep(2)
            page.click('[data-cy="button-sign-in"] button', force=True)
            print("Filled email, waiting for 2FA...")
            
            # Wait for 2FA manually
            code = input("Enter 2FA code: ")
            
            # Fill 2FA
            page.wait_for_selector('input.otp-input', state="visible", timeout=30000)
            inputs = page.query_selector_all('input.otp-input')
            for i, digit in enumerate(code):
                inputs[i].focus()
                time.sleep(0.05)
                inputs[i].type(digit, delay=50)
                time.sleep(0.15)
            
            # Click submit
            page.click('[data-cy="button-sign-in-otp"] button')
            print("Submitted 2FA, waiting for navigation...")
            time.sleep(5)
            
            # Navigate to admin page
            print("Navigating to admin/company/partner...")
            page.goto("https://crm.infinitegear.app/admin/company/partner")
            time.sleep(3)
            
            # Try to find and fill search
            print("\nTrying to find search input...")
            search_input = page.query_selector('input[placeholder="Pesquisar"]')
            if search_input:
                print("Found search input!")
                print(f"  Visible: {search_input.is_visible()}")
                print(f"  Enabled: {search_input.is_enabled()}")
                
                print("\nFilling search with 'Luiz Henrique da Silva'...")
                search_input.fill("Luiz Henrique da Silva")
                time.sleep(2)
                
                # Check if results appeared
                print("\nChecking for results...")
                page.wait_for_timeout(2000)
                
                # Look for the account name in the page
                if page.locator('text="Luiz Henrique da Silva"').count() > 0:
                    print(f"Found {page.locator('text=\"Luiz Henrique da Silva\"').count()} matches for 'Luiz Henrique da Silva'")
                    
                    # Try to click on the first match
                    print("\nTrying to click on account name...")
                    page.locator('text="Luiz Henrique da Silva"').first.click()
                    time.sleep(1)
                    
                    # Look for "Acessar" button
                    print("\nLooking for 'Acessar' button...")
                    if page.locator('text="Acessar"').count() > 0:
                        print(f"Found {page.locator('text=\"Acessar\"').count()} 'Acessar' buttons")
                        acessar_buttons = page.locator('text="Acessar"').all()
                        for idx, btn in enumerate(acessar_buttons):
                            print(f"  Button {idx}: visible={btn.is_visible()}, enabled={btn.is_enabled()}")
                    else:
                        print("No 'Acessar' button found")
                        
                    # Dump HTML to inspect
                    with open("after_click_dump.html", "w", encoding="utf-8") as f:
                        f.write(page.content())
                    print("HTML dumped to after_click_dump.html")
                else:
                    print("Account not found in search results!")
                    # Dump to see what's there
                    with open("search_results_dump.html", "w", encoding="utf-8") as f:
                        f.write(page.content())
                    print("HTML dumped to search_results_dump.html")
            else:
                print("Search input not found!")
                
            input("\nPress Enter to close...")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            input("Press Enter to close...")
        
        browser.close()

if __name__ == "__main__":
    debug_account_search()
