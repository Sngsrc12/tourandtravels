from fastapi import FastAPI, Request, Form, status, HTTPException,File, UploadFile,Query, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse,FileResponse
from fastapi.templating import Jinja2Templates
import json
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict
import os,shutil
import uuid
from fastapi.middleware.cors import CORSMiddleware
import bcrypt
from typing import Union
import os
from datetime import datetime, timedelta
import uuid
import aiofiles
import asyncio
from upload import *
from fastapi import Request   # ✅ for FastAPI routes

from upload import upload_to_root, upload_image  # ✅ import your helper functions

app = FastAPI()

# Set up templates folder
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev only; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




class UpdateVideo(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    thumbnail: Optional[str] = None
    videourl: Optional[List[str]] = None
    tag: Optional[List[str]] = None
    category: Optional[List[str]] = None


DATA_FILE = "data.json"
ACCOUNTS_FILE = "accounts.json"

# Create the JSON file if it doesn't exist
if not os.path.exists(ACCOUNTS_FILE):
    with open(ACCOUNTS_FILE, "w") as f:
        json.dump({"users": []}, f)

class UserCreate(BaseModel):
    username: str
    password: str

# Async load_accounts
async def load_accounts():
    async with aiofiles.open(ACCOUNTS_FILE, 'r') as f:
        content = await f.read()
        return json.loads(content)

# Async save_accounts
async def save_accounts(data):
    async with aiofiles.open(ACCOUNTS_FILE, 'w') as f:
        await f.write(json.dumps(data, indent=2))



class VideoEntry(BaseModel):
    title: str
    description: str
    thumbnail: str
    videourl: List[str]  # ✅ now expecting a list always
    tag: List[str]
    category: List[str]

class UploadData(BaseModel):
    uploader: str
    session_id: str
    videos: List[VideoEntry]

# -------------------
# File helpers
# -------------------

ENGAGEMENT_FILE = "engagement.json"

# Async load_data
async def load_data():
    if not os.path.exists(DATA_FILE):
        return {"data": {"data": []}}
    try:
        async with aiofiles.open(DATA_FILE, "r") as f:
            content = await f.read()
            return json.loads(content)
    except json.JSONDecodeError:
        return {"data": {"data": []}}


# Async save_data
async def save_data(data):
    async with aiofiles.open(DATA_FILE, "w") as f:
        await f.write(json.dumps(data, indent=2))



if not os.path.exists(ENGAGEMENT_FILE):
    with open(ENGAGEMENT_FILE, "w") as f:
        json.dump({}, f)


async def load_engagement():
    async with aiofiles.open(ENGAGEMENT_FILE, "r") as f:
        content = await f.read()
        return json.loads(content)


async def save_engagement(data):
    async with aiofiles.open(ENGAGEMENT_FILE, "w") as f:
        await f.write(json.dumps(data, indent=2))


@app.get("/api/load")
async def get_data():
    data = await load_data()
    return data


# Utils
def load_json(file): return json.load(open(file))
def save_json(file, data): json.dump(data, open(file, "w"), indent=2)

@app.get("/", response_class=HTMLResponse)
async def show_create_account(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def show_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/home", response_class=HTMLResponse)
async def serve_home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/update", response_class=HTMLResponse)
async def update_page(request: Request):
    return templates.TemplateResponse("test.html", {"request": request})

# -------------------
# POST API to add profile
# -------------------

SESSIONS_FILE = "sessions.json"



# Async load_sessions
async def load_sessions():
    try:
        async with aiofiles.open(SESSIONS_FILE, 'r') as f:
            content = await f.read()
            return json.loads(content)
    except FileNotFoundError:
        # If file doesn't exist, initialize with empty structure
        return {"sessions": []}

# Async save_sessions
async def save_sessions(data):
    async with aiofiles.open(SESSIONS_FILE, 'w') as f:
        await f.write(json.dumps(data, indent=2))

# Async session validation
async def is_session_valid(session_id: str) -> bool:
    sessions = await load_sessions()   # ✅ await here
    for session in sessions["sessions"]:
        if session["session_id"] == session_id:
            expires_at = datetime.fromisoformat(session["expires_at"])
            if expires_at > datetime.utcnow():
                return True
    return False



@app.get("/api/session-info")
def session_info(session_id: str):
    sessions = load_json("sessions.json")
    for session in sessions["sessions"]:
        if session["session_id"] == session_id:
            if datetime.utcnow() < datetime.fromisoformat(session["expires_at"]):
                return {"status": "success", "username": session["username"]}
            break
    return {"status": "error", "detail": "Session invalid or expired"}




import aiofiles
import shutil

CHUNK_SIZE = 1024 * 1024  # 1MB per chunk


async def save_upload_file(upload_file: UploadFile, destination: str) -> str:
    """Save uploaded file to disk in chunks (supports large files)."""
    async with aiofiles.open(destination, "wb") as out_file:
        while True:
            chunk = await upload_file.read(CHUNK_SIZE)
            if not chunk:
                break
            await out_file.write(chunk)
    await upload_file.close()
    return destination



# from imagekitio import ImageKit

# import base64
# import os

# imagekit = ImageKit(
#     private_key="private_29XJfeKMG0/QVEZ3irLC00wIkPw=",
#     public_key="public_0oRATqPOuZr2ZTLGjei5s5yUP+I=",
#     url_endpoint="https://ik.imagekit.io/w9x7ky91w"
# )


# def upload_to_imagekit(file_path, folder="uploads"):

#     with open(file_path, "rb") as f:
#         file_data = base64.b64encode(
#             f.read()
#         ).decode()

#     result = imagekit.upload_file(
#         file=file_data,
#         file_name=os.path.basename(file_path),
#         options={
#             "folder": f"/{folder}"
#         }
#     )

#     return result.response_metadata.raw["url"]

from imagekitio import ImageKit
import os

imagekit = ImageKit(
    private_key="YOUR_PRIVATE_KEY"
)

print("FILES OBJECT:")
print(dir(imagekit.files))

# from imagekitio import ImageKit
# from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions

# import base64
# import os

# imagekit = ImageKit(
#     private_key="private_29XJfeKMG0/QVEZ3irLC00wIkPw="
# )


# def upload_to_imagekit(file_path, folder="uploads"):

#     with open(file_path, "rb") as f:
#         file_data = base64.b64encode(
#             f.read()
#         ).decode()

#     result = imagekit.upload_file(
#         file=file_data,
#         file_name=os.path.basename(file_path),
#         options=UploadFileRequestOptions(
#             folder=f"/{folder}"
#         )
#     )

#     return result.url


from imagekitio import ImageKit
import base64
import os

imagekit = ImageKit(
    private_key="private_29XJfeKMG0/QVEZ3irLC00wIkPw="
)


import os


def upload_to_imagekit(file_path, folder="uploads"):

    with open(file_path, "rb") as f:

        response = imagekit.files.upload(
            file=f,
            file_name=os.path.basename(file_path),
            folder=f"/{folder}"
        )

    return response.url



@app.post("/api/add/sundarikanya")
async def add_video(
    uploader: str = Form(...),
    session_id: str = Form(...),

    title: str = Form(...),
    description: str = Form(...),

    tag: str = Form(...),
    category: str = Form(...),

    location: str = Form(""),
    map_url: str = Form(""),

    opening_days: str = Form(""),
    opening_time: str = Form(""),
    closing_time: str = Form(""),

    indian_ticket: float = Form(0),
    foreigner_ticket: float = Form(0),
    child_ticket: float = Form(0),

    best_time_to_visit: str = Form(""),

    facilities: str = Form(""),

    official_website: str = Form(""),

    thumbnail: UploadFile = File(...),

    video: List[UploadFile] = File(...)
):

    # Session Validation
    if not await is_session_valid(session_id):
        raise HTTPException(
            status_code=401,
            detail="Invalid session"
        )

    # Load Database
    data = await load_data()
    videos = data.get("data", {}).get("data", [])

    # Next ID
    max_id = max(
        [
            int(v["id"])
            for v in videos
            if str(v.get("id", "")).isdigit()
        ] or [0]
    )

    next_id = max_id + 1

    # --------------------------
    # Upload Thumbnail
    # --------------------------

    temp_thumb = (
        f"temp_thumb_"
        f"{datetime.now().timestamp()}_"
        f"{thumbnail.filename}"
    )

    await save_upload_file(
        thumbnail,
        temp_thumb
    )

    try:

        thumb_url = upload_to_imagekit(
            temp_thumb,
            folder="thumbnails"
        )

    finally:

        if os.path.exists(
            temp_thumb
        ):
            os.remove(
                temp_thumb
            )

    # --------------------------
    # Upload Videos
    # --------------------------

    video_urls = []

    for vfile in video:

        temp_vid = (
            f"temp_video_"
            f"{datetime.now().timestamp()}_"
            f"{vfile.filename}"
        )

        await save_upload_file(
            vfile,
            temp_vid
        )

        try:

            uploaded_url = upload_to_imagekit(
                temp_vid,
                folder="videos"
            )

            video_urls.append(
                uploaded_url
            )

        except Exception as e:

            print(
                f"Video Upload Failed: {e}"
            )

        finally:

            if os.path.exists(
                temp_vid
            ):
                os.remove(
                    temp_vid
                )

    # --------------------------
    # Create Record
    # --------------------------

    new_video = {

        "id":
            str(next_id),

        "uploader":
            uploader,

        "title":
            title,

        "description":
            description,

        "thumbnail":
            thumb_url,

        "videourl":
            video_urls,

        "tag":
            [
                t.strip()
                for t in tag.split(",")
                if t.strip()
            ],

        "category":
            [
                c.strip()
                for c in category.split(",")
                if c.strip()
            ],

        "location":
            location,

        "map_url":
            map_url,

        "opening_days":
            [
                d.strip()
                for d in opening_days.split(",")
                if d.strip()
            ],

        "opening_time":
            opening_time,

        "closing_time":
            closing_time,

        "ticket_prices":
            {
                "indian":
                    indian_ticket,

                "foreigner":
                    foreigner_ticket,

                "child":
                    child_ticket
            },

        "best_time_to_visit":
            best_time_to_visit,

        "facilities":
            [
                f.strip()
                for f in facilities.split(",")
                if f.strip()
            ],

        "official_website":
            official_website,

        "timestamp":
            datetime.utcnow().isoformat()
    }

    # Save Record
    videos.append(
        new_video
    )

    data.setdefault(
        "data",
        {}
    )["data"] = videos

    await save_data(
        data
    )

    return {

        "status":
            "success",

        "message":
            "Place added successfully",

        "id":
            new_video["id"],

        "thumbnail_link":
            thumb_url,

        "video_links":
            video_urls,

        "data":
            new_video
    }

# @app.post("/api/add/sundarikanya")
# async def add_video(
#     uploader: str = Form(...),
#     session_id: str = Form(...),
#     title: str = Form(...),
#     description: str = Form(...),
#     tag: str = Form(...),
#     category: str = Form(...),
#     thumbnail: UploadFile = File(...),
#     video: List[UploadFile] = File(...)
#     ):
#     # 1. Session validation
#     if not await is_session_valid(session_id):
#         raise HTTPException(status_code=401, detail="Invalid session")

#     # 2. Load database
#     data = await load_data()
#     videos = data.get("data", {}).get("data", [])

#     # 3. Next ID
#     max_id = max([int(v["id"]) for v in videos if str(v.get("id", "")).isdigit()] or [0])
#     next_id = max_id + 1

#     # 4. Handle thumbnail
#     temp_thumb = f"temp_thumb_{datetime.now().timestamp()}_{thumbnail.filename}"
#     await save_upload_file(thumbnail, temp_thumb)
#     thumb_url = upload_image(temp_thumb)  # keep your existing image upload logic
#     os.remove(temp_thumb)

#     # 5. Handle video uploads
#     video_urls = []
#     for vfile in video:
#         temp_vid = f"temp_video_{datetime.now().timestamp()}_{vfile.filename}"
#         await save_upload_file(vfile, temp_vid)

#         try:
#             # Upload to Catbox account (private)
#             direct_link = upload_to_root(temp_vid)
#             video_urls.append(direct_link)
#         except Exception as e:
#             print(f"❌ Upload failed for {vfile.filename}: {e}")
#             os.remove(temp_vid)
#             continue

#         os.remove(temp_vid)

#     # 6. Create new entry
#     new_video = {
#         "id": str(next_id),
#         "uploader": uploader,
#         "title": title,
#         "description": description,
#         "thumbnail": thumb_url,
#         "videourl": video_urls,
#         "tag": [t.strip() for t in tag.split(",") if t.strip()],
#         "category": [c.strip() for c in category.split(",") if c.strip()],
#         "timestamp": datetime.utcnow().isoformat()
#     }

#     videos.append(new_video)
#     data.setdefault("data", {})["data"] = videos
#     await save_data(data)

#     return {
#         "status": "success",
#         "message": "Video added",
#         "id": new_video["id"],
#         "video_links": video_urls,
#         "thumbnail_link": thumb_url
#     }

@app.get("/api/get/latest")
async def get_all_latest_videos():
    # 1. Load database
    data = await load_data()
    videos = data.get("data", {}).get("data", [])

    if not videos:
        raise HTTPException(status_code=404, detail="No videos found")

    # 2. Sort all videos by ID (numeric, descending → latest first)
    sorted_videos = sorted(videos, key=lambda v: int(v.get("id", 0)), reverse=True)

    return {
        "status": "success",
        "total": len(sorted_videos),
        "data": sorted_videos
    }


import random

@app.get("/api/get/recommended")
async def get_recommended():
    store = await load_data()
    all_entries = store.get("data", {}).get("data", [])

    # 🎲 Pick 15–20 random entries
    sample_size = random.randint(15, 20)
    recommended = random.sample(all_entries, min(sample_size, len(all_entries)))

    return {
        "status": "success",
        "total": len(recommended),
        "data": recommended
    }


@app.get("/api/get/sundarikanya")
async def get_video_by_id(
    id: Optional[str] = Query(None),
    page: int = Query(1, ge=1)
):
    data = (await load_data())["data"]["data"]
    total = len(data)
    
    # ✅ Return specific video by ID
    if id:
        result = next((item for item in data if item["id"] == id), None)  # no zfill
        if not result:
            raise HTTPException(status_code=404, detail=f"Video with ID {id} not found.")
        return result

    # ✅ Pagination logic from end
    per_page = 40
    start = max(total - (page * per_page), 0)
    end = total - ((page - 1) * per_page)
    paginated_data = data[start:end]

    return {
        "status": "success",
        "total": total,
        "page": page,
        "per_page": per_page,
        "data": list(reversed(paginated_data))  # newest first
    }



def clean_split_list(value):
    if isinstance(value, list):
        cleaned = []
        for v in value:
            cleaned.extend([x.strip() for x in v.split(",") if x.strip()])
        return cleaned
    return []


@app.get("/api/get/sundarikanya1")
async def get_sundari_entries(
    category: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(36, ge=1)
):
    store = await load_data()  # ✅ Await async function
    all_entries = store.get("data", {}).get("data", [])

    filtered_entries = []
    for entry in all_entries:
        cat_list = clean_split_list(entry.get("category", []))
        tag_list = clean_split_list(entry.get("tag", []))

        match_category = True
        match_tag = True

        if category:
            match_category = any(c.lower() == category.lower() for c in cat_list)

        if tag:
            match_tag = any(t.lower() == tag.lower() for t in tag_list)

        if match_category and match_tag:
            filtered_entries.append(entry)

    total = len(filtered_entries)

    # ✅ Pagination
    start = (page - 1) * limit
    end = start + limit
    paginated_data = filtered_entries[start:end]

    return {
        "status": "success",
        "filter": {"category": category, "tag": tag},
        "page": page,
        "limit": limit,
        "total": total,
        "data": paginated_data
    }



@app.post("/api/create-account")
def create_account(user: UserCreate):
    data = load_json(ACCOUNTS_FILE)
    if any(u["username"] == user.username for u in data["users"]):
        return {"status": "error", "detail": "Username already exists"}
    hashed = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()
    data["users"].append({"username": user.username, "password": hashed})
    save_json(ACCOUNTS_FILE, data)
    return {"status": "success", "username": user.username}


from datetime import datetime, timedelta
import uuid

SESSION_FILE = "sessions.json"


# Async load_sessions
async def load_sessions():
    try:
        async with aiofiles.open(SESSIONS_FILE, 'r') as f:
            content = await f.read()
            return json.loads(content)
    except FileNotFoundError:
        # If file doesn't exist, initialize with empty structure
        return {"sessions": []}

# Async save_sessions
async def save_sessions(data):
    async with aiofiles.open(SESSIONS_FILE, 'w') as f:
        await f.write(json.dumps(data, indent=2))


@app.post("/api/login")
async def login(user: UserCreate):
    accounts = await load_accounts()
    for account in accounts["users"]:
        if account["username"] == user.username:
            if bcrypt.checkpw(user.password.encode("utf-8"), account["password"].encode("utf-8")):
                # Generate session
                session_id = str(uuid.uuid4())
                expiry_time = (datetime.utcnow() + timedelta(hours=24)).isoformat()

                # Store session
                sessions = await load_sessions()
                sessions["sessions"].append({
                    "username": user.username,
                    "session_id": session_id,
                    "expires_at": expiry_time
                })
                await save_sessions(sessions)

                return {
                    "status": "success",
                    "message": "Login successful",
                    "session_id": session_id,
                    "expires_at": expiry_time
                }

            else:
                raise HTTPException(status_code=401, detail="Incorrect password")

    raise HTTPException(status_code=404, detail="User not found")


@app.get("/api/get/search")
async def search_sundari_entries(
    query: str = Query(..., description="Search by keyword in title, description, tag, or category"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(36, ge=1, le=100, description="Number of items per page"),
):
    data_store = await load_data()  # ✅ Use async version
    all_entries = data_store.get("data", {}).get("data", [])

    query_lower = query.lower()
    filtered_results = []

    for entry in all_entries:
        title = entry.get("title", "").lower()
        description = entry.get("description", "").lower()
        tags = [t.lower() for t in entry.get("tag", [])]
        categories = [c.lower() for c in entry.get("category", [])]

        if (
            query_lower in title or
            query_lower in description or
            any(query_lower in tag for tag in tags) or
            any(query_lower in cat for cat in categories)
        ):
            filtered_results.append(entry)

    # ✅ Pagination logic
    total = len(filtered_results)
    start = (page - 1) * limit
    end = start + limit
    paginated_results = filtered_results[start:end]

    return {
        "status": "success",
        "query": query,
        "page": page,
        "limit": limit,
        "total_results": total,
        "data": paginated_results
    }


@app.post("/api/get/update")
async def update_video(
    id: str = Form(...),

    session_id: str = Form(...),

    uploader: str = Form(...),

    title: str = Form(...),
    description: str = Form(...),

    tag: str = Form(...),
    category: str = Form(...),

    location: str = Form(""),
    map_url: str = Form(""),

    opening_days: str = Form(""),
    opening_time: str = Form(""),
    closing_time: str = Form(""),

    indian_ticket: float = Form(0),
    foreigner_ticket: float = Form(0),
    child_ticket: float = Form(0),

    best_time_to_visit: str = Form(""),

    facilities: str = Form(""),

    official_website: str = Form(""),

    thumbnail: Optional[UploadFile] = File(None),

    video: Optional[List[UploadFile]] = File(None)
    ):
    # ✅ Check session
    if not await is_session_valid(session_id):
        raise HTTPException(status_code=401, detail="Invalid session")

    # ✅ Load DB/data
    data = await load_data()
    videos = data.get("data", {}).get("data", [])
    video_obj = next((v for v in videos if v["id"] == id), None)

    if not video_obj:
        raise HTTPException(status_code=404, detail="Video not found")

    # ✅ Update metadata
    video_obj["uploader"] = uploader
    video_obj["title"] = title
    video_obj["description"] = description
    video_obj["tag"] = [t.strip() for t in tag.split(",") if t.strip()]
    video_obj["category"] = [c.strip() for c in category.split(",") if c.strip()]

    video_obj["location"] = location

    video_obj["map_url"] = map_url

    video_obj["opening_days"] = [
        d.strip()
        for d in opening_days.split(",")
        if d.strip()
    ]

    video_obj["opening_time"] = opening_time

    video_obj["closing_time"] = closing_time

    video_obj["ticket_prices"] = {
        "indian": indian_ticket,
        "foreigner": foreigner_ticket,
        "child": child_ticket
    }

    video_obj["best_time_to_visit"] = best_time_to_visit

    video_obj["facilities"] = [
        f.strip()
        for f in facilities.split(",")
        if f.strip()
    ]

    video_obj["official_website"] = official_website

    # ✅ Thumbnail update
    if thumbnail:
        temp_thumb = f"temp/thumb_{datetime.now().timestamp()}.jpg"
        async with aiofiles.open(temp_thumb, "wb") as f:
            await f.write(await thumbnail.read())
        try:
            # run sync upload in thread
            loop = asyncio.get_running_loop()
            uploaded_thumb = await loop.run_in_executor(None, upload_image, temp_thumb)
            video_obj["thumbnail"] = uploaded_thumb
        finally:
            os.remove(temp_thumb)

    # ✅ Video update
    if video:
        new_video_urls = []
        for vfile in video:
            temp_vid = f"temp/video_{datetime.now().timestamp()}_{vfile.filename}"
            async with aiofiles.open(temp_vid, "wb") as f:
                await f.write(await vfile.read())
            try:
                loop = asyncio.get_running_loop()
                uploaded_vid = await loop.run_in_executor(None, upload_to_imagekit, temp_vid)
                new_video_urls.append(uploaded_vid)
            finally:
                os.remove(temp_vid)

        # ✅ Append new URLs instead of overwriting
        existing_urls = video_obj.get("videourl", [])
        video_obj["videourl"] = existing_urls + new_video_urls

    # ✅ Save changes
    await save_data(data)

    return {"status": "success", "message": "Video updated with fresh links"}


@app.delete("/api/get/delete")
async def delete_video(id: str, session_id: str):
    if not await is_session_valid(session_id):
        raise HTTPException(status_code=401, detail="Invalid session")

    data_store = await load_data()
    all_entries = data_store.get("data", {}).get("data", [])

    entry_to_delete = next((e for e in all_entries if str(e.get("id")) == str(id)), None)
    if not entry_to_delete:
        raise HTTPException(status_code=404, detail="Video not found")

    shared_link = entry_to_delete.get("video_url")  # stored shared link
    if shared_link:
        try:
            dropbox_path = await get_dropbox_path_from_link(shared_link)
            await delete_from_dropbox(dropbox_path)
        except Exception as e:
            print(f"⚠️ Dropbox delete failed: {e}")

    # Remove from local storage
    updated_entries = [e for e in all_entries if str(e.get("id")) != str(id)]
    data_store["data"]["data"] = updated_entries
    await save_data(data_store)

    return {"status": "success", "deleted_id": id}




@app.get("/api/check-session")
def check_session(session_id: str):
    sessions = load_sessions()
    for session in sessions["sessions"]:
        if session["session_id"] == session_id:
            if datetime.utcnow() < datetime.fromisoformat(session["expires_at"]):
                return {"status": "valid", "username": session["username"]}
            else:
                return {"status": "expired"}
    return {"status": "invalid"}
