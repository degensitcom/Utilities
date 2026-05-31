import os
import requests

from dotenv import load_dotenv, dotenv_values
from twitchio.ext import commands
import asyncio
from pymongo import MongoClient
import datetime

ENV_FILE = "twitch_creds.env"

def access_token_is_valid(token):
    try:
        response = requests.get(
            "https://id.twitch.tv/oauth2/validate",
            headers={
                "Authorization": f"OAuth {token}"
            },
            timeout=30,
        )
        return response.status_code == 200
    except Exception:
        return False

def refresh_access_token():
    env = dotenv_values(ENV_FILE)

    response = requests.post(
        "https://id.twitch.tv/oauth2/token",
        params={
            "grant_type": "refresh_token",
            "refresh_token": env["TWITCH_REFRESH_TOKEN"],
            "client_id": env["TWITCH_CLIENT_ID"],
            "client_secret": env["TWITCH_CLIENT_SECRET"],
        },
        timeout=30,
    )

    response.raise_for_status()
    data = response.json()

    env["TWITCH_ACCESS_TOKEN"] = data["access_token"]

    if "refresh_token" in data:
        env["TWITCH_REFRESH_TOKEN"] = data["refresh_token"]

    with open(ENV_FILE, "w") as f:
        for key, value in env.items():
            f.write(f"{key}={value}\n")

    print("Token refreshed")

    return env["TWITCH_ACCESS_TOKEN"]

# Reload environment after refresh
load_dotenv(ENV_FILE,override=True)
load_dotenv(dotenv_path="production.env", override=True)

ACCESS_TOKEN = os.getenv("TWITCH_ACCESS_TOKEN")

if not ACCESS_TOKEN or not access_token_is_valid(ACCESS_TOKEN):
    print("Access token expired or invalid. Refreshing...")
    refresh_access_token()
else:
    print("Access token still valid.")

ACCESS_TOKEN = os.getenv("TWITCH_ACCESS_TOKEN")
CHANNEL = os.getenv("TWITCH_CHANNEL")
MONGO_CONNECTION_STRING = os.getenv("MONGO_CONNECTION_STRING")


def insert_topic(topic, username,MONGO_CONNECTION_STRING):
    # Replace with your actual connection string
    client = MongoClient(MONGO_CONNECTION_STRING)
    
    db = client["Sitcom"]
    collection = db["suggested_topics"]

    # Construct the document
    doc = {
        "topic": topic,
        "username": username,
        "creation_time": datetime.datetime.now(datetime.timezone.utc),
        "source":"TWITCH",
        "processed": False
    }

    result = collection.insert_one(doc)
    print(f"Successfully inserted document with ID: {result.inserted_id}")
    client.close()


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            token=ACCESS_TOKEN,
            prefix="!",
            initial_channels=[CHANNEL],
        )

    async def event_ready(self):
        print(f"Connected as {self.nick}")

    async def event_message(self, message):
        if message.echo:
            return

        print(f"{message.author.name}: {message.content}")
        topic = message.content.replace('!topic','')
        username = message.author.name
        if message.content.lower().startswith("!topic"):
            insert_topic(topic, username,MONGO_CONNECTION_STRING)
            await message.channel.send(
                "Adding the topic to play: "+topic+". Please wait 2-3 minutes for generation."
            )
            

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    print("ACCESS_TOKEN =", ACCESS_TOKEN)
    print("CHANNEL =", CHANNEL)
    bot = Bot()
    bot.run()