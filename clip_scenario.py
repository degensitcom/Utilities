import sys
import os
import boto3
import requests
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv
import obsws_python as obs  # Use the synchronous client for simplicity
from pymongo import MongoClient
from bson import ObjectId
import time 
import json
# Load environment variables from .env file
load_dotenv()

# --- CONFIGURATION from .env file ---
OBS_HOST = os.getenv("OBS_HOST")
OBS_PORT = int(os.getenv("OBS_PORT"))
OBS_PASSWORD = os.getenv("OBS_PASSWORD")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION")
MONGODB_URI = os.getenv("MONGODB_URI")
INTERNAL_API_URL = os.getenv("INTERNAL_API_URL")
INTERNAL_API_AUTH_TOKEN = os.getenv("INTERNAL_API_AUTH_TOKEN")
ENV = os.getenv("ENV")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def start_recording(ws):
    """Sends the command to start recording in OBS."""
    try:
        ws.start_record()
        print("SUCCESS: Recording started in OBS.")
    except Exception as e:
        print(f"ERROR: Could not start recording. Is OBS running and connected? {e}")
        sys.exit(1)


def stop_and_upload(ws, scenario_id):
    """
    Stops the recording, gets the file path,
    and uploads it to S3 if the scenario has never been clipped.
    The recording is deleted from the local file system at the end.
    """

    # get the scenario from the database
    client = None
    db = None
    scenarios_collection = None
    scenario = None

    try:
        client = MongoClient(os.getenv("MONGODB_URI"))
        db = client["Sitcom"]
        scenarios_collection = db["generated_scenario"]
        scenario = scenarios_collection.find_one({"_id": ObjectId(scenario_id)})
    except Exception as e:
        print(f"ERROR: Could not get scenario {scenario_id} from database. {e}")
        return

    if not scenario:
        print(f"ERROR: Scenario with id: {scenario_id} not found in database.")
        return

    try:
        time.sleep(0)
        # The stop_record call is synchronous and returns the path of the saved file
        response = ws.stop_record()
        recording_path = response.output_path
        if not recording_path:
            print(
                f"ERROR: Could not get recording file path for scenario {scenario_id} from OBS."
            )
            sys.exit(1)

        if not scenario.get("clips"):
            # Upload the file to S3
            print(recording_path)
            s3_key = upload_to_s3(recording_path, scenario_id)
            if(scenario.get("source")=="TG"):
                send_telegram_video_reply(scenario,recording_path)
            # Update the scenario document with the S3 key
            scenarios_collection.update_one(
                {"_id": ObjectId(scenario_id)}, {"$set": {"clips.landscape": s3_key}}
            )
            # internal_api_clip_url = f"{INTERNAL_API_URL}/scenarios/{scenario_id}/clips"
            # # Send a POST request to the internal API to create a portrait version of the clip and send a notification
            # requests.post(
            #     internal_api_clip_url,
            #     headers={"Authorization": INTERNAL_API_AUTH_TOKEN, "x-env": ENV},
            # )

        # Delete the local file
        try:
            os.remove(recording_path)
            print(
                f"SUCCESS: Local file '{os.path.basename(recording_path)}' for scenario {scenario_id} deleted."
            )
        except OSError as e:
            print(
                f"WARNING: Could not delete local file for scenario {scenario_id}. {e}"
            )

    except Exception as e:
        print(
            f"ERROR: Could not stop recording for scenario {scenario_id}. Is a recording in progress? {e}"
        )
        sys.exit(1)

def send_telegram_video_reply(scenario, video_path, caption= "Please find the video clip") -> tuple[bool, dict]:
    """
    Sends a local video file as a reply to a specific message using the requests API.
    """
    thumbnail_path = "C:/Users/user/Desktop/sitcom-windows-scripts/production/thumbnail.png"
    if not os.path.exists(video_path):
        return False, {"error": f"File not found at path: {video_path}"}
    print(f"DEBUG: Starting Telegram upload process for path: {video_path}")

    # Calculate file size for logging
    file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
    print(f"DEBUG: Video file size: {file_size_mb:.2f} MB")
    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"

    message_id = scenario["message_id"]
    chat_id = scenario["group_id"]
    reply_config = {
        "message_id": message_id,
        "chat_id": chat_id
    }
    print(f"DEBUG: Target Chat ID: {chat_id} | Replying to Message ID: {message_id}")
    payload = {
        "chat_id": chat_id,
        "caption": caption,
        "supports_streaming": "True",
        "reply_parameters": json.dumps(reply_config)
    }
    try:
        # print(f"UPLOADING: Sending request to Telegram API...")
        # with open(video_path, "rb") as video_file:
        #     files = {"video": video_file}
        #     response = requests.post(api_url, data=payload, files=files)
        with open(video_path, "rb") as video_file, open(thumbnail_path, "rb") as thumb_file:
            files = {
                "video": video_file,
                "thumbnail": thumb_file  # <-- This attaches the static thumbnail
            }
            response = requests.post(api_url, data=payload, files=files)
        response_json = response.json()
        return response_json.get("ok", False), response_json
        
    except Exception as e:
        print(f"ERROR: An unexpected error occurred during Telegram upload: {str(e)}")


def upload_to_s3(file_path, scenario_id):
    """Uploads a file to the configured S3 bucket."""
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )
    file_name = os.path.basename(file_path)
    file_extension = os.path.splitext(file_name)[1]
    s3_key = f"clips/{scenario_id}/landscape{file_extension}"
    try:
        print(f"UPLOADING: s3_key: {s3_key} file_name: '{file_name}' to S3 ...")
        s3_client.upload_file(file_path, S3_BUCKET_NAME, s3_key)
        print(f"SUCCESS: Upload of '{scenario_id}' complete.")
    except FileNotFoundError:
        print(f"ERROR: The file was not found: {file_path} for scenario {scenario_id}")
    except NoCredentialsError:
        print(
            "ERROR: AWS credentials not found. Please configure them in the .env file.",
        )
    except Exception as e:
        print(f"ERROR: Failed to upload file to S3 for scenario {scenario_id}. {e}")

    return s3_key


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ["start", "stop"]:
        print("Usage: python clip_scenario.py [start|stop <id>]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "stop" and len(sys.argv) < 3:
        print("Usage: python clip_scenario.py stop <id>")
        sys.exit(1)

    # Connect to obs-websocket
    try:
        print(
            f"Connecting to OBS at {OBS_HOST}:{OBS_PORT} with password {OBS_PASSWORD}..."
        )
        ws = obs.ReqClient(
            host=OBS_HOST, port=OBS_PORT, password=OBS_PASSWORD, timeout=3
        )
    except Exception as e:
        print(
            f"ERROR: Could not connect to OBS WebSocket. Is OBS running? Is the password correct? {e}"
        )
        sys.exit(1)

    if command == "start":
        start_recording(ws)
    elif command == "stop":
        scenario_id = sys.argv[2]
        stop_and_upload(ws, scenario_id)
