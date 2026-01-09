class Selectors:
    # Login
    LOGIN_START_BTN = 'text="Entrar com e-mail"' # Botão inicial
    # Found explicit data-cy attribute in HTML dump
    LOGIN_EMAIL_INPUT = '[data-cy="input-email"]'
    LOGIN_CODE_INPUT = 'input.otp-input' # There are 6 of these
    # Found explicit data-cy attribute for submit button wrapper
    LOGIN_SUBMIT_BTN = '[data-cy="button-sign-in"] button'
    LOGIN_SUBMIT_OTP_BTN = '[data-cy="button-sign-in-otp"] button'

    # Admin / Account Search
    ADMIN_SEARCH_INPUT = 'input[placeholder="Buscar..."]' # Corrected from visual validation
    # Selector for the account card needs to be dynamic based on text or specific structure
    # We will likely build dynamic xpath or css in the page object

    # Panels
    PANELS_URL = "https://crm.infinitegear.app/panels"
    NEW_PANEL_BTN = 'text="Novo painel"' # Corrected case based on screenshot
    # Using relative selectors based on labels because placeholders might be absent/different
    PANEL_NAME_INPUT = 'input:near(:text("Título"))' 
    PANEL_DESCRIPTION_INPUT = 'textarea:near(:text("Descrição"))' 
    PANEL_SAVE_BTN = 'button:has-text("Salvar")'
    
    # Stages (Fases) usually inside the panel creation modal
    ADD_STAGE_BTN = 'text=/Adicionar [fF]ase/' # Regex case insensitive
    STAGE_NAME_INPUT = 'input[placeholder="Nova fase"]'
    STAGE_TYPE_SELECT = 'mat-select' # Dropdown para tipo de fase (inicial/intermediária/final)
    CONFIRM_STAGE_BTN = 'button[aria-label="Confirmar"]'
    # Generic trash button often has an svg or specific class. 
    # Using a selector that looks for a button containing an svg, or aria-label if available.
    # We'll try a few common patterns or a broad approach + filtering in the page object if needed.
    DELETE_STAGE_BTN = 'button:has(svg.lucide-trash), button[aria-label="Excluir"], button:has(svg)'

    # Contacts/Tags
    CONTACTS_URL = "https://crm.infinitegear.app/contacts"
    FIRST_CONTACT_ROW = 'tbody tr:first-child' # Selecionar primeiro contato
    TAGS_EDIT_ICON = 'button:has(mat-icon[data-mat-icon-name="pencil"]):right-of(:text("Etiquetas"))'
    ADD_TAG_BTN = 'button:has(mat-icon[data-mat-icon-name="plus-circle"])'
    TAG_NAME_INPUT = 'mat-dialog-container input' # Scoped locally in page object
    TAG_SAVE_BTN = 'button:has-text("Salvar")' # Scoped locally in page object
    # User provided HTML: <div class="... cursor-pointer ..."><div> Salvar etiquetas </div></div>
    TAG_FINAL_SAVE_BTN = 'div.cursor-pointer:has-text("Salvar etiquetas")'
