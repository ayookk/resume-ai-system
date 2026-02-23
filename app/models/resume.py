"""
Resume database model
"""
from sqlalchemy import Column, String, Float, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base
import uuid


class Resume(Base):
    __tablename__ = "resumes"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # File information
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    
    # Parsed data
    raw_text = Column(Text)
    email = Column(String)
    phone = Column(String)
    skills = Column(JSON)  # List of skills
    education = Column(JSON)  # List of education entries
    word_count = Column(Float)
    
    # Analysis
    ats_score = Column(Float)
    suggestions = Column(JSON)  # List of suggestions
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "resume_id": self.id,
            "original_filename": self.original_filename,
            "file_path": self.file_path,
            "parsed_data": {
                "raw_text": self.raw_text,
                "email": self.email,
                "phone": self.phone,
                "skills": self.skills,
                "education": self.education,
                "word_count": self.word_count
            },
            "ats_score": self.ats_score,
            "suggestions": self.suggestions,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }