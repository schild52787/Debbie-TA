"""Main FastAPI application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
from app.database import init_db

# Import routers
from app.api import clients, deals

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Travel Agent Assistant API for managing clients, itineraries, disputes, and travel deals",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print(f"Starting {settings.APP_NAME} v{settings.VERSION}")
    # Database will be initialized via Alembic migrations
    # Uncomment below for quick testing without Alembic
    # init_db()


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print(f"Shutting down {settings.APP_NAME}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.VERSION,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.VERSION,
    }


# Include routers
app.include_router(clients.router, prefix="/api/clients", tags=["Clients"])
app.include_router(deals.router, prefix="/api/deals", tags=["Deals"])
# Additional routers can be added as needed:
# app.include_router(itineraries.router, prefix="/api/itineraries", tags=["Itineraries"])
# app.include_router(disputes.router, prefix="/api/disputes", tags=["Disputes"])
