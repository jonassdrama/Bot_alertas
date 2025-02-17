import gspread
import os
import datetime
import json
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# 🔹 CONFIGURACIÓN DEL BOT
TOKEN = os.getenv("TOKEN")
ADMIN_ID = 1570729026  # ⚠️ REEMPLAZA con tu ID de Telegram

if not TOKEN:
    raise ValueError("❌ ERROR: No se encontró el TOKEN de Telegram en las variables de entorno.")
app = Application.builder().token(TOKEN).build()

# 🔹 CONECTAR CON GOOGLE SHEETS
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_json = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
client = gspread.authorize(creds)

# 🔹 ABRIR LA HOJA DE CÁLCULO
SHEET_NAME = "1I6zyDy7N1vqOrq_2b6MFxL7ak8M8_FZpm0Q6cw-rkpc"
sheet = client.open_by_key(SHEET_NAME).sheet1

# 🔹 OPCIONES
IDIOMAS = [["🇪🇸 Español", "🇬🇧 English"]]
SERVICIOS_ESP = [["📢 Servicio 1 mes - $20"], ["📢 Servicio 1 año - $100"], ["🎥 Video personalizado - $30"]]
SERVICIOS_ENG = [["📢 1-month service - $20"], ["📢 1-year service - $100"], ["🎥 Custom video - $30"]]

# 🔹 MOSTRAR BOTÓN "EMPEZAR" AUTOMÁTICAMENTE
async def mostrar_boton_empezar(update: Update, context: CallbackContext) -> None:
    if update.message.text and update.message.text not in ["🚀 Empezar", "🇪🇸 Español", "🇬🇧 English"]:
        keyboard = ReplyKeyboardMarkup([["🚀 Empezar"]], one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("¡Bienvenido! / Welcome! 👋", reply_markup=keyboard)

# 🔹 MANEJAR "EMPEZAR"
async def empezar(update: Update, context: CallbackContext) -> None:
    keyboard = ReplyKeyboardMarkup(IDIOMAS, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("🌍 Elige tu idioma / Choose your language:", reply_markup=keyboard)

# 🔹 SELECCIONAR IDIOMA
async def seleccionar_idioma(update: Update, context: CallbackContext) -> None:
    idioma = update.message.text
    context.user_data["idioma"] = idioma

    if idioma == "🇪🇸 Español":
        mensaje = "📢 Elige una opción de alertas deportivas:"
        keyboard = ReplyKeyboardMarkup(SERVICIOS_ESP, one_time_keyboard=True, resize_keyboard=True)
    else:
        mensaje = "📢 Choose a sports alerts option:"
        keyboard = ReplyKeyboardMarkup(SERVICIOS_ENG, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(mensaje, reply_markup=keyboard)

# 🔹 MANEJAR SELECCIÓN DE SERVICIO
async def manejar_respuesta(update: Update, context: CallbackContext) -> None:
    opcion = update.message.text
    context.user_data["opcion"] = opcion
    idioma = context.user_data.get("idioma", "🇪🇸 Español")

    if idioma == "🇪🇸 Español":
        if "Servicio" in opcion:
            mensaje = "⚽ ¿Cuál es tu equipo favorito?"
            context.user_data["estado"] = "esperando_equipo"
        elif "Video personalizado" in opcion:
            mensaje = "🎥 Escribe el mensaje que quieres en el video"
            context.user_data["estado"] = "esperando_mensaje"
    else:
        if "service" in opcion:
            mensaje = "⚽ What is your favorite team?"
            context.user_data["estado"] = "esperando_equipo"
        elif "Custom video" in opcion:
            mensaje = "🎥 Write the message you want in the video"
            context.user_data["estado"] = "esperando_mensaje"

    await update.message.reply_text(mensaje)

# 🔹 MANEJAR RESPUESTAS DEL USUARIO
async def manejar_respuesta_usuario(update: Update, context: CallbackContext) -> None:
    estado = context.user_data.get("estado")
    idioma = context.user_data.get("idioma", "🇪🇸 Español")

    if estado == "esperando_equipo":
        context.user_data["equipo"] = update.message.text
        await registrar_peticion(update, context)

    elif estado == "esperando_mensaje":
        context.user_data["mensaje"] = update.message.text
        if idioma == "🇪🇸 Español":
            mensaje = "🎟️ ¿El video es para ti o para un amigo?"
        else:
            mensaje = "🎟️ Is the video for you or a friend?"
        context.user_data["estado"] = "esperando_servicio"
        await update.message.reply_text(mensaje)

    elif estado == "esperando_servicio":
        context.user_data["servicio"] = update.message.text
        await registrar_peticion(update, context)

# 🔹 REGISTRAR PETICIÓN EN GOOGLE SHEETS
async def registrar_peticion(update: Update, context: CallbackContext) -> None:
    usuario = update.message.chat.username or update.message.chat.id
    opcion = context.user_data.get("opcion", "N/A")
    equipo = context.user_data.get("equipo", "N/A")
    servicio = context.user_data.get("servicio", "N/A")
    mensaje = context.user_data.get("mensaje", "N/A")
    fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sheet.append_row([usuario, opcion, equipo, servicio, mensaje, fecha])

    idioma = context.user_data.get("idioma", "🇪🇸 Español")
    mensaje_final = "✅ Petición registrada. Nos pondremos en contacto contigo para completar el pago." if idioma == "🇪🇸 Español" else "✅ Request registered. We will contact you to complete the payment."

    await update.message.reply_text(mensaje_final)
    context.user_data.clear()

# 🔹 ENVIAR MENSAJES MANUALMENTE COMO ADMIN
async def enviar(update: Update, context: CallbackContext) -> None:
    if len(context.args) < 2:
        await update.message.reply_text("⚠️ Uso correcto: `/enviar ID mensaje`")
        return

    chat_id = context.args[0]
    mensaje = " ".join(context.args[1:])

    try:
        await context.bot.send_message(chat_id=chat_id, text=mensaje)
        await update.message.reply_text(f"✅ Mensaje enviado a {chat_id}.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error al enviar mensaje: {e}")

# 🔹 RESPONDER AL USUARIO DESDE EL ADMIN
async def responder(update: Update, context: CallbackContext) -> None:
    if len(context.args) < 2:
        await update.message.reply_text("⚠️ Uso correcto: `/responder ID mensaje`")
        return

    chat_id = context.args[0]
    mensaje = " ".join(context.args[1:])

    try:
        await context.bot.send_message(chat_id=chat_id, text=mensaje)
        await update.message.reply_text(f"✅ Respuesta enviada a {chat_id}.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error al enviar respuesta: {e}")

# 🔹 CONFIGURAR MANEJADORES
app.add_handler(MessageHandler(filters.Text(["🚀 Empezar"]), empezar))
app.add_handler(MessageHandler(filters.Text(["🇪🇸 Español", "🇬🇧 English"]), seleccionar_idioma))
app.add_handler(MessageHandler(filters.Text(["📢 Servicio 1 mes - $20", "📢 Servicio 1 año - $100", "🎥 Video personalizado - $30",
                                             "📢 1-month service - $20", "📢 1-year service - $100", "🎥 Custom video - $30"]),
                               manejar_respuesta))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_respuesta_usuario))
app.add_handler(CommandHandler("enviar", enviar))
app.add_handler(CommandHandler("responder", responder))
app.add_handler(MessageHandler(filters.ALL, mostrar_boton_empezar))  

# 🔹 INICIAR EL BOT
app.run_polling()








