import os
import json
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    def log_message(self, format, *args):
        pass

def run_server():
    server = HTTPServer(("0.0.0.0", 8080), PingHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_FILE = "dados.json"

def load():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"cartao": 0.0, "fisico": 0.0, "transacoes": []}

def save(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def eur(v):
    return f"{v:,.2f}€".replace(",", "X").replace(".", ",").replace("X", ".")

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = (
        "👋 *Olá! Sou o teu bot de despesas.*\n\n"
        "📖 *Como usar:*\n\n"
        "*Registar saída:*\n"
        "`-5.50 cartao cafe`\n"
        "`-20 fisico supermercado`\n\n"
        "*Registar entrada:*\n"
        "`+100 cartao salario`\n"
        "`+50 fisico freelance`\n\n"
        "*Comandos:*\n"
        "/saldo — ver saldos atuais\n"
        "/historico — últimas 10 transações\n"
        "/definir cartao 500 — definir saldo inicial\n"
        "/definir fisico 100 — definir saldo inicial\n"
        "/apagar — apagar última transação\n"
        "/ajuda — mostrar esta mensagem"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def ajuda(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await start(update, ctx)

async def saldo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = load()
    total = data["cartao"] + data["fisico"]
    msg = (
        f"📊 *Saldo atual:*\n\n"
        f"💳 Cartão: *{eur(data['cartao'])}*\n"
        f"🪙 Físico: *{eur(data['fisico'])}*\n"
        f"━━━━━━━━━━━━\n"
        f"🏦 Total: *{eur(total)}*"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def historico(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = load()
    txs = data["transacoes"][-10:][::-1]
    if not txs:
        await update.message.reply_text("📋 Nenhuma transação registada ainda.")
        return
    linhas = ["📋 *Últimas transações:*\n"]
    for tx in txs:
        sinal = "➕" if tx["tipo"] == "entrada" else "➖"
        metodo = "💳" if tx["metodo"] == "cartao" else "🪙"
        linhas.append(f"{sinal} {metodo} *{eur(tx['valor'])}* — {tx['descricao']}\n`{tx['data']}`")
    await update.message.reply_text("\n".join(linhas), parse_mode="Markdown")

async def definir(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    args = ctx.args
    if len(args) != 2:
        await update.message.reply_text("❌ Uso: /definir cartao 500 ou /definir fisico 100")
        return
    metodo = args[0].lower()
    if metodo not in ("cartao", "fisico"):
        await update.message.reply_text("❌ Método inválido. Usa `cartao` ou `fisico`.", parse_mode="Markdown")
        return
    try:
        valor = float(args[1].replace(",", "."))
    except ValueError:
        await update.message.reply_text("❌ Valor inválido.")
        return
    data = load()
    data[metodo] = valor
    save(data)
    emoji = "💳" if metodo == "cartao" else "🪙"
    await update.message.reply_text(
        f"✅ Saldo de {emoji} *{metodo.capitalize()}* definido para *{eur(valor)}*",
        parse_mode="Markdown"
    )

async def apagar(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = load()
    if not data["transacoes"]:
        await update.message.reply_text("❌ Nenhuma transação para apagar.")
        return
    tx = data["transacoes"].pop()
    sinal = 1 if tx["tipo"] == "entrada" else -1
    if tx["metodo"] == "cartao":
        data["cartao"] -= sinal * tx["valor"]
    else:
        data["fisico"] -= sinal * tx["valor"]
    save(data)
    await update.message.reply_text(
        f"🗑 Última transação apagada:\n*{tx['descricao']}* — {eur(tx['valor'])}",
        parse_mode="Markdown"
    )

async def mensagem(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.strip()
    partes = texto.split(maxsplit=2)

    if len(partes) < 3:
        await update.message.reply_text(
            "❓ Formato inválido.\n\nExemplos:\n`-5.50 cartao cafe`\n`+100 fisico salario`",
            parse_mode="Markdown"
        )
        return

    sinal_str, metodo_str, descricao = partes
    metodo_str = metodo_str.lower()

    if sinal_str.startswith("+"):
        tipo = "entrada"
    elif sinal_str.startswith("-"):
        tipo = "saida"
    else:
        await update.message.reply_text("❓ Começa com `+` para entrada ou `-` para saída.", parse_mode="Markdown")
        return

    try:
        valor = float(sinal_str.replace(",", ".").replace("+", "").replace("-", ""))
        if valor <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("❌ Valor inválido.", parse_mode="Markdown")
        return

    if metodo_str in ("cartao", "cartão", "card", "c"):
        metodo = "cartao"
    elif metodo_str in ("fisico", "físico", "f", "cash", "dinheiro"):
        metodo = "fisico"
    else:
        await update.message.reply_text("❌ Método inválido. Usa `cartao` ou `fisico`.", parse_mode="Markdown")
        return

    data = load()
    sinal = 1 if tipo == "entrada" else -1
    if metodo == "cartao":
        data["cartao"] += sinal * valor
    else:
        data["fisico"] += sinal * valor

    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    tx = {"tipo": tipo, "metodo": metodo, "valor": valor, "descricao": descricao, "data": agora}
    data["transacoes"].append(tx)
    save(data)

    emoji_tipo = "💰" if tipo == "entrada" else "💸"
    emoji_metodo = "💳" if metodo == "cartao" else "🪙"
    total = data["cartao"] + data["fisico"]

    msg = (
        f"{emoji_tipo} *{'Entrada' if tipo == 'entrada' else 'Saída'} registada!*\n\n"
        f"📝 {descricao}\n"
        f"💶 *{eur(valor)}* via {emoji_metodo} {'Cartão' if metodo == 'cartao' else 'Físico'}\n\n"
        f"━━━━━━━━━━━━\n"
        f"💳 Cartão: *{eur(data['cartao'])}*\n"
        f"🪙 Físico: *{eur(data['fisico'])}*\n"
        f"🏦 Total: *{eur(total)}*"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise ValueError("Define a variável de ambiente BOT_TOKEN")

    app = (
        Application.builder()
        .token(token)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ajuda", ajuda))
    app.add_handler(CommandHandler("saldo", saldo))
    app.add_handler(CommandHandler("historico", historico))
    app.add_handler(CommandHandler("definir", definir))
    app.add_handler(CommandHandler("apagar", apagar))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mensagem))

    logger.info("Bot iniciado!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
allowed_updates=Update.ALL_TYPES
