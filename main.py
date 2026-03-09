from fastapi import FastAPI, Depends
from sqlalchemy import text
from database import get_db
from cache import cache_client

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get("/db")
async def db(db=Depends(get_db)):
    result = await db.execute(text("SELECT 'Hello from database!'"))
    return {"message": result.scalar()}

@app.get("/redis-ping")
async def redis_ping():
    try:
        pong = await cache_client.ping()
        return {"status": "ok", "pong": pong}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
