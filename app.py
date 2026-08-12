import os
import uuid
import random
import asyncio
import aiofiles
import bcrypt

from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import FastAPI, Request, Form, HTTPException, File, UploadFile, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from imagekitio import ImageKit

# MongoDB storage layer (replaces data.json / accounts.json / sessions.json)
from db import (
    load_data,
    get_place,
    add_place,
    update_place,
    delete_place,
    load_accounts,
    add_account,
    find_session,
    create_session,
    init_indexes,
    close_db,
)

# Helpers from your project (keep upload.py in this folder)
from upload import *  # noqa: F401,F403
from upload import upload_to_root, upload_image  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_indexes()
    except Exception as e:
        print(f"WARNING: MongoDB connection issue: {e}")
    yield
    await close_db()


app = FastAPI(lifespan=lifespan)

# Set up templates folder
templates = Jinja2Templates(directory="templates")

# Default page size for every list endpoint.
PAGE_SIZE = 15

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev only; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class UserCreate(BaseModel):
    username: str
    password: str


# -------------------
# ImageKit (thumbnail / video uploads)
# -------------------
IMAGEKIT_PRIVATE_KEY = os.getenv(
    "IMAGEKIT_PRIVATE_KEY",
    "private_29XJfeKMG0/QVEZ3irLC00wIkPw=",  # TODO: move this to .env
)

imagekit = ImageKit(private_key=IMAGEKIT_PRIVATE_KEY)


def upload_to_imagekit(file_path: str, folder: str = "uploads") -> str:
    """Upload a file to ImageKit and return its URL."""
    with open(file_path, "rb") as f:
        response = imagekit.files.upload(
            file=f,
            file_name=os.path.basename(file_path),
            folder=f"/{folder}",
        )
    return response.url


# -------------------
# Sessions
# -------------------
async def is_session_valid(session_id: str) -> bool:
    session = await find_session(session_id)
    if not session:
        return False
    try:
        expires_at = datetime.fromisoformat(session["expires_at"])
    except (KeyError, ValueError, TypeError):
        return False
    return expires_at > datetime.utcnow()


# -------------------
# Pages
# -------------------
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


@app.get("/delete", response_class=HTMLResponse)
async def delete_page(request: Request):
    return templates.TemplateResponse("delete.html", {"request": request})


@app.get("/api/load")
async def get_data():
    return await load_data()


# -------------------
# File upload helpers
# -------------------
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


# -------------------
# POST API to add a place
# -------------------
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
    video: List[UploadFile] = File(...),
):
    # Session validation
    if not await is_session_valid(session_id):
        raise HTTPException(status_code=401, detail="Invalid session")

    # Load database (MongoDB) to compute the next ID
    data = await load_data()
    videos = data.get("data", {}).get("data", [])
    max_id = max(
        [int(v["id"]) for v in videos if str(v.get("id", "")).isdigit()] or [0]
    )
    next_id = max_id + 1

    # Upload thumbnail
    temp_thumb = f"temp_thumb_{datetime.now().timestamp()}_{thumbnail.filename}"
    await save_upload_file(thumbnail, temp_thumb)
    try:
        thumb_url = upload_to_imagekit(temp_thumb, folder="thumbnails")
    finally:
        if os.path.exists(temp_thumb):
            os.remove(temp_thumb)

    # Upload videos
    video_urls = []
    for vfile in video:
        temp_vid = f"temp_video_{datetime.now().timestamp()}_{vfile.filename}"
        await save_upload_file(vfile, temp_vid)
        try:
            uploaded_url = upload_to_imagekit(temp_vid, folder="videos")
            video_urls.append(uploaded_url)
        except Exception as e:
            print(f"Video Upload Failed: {e}")
        finally:
            if os.path.exists(temp_vid):
                os.remove(temp_vid)

    # Create record
    new_video = {
        "id": str(next_id),
        "uploader": uploader,
        "title": title,
        "description": description,
        "thumbnail": thumb_url,
        "videourl": video_urls,
        "tag": [t.strip() for t in tag.split(",") if t.strip()],
        "category": [c.strip() for c in category.split(",") if c.strip()],
        "location": location,
        "map_url": map_url,
        "opening_days": [d.strip() for d in opening_days.split(",") if d.strip()],
        "opening_time": opening_time,
        "closing_time": closing_time,
        "ticket_prices": {
            "indian": indian_ticket,
            "foreigner": foreigner_ticket,
            "child": child_ticket,
        },
        "best_time_to_visit": best_time_to_visit,
        "facilities": [f.strip() for f in facilities.split(",") if f.strip()],
        "official_website": official_website,
        "timestamp": datetime.utcnow().isoformat(),
    }

    # Save to MongoDB
    await add_place(new_video)

    return {
        "status": "success",
        "message": "Place added successfully",
        "id": new_video["id"],
        "thumbnail_link": thumb_url,
        "video_links": video_urls,
        "data": new_video,
    }


# -------------------
# Read APIs
# -------------------
@app.get("/api/get/latest")
async def get_all_latest_videos(
    page: int = Query(1, ge=1),
    limit: int = Query(PAGE_SIZE, ge=1, le=100),
):
    data = await load_data()
    videos = data.get("data", {}).get("data", [])
    if not videos:
        raise HTTPException(status_code=404, detail="No videos found")
    sorted_videos = sorted(videos, key=lambda v: int(v.get("id", 0)), reverse=True)
    start = (page - 1) * limit
    end = start + limit
    return {
        "status": "success",
        "page": page,
        "limit": limit,
        "total": len(sorted_videos),
        "data": sorted_videos[start:end],
    }


@app.get("/api/get/recommended")
async def get_recommended(
    page: int = Query(1, ge=1),
    limit: int = Query(PAGE_SIZE, ge=1, le=100),
):
    store = await load_data()
    all_entries = store.get("data", {}).get("data", [])
    total = len(all_entries)

    # Shuffle the whole list once, then paginate (15 per page by default)
    shuffled = random.sample(all_entries, total)
    start = (page - 1) * limit
    end = start + limit

    return {
        "status": "success",
        "page": page,
        "limit": limit,
        "total": total,
        "data": shuffled[start:end],
    }


@app.get("/api/get/sundarikanya")
async def get_video_by_id(
    id: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
):
    data = (await load_data())["data"]["data"]
    total = len(data)

    # Return specific video by ID
    if id:
        result = next((item for item in data if item["id"] == id), None)
        if not result:
            raise HTTPException(status_code=404, detail=f"Video with ID {id} not found.")
        return result

    # Pagination logic from the end (newest first)
    per_page = PAGE_SIZE
    start = max(total - (page * per_page), 0)
    end = total - ((page - 1) * per_page)
    paginated_data = data[start:end]

    return {
        "status": "success",
        "total": total,
        "page": page,
        "per_page": per_page,
        "data": list(reversed(paginated_data)),
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
    limit: int = Query(PAGE_SIZE, ge=1),
):
    store = await load_data()
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
    start = (page - 1) * limit
    end = start + limit
    paginated_data = filtered_entries[start:end]

    return {
        "status": "success",
        "filter": {"category": category, "tag": tag},
        "page": page,
        "limit": limit,
        "total": total,
        "data": paginated_data,
    }


@app.get("/api/get/search")
async def search_sundari_entries(
    query: str = Query(..., description="Search by keyword in title, description, tag, or category"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(PAGE_SIZE, ge=1, le=100, description="Number of items per page"),
):
    data_store = await load_data()
    all_entries = data_store.get("data", {}).get("data", [])

    query_lower = query.lower()
    filtered_results = []

    for entry in all_entries:
        title = entry.get("title", "").lower()
        description = entry.get("description", "").lower()
        tags = [t.lower() for t in entry.get("tag", [])]
        categories = [c.lower() for c in entry.get("category", [])]

        if (
            query_lower in title
            or query_lower in description
            or any(query_lower in tag for tag in tags)
            or any(query_lower in cat for cat in categories)
        ):
            filtered_results.append(entry)

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
        "data": paginated_results,
    }


# -------------------
# Accounts
# -------------------
@app.post("/api/create-account")
async def create_account(user: UserCreate):
    accounts = await load_accounts()
    if any(u["username"] == user.username for u in accounts["users"]):
        return {"status": "error", "detail": "Username already exists"}
    hashed = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()
    await add_account({"username": user.username, "password": hashed})
    return {"status": "success", "username": user.username}


@app.post("/api/login")
async def login(user: UserCreate):
    accounts = await load_accounts()
    for account in accounts["users"]:
        if account["username"] == user.username:
            if bcrypt.checkpw(user.password.encode("utf-8"), account["password"].encode("utf-8")):
                # Generate session
                session_id = str(uuid.uuid4())
                expiry_time = (datetime.utcnow() + timedelta(hours=24)).isoformat()
                await create_session(
                    {
                        "username": user.username,
                        "session_id": session_id,
                        "expires_at": expiry_time,
                    }
                )
                return {
                    "status": "success",
                    "message": "Login successful",
                    "session_id": session_id,
                    "expires_at": expiry_time,
                }
            else:
                raise HTTPException(status_code=401, detail="Incorrect password")
    raise HTTPException(status_code=404, detail="User not found")


@app.get("/api/session-info")
async def session_info(session_id: str):
    session = await find_session(session_id)
    if session:
        if datetime.utcnow() < datetime.fromisoformat(session["expires_at"]):
            return {"status": "success", "username": session["username"]}
    return {"status": "error", "detail": "Session invalid or expired"}


@app.get("/api/check-session")
async def check_session(session_id: str):
    session = await find_session(session_id)
    if not session:
        return {"status": "invalid"}
    if datetime.utcnow() < datetime.fromisoformat(session["expires_at"]):
        return {"status": "valid", "username": session["username"]}
    return {"status": "expired"}


# -------------------
# Update place
# -------------------
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
    video: Optional[List[UploadFile]] = File(None),
):
    # Check session
    if not await is_session_valid(session_id):
        raise HTTPException(status_code=401, detail="Invalid session")

    # Fetch the entry from MongoDB
    video_obj = await get_place(id)
    if not video_obj:
        raise HTTPException(status_code=404, detail="Video not found")

    # Update metadata
    video_obj["uploader"] = uploader
    video_obj["title"] = title
    video_obj["description"] = description
    video_obj["tag"] = [t.strip() for t in tag.split(",") if t.strip()]
    video_obj["category"] = [c.strip() for c in category.split(",") if c.strip()]
    video_obj["location"] = location
    video_obj["map_url"] = map_url
    video_obj["opening_days"] = [d.strip() for d in opening_days.split(",") if d.strip()]
    video_obj["opening_time"] = opening_time
    video_obj["closing_time"] = closing_time
    video_obj["ticket_prices"] = {
        "indian": indian_ticket,
        "foreigner": foreigner_ticket,
        "child": child_ticket,
    }
    video_obj["best_time_to_visit"] = best_time_to_visit
    video_obj["facilities"] = [f.strip() for f in facilities.split(",") if f.strip()]
    video_obj["official_website"] = official_website

    # Thumbnail update
    if thumbnail:
        temp_thumb = f"temp_thumb_{datetime.now().timestamp()}.jpg"
        async with aiofiles.open(temp_thumb, "wb") as f:
            await f.write(await thumbnail.read())
        try:
            loop = asyncio.get_running_loop()
            uploaded_thumb = await loop.run_in_executor(None, upload_image, temp_thumb)
            video_obj["thumbnail"] = uploaded_thumb
        finally:
            if os.path.exists(temp_thumb):
                os.remove(temp_thumb)

    # Video update - append new URLs instead of overwriting
    if video:
        new_video_urls = []
        for vfile in video:
            temp_vid = f"temp_video_{datetime.now().timestamp()}_{vfile.filename}"
            async with aiofiles.open(temp_vid, "wb") as f:
                await f.write(await vfile.read())
            try:
                loop = asyncio.get_running_loop()
                uploaded_vid = await loop.run_in_executor(None, upload_to_imagekit, temp_vid)
                new_video_urls.append(uploaded_vid)
            finally:
                if os.path.exists(temp_vid):
                    os.remove(temp_vid)

        existing_urls = video_obj.get("videourl", [])
        video_obj["videourl"] = existing_urls + new_video_urls

    # Save changes to MongoDB
    await update_place(video_obj)

    return {"status": "success", "message": "Video updated with fresh links"}


# -------------------
# Delete place
# -------------------
@app.delete("/api/get/delete")
async def delete_video(id: str, session_id: str):
    if not await is_session_valid(session_id):
        raise HTTPException(status_code=401, detail="Invalid session")

    entry_to_delete = await get_place(id)
    if not entry_to_delete:
        raise HTTPException(status_code=404, detail="Video not found")

    shared_link = entry_to_delete.get("video_url")
    if shared_link:
        try:
            dropbox_path = await get_dropbox_path_from_link(shared_link)
            await delete_from_dropbox(dropbox_path)
        except Exception as e:
            print(f"Dropbox delete failed: {e}")

    # Remove from MongoDB
    await delete_place(id)

    return {"status": "success", "deleted_id": id}


# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
