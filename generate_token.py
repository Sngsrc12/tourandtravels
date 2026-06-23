# # import os
# # import pickle
# # from google_auth_oauthlib.flow import InstalledAppFlow
# # from google.auth.transport.requests import Request

# # # Scope: Google Drive file access
# # SCOPES = ["https://www.googleapis.com/auth/drive.file"]

# # def main():
# #     creds = None
# #     token_file = "token.pickle"

# #     # If token.pickle exists, load it
# #     if os.path.exists(token_file):
# #         with open(token_file, "rb") as token:
# #             creds = pickle.load(token)

# #     # If no valid credentials, do OAuth flow
# #     if not creds or not creds.valid:
# #         if creds and creds.expired and creds.refresh_token:
# #             creds.refresh(Request())
# #         else:
# #             flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
# #             creds = flow.run_local_server(port=0)  # Opens browser for login
# #         with open(token_file, "wb") as token:
# #             pickle.dump(creds, token)

# #     print("✅ token.pickle has been created successfully!")

# # if __name__ == "__main__":
# #     main()




# # resp = requests.get(
# #     f"https://api.netlify.com/api/v1/sites/{SITE_ID}/deploys",
# #     headers={"Authorization": f"Bearer {TOKEN}"}
# # )

# # for d in resp.json():
# #     print("Deploy:", d["id"], "→ URL:", d["deploy_ssl_url"])


# # import requests

# # import os
# # import hashlib
# # import json
# # import requests
# # import time

# # NETLIFY_TOKEN = "nfp_4kXvGbVVUVpQyUAPeHo1zS78J8sRBHSseced"   # from Netlify dashboard
# # SITE_ID = "a1c03608-3b99-452d-8b13-bc152b84665e"



# NETLIFY_TOKEN = "nfp_4kXvGbVVUVpQyUAPeHo1zS78J8sRBHSseced"


# SITE_ID = "27ceba41-f9cc-410b-a30a-6ea3880c404c"   # your Netlify site ID
# FILE_PATH = "video.mp4"  # local file you want to upload

# import hashlib
# import requests
# import time
# import os

# FILE_PATH = "video.mp4"

# def sha1_of_file(path):
#     h = hashlib.sha1()
#     with open(path, "rb") as f:
#         for chunk in iter(lambda: f.read(8192), b""):
#             h.update(chunk)
#     return h.hexdigest()

# file_name = os.path.basename(FILE_PATH)
# sha1 = sha1_of_file(FILE_PATH)

# # 1. Create deploy
# deploy_url = f"https://api.netlify.com/api/v1/sites/{SITE_ID}/deploys"
# manifest = {
#     "files": {
#         f"/{file_name}": {"sha": sha1}
#     }
# }

# resp = requests.post(
#     deploy_url,
#     headers={"Authorization": f"Bearer {NETLIFY_TOKEN}"},
#     json=manifest
# )
# resp.raise_for_status()
# deploy_id = resp.json()["id"]
# print("Created deploy:", deploy_id)

# # 2. Upload file to the matching path
# put_url = f"https://api.netlify.com/api/v1/deploys/{deploy_id}/files/%2F{file_name}?sha={sha1}"
# with open(FILE_PATH, "rb") as f:
#     r = requests.put(
#         put_url,
#         headers={
#             "Authorization": f"Bearer {NETLIFY_TOKEN}",
#             "Content-Type": "application/octet-stream"
#         },
#         data=f
#     )
# print("Upload status:", r.status_code, r.text)

# # 3. Wait for deploy ready
# status = "uploading"
# while status not in ["ready", "error"]:
#     time.sleep(3)
#     check = requests.get(
#         f"https://api.netlify.com/api/v1/deploys/{deploy_id}",
#         headers={"Authorization": f"Bearer {NETLIFY_TOKEN}"}
#     ).json()
#     status = check["state"]
#     print("Deploy state:", status)

# if status == "ready":
#     site_url = check["links"]["permalink"]
#     file_url = f"{site_url}/{file_name}"
#     print("✅ File available at:", file_url)
# else:
#     print("❌ Deploy failed:", check)



import requests

BOT_TOKEN = "8416406359:AAGygVTGjxeSzVa_RQA6RaIDk2GZbTaKeFk"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
resp = requests.get(url).json()
print(resp)
