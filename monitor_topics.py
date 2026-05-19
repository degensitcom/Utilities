import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime, timedelta, timezone
from Scenario_generator.scenario_generator import *
# 1. Load the variables from .env into the environment
load_dotenv(dotenv_path="common_creds.env", override=True)
load_dotenv(dotenv_path="production.env", override=True)


# 2. Retrieve the URI
mongo_uri = os.getenv("MONGO_CONNECTION_STRING")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CHAT_GPT_API_KEY = os.getenv("CHAT_GPT_API_KEY")
# 3. Connect safely
if not mongo_uri:
    print("Error: MONGO_CONNECTION_STRING not found in environment variables.")
else:
    client = MongoClient(mongo_uri)
    db = client["Sitcom"] 
    suggested_topics_collection = db["suggested_topics"]
    generated_scenario_collection = db["generated_scenario"]
    days_ago = datetime.now() - timedelta(days=1)
    query = {
    "processed": False,
    "creation_time": {"$gte": days_ago}
    }
    suggested_topics = suggested_topics_collection.find(query)
    
          
for suggested_topic in suggested_topics:
    suggested_topic_id = suggested_topic.get('_id')
    print(f"Picked suggested topic id:  {suggested_topic_id}")
    topic = suggested_topic.get("topic")
    username = suggested_topic.get("username")
    user_id = suggested_topic.get("user_id")
    message_id = suggested_topic.get("message_id")
    group_id = suggested_topic.get("group_id")
    source = suggested_topic.get("source")
    try:
        success = True
        real_topic= topic
        if(topic.strip().endswith("--hide")):
             real_topic = topic.removesuffix("--hide")
        dialogues = get_scenario_text(real_topic,username,CHAT_GPT_API_KEY)
        if(topic.strip().endswith("--hide")):
            document = {
                "topic": "Sitcom",
                "real_topic": real_topic,
                "scenario": dialogues.get("scenario"),
                "user_id": user_id,
                "message_id": message_id,
                "group_id": group_id,
                "username": username,
                "source": source,
                "generation_time": datetime.now(timezone.utc),
                "unload": False,
                "processed": False
            }
        else:
             document = {
                "topic": topic,
                "scenario": dialogues.get("scenario"),
                "user_id": user_id,
                "message_id": message_id,
                "group_id": group_id,
                "username": username,
                "source": source,
                "generation_time": datetime.now(timezone.utc),
                "unload": False,
                "processed": False
            }
        result = generated_scenario_collection.insert_one(document)
        print(result.inserted_id)

        suggested_topics_collection.update_one(
                {"_id": suggested_topic_id},
                {
                    "$set": {
                        "processed": True
                         }
                }
            )
    except Exception as e:
            print(f"Failed processing {suggested_topic_id}. Error: {e}")
            suggested_topics_collection.update_one(
                {"_id": suggested_topic_id},
                {
                    "$set": {
                        "processed": "Failed"
                         }
                }
            )
