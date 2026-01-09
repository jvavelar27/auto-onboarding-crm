from playwright.sync_api import sync_playwright
import time

def debug_admin_page():
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
            
            # Now on admin page - dump HTML to inspect search input
            with open("admin_page_dump.html", "w", encoding="utf-8") as f:
                f.write(page.content())
            print("HTML dumped to admin_page_dump.html")
            
            # Try to find all input fields
            inputs = page.query_selector_all('input')
            print(f"\nFound {len(inputs)} input fields:")
            for idx, inp in enumerate(inputs):
                placeholder = inp.get_attribute('placeholder')
                input_type = inp.get_attribute('type')
                input_id = inp.get_attribute('id')
                input_name = inp.get_attribute('name')
                data_cy = inp.get_attribute('data-cy')
                print(f"{idx}: type={input_type}, placeholder={placeholder}, id={input_id}, name={input_name}, data-cy={data_cy}")
            
            input("\nPress Enter to close...")
            
        except Exception as e:
            print(f"Error: {e}")
            input("Press Enter to close...")
        
        browser.close()

if __name__ == "__main__":
    debug_admin_page()
