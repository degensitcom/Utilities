from pymongo import MongoClient
import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
async def topic_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /chart command, generates, and sends the chart."""

    TELEGRAM_BOT_TOKEN = context.bot_data.get("TELEGRAM_BOT_TOKEN")
    GEMINI_API_KEY = context.bot_data.get("GEMINI_API_KEY")
    MONGO_CONNECTION_STRING = context.bot_data.get("MONGO_CONNECTION_STRING")
    GROUP_ID = context.bot_data.get("GROUP_ID")

    chat = update.effective_chat
    group_id = chat.id
    print(group_id)
    print(type(group_id))
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
	        insert_topic(topic, username, user_id,MONGO_CONNECTION_STRING)
	        await update.message.reply_text(f"✅ **Topic:**\n{topic} added to processing", parse_mode='Markdown')
    	except Exception as e:
        	print(f"An error occurred: {e}")
    else:
        # Fallback if they just type /topic without text
        await update.message.reply_text("❌ Please provide a topic. \nExample: `/topic Talk about the distance of the sun`", parse_mode='Markdown')


def insert_topic(topic, username, user_id,MONGO_CONNECTION_STRING):
    # Replace with your actual connection string
    client = MongoClient(MONGO_CONNECTION_STRING)
    
    db = client["Sitcom"]
    collection = db["suggested_topics"]

    # Construct the document
    doc = {
        "topic": topic,
        "user_id": int(user_id),
        "username": username,
        "creation_time": datetime.datetime.now(datetime.timezone.utc),
        "processed": False
    }

    result = collection.insert_one(doc)
    print(f"Successfully inserted document with ID: {result.inserted_id}")
    client.close()