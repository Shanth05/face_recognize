# preprocess_photos.py
import boto3
import mysql.connector
import face_recognition
from pathlib import Path
import pickle

# Configuration
DB_CONFIG = {
    "host": "localhost",  # Replace with your DB host
    "user": "your_username",  # Replace with your DB username
    "password": "your_password",  # Replace with your DB password
    "database": "event_photos"
}
BUCKET_NAME = "event-photos-2025"  # Replace with your S3 bucket name

def download_from_s3(s3_key, local_path):
    s3_client = boto3.client('s3')
    s3_client.download_file(BUCKET_NAME, s3_key, local_path)

def get_face_encodings(image_path):
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)
    return encodings

def main():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    insert_photo_sql = "INSERT INTO photos (s3_key, url, face_encodings) VALUES (%s, %s, %s)"
    
    s3_client = boto3.client('s3')
    response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix="photos/")
    
    temp_dir = Path("temp_photos")
    temp_dir.mkdir(exist_ok=True)
    
    for obj in response.get('Contents', []):
        s3_key = obj['Key']
        url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{s3_key}"
        local_file = temp_dir / Path(s3_key).name
        
        download_from_s3(s3_key, str(local_file))
        
        encodings = get_face_encodings(str(local_file))
        if encodings:
            encodings_blob = pickle.dumps(encodings)
            cursor.execute(insert_photo_sql, (s3_key, url, encodings_blob))
            print(f"Processed {s3_key} with {len(encodings)} faces")
        else:
            cursor.execute("INSERT INTO photos (s3_key, url) VALUES (%s, %s)", (s3_key, url))
            print(f"Processed {s3_key} with no faces detected")
        
        local_file.unlink()  # Clean up
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()