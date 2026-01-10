# Manual de Execução da Automação (CLI / n8n)

Este manual descreve como executar o script de automação do CRM dividindo o processo de login em duas etapas (Solicitação de 2FA e Envio de Código), ideal para integrações com n8n ou execução via linha de comando.

## Pré-requisitos

*   Python instalado.
*   Ambiente virtual (`venv`) criado e dependências instaladas.
*   Arquivo `.env` configurado ou e-mail passado via argumento.

---

## FASE 1: Iniciar Autenticação (Solicitar 2FA)

Nesta etapa, o robô abre o navegador, faz o login com e-mail e aguarda a tela de código aparecer. O estado da sessão é salvo em `auth_state.json`.

**Comando:**

```bash
# Windows (PowerShell)
venv\Scripts\python.exe -m crm_automation.main --account-name "NOME_DO_CLIENTE" --email "SEU_EMAIL" --step init-auth --headful
```

**O que acontece:**
1.  Navegador abre.
2.  E-mail é preenchido e enviado.
3.  Robô aguarda confirmação de que a tela de código apareceu.
4.  Arquivo `auth_state.json` é criado/atualizado.
5.  Navegador fecha automaticamente.

**Saída no Terminal (Log):**
Procure por: `Session state saved to 'auth_state.json'. Waiting for 2FA code...`

---

## FASE 2: Concluir Autenticação e Rodar Automação

Nesta etapa, o robô reabre o navegador restaurando a sessão anterior, digita o código 2FA fornecido e executa todo o restante do fluxo (Painéis, Etiquetas, etc.).

**Comando:**

```bash
# Substitua 123456 pelo código recebido no e-mail
venv\Scripts\python.exe -m crm_automation.main --account-name "NOME_DO_CLIENTE" --email "SEU_EMAIL" --step complete-auth --code 123456 --headful
```

**O que acontece:**
1.  Navegador abre carregando `auth_state.json`.
2.  Código 2FA é preenchido.
3.  Login é validado.
4.  O script acessa a conta do cliente.
5.  Criação de Painéis e Etiquetas é executada.

---

## Dicas para n8n

Ao usar o node **"Execute Command"** no n8n:

1.  **Diretório de Trabalho (CWD):** Certifique-se de executar o comando dentro da pasta do projeto (ex: `C:\Users\avela\.vscode\projetos\Onboarding InfiniteCRM`).
2.  **Caminho do Python:** Use sempre o caminho absoluto do python dentro do `venv` para garantir que as bibliotecas certas sejam usadas.
3.  **Headful vs Headless:**
    *   Para testes visuais, use `--headful`.
    *   Para produção (servidor), remova `--headful` para rodar em background.
4.  **Arquivo de Estado:** O n8n deve ter permissão de escrita na pasta para criar o `auth_state.json`.

## Exemplo de Fluxo Lógico

1.  **n8n (Passo 1):** Executa comando da **FASE 1**.
2.  **n8n (Wait):** Aguarda input humano (ex: via Webhook ou Form) com o código 2FA.
3.  **n8n (Passo 2):** Recebe o código e executa comando da **FASE 2** passando `--code $nHeookInput`.

---

## FASE 3: Execução via API (Docker / Web Service)

Se você optar por rodar via Docker (recomendado para Render.com ou Railway), o script roda como um servidor HTTP.

### Endpoint 1: Iniciar (`POST /api/v1/auth/init`)
*   **Body:** `{ "email": "seu@email.com" }`
*   **Retorno:** JSON contendo `session_state`. Guarde este JSON no n8n!

### Endpoint 2: Completar (`POST /api/v1/auth/complete`)
*   **Body:**
    ```json
    {
      "email": "seu@email.com",
      "code": "123456",
      "account_name": "Nome Cliente",
      "session_state": { ... json_recebido_do_init ... }
    }
    ```
*   **Retorno:** Confirmação de sucesso.

### Como Rodar (Docker)
```bash
docker build -t crm-automation .
docker run -p 8000:8000 crm-automation
# A API estará em http://localhost:8000
```
