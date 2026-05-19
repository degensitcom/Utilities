from pymongo import MongoClient
import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from TTS_generator.modal_request import *

async def topic_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /chart command, generates, and sends the chart."""

    TELEGRAM_BOT_TOKEN = context.bot_data.get("TELEGRAM_BOT_TOKEN")
    GEMINI_API_KEY = context.bot_data.get("GEMINI_API_KEY")
    MONGO_CONNECTION_STRING = context.bot_data.get("MONGO_CONNECTION_STRING")
    GROUP_ID = context.bot_data.get("GROUP_ID")
    MODAL_API_KEY = context.bot_data.get("MODAL_API_KEY")
    
    group_id = update.effective_chat.id
    print(group_id)
    message_id = update.message.message_id
    if(str(group_id)!=str(GROUP_ID)):
        await update.message.reply_text("❌ Wrong group ID", parse_mode='Markdown')
        return
    # Extracting User Information
    user = update.effective_user
    user_id = user.id
    username = user.username if user.username else "Anonymous"
    if context.args:
    	try:
	        topic = " ".join(context.args)
	        insert_topic(topic, username, user_id,message_id, group_id,MONGO_CONNECTION_STRING,MODAL_API_KEY)
	        await update.message.reply_text(f"✅ **Topic:**\n{topic} added to processing", parse_mode='Markdown')
    	except Exception as e:
        	print(f"An error occurred: {e}")
    else:
        # Fallback if they just type /topic without text
        await update.message.reply_text("❌ Please provide a topic. \nExample: `/topic Talk about the distance of the sun`", parse_mode='Markdown')


def insert_topic(topic, username, user_id,message_id, group_id,MONGO_CONNECTION_STRING,MODAL_API_KEY):
    # Replace with your actual connection string
    client = MongoClient(MONGO_CONNECTION_STRING)
    
    db = client["Sitcom"]
    collection = db["suggested_topics"]

    # Construct the document
    doc = {
        "topic": topic,
        "user_id": int(user_id),
        "message_id": int(message_id),
        "group_id": str(group_id),
        "username": username,
        "creation_time": datetime.datetime.now(datetime.timezone.utc),
        "source":"TG",
        "processed": False
    }

    result = collection.insert_one(doc)
    print(f"Successfully inserted document with ID: {result.inserted_id}")
    client.close()
    get_modal_up(MODAL_API_KEY)