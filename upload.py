# import os
import requests
# import xml.etree.ElementTree as ET

# # === CONFIG FOR NEXTCLOUD VIDEO UPLOAD ===
# NEXTCLOUD_URL = "https://tio.lv.tab.digital"
# USERNAME = "mglove7800@gmail.com"
# PASSWORD = "sanjay@979227877"

# # === CONFIG FOR IMAGE UPLOAD ===
IMGBB_API_KEY = "ccc2c8268236991b9eeb435d41ae4271"


# # === Upload Video to Nextcloud ===
# def upload_to_root(local_file_path):
#     file_name = os.path.basename(local_file_path)
#     webdav_url = f"{NEXTCLOUD_URL}/remote.php/dav/files/{USERNAME}/{file_name}"

#     print(f"⬆️ Uploading {file_name} → Nextcloud...")

#     with open(local_file_path, "rb") as f:
#         res = requests.put(webdav_url, data=f, auth=(USERNAME, PASSWORD))
#     if res.status_code not in (200, 201, 204):
#         raise Exception(f"❌ Upload failed: {res.status_code} {res.text}")

#     print(f"✅ Uploaded to Nextcloud as: {file_name}")

#     # --- Create share link ---
#     share_url = f"{NEXTCLOUD_URL}/ocs/v2.php/apps/files_sharing/api/v1/shares"
#     headers = {"OCS-APIRequest": "true"}
#     data = {"path": file_name, "shareType": 3}  # 3 = public link

#     res = requests.post(share_url, auth=(USERNAME, PASSWORD), headers=headers, data=data)
#     if res.status_code != 200:
#         raise Exception(f"❌ Error creating share: {res.status_code} {res.text}")

#     root = ET.fromstring(res.text)
#     public_link = root.find(".//url").text
#     direct_link = public_link + "/download"

#     print("🌍 Public link:", public_link)
#     print("🎬 Direct link:", direct_link)

#     return direct_link

# import os
# import requests

# # === CONFIG ===
# USERNAME = "sanjayyadav11210@gmail.com"
# PASSWORD = "sanjZ@11602079"

# def get_pcloud_auth_token():
#     token_file = "pcloud_token.txt"

#     if os.path.exists(token_file):
#         with open(token_file, "r") as f:
#             token = f.read().strip()
#             if is_token_valid(token):
#                 print("✅ Using saved auth token.")
#                 return token
#             else:
#                 print("🔁 Token expired or invalid. Re-authenticating...")

#     auth_url = "https://api.pcloud.com/login"
#     params = {
#         "getauth": 1,
#         "logout": 1,
#         "username": USERNAME,
#         "password": PASSWORD
#     }

#     response = requests.get(auth_url, params=params)
#     data = response.json()

#     if data.get("auth"):
#         token = data["auth"]
#         with open(token_file, "w") as f:
#             f.write(token)
#         print("✅ Authenticated and token saved.")
#         return token
#     else:
#         raise Exception("❌ Authentication failed:", data)

# def is_token_valid(token):
#     response = requests.get("https://api.pcloud.com/userinfo", params={"auth": token})
#     return response.status_code == 200 and response.json().get("result") == 0

# def upload_to_pcloud(file_path, auth_token):
#     file_name = os.path.basename(file_path)
#     url = "https://api.pcloud.com/uploadfile"
#     params = {
#         "auth": auth_token,
#         "folderid": 0
#     }

#     with open(file_path, "rb") as f:
#         files = {"file": f}
#         response = requests.post(url, params=params, files=files)

#     data = response.json()
#     if "metadata" not in data:
#         raise Exception("❌ Upload failed:", data)

#     metadata = data["metadata"][0]
#     print(f"✅ Uploaded: {metadata['name']} (fileid: {metadata['fileid']})")
#     return metadata

# # ✅ Get permanent direct downloadable/streamable link
# def generate_direct_stream_link(fileid, auth_token):
#     # Step 1: Get publink (permanent code)
#     publink_url = "https://api.pcloud.com/getfilepublink"
#     publink_params = {
#         "auth": auth_token,
#         "fileid": fileid
#     }

#     publink_response = requests.get(publink_url, params=publink_params)
#     publink_data = publink_response.json()

#     if "code" not in publink_data:
#         raise Exception("❌ Failed to get publink:", publink_data)

#     publink_code = publink_data["code"]

#     # Step 2: Use publink code to get real direct download URL
#     direct_url = "https://api.pcloud.com/getpublinkdownload"
#     direct_params = {
#         "code": publink_code
#     }

#     direct_response = requests.get(direct_url, params=direct_params)
#     direct_data = direct_response.json()

#     if "hosts" in direct_data and "path" in direct_data:
#         host = direct_data["hosts"][0]
#         path = direct_data["path"]
#         return f"https://{host}{path}"
#     else:
#         raise Exception("❌ Failed to generate streamable link:", direct_data)

# def upload_to_root(file_path):
#     auth_token = get_pcloud_auth_token()
#     metadata = upload_to_pcloud(file_path, auth_token)
#     stream_link = generate_direct_stream_link(metadata["fileid"], auth_token)
#     print("🎬 Permanent Direct Streaming Link:", stream_link)
#     return stream_link




# import os
# import hashlib
# import json
# import requests
# import os, hashlib, json, requests, time

# # === CONFIG ===
# NETLIFY_TOKEN = "nfp_4kXvGbVVUVpQyUAPeHo1zS78J8sRBHSseced"   # from Netlify dashboard
# SITE_ID = "a1c03608-3b99-452d-8b13-bc152b84665e"



# import os
# import time
# from supabase import create_client, Client

# # 🔑 Replace with your Supabase project details
# SUPABASE_URL = "https://qkamixtyilqygcohrzmw.supabase.co"
# SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFrYW1peHR5aWxxeWdjb2hyem13Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NzA5Nzk3NiwiZXhwIjoyMDcyNjczOTc2fQ.v56ENRgS1OR9ZhRKY5hNTYlQBIywl2zo2SptOWjkzJE"
# BUCKET_NAME = "Sundarikanya"

# # Create client
# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# def upload_to_root(file_path: str) -> str:
#     # Unique filename with timestamp
#     file_name = f"{int(time.time())}_{os.path.basename(file_path)}"

#     # Upload file
#     with open(file_path, "rb") as f:
#         res = supabase.storage.from_(BUCKET_NAME).upload(file_name, f)

#     if res:
#         # Get permanent public link
#         public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(file_name)
#         print("🎬 Direct Streaming Link:", public_url)
#         return public_url
#     else:
#         raise Exception("❌ Upload failed")

# import os
# import re
# import time
# import subprocess
# import internetarchive
# import requests  # used to detect HTTPError exceptions

# # Put your keys here or load from env
# IA_ACCESS_KEY = "EPwuN4xAfksklbuj"
# IA_SECRET_KEY = "yWxtZoYKkTJ6R6VO"

# # Reusable session
# _session = internetarchive.get_session(config={
#     "s3": {"access": IA_ACCESS_KEY, "secret": IA_SECRET_KEY}
# })

# def _make_identifier(file_path: str) -> str:
#     """Create a valid archive.org identifier from filename + timestamp."""
#     base = os.path.splitext(os.path.basename(file_path))[0]
#     # Replace invalid chars with dash
#     base = re.sub(r"[^A-Za-z0-9_.-]", "-", base)
#     # Ensure starts with alnum
#     if not re.match(r"^[A-Za-z0-9]", base):
#         base = "v" + base
#     identifier = f"{base}-{int(time.time())}"
#     # Truncate to <=100 chars (archive allows up to 100)
#     return identifier[:100]

# def _compress_with_ffmpeg(input_path: str, crf: int = 28, preset: str = "fast") -> str:
#     """
#     Compress the video using ffmpeg (if ffmpeg is available).
#     Returns path to compressed file.
#     """
#     if not shutil.which("ffmpeg"):
#         raise RuntimeError("ffmpeg not found on PATH. Install ffmpeg or run without compression.")
#     dirname = os.path.dirname(input_path) or "."
#     name = os.path.splitext(os.path.basename(input_path))[0]
#     out = os.path.join(dirname, f"{name}-compressed.mp4")
#     cmd = [
#         "ffmpeg", "-y", "-i", input_path,
#         "-vcodec", "libx264", "-crf", str(crf), "-preset", preset,
#         "-acodec", "aac", "-b:a", "128k",
#         out
#     ]
#     subprocess.run(cmd, check=True)
#     return out

# import shutil

# def upload_to_root(file_path: str, compress: bool = False, attempts: int = 3, crf: int = 28) -> str:
#     """
#     Upload a file to archive.org and return the direct video URL.
#     - compress: if True, will try to compress the file with ffmpeg before upload.
#     - attempts: number of upload attempts (sequential retries with backoff).
#     - crf: compression quality (lower = better quality / larger file).
#     """
#     if not os.path.exists(file_path):
#         raise FileNotFoundError(f"File not found: {file_path}")

#     upload_file = file_path

#     # Optional compression step (recommended to speed up upload)
#     if compress:
#         try:
#             print("⚙️ Compressing video before upload...")
#             upload_file = _compress_with_ffmpeg(file_path, crf=crf)
#             print("✅ Compression finished:", upload_file)
#         except Exception as e:
#             # fallback to original file if compression fails
#             print("⚠️ Compression failed — continuing with original file. Reason:", str(e))
#             upload_file = file_path

#     identifier = _make_identifier(upload_file)
#     metadata = {
#         "title": os.path.basename(upload_file),
#         "mediatype": "movies",
#         "description": f"Uploaded at {time.ctime()} using Python script",
#         "creator": "PythonUploader",
#     }

#     item = _session.get_item(identifier)

#     last_exc = None
#     for attempt in range(1, attempts + 1):
#         try:
#             print(f"⬆️  Upload attempt {attempt}/{attempts} -> identifier: {identifier}")
#             # Supported args: metadata, queue_derive, validate_identifier, verbose
#             responses = item.upload([upload_file], metadata=metadata, queue_derive=False, verbose=True)

#             # responses is a list of response-like objects; check their status codes
#             codes = [getattr(r, "status_code", None) for r in responses]
#             if all(code == 200 for code in codes):
#                 public_url = f"https://archive.org/download/{identifier}/{os.path.basename(upload_file)}"
#                 print("🎬 Direct Streaming Link:", public_url)
#                 return public_url
#             else:
#                 # Non-200 codes — raise to trigger retry
#                 last_exc = RuntimeError(f"Upload returned non-200 codes: {codes}")
#                 print("❌ Upload returned codes:", codes)
#         except requests.exceptions.HTTPError as http_e:
#             last_exc = http_e
#             print("❌ HTTP error during upload:", str(http_e))
#         except Exception as e:
#             last_exc = e
#             print("❌ Upload failed with exception:", str(e))

#         # backoff before next attempt
#         if attempt < attempts:
#             backoff = 2 ** attempt
#             print(f"⏳ Backing off {backoff}s before retry...")
#             time.sleep(backoff)

#     # If we reach here, all attempts failed
#     raise RuntimeError(f"Upload failed after {attempts} attempts. Last error: {last_exc}")



# def upload_to_root(file_path):
#     url = "https://pixeldrain.com/api/file"
#     headers = {"Authorization": f"Basic {API_KEY}"}
#     with open(file_path, "rb") as f:
#         response = requests.post(url, headers=headers, files={"file": f})
    
#     if response.status_code == 200:
#         data = response.json()
#         file_id = data["id"]
#         share_link = f"https://pixeldrain.com/u/{file_id}"
#         raw_link = f"https://pixeldrain.com/api/file/{file_id}"
#         print("✅ Upload successful!")
#         print("Share link:", share_link)
#         print("Direct link:", raw_link)
#         return raw_link
#     else:
#         print("❌ Upload failed:", response.text)
#         return None



import os
import random
import requests

# Your Catbox userhash (from your account)
USERHASH = "89e13790c452d9ad182194fd9"

def generate_filename(extension=".mp4"):
    """Generate random 12-digit filename"""
    return f"{random.randint(10**11, (10**12)-1)}{extension}"

def upload_to_root(file_path):
    """Upload file to Catbox account and return direct .mp4 link"""
    _, ext = os.path.splitext(file_path)
    new_name = generate_filename(ext)
    url = "https://catbox.moe/user/api.php"

    file_size = os.path.getsize(file_path)
    print(f"📦 Uploading {new_name} ({round(file_size/1024/1024,2)} MB)")

    # size check
    if file_size > 1024 * 1024 * 1024:
        raise Exception("❌ File too large for Catbox (limit 1 GB).")

    with open(file_path, "rb") as f:
        response = requests.post(
            url,
            data={"reqtype": "fileupload", "userhash": USERHASH},
            files={"fileToUpload": (new_name, f)},
            timeout=120
        )

    print("🪣 Raw server reply:", repr(response.text))

    if response.status_code == 200:
        link = response.text.strip()
        if link.startswith("https://"):
            print("✅ Upload successful!")
            print("Renamed file:", new_name)
            print("Direct link:", link)
            return link
        else:
            raise Exception(f"❌ Upload failed, server message: {link or 'empty response'}")
    else:
        raise Exception(f"❌ HTTP Error {response.status_code}: {response.text}")





# === Upload Image to ImgBB ===
def upload_image(image_path):
    upload_url = "https://api.imgbb.com/1/upload"
    with open(image_path, "rb") as img_file:
        payload = {"key": IMGBB_API_KEY}
        files = {"image": img_file}
        response = requests.post(upload_url, data=payload, files=files)

    if response.status_code == 200:
        data = response.json()
        print("✅ Uploaded Successfully")
        print("🖼️ Image Link:", data['data']['url'])
        print("🗑️ Delete Link:", data['data']['delete_url'])
        return data['data']['url']
    else:
        print("❌ Upload failed:", response.text)
        return None



def delete_from_dropbox(file_url: str):
    """
    Delete a file from Dropbox using a shared or raw link.
    """
    try:
        # Normalize shared/raw links
        if "?raw=1" in file_url:
            file_url = file_url.replace("?raw=1", "")
        if "?dl=0" in file_url:
            file_url = file_url.replace("?dl=0", "")

        # Get Dropbox metadata from shared link
        metadata = dbx.sharing_get_shared_link_metadata(file_url)
        dropbox_path = metadata.path_lower  # actual path in Dropbox

        # Delete file from Dropbox
        dbx.files_delete_v2(dropbox_path)
        print(f"✅ Deleted from Dropbox: {dropbox_path}")
        return True

    except Exception as e:
        print(f"❌ Dropbox delete error: {e}")
        return False

async def get_dropbox_path_from_link(shared_link: str) -> str:
    """
    Convert Dropbox shared link to internal path_display
    """
    url = "https://api.dropboxapi.com/2/sharing/get_shared_link_metadata"
    headers = {
        "Authorization": f"Bearer {DROPBOX_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"url": shared_link}

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            result = await resp.json()
            if resp.status != 200:
                raise Exception(f"❌ Failed to get metadata: {result}")
            return result["path_lower"]  # or path_display
