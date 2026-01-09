# CRM Automation Project

Ferramenta de automação CLI para configuração de contas no InfiniteCRM, baseada em Playwright.

## Instalação

1. Clone o repositório.
2. Crie um ambiente virtual (recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate     # Windows
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```
4. Configure o ambiente:
   - Copie `.env.example` para `.env`
   - Preencha `CRM_EMAIL` se desejar.

## Uso

O comando principal é executado via módulo `crm_automation.main`.

### Sintaxe Básica
```bash
python -m crm_automation.main --account-name "Nome da Conta" --headful
```

### Argumentos
- `--account-name`: **(Obrigatório)** O nome da conta/parceiro a ser pesquisado.
- `--email`: O email de login (se não estiver no .env).
- `--headful`: Executa com o navegador visível (recomendado para 1ª vez).
- `--dry-run`: Simula a execução sem clicar/salvar (modo teste seguro).
- `--screenshot-dir`: Pasta para salvar erros (padrão: `screenshots`).

### Exemplo Completo
```bash
python -m crm_automation.main --account-name "Luiz Henrique Tassilva" --email "admin@example.com" --headful
```

## Como Funciona o Login (2FA)
O script irá pausar no terminal e exibir:
`>>> DIGITE O CÓDIGO DE VERIFICAÇÃO (2FA):`
Você deve olhar seu email/SMS, pegar o código e digitar no terminal, depois pressionar Enter. O script continuará automaticamente.

## Estrutura do Projeto
- `crm_automation/main.py`: Ponto de entrada.
- `crm_automation/pages/`: Page Objects (Lógica de cada tela).
- `crm_automation/selectors.py`: Seletores CSS/Texto centralizados.
- `crm_automation/config.py`: Configurações globais.

## Testes
Para rodar os testes unitários:
```bash
pytest tests/
```

## Acceptance Checklist
Antes de entregar ou rodar em produção, verifique:
- [ ] Rodar com `--dry-run` e verificar se os logs fazem sentido.
- [ ] Verificar credentials no `.env`.
- [ ] Garantir que o terminal permite input interativo para o 2FA.
- [ ] Checar pasta `screenshots` após uma execução falha proposital.
