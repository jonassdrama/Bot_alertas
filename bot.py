import json
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# 🔹 TOKEN del bot de Telegram
TOKEN = "7287863294:AAFiMdZMWBvZYfsts44s2Ig_AkycNKh5HFU"

# 🔹 Autenticación con Google Sheets usando variable de entorno
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Cargar credenciales desde la variable de entorno
creds_json = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)

# Conectar con Google Sheets
client = gspread.authorize(creds)

# 🔹 Abrir la hoja de cálculo (nombre ya puesto)
SHEET_NAME = "1I6zyDy7N1vqOrq_2b6MFxL7ak8M8_FZpm0Q6cw-rkpc"
sheet = client.open_by_key(SHEET_NAME).sheet1

# 🔹 Comando /start
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "¡Bienvenido a Isa Winning Bot! 🏆\n"
        "Envía tu predicción en formato: 'Equipo1 X - Equipo2 Y'"
    )

# 🔹 Función para guardar predicciones en Google Sheets
async def guardar_en_sheets(update: Update, context: CallbackContext) -> None:
    usuario = update.message.chat.username or update.message.chat.id
    texto = update.message.text

    # Validar formato
    if " - " not in texto:
        await update.message.reply_text("⚠️ Formato incorrecto. Usa: 'Equipo1 X - Equipo2 Y'")
        return

    # Guardar en Google Sheets
    sheet.append_row([str(usuario), texto])

    await update.message.reply_text("✅ Predicción guardada correctamente.")

# 🔹 Función principal para ejecutar el bot
def main():
    app = Application.builder().token(TOKEN).build()

    # Manejar comandos y mensajes
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, guardar_en_sheets))

    print("🤖 Bot en marcha con Webhooks...")

    # Configuración del Webhook en Render
    PORT = int(os.environ.get("PORT", 5000))
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"
    )

if __name__ == "__main__":
    main()

