# 🚀 AI Resume & Recruitment Optimization System

An AI-powered platform that helps job seekers optimize their resumes and identify genuine hiring opportunities vs. resume harvesting schemes.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [Roadmap](#roadmap)
- [Contact](#contact)

---

## ✨ Features

### 🎯 Resume Analysis & Optimization
- **PDF Parsing**: Extracts text, contact info, skills, and education from resume PDFs
- **ATS Scoring**: Calculates resume compatibility score (0-100) based on industry standards
- **Skill Extraction**: Automatically identifies 53+ technical skills including Python, SQL, AWS, ML frameworks
- **Personalized Suggestions**: Provides actionable recommendations to improve resume effectiveness

### 🔍 Advanced Hiring Type Detection ⭐ (Unique Feature)
Identifies whether a job posting is **Active Hiring** or **Pipeline/Evergreen** (resume harvesting) by analyzing:

- **Requisition ID Patterns**: Detects generic IDs like "EVERGREEN_ENG_2024"
- **Location Blast Detection**: Flags postings in 5+ cities as likely resume collection
- **Posting Age Analysis**: Identifies stale postings (45+ days) that may be inactive
- **Job Specificity Scoring**: Analyzes presence of manager names, salary ranges, team details
- **Application Strategy**: Provides tailored advice based on hiring type

**Why This Matters**: Most job seekers waste time applying to fake postings. This feature helps candidates focus on real opportunities.

### 💾 Database Persistence
- All resumes and job analyses saved to SQLite database
- Complete CRUD operations via REST API
- Pagination support for listing records
- Data persists between server restarts

### 📊 RESTful API
- Interactive API documentation at `/docs` (Swagger UI)
- Request/response validation with Pydantic
- Error handling and status codes
- CORS enabled for frontend integration

---

## 🛠️ Tech Stack

**Backend Framework:**
- FastAPI 0.109 - High-performance async API framework
- Uvicorn - ASGI server with auto-reload

**AI/ML Libraries:**
- PyPDF2 - PDF text extraction
- Sentence Transformers - Embeddings (ready for semantic search)
- LangChain - LLM orchestration framework
- OpenAI SDK - AI content generation (ready for integration)

**Database:**
- SQLAlchemy 2.0 - ORM for database operations
- SQLite - Lightweight database (upgradeable to PostgreSQL)

**Data Processing:**
- Pandas, NumPy - Data manipulation
- Python Regex - Pattern matching for skill/contact extraction

**Development Tools:**
- Python-dotenv - Environment variable management
- Pydantic - Data validation
- Git - Version control

---

## 📦 Installation

### Prerequisites
- Python 3.11+ (tested on 3.13)
- Git

### Setup

1. **Clone the repository:**
```bash
git clone https://github.com/YOUR_USERNAME/resume-ai-system.git
cd resume-ai-system
```

2. **Create virtual environment:**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
```bash
# Copy .env.example to .env
cp .env.example .env

# Edit .env and add your API keys (optional for basic features)
```

5. **Run the application:**
```bash
uvicorn app.main:app --reload
```

6. **Access the API:**
- API Docs: http://localhost:8000/docs
- API: http://localhost:8000

---

## 🚀 Usage

### Upload and Analyze a Resume

**Via API Documentation (Swagger UI):**
1. Go to http://localhost:8000/docs
2. Navigate to **POST /api/v1/resumes/upload**
3. Click "Try it out"
4. Upload your PDF resume
5. View ATS score, extracted skills, and suggestions

**Via cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/resumes/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_resume.pdf"
```

### Analyze a Job Posting

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/jobs/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "Senior Engineer - Join our talent pool! Multiple locations. Email careers@company.com. Requisition: EVERGREEN_2024",
    "posted_date": "2023-06-01"
  }'
```

**Example Response:**
```json
{
  "status": "success",
  "analysis": {
    "hiring_type": "🟡 Pipeline/Evergreen",
    "confidence": "High",
    "active_score": 2,
    "passive_score": 15,
    "insights": [
      "🚩 Found 8 cities and 2 multi-location keywords",
      "🚩 Posting is 996 days old (likely stale)",
      "⚠️ Low specificity - vague job description"
    ],
    "application_strategy": [
      "⏳ Set expectations for slow/no response",
      "🤝 Try to network with employees instead",
      "🔍 Look for actual active roles at this company"
    ]
  }
}
```

---

## 📡 API Endpoints

### Resume Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/resumes/upload` | Upload and parse resume PDF |
| GET | `/api/v1/resumes/` | List all resumes (paginated) |
| GET | `/api/v1/resumes/{id}` | Get specific resume by ID |
| DELETE | `/api/v1/resumes/{id}` | Delete resume |

### Job Analysis Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/jobs/analyze` | Analyze job posting for hiring type |
| GET | `/api/v1/jobs/` | List all job analyses (paginated) |
| GET | `/api/v1/jobs/{id}` | Get specific analysis by ID |

### Utility Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint with API info |
| GET | `/health` | Health check |
| GET | `/docs` | Interactive API documentation |

---

## 📁 Project Structure
```
resume-ai-system/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── database.py             # Database configuration
│   │
│   ├── api/                    # API endpoints
│   │   ├── __init__.py
│   │   ├── resumes.py          # Resume CRUD operations
│   │   └── jobs.py             # Job analysis operations
│   │
│   ├── models/                 # Database models
│   │   ├── __init__.py
│   │   ├── resume.py           # Resume ORM model
│   │   └── job_analysis.py     # Job analysis ORM model
│   │
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── resume_parser.py    # PDF parsing & ATS scoring
│   │   └── hiring_detector.py  # Hiring type detection
│   │
│   └── schemas/                # Pydantic models (future)
│
├── uploads/                    # Uploaded resume files
├── resume_ai.db                # SQLite database
├── .env                        # Environment variables (not in repo)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🗺️ Roadmap

### ✅ Completed (v0.2.0)
- Resume PDF parsing and ATS scoring
- Advanced hiring type detection (Active vs Pipeline)
- Database persistence with SQLAlchemy
- RESTful API with complete CRUD operations
- Interactive API documentation

### 🚧 In Progress (v0.3.0)
- [ ] User authentication and authorization
- [ ] Streamlit frontend UI
- [ ] Unit tests and integration tests
- [ ] Enhanced skill extraction with NLP

### 🔮 Future Enhancements (v1.0.0+)
- [ ] Semantic job matching with vector embeddings
- [ ] AI-powered cover letter generation
- [ ] Resume-to-job match scoring
- [ ] PostgreSQL database upgrade
- [ ] React frontend with TypeScript
- [ ] Email notifications for application tracking
- [ ] Cloud deployment (Google Cloud Run / Railway)
- [ ] Analytics dashboard for job market insights

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👤 Contact

**Kervin Benoit**

- 📧 Email: Benoit.kervin@gmail.com
- 💼 LinkedIn: [Your LinkedIn](linkedin.com/in/kervin-benoit-592b52126/)
- 🐙 GitHub: [Your GitHub](https://github.com/ayookk)
- 📍 Location: Greenacres, Florida

---

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Inspired by the need to help job seekers avoid resume harvesting schemes
- Research on hiring patterns from Indeed, LinkedIn, and Reddit communities

---

**⭐ If you find this project helpful, please consider giving it a star!**