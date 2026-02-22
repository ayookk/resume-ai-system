from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import the resume router
from app.api import resumes

app = FastAPI(
    title="AI Resume & Recruitment System",
    description="AI-powered resume optimization and job matching platform",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the resume router
app.include_router(resumes.router, prefix="/api/v1/resumes", tags=["Resumes"])

@app.get("/")
def root():
    return {
        "message": "AI Resume & Recruitment System API",
        "status": "running",
        "version": "0.1.0",
        "docs": "http://localhost:8000/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)