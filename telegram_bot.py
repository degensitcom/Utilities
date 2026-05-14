import sys
import os
import io
from Chart_generator.chart_helper import *
from Add_Topic.topic_helper import *
from dotenv import load_dotenv
# --- Telegram Bot Imports ---
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
load_dotenv(dotenv_path="common_creds.env", override=True)
load_dotenv(dotenv_path="production.env", override=True)

# --- Configuration ---
TELEGRAM_BOT_TOKEN =os.getenv('TELEGRAM_BOT_TOKEN')
CG_KEY = os.getenv('CG_KEY')
MONGO_CONNECTION_STRING = os.getenv("MONGO_CONNECTION_STRING")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROUP_ID = os.getenv("GROUP_ID")
MODAL_API_KEY = os.getenv("MODAL_API_KEY")

# ----------------------------------------------------------------------
# --- Telegram Bot Handlers --------------------------------------------
# ----------------------------------------------------------------------



# async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Handles the /start command."""
#     await update.message.reply_text(
#         "Welcome! Use the /chart command to get a generated candlestick chart. 🚀"
#     )

def main():
    """Starts the bot."""
    if TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        print("!!! ERROR: Please replace 'YOUR_TELEGRAM_BOT_TOKEN_HERE' with your actual bot token. !!!")
        return

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.bot_data["CG_KEY"] = CG_KEY
    app.bot_data["TELEGRAM_BOT_TOKEN"] = TELEGRAM_BOT_TOKEN
    app.bot_data["GEMINI_API_KEY"] = GEMINI_API_KEY
    app.bot_data["MONGO_CONNECTION_STRING"] = MONGO_CONNECTION_STRING
    app.bot_data["GROUP_ID"] = GROUP_ID
    app.bot_data["MODAL_API_KEY"] = MODAL_API_KEY

    # Register command handlers
    # app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("chart", chart_command))
    app.add_handler(CommandHandler("topic", topic_command))
    print("Bot is running... Press Ctrl-C to stop.")
    app.run_polling(poll_interval=1.0)


if __name__ == "__main__":
    main()