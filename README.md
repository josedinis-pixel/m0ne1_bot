# 💰 Finance Bot — Telegram

Bot para controlar despesas diretamente pelo Telegram.

## Comandos

| Mensagem | Descrição |
|---|---|
| `-5.50 cartao cafe` | Saída de 5,50€ no cartão |
| `-20 fisico supermercado` | Saída de 20€ em dinheiro físico |
| `+100 cartao salario` | Entrada de 100€ no cartão |
| `+50 fisico freelance` | Entrada de 50€ em físico |
| `/saldo` | Ver saldos atuais |
| `/historico` | Últimas 10 transações |
| `/definir cartao 500` | Definir saldo inicial do cartão |
| `/definir fisico 100` | Definir saldo inicial do físico |
| `/apagar` | Apagar última transação |

## Como colocar no Railway (grátis)

### 1. Criar conta no GitHub
- Vai a https://github.com e cria uma conta gratuita

### 2. Criar repositório
- Clica em "New repository"
- Nome: `finance-bot`
- Deixa privado
- Clica "Create repository"

### 3. Fazer upload dos ficheiros
- Clica em "uploading an existing file"
- Faz upload de: `bot.py`, `requirements.txt`, `Procfile`
- Clica "Commit changes"

### 4. Criar conta no Railway
- Vai a https://railway.app
- Clica "Login with GitHub"

### 5. Criar projeto
- Clica "New Project"
- Escolhe "Deploy from GitHub repo"
- Seleciona o teu repositório `finance-bot`

### 6. Adicionar a variável de ambiente
- No projeto, clica na tab "Variables"
- Clica "New Variable"
- Nome: `BOT_TOKEN`
- Valor: o token do teu bot (ex: `123456789:AAFxxx...`)
- Clica "Add"

### 7. Deploy
- Vai à tab "Deployments"
- O bot deve iniciar automaticamente
- Verifica os logs — deve aparecer "Bot iniciado!"

### Pronto! 🎉
Abre o Telegram, envia uma mensagem ao teu bot e ele responde.
