"""
AI Cover Letter Generator using OpenAI
"""
from openai import OpenAI
import os
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

class CoverLetterGenerator:
    def __init__(self):
        """Initialize OpenAI API"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=api_key)
    
    def generate_cover_letter(
        self,
        resume_data: Dict,
        job_data: Dict,
        tone: str = "professional"
    ) -> str:
        """
        Generate a personalized cover letter
        
        Args:
            resume_data: Dictionary with parsed resume data
            job_data: Dictionary with job information
            tone: Tone of the letter (professional, enthusiastic, formal)
            
        Returns:
            Generated cover letter text
        """
        # Extract key information
        candidate_name = resume_data.get('contact', {}).get('name', 'Candidate')
        skills = resume_data.get('skills', [])
        experience = resume_data.get('experience', [])
        
        job_title = job_data.get('title', 'Position')
        company = job_data.get('company', 'Company')
        job_description = job_data.get('description', '')
        
        # Build the prompt
        prompt = f"""You are an expert career coach writing a compelling cover letter.

**Candidate Information:**
Name: {candidate_name}
Top Skills: {', '.join(skills[:8])}
Recent Experience: {self._summarize_experience(experience)}

**Job Information:**
Position: {job_title}
Company: {company}
Job Description: {job_description[:500]}

**Instructions:**
Write a {tone} cover letter (250-300 words) that:
1. Opens with enthusiasm for the specific role and company
2. Highlights 2-3 relevant experiences that match the job requirements
3. Connects the candidate's skills to the company's needs
4. Shows genuine interest in the company/industry
5. Closes with a strong call to action

**Tone Guidelines:**
- Professional: Formal, business-appropriate, confident
- Enthusiastic: Energetic, passionate, but still professional  
- Formal: Very traditional, corporate language

**Format:**
Do NOT include:
- [Your Name], [Your Address], [Date] (they'll add these themselves)
- "Dear Hiring Manager" or salutation (they'll customize)
- Signature line

Start directly with the opening paragraph.
Write in first person ("I am excited to apply...").
Keep it concise and impactful.

Generate the cover letter now:"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Fast and cheap model
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert career coach and professional writer specializing in compelling cover letters."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,  # Balanced creativity
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            raise Exception(f"Error generating cover letter: {str(e)}")
    
    def _summarize_experience(self, experience_list: list) -> str:
        """Summarize experience for the prompt"""
        if not experience_list or len(experience_list) == 0:
            return "Entry-level professional seeking first opportunity"
        
        # Get most recent 2 positions
        summaries = []
        for exp in experience_list[:2]:
            title = exp.get('title', '')
            company = exp.get('company', '')
            if title and company:
                summaries.append(f"{title} at {company}")
        
        return "; ".join(summaries) if summaries else "Experienced professional"


# Test the generator
if __name__ == "__main__":
    print("🧪 Testing Cover Letter Generator...")
    
    try:
        generator = CoverLetterGenerator()
        
        # Test data
        test_resume = {
            "contact": {"name": "Kervin Benoit"},
            "skills": ["Python", "SQL", "Machine Learning", "FastAPI", "Data Science"],
            "experience": [
                {
                    "title": "Warehouse Supply Inventory Analyst",
                    "company": "ALDI USA"
                }
            ]
        }
        
        test_job = {
            "title": "Data Scientist",
            "company": "TechCorp",
            "description": "We're looking for a data scientist with Python and ML experience to join our team..."
        }
        
        print("\n🔄 Generating cover letter... (this may take a few seconds)")
        cover_letter = generator.generate_cover_letter(test_resume, test_job, tone="professional")
        
        print("\n✅ Cover Letter Generated Successfully!")
        print("\n" + "="*70)
        print(cover_letter)
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")