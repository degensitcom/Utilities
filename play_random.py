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


def get_or_reset_document(collection):
    """
    1. Finds a doc where processed=False and generation_time is within the last 24h.
    2. If not found, picks a random doc where processed=True and resets it.
    """
    # Define the 30 day window
    thirty_day_ago = datetime.now() - timedelta(days=30)


    # 1. Attempt to find an existing document that fits the criteria
    query = {
        "processed": False, "unload": True,
        "generation_time": {"$gte": thirty_day_ago}
    }

    count = collection.count_documents(query)
    if count > 2:
        return 0

    print(f"Found only {count} documents (<= 2). Resetting a random document...")

    # 2. If no match, pick a random one that is currently 'processed = True'
    # The $match stage ensures we only pick from already-completed documents
    pipeline = [
        { "$match": { "processed": True, "unload": True } },
        { "$sample": { "size": 1 } }
    ]
    
    random_cursor = collection.aggregate(pipeline)
    random_list = list(random_cursor)

    if not random_list:
        print("No documents found to process or reset.")
        return None

    # 3. Update the chosen random document to 'False' and 'Now'
    target_id = random_list[0]['_id']
    print(target_id)
    
    updated_doc = collection.find_one_and_update(
        {"_id": target_id},
        {
            "$set": {
                "processed": False
            }
        },
       
    )


# 3. Connect safely
if not mongo_uri:
    print("Error: MONGO_CONNECTION_STRING not found in environment variables.")
else:
    client = MongoClient(mongo_uri)
    db = client["Sitcom"] 
    generated_scenario_collection = db["generated_scenario"]
    get_or_reset_document(generated_scenario_collection)