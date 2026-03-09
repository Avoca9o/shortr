from fastapi import FastAPI, Depends, HTTPException, Header
from typing import Optional
from contextlib import asynccontextmanager
from database import get_db, init_models, close_db, add_link_db, get_link_db, delete_link_db, delete_link_without_user_db, update_link_db, increase_link_access_count_db, get_link_by_original_url_db, create_user_db, get_user_by_username_db, get_top_10_links_db
from cache import cache_client
from generator import generate_short_url
from datetime import datetime, timedelta
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import os
from auth import hash_password, create_access_token, verify_password, decode_access_token
from fastapi import BackgroundTasks
from database import AsyncSessionLocal
from qr_generator import generate_qr_code

load_dotenv()

BASE_URL = os.getenv("BASE_URL")


def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = authorization.removeprefix("Bearer ")
    try:
        payload = decode_access_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload["user_id"]

def get_current_user_optional(authorization: Optional[str] = Header(None)):
    if not authorization:
        return None
    if not authorization.startswith("Bearer "):
        return None
    token = authorization.removeprefix("Bearer ")
    try:
        payload = decode_access_token(token)
    except Exception:
        return None
    return payload["user_id"]

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("App starting up")
    await init_models()
    yield
    print("App shutting down")
    await close_db()

app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.post("/links/shorten")
async def shorten_link(url: str, custom_alias: str = None, qrcode: bool = False, expires_at: datetime = None, db=Depends(get_db), current_user=Depends(get_current_user_optional)):
    if custom_alias:
        short_url = custom_alias
    else:
        short_url = generate_short_url()
    if not expires_at:
        expires_at = datetime.now() + timedelta(days=1)
    try:
        await add_link_db(db, url, short_url, expires_at, current_user)
    except Exception as e:
        return {"error": "Failed to add shortened link to database", "detail": str(e)}
    try:
        if expires_at:
            ttl = int((expires_at - datetime.now()).total_seconds())
        await cache_client.set(short_url, url, ex=ttl)
    except Exception as e:
        return {"error": "Failed to cache shortened link", "detail": str(e)}
    if qrcode:
        return generate_qr_code(BASE_URL + '/links/' + short_url)
    return {"short_url": BASE_URL + '/links/' + short_url}

@app.get("/links/top-10")
async def get_top_10_links(db=Depends(get_db)):
    try:
        links = await get_top_10_links_db(db)
    except Exception as e:
        print(f"Error getting top 10 links from database: {e}")
        return {"error": "Failed to get top 10 links from database", "detail": str(e)}
    return {
        "links": links
    }


@app.get("/links/search")
async def search_link(original_url: str, db=Depends(get_db)):
    try:
        link = await get_link_by_original_url_db(db, original_url)
    except Exception as e:
        print(f"Error getting link from database: {e}")
        return {"error": "Failed to get link from database", "detail": str(e)}
    return {
        "short_url": BASE_URL + '/links/' + link.short_url
    }


@app.get("/links/{short_url}")
async def redirect_to_original_url(short_url: str, background_tasks: BackgroundTasks, db=Depends(get_db)):
    background_tasks.add_task(increment_access_count, short_url)

    original_url = None
    try:
        original_url = await cache_client.get(short_url)
    except Exception as e:
        print(f"Error getting link from cache: {e}")
        return {"error": "Failed to get link from cache", "detail": str(e)}
    if original_url:
        print(f"Link found in cache, redirecting to {original_url}")
        return RedirectResponse(url=original_url)

    print(f"Link not found in cache, getting from database")
    link = None
    try:
        link = await get_link_db(db, short_url)
    except Exception as e:
        print(f"Error getting link from database: {e}")
        return {"error": "Failed to get link from database", "detail": str(e)}
    if not link:
        return {"error": "Link not found"}
    original_url = link.original_url

    if link.expires_at and link.expires_at < datetime.now():
        try:
            await delete_link_without_user_db(db, short_url)
            await cache_client.delete(short_url)
        except Exception as e:
            print(f"Error deleting link from database and cache: {e}")
            return {"error": "Failed to delete link from database and cache", "detail": str(e)}
        return {"error": "Link expired"}
    return RedirectResponse(url=original_url)

@app.delete("/links/{short_url}")
async def delete_link(short_url: str, db=Depends(get_db), current_user=Depends(get_current_user)):
    try:
        await delete_link_db(db, current_user, short_url)
    except Exception as e:
        print(f"Error deleting link from database: {e}")
        return {"error": "Failed to delete link from database", "detail": str(e)}
    try:
        await cache_client.delete(short_url)
    except Exception as e:
        print(f"Error deleting link from cache: {e}")
        return {"error": "Failed to delete link from cache", "detail": str(e)}
    return {"message": "Link deleted successfully"}

@app.put("/links/{short_url}")
async def update_link(short_url: str, url: str, db=Depends(get_db), current_user=Depends(get_current_user)):
    try:
        await update_link_db(db, current_user, short_url, url)
    except Exception as e:
        print(f"Error updating link in database: {e}")
        return {"error": "Failed to update link in database", "detail": str(e)}
    try:
        await cache_client.set(short_url, url)
    except Exception as e:
        print(f"Error updating link in cache: {e}")
        return {"error": "Failed to update link in cache", "detail": str(e)}
    return {"message": "Link updated successfully"}

@app.get("/links/{short_url}/stats")
async def get_link_stats(short_url: str, db=Depends(get_db)):
    try:
        link = await get_link_db(db, short_url)
    except Exception as e:
        print(f"Error getting link from database: {e}")
        return {"error": "Failed to get link from database", "detail": str(e)}
    if not link:
        return {"error": "Link not found"}
    return {
        "original_url": link.original_url,
        "created_at": link.created_at,
        "access_count": link.access_count,
        "last_accessed_at": link.last_accessed_at
    }

@app.post("/auth/register")
async def register(username: str, password: str, db=Depends(get_db)):
    try:
        hashed_password = hash_password(password)
        await create_user_db(db, username, hashed_password)
    except Exception as e:
        print(f"Error creating user in database: {e}")
        return {"error": "Failed to create user in database", "detail": str(e)}
    return {"message": "User created successfully"}

@app.post("/auth/login")
async def login(username: str, password: str, db=Depends(get_db)):
    try:
        user = await get_user_by_username_db(db, username)
    except Exception as e:
        print(f"Error getting user from database: {e}")
        return {"error": "Failed to get user from database", "detail": str(e)}
    if not user:
        return {"error": "Invalid username or password"}
    if not verify_password(password, user.hashed_password):
        return {"error": "Invalid username or password"}
    return {"access_token": create_access_token({"user_id": user.id})}

async def increment_access_count(short_url: str):
    async with AsyncSessionLocal() as db:
        try:
            await increase_link_access_count_db(db, short_url)
        except Exception as e:
            print(f"Error increasing link access count in database: {e}")
