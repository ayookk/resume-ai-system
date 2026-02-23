"""
Semantic Job Matching using Sentence Transformers
Uses ML embeddings to find semantic similarity between resumes and jobs
"""
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import Dict, List, Tuple
import os


class SemanticMatcher:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the semantic matcher with a pre-trained model
        
        Args:
            model_name: Hugging Face model name (all-MiniLM-L6-v2 is fast and good)
        """
        print(f"🔄 Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        print(f"✅ Model loaded successfully!")
        
        # Cache for embeddings (in production, use Redis or database)
        self.embedding_cache = {}
    
    def get_embedding(self, text: str, cache_key: str = None) -> np.ndarray:
        """
        Get embedding for text (with optional caching)
        
        Args:
            text: Text to embed
            cache_key: Optional key for caching
            
        Returns:
            Embedding vector
        """
        if cache_key and cache_key in self.embedding_cache:
            return self.embedding_cache[cache_key]
        
        embedding = self.model.encode(text, convert_to_numpy=True)
        
        if cache_key:
            self.embedding_cache[cache_key] = embedding
        
        return embedding
    
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score (0-100)
        """
        # Cosine similarity
        similarity = np.dot(embedding1, embedding2) / (
            np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
        )
        
        # Convert to percentage (0-100)
        return float(similarity * 100)
    
    def match_resume_to_job(
        self,
        resume_text: str,
        job_description: str,
        resume_id: str = None,
        job_id: str = None
    ) -> Dict:
        """
        Match a resume to a job description
        
        Args:
            resume_text: Full resume text
            job_description: Job description text
            resume_id: Optional ID for caching
            job_id: Optional ID for caching
            
        Returns:
            Match result with similarity score and breakdown
        """
        # Get embeddings
        resume_embedding = self.get_embedding(
            resume_text,
            cache_key=f"resume_{resume_id}" if resume_id else None
        )
        
        job_embedding = self.get_embedding(
            job_description,
            cache_key=f"job_{job_id}" if job_id else None
        )
        
        # Calculate overall similarity
        overall_score = self.calculate_similarity(resume_embedding, job_embedding)
        
        # Determine match level
        if overall_score >= 80:
            match_level = "Excellent Match"
            color = "🟢"
        elif overall_score >= 65:
            match_level = "Good Match"
            color = "🟡"
        elif overall_score >= 50:
            match_level = "Fair Match"
            color = "🟠"
        else:
            match_level = "Weak Match"
            color = "🔴"
        
        return {
            "match_score": round(overall_score, 2),
            "match_level": match_level,
            "color": color,
            "recommendation": self._get_recommendation(overall_score)
        }
    
    def match_resume_to_multiple_jobs(
        self,
        resume_text: str,
        jobs: List[Dict],
        resume_id: str = None
    ) -> List[Dict]:
        """
        Match a resume to multiple jobs and rank them
        
        Args:
            resume_text: Full resume text
            jobs: List of job dicts with 'id', 'title', 'company', 'description'
            resume_id: Optional resume ID for caching
            
        Returns:
            Ranked list of job matches
        """
        # Get resume embedding once
        resume_embedding = self.get_embedding(
            resume_text,
            cache_key=f"resume_{resume_id}" if resume_id else None
        )
        
        matches = []
        
        for job in jobs:
            job_embedding = self.get_embedding(
                job['description'],
                cache_key=f"job_{job.get('id')}" if job.get('id') else None
            )
            
            score = self.calculate_similarity(resume_embedding, job_embedding)
            
            matches.append({
                "job_id": job.get('id'),
                "job_title": job.get('title', 'Unknown'),
                "company": job.get('company', 'Unknown'),
                "match_score": round(score, 2),
                "match_level": self._get_match_level(score),
                "job_description": job.get('description', '')[:200] + "..."
            })
        
        # Sort by match score (highest first)
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        
        return matches
    
    def _get_match_level(self, score: float) -> str:
        """Helper to get match level from score"""
        if score >= 80:
            return "🟢 Excellent Match"
        elif score >= 65:
            return "🟡 Good Match"
        elif score >= 50:
            return "🟠 Fair Match"
        else:
            return "🔴 Weak Match"
    
    def _get_recommendation(self, score: float) -> str:
        """Generate recommendation based on match score"""
        if score >= 80:
            return "✅ Apply immediately! Your profile is an excellent fit for this role."
        elif score >= 65:
            return "👍 Strong candidate. Tailor your resume to highlight relevant skills."
        elif score >= 50:
            return "⚠️ Possible fit. Consider gaining more relevant experience or skills."
        else:
            return "❌ Weak match. Focus on roles that better align with your background."


# Test the matcher
if __name__ == "__main__":
    print("🧪 Testing Semantic Matcher...")
    print("=" * 70)
    
    try:
        matcher = SemanticMatcher()
        
        # Test resume
        test_resume = """
        Data Scientist with 5 years experience in machine learning, Python, SQL,
        and data visualization. Expert in PyTorch, TensorFlow, pandas, scikit-learn.
        Built recommendation systems and predictive models for Fortune 500 companies.
        """
        
        # Test jobs
        test_jobs = [
            {
                "id": "job1",
                "title": "Senior Data Scientist",
                "company": "Google",
                "description": "Looking for ML expert with Python, TensorFlow, deep learning experience..."
            },
            {
                "id": "job2",
                "title": "Frontend Developer",
                "company": "Facebook",
                "description": "Need React, JavaScript, CSS expert for building user interfaces..."
            },
            {
                "id": "job3",
                "title": "Machine Learning Engineer",
                "company": "Amazon",
                "description": "ML engineer needed. PyTorch, Python, model deployment experience required..."
            }
        ]
        
        print("\n📊 Matching resume to jobs...\n")
        
        matches = matcher.match_resume_to_multiple_jobs(test_resume, test_jobs)
        
        for i, match in enumerate(matches, 1):
            print(f"{i}. {match['match_level']} - {match['job_title']} at {match['company']}")
            print(f"   Score: {match['match_score']}%")
            print()
        
        print("=" * 70)
        print("✅ Semantic Matcher tested successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")