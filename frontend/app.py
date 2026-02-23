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
    ["📄 Resume Analysis", "🔍 Job Analysis", "📊 View History"]
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