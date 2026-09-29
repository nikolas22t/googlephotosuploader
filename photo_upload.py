__version__ = "0.1.0"

import os
import json
import requests
import hashlib
import time
import urllib.parse
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Folder containing media to upload
MEDIA_FOLDER = "/Users/username/Downloads/Upload"

# OAuth scopes (Google Photos API permissions)
SCOPES = ['https://www.googleapis.com/auth/photoslibrary.appendonly']

# Batch size for uploads
BATCH_SIZE = 50

# File to store uploaded file hashes (to avoid duplicates)
HASH_FILE = "uploaded_hashes.json"

# Allowed file types for upload
MEDIA_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.mp4', '.mov', '.avi')

# Authenticate with Google Photos API
def authenticate():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token_file:
            token_file.write(creds.to_json())
    return creds

# Calculate SHA1 hash of a file
def file_hash(path):
    h = hashlib.sha1()
    with open(path, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

# Load uploaded file hashes from JSON file
def load_uploaded_hashes():
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, 'r') as f:
            return set(json.load(f))
    return set()

# Save uploaded file hashes to JSON file
def save_uploaded_hashes(hashes):
    with open(HASH_FILE, 'w') as f:
        json.dump(list(hashes), f)

# Upload a single media file and return the upload token
def get_upload_token(file_path, creds):
    upload_url = "https://photoslibrary.googleapis.com/v1/uploads"

    # ✅ Safely encode filename to avoid UnicodeEncodeError
    safe_filename = urllib.parse.quote(os.path.basename(file_path), safe='')
    if safe_filename != os.path.basename(file_path):
        print(f"[INFO] Filename encoded for upload: {os.path.basename(file_path)} -> {safe_filename}")

    headers = {
        "Authorization": f"Bearer {creds.token}",
        "Content-type": "application/octet-stream",
        "X-Goog-Upload-File-Name": safe_filename,
        "X-Goog-Upload-Protocol": "raw",
    }

    with open(file_path, 'rb') as f:
        response = requests.post(upload_url, data=f, headers=headers)

    if response.status_code == 200:
        return response.text
    else:
        print(f"Error uploading {file_path}: {response.text}")
        return None

# Create media items in batch
def create_media_items_batch(upload_tokens, creds):
    if not upload_tokens:
        return
    create_item_url = "https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate"
    new_media_items = [{"description": "", "simpleMediaItem": {"uploadToken": token}} for token in upload_tokens]
    body = {"newMediaItems": new_media_items}
    res = requests.post(create_item_url, headers={"Authorization": f"Bearer {creds.token}", "Content-type": "application/json"}, json=body)
    if res.status_code == 200:
        print(f"Batch of {len(upload_tokens)} media files uploaded successfully.")
    else:
        print(f"Error creating media items batch: {res.text}")

def main():
    creds = authenticate()
    uploaded_hashes = load_uploaded_hashes()
    
    # Recursively collect all media files in folder
    media_files = []
    for root, dirs, files in os.walk(MEDIA_FOLDER):
        for f in files:
            if f.lower().endswith(MEDIA_EXTENSIONS):
                media_files.append(os.path.join(root, f))
    
    total_files = len(media_files)
    print(f"Total number of files to upload: {total_files}")
    
    batch_tokens = []
    new_uploaded_hashes = set()
    batch_count = 0
    batch_times = []

    for i, file_path in enumerate(media_files, 1):
        h = file_hash(file_path)
        if h in uploaded_hashes:
            print(f"Skipping (already uploaded): {file_path}")
            continue
        
        token = get_upload_token(file_path, creds)
        if token:
            batch_tokens.append(token)
            new_uploaded_hashes.add(h)
        
        # Upload batch when batch size is reached or last file is processed
        if len(batch_tokens) == BATCH_SIZE or i == len(media_files):
            batch_count += 1
            start_time = time.time()
            create_media_items_batch(batch_tokens, creds)
            end_time = time.time()
            
            elapsed = end_time - start_time
            batch_times.append(elapsed)
            
            # Estimate remaining time
            avg_time = sum(batch_times) / len(batch_times)
            remaining_batches = ((total_files - i) // BATCH_SIZE) + 1
            est_remaining = remaining_batches * avg_time
            
            print(f"Batch {batch_count} of {len(batch_tokens)} files took {elapsed:.2f} seconds")
            print(f"Estimated time remaining: {est_remaining/60:.2f} minutes")
            
            uploaded_hashes.update(new_uploaded_hashes)
            save_uploaded_hashes(uploaded_hashes)
            batch_tokens = []
            new_uploaded_hashes = set()

if __name__ == "__main__":
    main()

