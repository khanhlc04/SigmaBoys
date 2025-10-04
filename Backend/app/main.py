from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import environment, cache
from app.services.database import db_service

# Khởi tạo app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API tổng hợp dữ liệu môi trường từ nhiều nguồn"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    environment.router,
    prefix=settings.API_V1_PREFIX,
    tags=["Environment"]
)

app.include_router(
    cache.router,
    prefix=settings.API_V1_PREFIX,
    tags=["Cache"]
)

# MongoDB connection events
@app.on_event("startup")
async def startup_event():
    """Connect to MongoDB on startup"""
    await db_service.connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_event():
    """Disconnect from MongoDB on shutdown"""
    await db_service.close_mongo_connection()

@app.get("/")
async def root():
    return {
        "message": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Run app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )