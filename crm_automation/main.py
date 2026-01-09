import argparse
import sys
from playwright.sync_api import sync_playwright
from crm_automation.config import Config
from crm_automation.core.logger import logger, setup_logger
from crm_automation.pages.login_page import LoginPage
from crm_automation.pages.admin_page import AdminPage
from crm_automation.pages.panels_page import PanelsPage
from crm_automation.pages.contacts_page import ContactsPage
import logging

import os

def parse_args():
    parser = argparse.ArgumentParser(description="CRM Automation Tool")
    
    parser.add_argument("--account-name", required=True, help="Nome da conta a automatizar")
    parser.add_argument("--email", help="Email para login (opcional, pode vir do .env)")
    parser.add_argument("--dry-run", action="store_true", help="Simula ações sem executar mudanças")
    parser.add_argument("--headful", action="store_true", help="Roda com navegador visível")
    parser.add_argument("--screenshot-dir", default="screenshots", help="Diretório para salvar screenshots de falha")
    
    # New Auth Arguments
    parser.add_argument("--step", choices=['init-auth', 'complete-auth', 'full'], default='full',
                        help="Passo da automação: 'init-auth' (pede código), 'complete-auth' (envia código), 'full' (interativo)")
    parser.add_argument("--code", help="Código 2FA (obrigatório para --step complete-auth)")
    parser.add_argument("--auth-file", default="auth_state.json", help="Arquivo para salvar/ler sessão de login")
    
    return parser.parse_args()

def run_automation(args):
    email = Config.get_email(args.email)
    if not email:
        logger.error("Email not provided via CLI or .env")
        sys.exit(1)

    headless = not args.headful
    
    logger.info(f"Starting automation for account: {args.account_name}")
    logger.info(f"Mode: {'DRY-RUN' if args.dry_run else 'LIVE'} | Step: {args.step}")
    
    with sync_playwright() as p:
        # Determine storage state to load
        storage_state_path = args.auth_file if args.step == 'complete-auth' and os.path.exists(args.auth_file) else None
        
        if args.step == 'complete-auth' and not storage_state_path:
             logger.warning(f"Auth file '{args.auth_file}' not found. Starting fresh session (login might fail if not saved).")

        browser = p.chromium.launch(headless=headless, slow_mo=500 if args.headful else 0)
        
        # Create context with storage state if available
        context = browser.new_context(storage_state=storage_state_path)
        page = context.new_page()
        
        # Instantiate Pages
        login_page = LoginPage(page, dry_run=args.dry_run)
        admin_page = AdminPage(page, dry_run=args.dry_run)
        panels_page = PanelsPage(page, dry_run=args.dry_run)
        contacts_page = ContactsPage(page, dry_run=args.dry_run)
        
        try:
            # 1. Login Logic
            if not args.dry_run:
                # If restoring session, we might be already logged in or need to go to login page to enter code
                # The requirement says: "Reabre o site já na tela de verificação 2FA"
                # so we go to the login URL.
                page.goto(Config.URL_LOGIN if hasattr(Config, 'URL_LOGIN') else "https://crm.infinitegear.app/login")
            
            if args.step == 'init-auth':
                # Part 1: Init Login -> Wait for Code -> Save State -> Exit
                login_page.initiate_login(email)
                
                # Save state
                context.storage_state(path=args.auth_file)
                logger.info(f"Session state saved to '{args.auth_file}'. Waiting for 2FA code...")
                return # Exit successfully after part 1

            elif args.step == 'complete-auth':
                # Part 2: Submit Code -> Continue
                if not args.code:
                    logger.error("--code is required for complete-auth step.")
                    sys.exit(1)
                
                # User Feedback: Must re-do the email entry to get to the code screen
                # effectively restoring the UI state
                login_page.initiate_login(email)
                login_page.submit_otp(args.code)
                
            else: # 'full'
                # Legacy interactive mode
                login_page.login(email)
            
            # --- POST-LOGIN FLOW (unchanged) ---
            
            # 2. Access Admin / Account
            admin_page.access_account(args.account_name)
            
            # 3. Create Panels
            panels_page.go_to_panels()
            panels_page.create_all_panels()
            
            # 4. Create Tags
            contacts_page.go_to_contacts()
            contacts_page.create_tags()
            
            logger.info("Automation successfully completed!")
            
        except Exception as e:
            logger.error(f"Automation failed: {e}")
            if not args.dry_run:
                os.makedirs(args.screenshot_dir, exist_ok=True)
                timestamp = os.urandom(4).hex()
                screenshot_path = os.path.join(args.screenshot_dir, f"error_{timestamp}.png")
                page.screenshot(path=screenshot_path)
                logger.info(f"Screenshot saved to {screenshot_path}")
            sys.exit(1)
        finally:
            browser.close()

if __name__ == "__main__":
    args = parse_args()
    setup_logger(level=logging.INFO)
    run_automation(args)
