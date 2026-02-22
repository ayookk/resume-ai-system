"""
Advanced Hiring Type Detector
Analyzes job descriptions to determine if company is actively hiring vs building a talent pipeline
Uses text analysis + structural metadata to detect resume harvesting
"""
from typing import Dict, List, Optional
import re
from datetime import datetime, timedelta


class HiringDetector:
    def __init__(self):
        # ACTIVE HIRING INDICATORS
        self.active_indicators = {
            'urgency': [
                'urgent hiring', 'urgently hiring', 'immediate start', 
                'immediate availability', 'asap', 'quick start',
                'fast-paced hiring', 'rapid hiring', 'hiring immediately'
            ],
            'specificity': [
                'reporting to', 'reporting directly to', 'join our team of',
                'backfill', 'new team member', 'specific role',
                'funded position', 'approved headcount', 'open position'
            ],
            'timeline': [
                'start date', 'expected start', 'target start',
                'hiring timeline', 'interview schedule', 'onboarding'
            ],
            'vacancy': [
                'open role', 'vacancy', 'opening', 'position available',
                'now hiring', 'accepting applications', 'apply now'
            ]
        }
        
        # PASSIVE/PIPELINE INDICATORS
        self.passive_indicators = {
            'evergreen': [
                'ongoing need', 'continuous recruitment', 'always hiring',
                'evergreen', 'rolling basis', 'continuous hiring',
                'year-round recruitment'
            ],
            'pipeline': [
                'future opportunities', 'talent pool', 'talent pipeline',
                'talent community', 'career opportunities', 'join our database',
                'future openings', 'potential opportunities'
            ],
            'general': [
                'general interest', 'open application', 'speculative application',
                'expression of interest', 'submit your resume',
                'keep you in mind', 'future consideration'
            ],
            'vague': [
                'various positions', 'multiple roles', 'several opportunities',
                'range of positions', 'diverse opportunities'
            ]
        }
        
        # RED FLAGS FOR RESUME HARVESTING
        self.red_flags = {
            'location_blast': [
                'multiple locations', 'various locations', 'nationwide',
                'all locations', 'remote - us', 'remote - global'
            ],
            'generic_contact': [
                'email resume to', 'send resume to', 'forward cv to',
                'jobs@', 'careers@', 'hr@', 'recruiting@'
            ],
            'vague_benefits': [
                'competitive salary', 'competitive compensation',
                'market rate', 'commensurate with experience',
                'to be discussed', 'tbd', 'negotiable'
            ],
            'no_team_info': [
                'growing company', 'dynamic team', 'talented team',
                'innovative company'  # without specific department
            ]
        }
    
    def extract_requisition_id(self, text: str) -> Optional[str]:
        """
        Extract requisition/job ID from posting
        
        Pattern detection:
        - REQ-2024-0452 (specific, likely real)
        - EVERGREEN_SALES (generic, likely pipeline)
        """
        patterns = [
            r'(?:req|requisition|job)\s*(?:id|#|number)?\s*:?\s*([A-Z0-9_-]+)',
            r'(?:reference|ref)\s*(?:number|#)?\s*:?\s*([A-Z0-9_-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def analyze_req_id(self, req_id: Optional[str]) -> Dict:
        """
        Analyze requisition ID for red flags
        
        Returns:
            Analysis of the req ID
        """
        if not req_id:
            return {
                "has_req_id": False,
                "is_suspicious": True,
                "reason": "No requisition ID found - possible unstructured posting"
            }
        
        req_id_upper = req_id.upper()
        
        # Check for evergreen patterns
        evergreen_terms = ['EVERGREEN', 'GENERIC', 'POOL', 'PIPELINE', 'GENERAL']
        if any(term in req_id_upper for term in evergreen_terms):
            return {
                "has_req_id": True,
                "req_id": req_id,
                "is_suspicious": True,
                "reason": f"Requisition ID '{req_id}' contains evergreen/generic terms"
            }
        
        # Check for overly simple IDs (e.g., "12345" or "A1")
        if len(req_id) <= 4 and req_id.isalnum():
            return {
                "has_req_id": True,
                "req_id": req_id,
                "is_suspicious": True,
                "reason": f"Suspiciously simple req ID: '{req_id}'"
            }
        
        # Specific, complex IDs are usually legitimate
        return {
            "has_req_id": True,
            "req_id": req_id,
            "is_suspicious": False,
            "reason": "Specific requisition ID suggests real opening"
        }
    
    def detect_location_blast(self, text: str) -> Dict:
        """
        Detect if job is posted in many locations (red flag)
        """
        # Count location mentions
        location_count = 0
        for keyword in self.red_flags['location_blast']:
            if keyword in text.lower():
                location_count += 1
        
        # Look for multiple city names
        cities_pattern = r'\b(?:New York|Los Angeles|Chicago|Houston|Phoenix|Philadelphia|San Antonio|San Diego|Dallas|San Jose|Austin|Jacksonville|Fort Worth|Columbus|Charlotte|San Francisco|Indianapolis|Seattle|Denver|Washington|Boston|El Paso|Nashville|Detroit|Oklahoma City|Portland|Las Vegas|Memphis|Louisville|Baltimore|Milwaukee|Albuquerque|Tucson|Fresno|Mesa|Sacramento|Atlanta|Kansas City|Colorado Springs|Omaha|Raleigh|Miami|Long Beach|Virginia Beach|Oakland|Minneapolis|Tulsa|Tampa|Arlington|New Orleans)\b'
        cities_found = len(re.findall(cities_pattern, text))
        
        is_blast = location_count > 0 or cities_found >= 5
        
        return {
            "is_location_blast": is_blast,
            "cities_mentioned": cities_found,
            "blast_keywords": location_count,
            "reason": f"Found {cities_found} cities and {location_count} multi-location keywords" if is_blast else "Normal location specificity"
        }
    
    def analyze_specificity(self, text: str) -> Dict:
        """
        Analyze how specific the job description is
        Vague = pipeline, Specific = real role
        """
        specificity_score = 0
        details_found = []
        
        # Check for specific manager/team mentions
        if re.search(r'reporting to \w+|reports to \w+', text, re.IGNORECASE):
            specificity_score += 2
            details_found.append("Specific manager mentioned")
        
        # Check for department/team specificity
        departments = ['engineering', 'marketing', 'sales', 'operations', 'product', 'design', 'data', 'finance']
        dept_mentions = sum(1 for dept in departments if dept in text.lower())
        if dept_mentions >= 2:
            specificity_score += 1
            details_found.append(f"{dept_mentions} specific departments")
        
        # Check for project/tech stack details
        if re.search(r'working on|project|tech stack|tools we use', text, re.IGNORECASE):
            specificity_score += 1
            details_found.append("Project/tech details mentioned")
        
        # Check for compensation transparency
        if re.search(r'\$[\d,]+|salary range|pay range|\d+k-\d+k', text, re.IGNORECASE):
            specificity_score += 2
            details_found.append("Specific compensation mentioned")
        
        return {
            "specificity_score": specificity_score,
            "details_found": details_found,
            "is_specific": specificity_score >= 3,
            "reason": "High specificity suggests active hiring" if specificity_score >= 3 else "Low specificity suggests generic pipeline"
        }
    
    def count_indicators(self, text: str, indicators: Dict[str, List[str]]) -> Dict[str, int]:
        """Count indicator matches by category"""
        text_lower = text.lower()
        matches = {}
        
        for category, keywords in indicators.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            matches[category] = count
        
        return matches
    
    def analyze_hiring_type(self, job_description: str, posted_date: Optional[str] = None) -> Dict:
        """
        Comprehensive hiring type analysis
        
        Args:
            job_description: Full job posting text
            posted_date: Optional posting date (ISO format: YYYY-MM-DD)
            
        Returns:
            Complete analysis with hiring type, confidence, and insights
        """
        # 1. Text-based analysis
        active_matches = self.count_indicators(job_description, self.active_indicators)
        passive_matches = self.count_indicators(job_description, self.passive_indicators)
        red_flag_matches = self.count_indicators(job_description, self.red_flags)
        
        active_score = sum(active_matches.values())
        passive_score = sum(passive_matches.values())
        red_flag_score = sum(red_flag_matches.values())
        
        # 2. Structural analysis
        req_id_analysis = self.analyze_req_id(
            self.extract_requisition_id(job_description)
        )
        location_analysis = self.detect_location_blast(job_description)
        specificity_analysis = self.analyze_specificity(job_description)
        
        # 3. Posting age analysis (if date provided)
        posting_age_days = None
        is_stale = False
        if posted_date:
            try:
                post_date = datetime.fromisoformat(posted_date.replace('Z', '+00:00'))
                age = datetime.now() - post_date.replace(tzinfo=None)
                posting_age_days = age.days
                is_stale = posting_age_days > 45
            except:
                pass
        
        # 4. Calculate weighted final score
        # Active signals (positive)
        final_active_score = active_score * 2  # Text indicators
        if specificity_analysis['is_specific']:
            final_active_score += 3
        if not req_id_analysis['is_suspicious']:
            final_active_score += 2
        
        # Pipeline signals (negative for active hiring)
        final_passive_score = passive_score * 2
        if req_id_analysis['is_suspicious']:
            final_passive_score += 3
        if location_analysis['is_location_blast']:
            final_passive_score += 3
        final_passive_score += red_flag_score
        if is_stale:
            final_passive_score += 2
        
        # 5. Determine hiring type
        if final_active_score > final_passive_score * 1.5:
            hiring_type = "🟢 Active Hiring"
            confidence = "High" if final_active_score >= 8 else "Medium"
            explanation = (
                "This is a real, funded position with an immediate hiring need. "
                "The company is actively screening candidates now and likely has a "
                "specific vacancy to fill. Expect a structured process with faster response times."
            )
        elif final_passive_score > final_active_score * 1.5:
            hiring_type = "🟡 Pipeline/Evergreen"
            confidence = "High" if final_passive_score >= 8 else "Medium"
            explanation = (
                "This appears to be a talent pipeline or 'evergreen' requisition. "
                "The company is collecting resumes for future opportunities rather than "
                "filling an immediate vacancy. Response times may be slow or nonexistent."
            )
        else:
            hiring_type = "⚪ Mixed Signals"
            confidence = "Low"
            explanation = (
                "This posting shows conflicting indicators. It may be a legitimate role "
                "with poor job description quality, or a semi-active pipeline."
            )
        
        # 6. Generate detailed insights
        insights = []
        
        # Active signals
        if active_score > 0:
            insights.append(f"✅ {active_score} active hiring signals detected")
            top_active = max(active_matches.items(), key=lambda x: x[1])
            if top_active[1] > 0:
                insights.append(f"   → Strongest: {top_active[0]} ({top_active[1]} mentions)")
        
        # Passive/pipeline signals
        if passive_score > 0:
            insights.append(f"⚠️ {passive_score} pipeline/evergreen signals detected")
            top_passive = max(passive_matches.items(), key=lambda x: x[1])
            if top_passive[1] > 0:
                insights.append(f"   → Strongest: {top_passive[0]} ({top_passive[1]} mentions)")
        
        # Red flags
        if red_flag_score > 0:
            insights.append(f"🚩 {red_flag_score} resume harvesting red flags")
        
        # Structural issues
        if req_id_analysis['is_suspicious']:
            insights.append(f"🚩 {req_id_analysis['reason']}")
        
        if location_analysis['is_location_blast']:
            insights.append(f"🚩 {location_analysis['reason']}")
        
        if not specificity_analysis['is_specific']:
            insights.append(f"⚠️ Low specificity - vague job description")
        
        if is_stale:
            insights.append(f"🚩 Posting is {posting_age_days} days old (likely stale)")
        
        # 7. Application strategy
        if hiring_type == "🟢 Active Hiring":
            strategy = [
                "✅ Apply quickly - this is a time-sensitive opportunity",
                "📝 Tailor resume to exact requirements in posting",
                "⚡ Expect standard interview process with defined timeline",
                "👥 Competition is high - differentiate yourself clearly",
                "📞 Follow up within 1 week if no response"
            ]
        elif hiring_type == "🟡 Pipeline/Evergreen":
            strategy = [
                "⏳ Set expectations for slow/no response",
                "🤝 Try to network with employees instead of just applying",
                "🔍 Look for actual active roles at this company",
                "📧 Consider reaching out directly to hiring managers",
                "💡 This may be resume harvesting - apply selectively"
            ]
        else:
            strategy = [
                "🔎 Research company's careers page directly",
                "📞 Call/email recruiter to verify if role is active",
                "🎯 Prepare for both structured and exploratory interviews",
                "⚖️ Weigh time investment carefully"
            ]
        
        return {
            "hiring_type": hiring_type,
            "confidence": confidence,
            "explanation": explanation,
            
            # Scores
            "active_score": final_active_score,
            "passive_score": final_passive_score,
            "red_flag_score": red_flag_score,
            
            # Detailed breakdowns
            "active_indicators": active_matches,
            "passive_indicators": passive_matches,
            "red_flags": red_flag_matches,
            
            # Structural analysis
            "requisition_analysis": req_id_analysis,
            "location_analysis": location_analysis,
            "specificity_analysis": specificity_analysis,
            "posting_age_days": posting_age_days,
            "is_stale": is_stale,
            
            # Guidance
            "insights": insights,
            "application_strategy": strategy
        }


# Test the detector
if __name__ == "__main__":
    detector = HiringDetector()
    
    print("=" * 80)
    print("🧪 TESTING ADVANCED HIRING TYPE DETECTOR")
    print("=" * 80)
    
    # Test 1: Clear active hiring
    print("\n📋 TEST 1: Active Hiring Example")
    print("-" * 80)
    active_job = """
    Software Engineer - Machine Learning Team
    Requisition ID: REQ-2024-ML-1847
    
    We have an immediate opening for a ML Engineer to join our Data Science team,
    reporting directly to Sarah Chen, VP of AI. 
    
    Start date: March 15, 2024
    Salary range: $140,000 - $180,000
    
    You'll be working on our recommendation engine project using PyTorch and TensorFlow.
    Our team of 8 engineers is based in San Francisco.
    
    Apply now - interviews happening this week!
    """
    
    result = detector.analyze_hiring_type(active_job, posted_date="2024-02-15")
    print(f"Hiring Type: {result['hiring_type']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Active Score: {result['active_score']} | Passive Score: {result['passive_score']}")
    print("\nInsights:")
    for insight in result['insights']:
        print(f"  {insight}")
    
    # Test 2: Clear pipeline/evergreen
    print("\n\n📋 TEST 2: Pipeline/Evergreen Example")
    print("-" * 80)
    pipeline_job = """
    Senior Software Engineers - Future Opportunities
    Requisition: EVERGREEN_ENG_2024
    
    Join our talent pool! We're always looking for talented engineers
    across multiple locations nationwide.
    
    Submit your resume for future consideration. We'll keep you in mind
    for various positions as they become available.
    
    Locations: New York, Los Angeles, Chicago, Houston, Phoenix, San Francisco, 
    Seattle, Denver, Austin, Dallas, Miami, Boston, Atlanta
    
    Email your resume to: careers@company.com
    Competitive salary commensurate with experience.
    """
    
    result = detector.analyze_hiring_type(pipeline_job, posted_date="2023-06-01")
    print(f"Hiring Type: {result['hiring_type']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Active Score: {result['active_score']} | Passive Score: {result['passive_score']}")
    print("\nInsights:")
    for insight in result['insights']:
        print(f"  {insight}")
    print("\nApplication Strategy:")
    for tip in result['application_strategy'][:3]:
        print(f"  {tip}")
    
    print("\n\n✅ Hiring Detector initialized and tested successfully!")
    print("=" * 80)