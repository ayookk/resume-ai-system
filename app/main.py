from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI Resume & Recruitment System",
    description="AI-powered resume optimization and job matching platform",
    version="0.1.0"
)

# CORS middleware (allows frontend to talk to backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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