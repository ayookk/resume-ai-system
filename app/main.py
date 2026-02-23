from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Import database and models
from app.database import engine, Base
from app.models import Resume, JobAnalysis

# Import routers
from app.api import resumes, jobs, cover_letters, matching


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager - runs on startup and shutdown
    Creates database tables on startup
    """
    # Startup: Create all database tables
    print("🗄️  Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized!")
    
    yield
    
    # Shutdown: cleanup if needed
    print("👋 Shutting down...")


app = FastAPI(
    title="AI Resume & Recruitment System",
    description="AI-powered resume optimization and job matching platform with hiring type detection",
    version="0.2.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(resumes.router, prefix="/api/v1/resumes", tags=["Resumes"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["Jobs"])
app.include_router(cover_letters.router, prefix="/api/v1/cover-letters", tags=["Cover Letters"])
app.include_router(matching.router, prefix="/api/v1/matching", tags=["Semantic Matching"])

@app.get("/")
def root():
    return {
        "message": "AI Resume & Recruitment System API",
        "status": "running",
        "version": "0.2.0",
        "features": [
            "Resume parsing and ATS scoring",
            "Advanced hiring type detection (Active vs Pipeline)",
            "Application strategy recommendations",
            "Database storage for resumes and job analyses"
        ],
        "docs": "http://localhost:8000/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)