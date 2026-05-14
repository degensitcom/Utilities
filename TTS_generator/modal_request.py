import requests
import io
import threading
url = "https://degen-sitcom--example-chatterbox-tts-chatterbox-api-endpoint.modal.run"

def get_character_audio(line, character, modal_api_key):
    
    # Headers from your -H flags
    headers = {
        "Content-Type": "application/json",
        "Authorization": modal_api_key
    }
    
    # Data payload from your -d flag
    payload = {
        "character": character,
        "text": line
    }

    try:
        # Making the POST request
        response = requests.post(url, json=payload, headers=headers)
        
        # Raise an exception if the request was unsuccessful (e.g., 400 or 500 errors)
        response.raise_for_status()

        # Wrap the binary content in a BytesIO object
        audio_buffer = io.BytesIO(response.content)
        
        # Optional: Reset pointer to the start of the "file"
        audio_buffer.seek(0)
        
        return audio_buffer

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def get_modal_up(modal_api_key):
    # Headers from your -H flags
    headers = {
        "Content-Type": "application/json",
        "Authorization": modal_api_key
    }
    
    # Data payload from your -d flag
    payload = {
        "character": "TRUMP",
        "text": "test"
    }
    threading.Thread(target=hit_it, args=(headers, payload), daemon=True).start()


def hit_it(headers,payload):
    try:
        # We set a short timeout so the thread doesn't hang forever
        requests.post(url, json=payload, headers=headers, timeout=2)
    except Exception as e:
        print(f"Thread Error: {e}")
        # pass # We truly do not care if it fails