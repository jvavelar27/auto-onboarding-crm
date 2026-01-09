from crm_automation.pages.base_page import BasePage
from crm_automation.selectors import Selectors
from crm_automation.core.logger import logger

class ContactsPage(BasePage):
    def go_to_contacts(self):
        self.navigate(Selectors.CONTACTS_URL)

    def create_tags(self):
        """
        Creates tags (labels) for a contact.
        """
        logger.info("--- Creating Tags ---")
        
        # 1. Navigate to Contacts
        self.navigate(Selectors.CONTACTS_URL)
        
        # 2. Click on the first contact
        logger.info("Accessing first contact to manage tags...")
        if not self.dry_run:
            try:
                self.page.wait_for_selector(Selectors.FIRST_CONTACT_ROW, timeout=15000)
            except:
                logger.error("Contacts list did not load or is empty!")
                self.page.screenshot(path="screenshots/error_contacts_list.png")
                return

        self.click(Selectors.FIRST_CONTACT_ROW, "First Contact Row")
        
        # 3. Open Tags Edit Modal/Section
        # Wait for the side panel/modal to load
        if not self.dry_run:
            self.page.wait_for_timeout(2000)

        # Try to find the edit tags button
        # Selector "Editar etiquetas" might be a tooltip or aria-label
        try:
            self.page.wait_for_selector(Selectors.TAGS_EDIT_ICON, timeout=5000)
            self.click(Selectors.TAGS_EDIT_ICON, "Edit Tags Pencil")
        except:
            logger.warning("Edit tags button not found with primary selector. Trying fallback...")
            # Fallback: look for a pencil icon near "Etiquetas"
            try:
                self.page.locator('div:has-text("Etiquetas")').locator('button').first.click()
            except Exception as e:
                logger.error(f"Failed to find Edit Tags button: {e}")
                self.page.screenshot(path="screenshots/error_edit_tags_btn.png")
                return
        
        # Define tags to add
        tags_to_add = ["Paciente", "Lead", "Equipe"]
        
        for tag_name in tags_to_add:
            if self.dry_run:
                logger.info(f"[DRY RUN] Would add tag: {tag_name}")
                continue

            logger.info(f"Processing Tag: {tag_name}")
            
            try:
                # Ensure the Tag Editor popover is open
                if not self.page.locator(Selectors.ADD_TAG_BTN).is_visible():
                    logger.info("Opening Tag Editor popover...")
                    self.click(Selectors.TAGS_EDIT_ICON, "Edit Tags Pencil")
                    self.page.wait_for_selector(Selectors.ADD_TAG_BTN, timeout=5000)

                # 4. Click "+" (Add tag button)
                self.click(Selectors.ADD_TAG_BTN, "Add Tag Plus Button")
                
                # 5. Handle the "Criando nova etiqueta" Modal
                modal_selector = 'mat-dialog-container'
                self.page.wait_for_selector(modal_selector, state='visible', timeout=7000)
                # Wait for any potential overlap/animation
                self.page.wait_for_timeout(500)
                
                active_modal = self.page.locator(modal_selector).last
                tag_input = active_modal.locator('input').first
                
                logger.info(f"Filling tag: {tag_name}")
                tag_input.wait_for(state='visible', timeout=3000)
                tag_input.click()
                tag_input.fill("") # Clear existing if any
                tag_input.fill(tag_name)
                
                # 6. Save INDIVIDUAL Tag (The 'Salvar' button inside the modal)
                # Using get_by_role for better accuracy in Angular/Material apps
                save_modal_btn = active_modal.get_by_role("button", name="Salvar", exact=True)
                save_modal_btn.click()
                
                # Wait for modal to disappear (Critical: save must finish)
                active_modal.wait_for(state='hidden', timeout=10000)
                logger.info(f"Tag '{tag_name}' saved successfully.")
                self.page.wait_for_timeout(300) # Short breather
                
            except Exception as e:
                logger.error(f"Failed to add tag '{tag_name}': {e}")
                self.page.screenshot(path=f"screenshots/error_tag_{tag_name}.png")
                # Try to recover
                try: 
                    self.page.keyboard.press("Escape")
                    self.page.wait_for_timeout(500)
                except: pass

        # 7. Final Save (The 'Salvar etiquetas' button at the bottom of the popover)
        logger.info("Clicking final 'Salvar etiquetas' button...")
        try:
            # 1. Be absolutely sure the tag creation modal is gone
            self.page.locator('mat-dialog-container').wait_for(state='detached', timeout=5000)
            self.page.wait_for_timeout(500) # UI Settlement

            # 2. Find the button using the specific selector
            final_save_btn = self.page.locator(Selectors.TAG_FINAL_SAVE_BTN).last
            
            # Wait for it to be attached/visible
            final_save_btn.wait_for(state='attached', timeout=5000)
            
            logger.info("Found 'Salvar etiquetas' button. Clicking...")
            # Use JS click to bypass potential overlays or 'div not clickable' issues
            final_save_btn.evaluate("el => el.click()")
            logger.info("Final 'Salvar etiquetas' clicked successfully (JS).")
                
            self.page.wait_for_timeout(2000)
            
        except Exception as e:
            logger.error(f"Failed to click final 'Salvar etiquetas': {e}")
            self.page.screenshot(path="screenshots/error_final_save_tags.png")


        logger.info("Tags creation flow complete.")
