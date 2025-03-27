# upload_photos_to_s3.py
import boto3 # type: ignore
from pathlib import Path

def upload_to_s3(local_dir, bucket_name):
    s3_client = boto3.client('s3')  # Ensure AWS credentials are configured
    photos_dir = Path(local_dir)
    
    for file in photos_dir.glob("*.jpg"):
        s3_key = f"photos/{file.name}"
        s3_client.upload_file(str(file), bucket_name, s3_key)
        print(f"Uploaded {file.name} to s3://{bucket_name}/{s3_key}")

def main():
    local_dir = "path/to/photos"  # Replace with the folder containing photos
    bucket_name = "event-photos-2025"  # Replace with your S3 bucket name
    upload_to_s3(local_dir, bucket_name)

if __name__ == "__main__":
    main()