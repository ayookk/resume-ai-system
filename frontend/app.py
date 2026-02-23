"""
Streamlit Frontend for AI Resume & Recruitment System
"""
import streamlit as st
import requests
import json
from datetime import datetime

# API configuration
API_BASE_URL = "http://localhost:8000/api/v1"

# Page config
st.set_page_config(
    page_title="AI Resume & Job Analysis",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("🗂️ Navigation")
page = st.sidebar.radio(
    "Choose a feature:",
    ["📄 Resume Analysis", "🔍 Job Analysis", "✍️ Generate Cover Letter", "🎯 Job Matching", "📊 View History"]
)

st.sidebar.markdown("---")
st.sidebar.info("""
**AI Resume & Recruitment System**

This tool helps you:
- Optimize your resume for ATS
- Detect fake job postings
- Get application strategies
""")

# Main content
if page == "📄 Resume Analysis":
    st.markdown('<p class="main-header">📄 Resume Analysis & ATS Scoring</p>', unsafe_allow_html=True)
    
    st.markdown("""
    Upload your resume to get:
    - **ATS Compatibility Score** (0-100)
    - **Extracted Skills** automatically detected
    - **Improvement Suggestions** personalized to your resume
    """)
    
    st.markdown("---")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload your resume (PDF only)",
        type=['pdf'],
        help="Upload your resume in PDF format for analysis"
    )
    
    if uploaded_file is not None:
        st.info(f"📎 File uploaded: **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")
        
        if st.button("🚀 Analyze Resume", type="primary", use_container_width=True):
            with st.spinner("🔄 Analyzing your resume... This may take a few seconds."):
                try:
                    # Upload to API
                    files = {'file': uploaded_file}
                    response = requests.post(f"{API_BASE_URL}/resumes/upload", files=files)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        st.success("✅ Resume analyzed successfully!")
                        
                        # Display ATS Score
                        st.markdown("### 📊 ATS Compatibility Score")
                        ats_score = data.get('ats_score', 0)
                        
                        col1, col2, col3 = st.columns([2, 1, 1])
                        
                        with col1:
                            # Score gauge
                            if ats_score >= 85:
                                score_color = "🟢"
                                score_label = "Excellent"
                            elif ats_score >= 70:
                                score_color = "🟡"
                                score_label = "Good"
                            else:
                                score_color = "🔴"
                                score_label = "Needs Improvement"
                            
                            st.metric(
                                label="Your Score",
                                value=f"{ats_score}/100",
                                delta=score_label
                            )
                            st.progress(ats_score / 100)
                        
                        with col2:
                            st.metric("Skills Found", len(data['parsed_data'].get('skills', [])))
                        
                        with col3:
                            st.metric("Word Count", data['parsed_data'].get('word_count', 0))
                        
                        st.markdown("---")
                        
                        # Display Skills
                        st.markdown("### 🎯 Extracted Skills")
                        skills = data['parsed_data'].get('skills', [])
                        if skills:
                            # Display as columns of badges
                            skill_cols = st.columns(4)
                            for idx, skill in enumerate(skills):
                                with skill_cols[idx % 4]:
                                    st.markdown(f"**`{skill}`**")
                        else:
                            st.warning("No technical skills detected. Consider adding more specific skills.")
                        
                        st.markdown("---")
                        
                        # Display Contact Info
                        st.markdown("### 📧 Contact Information")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            email = data['parsed_data'].get('email')
                            if email:
                                st.success(f"✅ Email: {email}")
                            else:
                                st.error("❌ No email found - add to resume!")
                        
                        with col2:
                            phone = data['parsed_data'].get('phone')
                            if phone:
                                st.success(f"✅ Phone: {phone}")
                            else:
                                st.error("❌ No phone found - add to resume!")
                        
                        st.markdown("---")
                        
                        # Display Suggestions
                        st.markdown("### 💡 Improvement Suggestions")
                        suggestions = data.get('suggestions', [])
                        if suggestions:
                            for suggestion in suggestions:
                                st.info(suggestion)
                        else:
                            st.success("🎉 Your resume looks great! No major issues detected.")
                        
                        # Store resume ID
                        st.session_state['last_resume_id'] = data.get('resume_id')
                        
                    else:
                        st.error(f"❌ Error: {response.status_code} - {response.text}")
                
                except Exception as e:
                    st.error(f"❌ Error analyzing resume: {str(e)}")

elif page == "🔍 Job Analysis":
    st.markdown('<p class="main-header">🔍 Job Posting Analysis</p>', unsafe_allow_html=True)
    
    st.markdown("""
    Paste a job description to detect:
    - **Active Hiring** 🟢 (Real, immediate openings)
    - **Pipeline/Evergreen** 🟡 (Resume harvesting)
    - **Application Strategy** tailored to the hiring type
    """)
    
    st.markdown("---")
    
    # Job description input
    job_description = st.text_area(
        "Paste the full job description here:",
        height=300,
        placeholder="Copy and paste the complete job posting including title, requirements, company info, etc."
    )
    
    col1, col2 = st.columns([3, 1])
    with col1:
        posted_date = st.date_input(
            "When was this job posted? (optional)",
            value=None,
            help="Helps detect stale postings"
        )
    
    if st.button("🔍 Analyze Job Posting", type="primary", use_container_width=True, disabled=not job_description):
        with st.spinner("🔄 Analyzing job posting..."):
            try:
                payload = {
                    "job_description": job_description,
                    "posted_date": posted_date.isoformat() if posted_date else None
                }
                
                response = requests.post(f"{API_BASE_URL}/jobs/analyze", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    analysis = data['analysis']
                    
                    st.success("✅ Job posting analyzed!")
                    
                    # Hiring Type
                    st.markdown("### 🎯 Hiring Type Detection")
                    
                    hiring_type = analysis['hiring_type']
                    confidence = analysis['confidence']
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Hiring Type", hiring_type)
                    with col2:
                        st.metric("Confidence", confidence)
                    with col3:
                        active_score = analysis['active_score']
                        passive_score = analysis['passive_score']
                        st.metric("Active vs Passive", f"{active_score} vs {passive_score}")
                    
                    # Explanation
                    if "🟢" in hiring_type:
                        st.markdown(f'<div class="success-box">{analysis["explanation"]}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="warning-box">{analysis["explanation"]}</div>', unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # Insights
                    st.markdown("### 🔍 Detailed Insights")
                    insights = analysis.get('insights', [])
                    for insight in insights:
                        if "🚩" in insight:
                            st.error(insight)
                        elif "⚠️" in insight:
                            st.warning(insight)
                        else:
                            st.info(insight)
                    
                    st.markdown("---")
                    
                    # Application Strategy
                    st.markdown("### 📋 Recommended Application Strategy")
                    strategy = analysis.get('application_strategy', [])
                    for tip in strategy:
                        st.success(tip)
                    
                    # Additional Details (expandable)
                    with st.expander("🔬 Technical Analysis Details"):
                        st.json(analysis)
                
                else:
                    st.error(f"❌ Error: {response.status_code} - {response.text}")
            
            except Exception as e:
                st.error(f"❌ Error analyzing job: {str(e)}")

elif page == "✍️ Generate Cover Letter":
    st.markdown('<p class="main-header">✍️ AI Cover Letter Generator</p>', unsafe_allow_html=True)
    
    st.markdown("""
    Generate a personalized, professional cover letter powered by AI.
    Customize the tone and let AI craft the perfect application letter!
    """)
    
    st.markdown("---")
    
    # Job Details
    st.markdown("### 📋 Job Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        job_title = st.text_input(
            "Job Title",
            placeholder="e.g., Data Scientist, Software Engineer"
        )
    
    with col2:
        company_name = st.text_input(
            "Company Name",
            placeholder="e.g., Google, Amazon, Microsoft"
        )
    
    job_description = st.text_area(
        "Job Description",
        height=200,
        placeholder="Paste the job description here..."
    )
    
    st.markdown("---")
    
    # Resume Data (simplified)
    st.markdown("### 👤 Your Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        candidate_name = st.text_input(
            "Your Name",
            placeholder="e.g., John Doe"
        )
    
    with col2:
        tone = st.selectbox(
            "Cover Letter Tone",
            ["professional", "enthusiastic", "formal"],
            help="Choose the tone that matches your personality and the company culture"
        )
    
    skills_input = st.text_input(
        "Your Top Skills (comma-separated)",
        placeholder="e.g., Python, SQL, Machine Learning, Data Analysis"
    )
    
    experience_input = st.text_area(
        "Your Recent Experience (brief summary)",
        height=100,
        placeholder="e.g., Data Analyst at TechCorp (2020-2024): Led data analysis projects..."
    )
    
    st.markdown("---")
    
    # Generate button
    if st.button("✨ Generate Cover Letter", type="primary", use_container_width=True, 
                 disabled=not (job_title and company_name and job_description and candidate_name)):
        
        with st.spinner("🤖 AI is writing your cover letter... This may take 10-15 seconds."):
            try:
                # Parse skills
                skills = [s.strip() for s in skills_input.split(",") if s.strip()]
                
                # Parse experience
                experience = []
                if experience_input:
                    experience.append({
                        "title": "Recent Role",
                        "company": "Previous Company",
                        "description": experience_input
                    })
                
                # Build resume data
                resume_data = {
                    "contact": {"name": candidate_name},
                    "skills": skills,
                    "experience": experience
                }
                
                # Build job data
                job_data = {
                    "title": job_title,
                    "company": company_name,
                    "description": job_description
                }
                
                # Call API
                payload = {
                    "resume_data": resume_data,
                    "job_data": job_data,
                    "tone": tone
                }
                
                response = requests.post(f"{API_BASE_URL}/cover-letters/generate", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    cover_letter = data['cover_letter']
                    word_count = data['word_count']
                    
                    st.success("✅ Cover letter generated successfully!")
                    
                    # Display metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Word Count", word_count)
                    with col2:
                        st.metric("Tone", tone.capitalize())
                    with col3:
                        st.metric("Status", "Ready ✅")
                    
                    st.markdown("---")
                    
                    # Display cover letter
                    st.markdown("### 📝 Your Cover Letter")
                    
                    # Show in a nice box
                    st.text_area(
                        "Cover Letter (click to copy)",
                        value=cover_letter,
                        height=400,
                        label_visibility="collapsed"
                    )
                    
                    # Download button
                    st.download_button(
                        label="📥 Download as Text File",
                        data=cover_letter,
                        file_name=f"cover_letter_{company_name.replace(' ', '_').lower()}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                    
                    # Tips
                    st.info("""
                    **💡 Next Steps:**
                    - Review and personalize the letter with specific examples
                    - Add your contact information at the top
                    - Include a proper salutation (Dear Hiring Manager, etc.)
                    - Sign off with your name at the bottom
                    """)
                
                else:
                    st.error(f"❌ Error: {response.status_code} - {response.text}")
            
            except Exception as e:
                st.error(f"❌ Error generating cover letter: {str(e)}") 
   
elif page == "🎯 Job Matching":
    st.markdown('<p class="main-header">🎯 Semantic Job Matching</p>', unsafe_allow_html=True)
    
    st.markdown("""
    Find your best job matches using AI-powered semantic analysis!
    Our system understands **meaning**, not just keywords.
    """)
    
    st.markdown("---")
    
    # Resume input
    st.markdown("### 📄 Your Resume")
    
    resume_input_method = st.radio(
        "How would you like to provide your resume?",
        ["Paste Resume Text", "Use Uploaded Resume"],
        horizontal=True
    )
    
    resume_text = ""
    
    if resume_input_method == "Paste Resume Text":
        resume_text = st.text_area(
            "Paste your resume text here:",
            height=200,
            placeholder="Copy and paste your full resume here..."
        )
    else:
        # Fetch available resumes
        try:
            response = requests.get(f"{API_BASE_URL}/resumes/?limit=50")
            if response.status_code == 200:
                data = response.json()
                resumes = data.get('resumes', [])
                
                if resumes:
                    resume_options = {
                        f"{r['original_filename']} (Score: {r['ats_score']})": r['resume_id']
                        for r in resumes
                    }
                    
                    selected = st.selectbox(
                        "Select a previously uploaded resume:",
                        options=list(resume_options.keys())
                    )
                    
                    if selected:
                        resume_id = resume_options[selected]
                        # Get the full resume
                        resume_response = requests.get(f"{API_BASE_URL}/resumes/{resume_id}")
                        if resume_response.status_code == 200:
                            resume_data = resume_response.json()['resume']
                            resume_text = resume_data['parsed_data']['raw_text']
                            st.success(f"✅ Loaded: {selected}")
                else:
                    st.warning("No resumes uploaded yet. Upload one in Resume Analysis first!")
        except Exception as e:
            st.error(f"Error loading resumes: {str(e)}")
    
    st.markdown("---")
    
    # Job input
    st.markdown("### 💼 Job Descriptions to Match")
    
    matching_mode = st.radio(
        "Matching Mode:",
        ["Single Job", "Multiple Jobs (Ranking)"],
        horizontal=True
    )
    
    if matching_mode == "Single Job":
        st.markdown("**Match against one job:**")
        
        col1, col2 = st.columns(2)
        with col1:
            job_title = st.text_input("Job Title", placeholder="e.g., Data Scientist")
        with col2:
            company = st.text_input("Company", placeholder="e.g., Google")
        
        job_description = st.text_area(
            "Job Description:",
            height=200,
            placeholder="Paste the full job description here..."
        )
        
        if st.button("🎯 Calculate Match Score", type="primary", use_container_width=True,
                     disabled=not (resume_text and job_description)):
            
            with st.spinner("🔄 Analyzing semantic similarity..."):
                try:
                    payload = {
                        "resume_text": resume_text,
                        "job_description": job_description
                    }
                    
                    response = requests.post(f"{API_BASE_URL}/matching/match", json=payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        match = data['match']
                        
                        st.success("✅ Match analysis complete!")
                        
                        # Big score display
                        col1, col2, col3 = st.columns([2, 2, 2])
                        
                        with col1:
                            st.metric(
                                "Match Score",
                                f"{match['match_score']}%",
                                delta=match['match_level']
                            )
                        
                        with col2:
                            st.metric(
                                "Match Level",
                                match['match_level'],
                                delta=match['color']
                            )
                        
                        with col3:
                            if match['match_score'] >= 65:
                                st.metric("Recommendation", "Apply!", delta="✅")
                            else:
                                st.metric("Recommendation", "Consider", delta="⚠️")
                        
                        # Progress bar
                        st.progress(match['match_score'] / 100)
                        
                        # Recommendation
                        st.info(f"**💡 {match['recommendation']}**")
                        
                        # Additional context
                        with st.expander("📊 Understanding Your Score"):
                            st.markdown("""
                            **Score Breakdown:**
                            - **80-100%**: 🟢 Excellent Match - You're a top candidate
                            - **65-79%**: 🟡 Good Match - Strong fit with some gaps
                            - **50-64%**: 🟠 Fair Match - Consider skill development
                            - **0-49%**: 🔴 Weak Match - Focus on better-aligned roles
                            
                            **What This Means:**
                            Semantic matching analyzes the *meaning* of your experience vs job requirements,
                            not just keyword matches. A high score means your background genuinely aligns
                            with what the company needs.
                            """)
                    
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    else:  # Multiple jobs ranking
        st.markdown("**Add multiple jobs to rank by match score:**")
        
        num_jobs = st.number_input("How many jobs to compare?", min_value=2, max_value=10, value=3)
        
        jobs = []
        
        for i in range(num_jobs):
            with st.expander(f"Job {i+1}", expanded=(i==0)):
                col1, col2 = st.columns(2)
                with col1:
                    title = st.text_input(f"Job Title {i+1}", key=f"title_{i}", placeholder="e.g., Data Scientist")
                with col2:
                    comp = st.text_input(f"Company {i+1}", key=f"company_{i}", placeholder="e.g., Google")
                
                desc = st.text_area(
                    f"Job Description {i+1}:",
                    key=f"desc_{i}",
                    height=150,
                    placeholder="Paste job description..."
                )
                
                if title and comp and desc:
                    jobs.append({
                        "id": f"job_{i+1}",
                        "title": title,
                        "company": comp,
                        "description": desc
                    })
        
        if st.button("🏆 Rank Jobs by Match", type="primary", use_container_width=True,
                     disabled=not (resume_text and len(jobs) >= 2)):
            
            with st.spinner(f"🔄 Ranking {len(jobs)} jobs by semantic similarity..."):
                try:
                    payload = {
                        "resume_text": resume_text,
                        "jobs": jobs
                    }
                    
                    response = requests.post(f"{API_BASE_URL}/matching/match-multiple", json=payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        matches = data['matches']
                        
                        st.success(f"✅ Ranked {data['total_jobs']} jobs!")
                        
                        st.markdown("### 🏆 Your Best Matches (Ranked)")
                        
                        for i, match in enumerate(matches, 1):
                            score = match['match_score']
                            
                            # Different styling based on rank
                            if i == 1:
                                icon = "🥇"
                                color = "#FFD700"
                            elif i == 2:
                                icon = "🥈"
                                color = "#C0C0C0"
                            elif i == 3:
                                icon = "🥉"
                                color = "#CD7F32"
                            else:
                                icon = f"{i}."
                                color = "#666666"
                            
                            with st.container():
                                col1, col2, col3 = st.columns([1, 4, 2])
                                
                                with col1:
                                    st.markdown(f"### {icon}")
                                
                                with col2:
                                    st.markdown(f"**{match['job_title']}** at {match['company']}")
                                    st.caption(match['match_level'])
                                
                                with col3:
                                    st.metric("Match", f"{score}%")
                                
                                st.progress(score / 100)
                                st.markdown("---")
                    
                    else:
                        st.error(f"Error: {response.status_code}")
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                
elif page == "📊 View History":
    st.markdown('<p class="main-header">📊 Analysis History</p>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📄 Resumes", "🔍 Job Analyses"])
    
    with tab1:
        st.markdown("### Uploaded Resumes")
        try:
            response = requests.get(f"{API_BASE_URL}/resumes/?limit=20")
            if response.status_code == 200:
                data = response.json()
                resumes = data.get('resumes', [])
                
                if resumes:
                    st.success(f"Found {data['total']} resume(s)")
                    
                    for resume in resumes:
                        with st.expander(f"📄 {resume['original_filename']} - Score: {resume['ats_score']}/100"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write(f"**Resume ID:** {resume['resume_id']}")
                                st.write(f"**ATS Score:** {resume['ats_score']}/100")
                                st.write(f"**Skills:** {len(resume['parsed_data']['skills'])}")
                            
                            with col2:
                                st.write(f"**Email:** {resume['parsed_data'].get('email', 'N/A')}")
                                st.write(f"**Phone:** {resume['parsed_data'].get('phone', 'N/A')}")
                                st.write(f"**Uploaded:** {resume.get('created_at', 'N/A')}")
                            
                            if st.button(f"🗑️ Delete", key=f"del_resume_{resume['resume_id']}"):
                                del_response = requests.delete(f"{API_BASE_URL}/resumes/{resume['resume_id']}")
                                if del_response.status_code == 200:
                                    st.success("Deleted!")
                                    st.rerun()
                else:
                    st.info("No resumes uploaded yet. Go to Resume Analysis to upload one!")
        
        except Exception as e:
            st.error(f"Error loading resumes: {str(e)}")
    
    with tab2:
        st.markdown("### Job Analyses")
        try:
            response = requests.get(f"{API_BASE_URL}/jobs/?limit=20")
            if response.status_code == 200:
                data = response.json()
                analyses = data.get('analyses', [])
                
                if analyses:
                    st.success(f"Found {data['total']} job analysis/analyses")
                    
                    for analysis in analyses:
                        with st.expander(f"{analysis['hiring_type']} - {analysis['job_description'][:100]}..."):
                            st.write(f"**Hiring Type:** {analysis['hiring_type']}")
                            st.write(f"**Confidence:** {analysis['confidence']}")
                            st.write(f"**Scores:** Active: {analysis['active_score']}, Passive: {analysis['passive_score']}")
                            st.write(f"**Analyzed:** {analysis.get('created_at', 'N/A')}")
                            
                            st.markdown("**Insights:**")
                            for insight in analysis.get('insights', []):
                                st.write(f"- {insight}")
                else:
                    st.info("No job analyses yet. Go to Job Analysis to analyze one!")
        
        except Exception as e:
            st.error(f"Error loading job analyses: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888;'>
    <p>Built with ❤️ by Kervin Benoit | 
    <a href='https://github.com/your-username/resume-ai-system'>GitHub</a> | 
    <a href='http://localhost:8000/docs'>API Docs</a>
    </p>
</div>
""", unsafe_allow_html=True)