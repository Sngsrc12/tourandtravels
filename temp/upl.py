import os
import requests
import xml.etree.ElementTree as ET

# --- CONFIG ---
NEXTCLOUD_URL = "https://tio.lv.tab.digital"
USERNAME = "mglove7800@gmail.com"    # your login email
PASSWORD = "sanjay@979227877"        # your password
LOCAL_FILE = "temp.mp4"              # file you want to upload
REMOTE_FILE = "temp.mp4"             # remote file name

# --- Step 1: Test login (PROPFIND request) ---
webdav_url = f"{NEXTCLOUD_URL}/remote.php/dav/files/{USERNAME}/"
print(f"🔍 Testing WebDAV login at: {webdav_url}")
res = requests.request("PROPFIND", webdav_url, auth=(USERNAME, PASSWORD))
if res.status_code not in (207, 200):
    print("❌ Login failed:", res.status_code, res.text)
    exit(1)
print("✅ Login successful")

# --- Step 2: Upload file ---
upload_url = f"{webdav_url}{REMOTE_FILE}"
print(f"⬆️ Uploading {LOCAL_FILE} ({os.path.getsize(LOCAL_FILE)} bytes) → {upload_url}")
with open(LOCAL_FILE, "rb") as f:
    res = requests.put(upload_url, data=f, auth=(USERNAME, PASSWORD))

if res.status_code not in (200, 201, 204):
    print("❌ Upload failed:", res.status_code, res.text)
    exit(1)
print("✅ Upload successful")

# --- Step 3: Create public share link ---
share_url = f"{NEXTCLOUD_URL}/ocs/v2.php/apps/files_sharing/api/v1/shares"
headers = {"OCS-APIRequest": "true"}
data = {"path": REMOTE_FILE, "shareType": 3}  # 3 = public link

res = requests.post(share_url, auth=(USERNAME, PASSWORD), headers=headers, data=data)

if res.status_code == 200:
    try:
        root = ET.fromstring(res.text)
        public_link = root.find(".//url").text
        direct_link = public_link + "/download"
        print("🌍 Public share link:", public_link)
        print("🎬 Direct video link:", direct_link)
    except Exception as e:
        print("⚠️ Could not parse XML:", e)
        print("Raw response:", res.text)
else:
    print("❌ Error creating share:", res.status_code, res.text)
