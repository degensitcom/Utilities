import os
import io
import requests
import boto3
from dotenv import load_dotenv


def stream_wav_to_s3(audio_wav_bytes, s3_path):

    # 1. Setup S3 Client
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION")
    )
    bucket = os.getenv("S3_BUCKET_NAME")
    
    # 1. Upload directly to S3
    print(f"Streaming directly to S3: {s3_path}")
    s3.upload_fileobj(
        audio_wav_bytes, 
        bucket, 
        s3_path,
        ExtraArgs={'ContentType': 'audio/wav'} # Ensures it plays in browsers
    )
    print("Done streaming!")

