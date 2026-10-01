import os
import uvicorn
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Import routers from local modules
from mock_vietful import router as vietful_router

load_dotenv()

app = FastAPI(
    title="CDMS - Change Data Management Service",
    description="Prototype Change Data Management Service for tracking and synchronizing inventory data changes.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register VietFul Mock Inventory API router
app.include_router(vietful_router)

@app.get("/", status_code=status.HTTP_200_OK, tags=["System Health"])
def read_root():
    """
    Root endpoint serving basic service description and status details.
    """
    return {
        "service": "Change Data Management Service (CDMS)",
        "status": "running",
        "version": "1.0.0",
        "documentation": "/docs"
    }

@app.get("/health", status_code=status.HTTP_200_OK, tags=["System Health"])
def health_check():
    """
    Health check endpoint utilized by Docker container healthchecks and orchestrators.
    """
    return {
        "status": "healthy",
        "database": "pending_connection"  # Will be dynamically connected in Phase 2
    }

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host=host, port=port, reload=True)
