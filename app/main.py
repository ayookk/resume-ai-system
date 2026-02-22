from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from app.api import resumes, jobs

app = FastAPI(
    title="AI Resume & Recruitment System",
    description="AI-powered resume optimization and job matching platform with hiring type detection",
    version="0.2.0"
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

@app.get("/")
def root():
    return {
        "message": "AI Resume & Recruitment System API",
        "status": "running",
        "version": "0.2.0",
        "features": [
            "Resume parsing and ATS scoring",
            "Advanced hiring type detection (Active vs Pipeline)",
            "Application strategy recommendations"
        ],
        "docs": "http://localhost:8000/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)