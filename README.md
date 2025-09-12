# Google Photos Uploader

This script uploads photos and videos to Google Photos using the Google Photos Library API.

---

## 🔑 Setup Google Photos API

### 1. Create a Google Cloud Project
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Click **Select a project → New Project**
- Name it `GooglePhotosUploader`
- Click **Create**

### 2. Enable the API
- In your project, go to **APIs & Services → Library**
- Search for **Google Photos Library API**
- Click **Enable**

### 3. Configure OAuth Consent Screen
- Go to **APIs & Services → OAuth consent screen**
- Choose **External**
- Fill out required fields (App name, User email, Developer contact)
- Save and continue
- Add yourself as a **Test User** with your Gmail account

### 4. Create OAuth Credentials
- Go to **APIs & Services → Credentials**
- Click **+ Create Credentials → OAuth client ID**
- Choose **Desktop app**
- Name it `GooglePhotosUploaderDesktop`
- Click **Create**
- Download the file `credentials.json`

### 5. Save Credentials
Place the file in the same folder as the script and rename it to:


---

## ▶️ Usage

Run the script with:

```bash
python3 photo_upload.py



googlephotosuploader/
│── photo_upload.py          # main uploader script
│── credentials.json         # API credentials (downloaded from Google Cloud)
│── token.json               # auto-created after login
│── uploaded_hashes.json     # auto-created to track uploads


