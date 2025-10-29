"""
KIVerdienst v2 - FastAPI Backend
Main application entry point
"""
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from database import engine, Base, check_db_connection

# Import routes
from routes import setup, brands, system, debug

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info("Starting KIVerdienst v2 Backend...")
    
    # Check database connection
    db_ok, db_msg = check_db_connection()
    if db_ok:
        logger.info(f"✓ {db_msg}")
    else:
        logger.error(f"✗ {db_msg}")
    
    logger.info("Backend is ready!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down KIVerdienst v2 Backend...")


# Create FastAPI app
app = FastAPI(
    title="KIVerdienst v2 API",
    description="Autonomous TikTok Content Generation System",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS configuration
allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:5000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if os.getenv("DEBUG") == "true" else "An error occurred"
        }
    )


# Health check endpoint
@app.get("/api/health")
async def health_check():
    """
    Health check endpoint
    Returns the status of the API and database
    """
    db_ok, db_msg = check_db_connection()
    
    return {
        "status": "ok" if db_ok else "degraded",
        "api": "running",
        "database": db_msg,
        "version": "2.0.0"
    }


# Root endpoint
@app.get("/api")
async def root():
    """Root API endpoint"""
    return {
        "name": "KIVerdienst v2 API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }


# Include routers
app.include_router(setup.router, prefix="/api/setup", tags=["Setup"])
app.include_router(brands.router, prefix="/api/brands", tags=["Brands"])
app.include_router(system.router, prefix="/api/system", tags=["System"])
app.include_router(debug.router, prefix="/api/debug", tags=["Debug"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("BACKEND_PORT", 8000)),
        reload=os.getenv("DEBUG", "false").lower() == "true"
    )
