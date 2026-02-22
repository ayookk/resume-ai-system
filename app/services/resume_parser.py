"""
Resume Parser Service
Extracts text and structured data from PDF resumes
"""
import PyPDF2
import re
from typing import Dict, List, Optional


class ResumeParser:
    def __init__(self):
        # Common technical skills to look for
        self.tech_skills = [
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'sql', 'r', 'go', 'rust', 'scala',
            'react', 'vue', 'angular', 'node.js', 'express', 'django', 'flask', 'fastapi', 'spring',
            'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'keras', 'opencv',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'terraform', 'ansible',
            'postgresql', 'mysql', 'mongodb', 'redis', 'cassandra', 'elasticsearch',
            'machine learning', 'deep learning', 'nlp', 'computer vision', 'data science',
            'rest api', 'graphql', 'microservices', 'agile', 'scrum', 'git', 'ci/cd'
        ]
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract raw text from PDF file
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text as string
        """
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
    
    def extract_email(self, text: str) -> Optional[str]:
        """Extract email address from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        return match.group(0) if match else None
    
    def extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number from text"""
        # Matches formats: (123) 456-7890, 123-456-7890, 123.456.7890, +1-123-456-7890
        phone_pattern = r'(\+\d{1,3}[-.\s]??)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        match = re.search(phone_pattern, text)
        return match.group(0) if match else None
    
    def extract_skills(self, text: str) -> List[str]:
        """
        Extract technical skills from resume text
        
        Args:
            text: Resume text
            
        Returns:
            List of found skills
        """
        text_lower = text.lower()
        found_skills = []
        
        for skill in self.tech_skills:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                # Capitalize properly for display
                found_skills.append(skill.title())
        
        # Remove duplicates and sort
        return sorted(list(set(found_skills)))
    
    def extract_education(self, text: str) -> List[Dict[str, str]]:
        """
        Extract education information
        
        Returns:
            List of education entries
        """
        education = []
        
        # Common degree patterns
        degree_patterns = [
            r"(Bachelor'?s?|B\.?S\.?|B\.?A\.?|Master'?s?|M\.?S\.?|M\.?A\.?|Ph\.?D\.?|MBA)",
            r"(Associate'?s?|A\.?S\.?|A\.?A\.?)"
        ]
        
        for pattern in degree_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Extract surrounding context (50 chars before and after)
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end].strip()
                
                education.append({
                    "degree": match.group(0),
                    "context": context
                })
        
        return education[:3]  # Return max 3 education entries
    
    def calculate_ats_score(self, parsed_data: Dict) -> float:
        """
        Calculate ATS compatibility score (0-100)
        
        Scoring breakdown:
        - Contact info (email + phone): 20 points
        - Skills section: 30 points
        - Education: 20 points
        - Experience indicators: 30 points
        
        Args:
            parsed_data: Dictionary with parsed resume data
            
        Returns:
            Score between 0 and 100
        """
        score = 0.0
        
        # Contact info (20 points total)
        if parsed_data.get('email'):
            score += 10
        if parsed_data.get('phone'):
            score += 10
        
        # Skills (30 points total)
        skills = parsed_data.get('skills', [])
        if len(skills) >= 8:
            score += 30
        elif len(skills) >= 5:
            score += 20
        elif len(skills) >= 3:
            score += 10
        
        # Education (20 points)
        education = parsed_data.get('education', [])
        if len(education) > 0:
            score += 20
        
        # Experience indicators (30 points)
        # Look for common experience keywords in text
        text_lower = parsed_data.get('raw_text', '').lower()
        experience_keywords = ['experience', 'worked', 'developed', 'managed', 'led', 'designed']
        found_keywords = sum(1 for keyword in experience_keywords if keyword in text_lower)
        
        if found_keywords >= 4:
            score += 30
        elif found_keywords >= 2:
            score += 20
        elif found_keywords >= 1:
            score += 10
        
        return min(score, 100.0)  # Cap at 100
    
    def generate_suggestions(self, parsed_data: Dict, ats_score: float) -> List[str]:
        """
        Generate improvement suggestions based on parsed data
        
        Args:
            parsed_data: Parsed resume data
            ats_score: Calculated ATS score
            
        Returns:
            List of suggestion strings
        """
        suggestions = []
        
        if ats_score < 70:
            if not parsed_data.get('email'):
                suggestions.append("⚠️ Add a professional email address in the contact section")
            
            if not parsed_data.get('phone'):
                suggestions.append("⚠️ Include a phone number for contact purposes")
            
            skills_count = len(parsed_data.get('skills', []))
            if skills_count < 5:
                suggestions.append(f"💡 Add more relevant skills (currently {skills_count}, aim for 8-12)")
            
            if len(parsed_data.get('education', [])) == 0:
                suggestions.append("📚 Include your education background")
            
            text = parsed_data.get('raw_text', '').lower()
            if 'experience' not in text and 'worked' not in text:
                suggestions.append("💼 Add work experience with action verbs (developed, led, managed)")
        
        if ats_score >= 70 and ats_score < 85:
            suggestions.append("✅ Good score! Consider adding more quantifiable achievements")
            suggestions.append("💡 Use industry-specific keywords from job descriptions")
        
        if ats_score >= 85:
            suggestions.append("🎉 Excellent ATS score! Your resume is well-optimized")
        
        return suggestions
    
    def parse_resume(self, pdf_path: str) -> Dict:
        """
        Main function to parse resume and return structured data
        
        Args:
            pdf_path: Path to PDF resume file
            
        Returns:
            Dictionary with parsed data and analysis
        """
        # Extract text
        raw_text = self.extract_text_from_pdf(pdf_path)
        
        # Extract components
        email = self.extract_email(raw_text)
        phone = self.extract_phone(raw_text)
        skills = self.extract_skills(raw_text)
        education = self.extract_education(raw_text)
        
        # Build structured data
        parsed_data = {
            "raw_text": raw_text,
            "email": email,
            "phone": phone,
            "skills": skills,
            "education": education,
            "word_count": len(raw_text.split())
        }
        
        # Calculate ATS score
        ats_score = self.calculate_ats_score(parsed_data)
        
        # Generate suggestions
        suggestions = self.generate_suggestions(parsed_data, ats_score)
        
        return {
            "parsed_data": parsed_data,
            "ats_score": ats_score,
            "suggestions": suggestions,
            "status": "success"
        }


# Test the parser
if __name__ == "__main__":
    parser = ResumeParser()
    print("✅ Resume Parser initialized successfully!")
    print(f"📊 Tracking {len(parser.tech_skills)} technical skills")