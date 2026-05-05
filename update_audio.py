import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime, timedelta
from TTS_generator.s3_uploader import *
from TTS_generator.modal_request import *
# 1. Load the variables from .env into the environment

load_dotenv(dotenv_path="common_creds.env", override=True)
load_dotenv(dotenv_path="production.env", override=True)

# 2. Retrieve the URI
mongo_uri = os.getenv("MONGO_CONNECTION_STRING")
modal_api_key = os.getenv("MODAL_API_KEY")
# 3. Connect safely
if not mongo_uri:
    print("Error: MONGO_CONNECTION_STRING not found in environment variables.")
else:
    client = MongoClient(mongo_uri)
    db = client["Sitcom"] 
    collection = db["generated_scenario"]

    days_ago = datetime.now() - timedelta(days=1)
    query = {
    "new_tts_audio": {"$exists": False},
    "generation_time": {"$gte": days_ago},
    "unload": False
    }
    results = collection.find(query)
                 
for scenario in results:
    scenario_id = scenario.get('_id')
    dialogues = scenario.get("scenario", [])
    print(f"Picked scenario id: {scenario_id}")
    audio_buffer = []
    success = True
    for i, dialogue in enumerate(dialogues): # Added 'i' to ensure unique filenames
        try:
            line = dialogue['line']
            character = dialogue['character']
            
            s3_path = f"Sitcom/{scenario_id}/{i}_{character.replace(' ', '_')}.wav"
            dialogue['audio_path'] = s3_path
            audio_wav_bytes = get_character_audio(line, character, modal_api_key)
            audio_buffer.append({
                "bytes": audio_wav_bytes,
                "path": s3_path,
                "index": i
            })
            # stream_wav_to_s3(audio_wav_bytes, s3_path)
            
        except Exception as e:
            print(f"Modal failed at line {i}: {e}")
            success = False
            break

    if success:
        print("Generation complete. Starting serial S3 uploads...")
        try:
            for item in audio_buffer:
                # Low-cost operation (Network I/O)
                stream_wav_to_s3(item["bytes"], item["path"])

                # Update the dialogue object with the new path
                dialogues[item["index"]]['audio_path'] = item["path"]

        except Exception as e:
            print(f"S3 Upload failed: {e}")
            success = False
            
    if success:
        # We update the scenario list AND the status flags
        collection.update_one(
            {"_id": scenario_id},
            {
                "$set": {
                    "scenario": dialogues, # This saves the new audio_paths back to Mongo
                    "new_tts_audio": True, 
                    "unload": True
                    }
            }
        )
    else:
    # We update the scenario list AND the status flags
        collection.update_one(
            {"_id": scenario_id},
            {
                "$set": {
                    "unload": "failed"}
            }
        )
