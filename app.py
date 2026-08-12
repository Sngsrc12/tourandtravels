"""
Public read-only API (deployed on Render/Vercel via uvicorn app:app).

All data comes from MongoDB Atlas (MyTraveldata -> Data collection) via db.py.
All list endpoints paginate 15 items per page. Reads are served from an
in-process cache in db.py and tagged with a short Cache-Control header, so
repeated / concurrent requests are fast and light on Atlas.
"""

import random

from typing import List, Optional

from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

# MongoDB storage layer (MyTraveldata -> Data collection)
from db import load_data

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

# Default page size for every list endpoint.
PAGE_SIZE = 15

# Public read responses can be cached by browsers/proxies for a short time
# (kept in sync with the in-process cache TTL in db.py).
CACHE_MAX_AGE = 60


def cached_json(content: dict):
    """Return a JSON response with a short Cache-Control header."""
    return JSONResponse(
        content=content,
        headers={"Cache-Control": f"public, max-age={CACHE_MAX_AGE}"},
    )


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
    return cached_json(await load_data())


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

    return cached_json({
        "status": "success",
        "total": total,
        "page": page,
        "per_page": per_page,
        "data": list(reversed(paginated_data)),
    })


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

    return cached_json({
        "status": "success",
        "filter": {"category": category, "tag": tag},
        "page": page,
        "limit": limit,
        "total": total,
        "data": paginated_data,
    })


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

    return cached_json({
        "status": "success",
        "query": query,
        "page": page,
        "limit": limit,
        "total_results": total,
        "data": paginated_results,
    })


@app.get("/api/get/bestcategory")
async def get_best_category():
    data_store = await load_data()
    all_entries = data_store.get("data", {}).get("data", [])

    category_counter = {}

    for entry in all_entries:
        categories = entry.get("category", [])
        for cat in categories:
            cat_clean = cat.strip().lower()
            if cat_clean:
                category_counter[cat_clean] = category_counter.get(cat_clean, 0) + 1

    # Sort by frequency descending
    sorted_categories = sorted(category_counter.items(), key=lambda x: x[1], reverse=True)

    best_categories = [{"category": cat, "count": count} for cat, count in sorted_categories]

    return cached_json({
        "status": "success",
        "total_categories": len(best_categories),
        "best_categories": best_categories,
    })


@app.get("/api/get/atest")
async def get_all_latest_videos(
    page: int = Query(1, ge=1),
    limit: int = Query(PAGE_SIZE, ge=1),
):
    # Load database from MongoDB
    data = await load_data()
    videos = data.get("data", {}).get("data", [])

    if not videos:
        raise HTTPException(status_code=404, detail="No videos found")

    # Sort videos by ID (numeric, descending -> latest first)
    sorted_videos = sorted(videos, key=lambda v: int(v.get("id", 0)), reverse=True)

    # Pagination logic
    start = (page - 1) * limit
    end = start + limit
    paginated_videos = sorted_videos[start:end]

    return cached_json({
        "status": "success",
        "page": page,
        "limit": limit,
        "total": len(sorted_videos),
        "data": paginated_videos,
    })


@app.get("/api/get/recommended")
async def get_recommended(
    page: int = Query(1, ge=1),
    limit: int = Query(PAGE_SIZE, ge=1, le=100),
):
    store = await load_data()
    all_entries = store.get("data", {}).get("data", [])

    # Shuffle the whole list once, then paginate (15 per page by default)
    shuffled = random.sample(all_entries, len(all_entries))

    total = len(all_entries)
    start = (page - 1) * limit
    end = start + limit
    paginated = shuffled[start:end]

    return cached_json({
        "status": "success",
        "page": page,
        "limit": limit,
        "total": total,
        "data": paginated,
    })
