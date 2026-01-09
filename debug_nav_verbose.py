from playwright.sync_api import sync_playwright
import time

def debug_navigation_verbose():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)  # Slow down for visibility
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
            print("Submitted 2FA, waiting for dashboard to load...")
            
            # Wait for any navigation to complete
            time.sleep(8)
            
            print(f"\nCurrent URL after login: {page.url}")
            
            # Now navigate to admin page
            print("\nNavigating to admin/company/partner...")
            page.goto("https://crm.infinitegear.app/admin/company/partner", wait_until="networkidle")
            print(f"Arrived at: {page.url}")
            
            # Wait longer for page to fully load
            time.sleep(5)
            
            # Dump page to inspect
            with open("partner_page_dump.html", "w", encoding="utf-8") as f:
                f.write(page.content())
            print("HTML dumped to partner_page_dump.html")
            
            # Look for ALL input fields on page
            print("\n=== ALL INPUT FIELDS ON PAGE ===")
            inputs = page.query_selector_all('input')
            print(f"Total inputs found: {len(inputs)}")
            for idx, inp in enumerate(inputs):
                placeholder = inp.get_attribute('placeholder')
                input_type = inp.get_attribute('type')
                input_id = inp.get_attribute('id')
                input_class = inp.get_attribute('class')
                visible = inp.is_visible()
                print(f"{idx}: visible={visible}, type={input_type}, placeholder={placeholder}, id={input_id}")
                if idx < 5 and placeholder:  # Show first 5 with placeholders
                    print(f"     class={input_class}")
            
            # Look for search-related text
            print("\n=== LOOKING FOR SEARCH/BUSCAR TEXT ===")
            if page.locator('text*="Pesquisar"').count() > 0:
                print(f"Found 'Pesquisar' text {page.locator('text*=\"Pesquisar\"').count()} times")
            if page.locator('text*="Buscar"').count() > 0:
                print(f"Found 'Buscar' text {page.locator('text*=\"Buscar\"').count()} times")
                
            # Check page title
            print(f"\nPage title: {page.title()}")
            
            input("\n\nPress Enter to close browser and exit...")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            input("Press Enter to close...")
        
        browser.close()

if __name__ == "__main__":
    debug_navigation_verbose()
