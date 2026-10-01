from fastapi import FastAPI, Response
from contextlib import asynccontextmanager
from app.db import init_db, check_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello, FastAPI!"}


@app.get("/health")
async def health_check(response: Response):
    ok = check_db()
    response.status_code = 200 if ok else 503
    return {"status": "healthy" if ok else "unhealthy"}

