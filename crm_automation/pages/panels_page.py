from crm_automation.pages.base_page import BasePage
from crm_automation.selectors import Selectors
from crm_automation.core.logger import logger

class PanelsPage(BasePage):
    def go_to_panels(self):
        self.navigate(Selectors.PANELS_URL)

    def create_panel(self, name: str, description: str, stages_data: list):
        """
        Creates a single panel with stages.
        """
        logger.info(f"--- Processing Panel: {name} ---")
        
        # Create new panel
        self.page.wait_for_selector(Selectors.NEW_PANEL_BTN, state='visible')
        self.click(Selectors.NEW_PANEL_BTN, "New Panel Button")
        
        # Scoped interaction: Define the modal locator
        modal = self.page.locator('mat-dialog-container')
        
        try:
             # Wait for the modal container to be attached and visible
            modal.wait_for(state='visible', timeout=10000)
             # Wait for internal element (header/title) to ensure it's loaded
            modal.get_by_text("Criação de painel").wait_for(state='visible', timeout=5000)
            logger.info("Modal opened and mapped.")
        except:
            logger.error("Modal container or header not found!")
            self.page.screenshot(path="screenshots/error_modal_open.png")
            raise

        # Helper to scope fills
        def fill_in_modal_indexed(element_type, index, value, log_name):
            try:
                inp = modal.locator(element_type).nth(index)
                inp.wait_for(state='visible', timeout=3000)
                inp.click()
                self.page.wait_for_timeout(200) # Small wait for focus
                self.page.keyboard.press("Control+A")
                self.page.keyboard.press("Delete")
                inp.type(value)
                logger.info(f"Filled {log_name} with '{value}'")
                
                # Verify
                actual = inp.input_value()
                if actual != value:
                    logger.warning(f"Value mismatch for {log_name}. Expected '{value}', got '{actual}'. Retrying...")
                    inp.click()
                    self.page.keyboard.press("Control+A")
                    self.page.keyboard.press("Delete")
                    inp.type(value)
            except Exception as e:
                 logger.error(f"Failed to fill {log_name}: {e}")
                 self.page.screenshot(path=f"screenshots/error_fill_{log_name}.png")
                 raise e

        # Title is the first input, Description is the first textarea
        fill_in_modal_indexed('input', 0, name, "Panel Name")
        fill_in_modal_indexed('textarea', 0, description, "Panel Description")

        # Excluir todas as fases padrões
        if not self.dry_run:
            logger.info("Clearing default stages...")
            
            # Focus on description and scroll down
            try:
                modal.locator('textarea').first.click()
                self.page.keyboard.press("PageDown")
                self.page.keyboard.press("PageDown")
                self.page.wait_for_timeout(500)
            except: pass

            max_attempts = 15
            for attempt in range(max_attempts):
                delete_buttons = modal.locator('button:has(mat-icon[data-mat-icon-name="trash"])')
                stage_rows = delete_buttons.count()
                
                if stage_rows == 0:
                     self.page.wait_for_timeout(1000)
                     stage_rows = delete_buttons.count()
                
                if stage_rows == 0:
                    logger.info("No more stages to delete.")
                    break
                
                logger.info(f"Deleting 1 of {stage_rows} stages...")
                delete_btn = delete_buttons.first
                
                try:
                    # Scroll into view if needed
                    delete_btn.scroll_into_view_if_needed()
                    if delete_btn.is_visible():
                        delete_btn.click(force=True)
                        self.page.wait_for_timeout(1000)
                    else:
                         # Try scrolling container manually if scroll_into_view fails
                        modal.locator('mat-dialog-content').evaluate('(el) => el.scrollTop += 100')
                        if delete_btn.is_visible():
                             delete_btn.click(force=True)
                except Exception as e:
                    logger.error(f"Error deleting stage: {e}")

        # Add Stages
        for idx, (stage_name, stage_type) in enumerate(stages_data):
            logger.info(f"Adding stage {idx + 1}/{len(stages_data)}: {stage_name} ({stage_type})")
            
            # Count existing inputs to verify new addition
            initial_count = modal.locator(Selectors.STAGE_NAME_INPUT).count()
            
            try:
                # Find add button INSIDE modal
                add_btn = modal.locator(Selectors.ADD_STAGE_BTN)
                
                # Scroll button into view specifically before clicking
                try:
                    add_btn.evaluate('(el) => el.scrollIntoView({block: "center", behavior: "auto"})')
                except: pass
                
                add_btn.click(force=True)
                
                # Wait for count to increase - Reduced timeout to ~1s as requested
                def wait_for_new_input():
                    for _ in range(10): # 1 second (10 * 100ms)
                        if modal.locator(Selectors.STAGE_NAME_INPUT).count() > initial_count:
                            return True
                        self.page.wait_for_timeout(100)
                    return False

                if not wait_for_new_input():
                    # Retry click if count didn't increase
                    logger.warning("Stage input count did not increase. Retrying click...")
                    add_btn.click(force=True)
                    if not wait_for_new_input():
                         raise Exception("Failed to add new stage input row")

            except Exception as e:
                logger.error(f"Failed to click add stage: {e}")
                self.page.screenshot(path=f"screenshots/error_add_{idx}.png")
                raise e
            
            if not self.dry_run:
                # Type Stage Name in the NEW last input
                stage_inputs = modal.locator(Selectors.STAGE_NAME_INPUT)
                stage_input = stage_inputs.nth(initial_count) # Index of new item is equal to initial count
                
                stage_input.scroll_into_view_if_needed()
                stage_input.click()
                
                # Double check empty just in case
                self.page.keyboard.press("Control+A")
                self.page.keyboard.press("Delete")
                
                stage_input.type(stage_name)
                
                # Select stage type
                try:
                    # Index strategy: 2 top selects + idx
                    target_select_index = 2 + idx
                    all_selects = modal.locator('mat-select')
                    
                    if all_selects.count() > target_select_index:
                        stage_type_select = all_selects.nth(target_select_index)
                    else:
                        stage_type_select = all_selects.last
                    
                    stage_type_select.scroll_into_view_if_needed()
                    stage_type_select.click()
                    self.page.wait_for_timeout(200) # Reduced from 500ms
                    
                    option = self.page.locator('mat-option').filter(has_text=stage_type).first
                    if option.is_visible():
                        option.click()
                        self.page.wait_for_timeout(200) # Reduced from 500ms
                        logger.info(f"Selected {stage_type}")
                        self.page.wait_for_timeout(200) # Reduced from 300ms
                    else:
                        option = self.page.locator('mat-option').get_by_text(stage_type, exact=True).first
                        if option.is_visible():
                             option.click()
                             self.page.wait_for_timeout(300)
                        else:
                             # Try partial match/fallback
                             logger.warning(f"Exact option '{stage_type}' not found. Trying contains.")
                             self.page.keyboard.press("Escape")

                except Exception as e:
                    logger.warning(f"Could not select stage type: {e}")

            if not self.dry_run:
                # FINAL SCROLL Fix: Target the 'Adicionar Fase' button specifically
                try:
                    add_btn_next = modal.locator(Selectors.ADD_STAGE_BTN)
                    # Force the button into view so it's ready for the next iteration
                    add_btn_next.evaluate('(el) => el.scrollIntoView({block: "center", behavior: "auto"})')
                    self.page.wait_for_timeout(300)
                except Exception as e:
                     logger.warning(f"Scroll to Add Button failed: {e}")

        # Save Panel (Inside modal)
        save_btn = modal.locator('button:has-text("Salvar")')
        save_btn.scroll_into_view_if_needed()
        save_btn.click()
        
        # Wait for modal to disappear
        if not self.dry_run:
             try:
                modal.wait_for(state='hidden', timeout=5000)
                logger.info(f"Panel {name} saved.")
             except:
                logger.warning("Modal might not have closed properly.")

    def create_all_panels(self):
        # Definições exatas conforme solicitado pelo usuário
        panels = [
            {
                "name": "Pré-Consulta",
                "description": "Nesse painel está a jornada do lead desde o primeiro contato até o comparecimento à consulta.",
                "stages": [
                    ("Em Contato", "Fase inicial"),
                    ("Follow-Up", "Fase intermediária"),
                    ("Não Respondeu Follow-Up", "Fase intermediária"),
                    ("Interessado", "Fase intermediária"),
                    ("Não Respondeu Agendamento", "Fase intermediária"),
                    ("Agendado", "Fase final"),
                    ("Confirmado", "Fase final"),
                    ("Compareceu na Consulta", "Fase final"),
                    ("Remarcação", "Fase intermediária"),
                    ("Não Interessado", "Fase final")
                ]
            },
            {
                "name": "Pós-Consulta",
                "description": "Nesse painel está a jornada do paciente após a consulta para fidelização e novos agendamentos.",
                "stages": [
                    ("Pós-Consulta Imediato", "Fase inicial"),
                    ("3 dias", "Fase intermediária"),
                    ("7 dias", "Fase intermediária"),
                    ("15 dias", "Fase intermediária"),
                    ("30 dias", "Fase intermediária"),
                    ("3 meses", "Fase intermediária"),
                    ("6 meses", "Fase intermediária"),
                    ("1 ano", "Fase intermediária"),
                    ("Nova Consulta", "Fase final")
                ]
            },
            {
                "name": "Indicação",
                "description": "Nesse painel está a jornada do paciente indicado, desde a sua indicação até o seu comparecimento na consulta.",
                "stages": [
                    ("Indicado", "Fase inicial"),
                    ("Validado", "Fase intermediária"),
                    ("Em Contato", "Fase intermediária"),
                    ("Não Respondeu", "Fase intermediária"),
                    ("Agendado", "Fase intermediária"),
                    ("Compareceu", "Fase final"),
                    ("Não Interessado", "Fase final")
                ]
            },
            {
                "name": "Tarefas",
                "description": "Nesse painel ficam as tarefas de todos os setores da clínica.",
                "stages": [
                    ("Não Iniciadas", "Fase inicial"),
                    ("Em Andamento", "Fase intermediária"),
                    ("Concluídas", "Fase final")
                ]
            }
        ]

        for panel in panels:
            logger.info(f"--- Processing Panel: {panel['name']} ---")
            self.create_panel(panel["name"], panel["description"], panel["stages"])
            # Wait a bit between panels
            if not self.dry_run:
                self.page.wait_for_timeout(3000)
