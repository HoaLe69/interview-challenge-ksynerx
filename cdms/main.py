from fastapi import FastAPI

app = FastAPI(
    titlej="FastAPI Demo",
    description="My first FastAPI application",
    version="1.0.0"
)


@app.get("/")
async def root():
    return {"message": "Hello, FastAPI!"}


@app.get("health")
async def health_check():
    return {"status": "ok"}

