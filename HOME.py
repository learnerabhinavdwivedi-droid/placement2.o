import streamlit as st
import numpy as np
import joblib
import pandas as pd
import pdfplumber
import time
import base64
import os
from openai import OpenAI

# ---------------- 1. CONFIG & SESSION STATE ----------------
st.set_page_config(page_title="PlacementIQ Pro2", layout="wide", page_icon="🚀")

# Initialize Session State variables to prevent errors on page reload
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "target_role" not in st.session_state:
    st.session_state.target_role = "Software Engineer"
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- 2. LOGO HANDLING ----------------
def get_base64_image(image_path):
    try:
        if os.path.exists(image_path):
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
    except Exception:
        return ""
    return ""

current_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(current_dir, "logo.png")
img_base64 = get_base64_image(image_path)

# ---------------- 3. GLOBAL STYLES ----------------
st.markdown(f"""
<style>
    html, body, [class*="css"] {{ font-family: 'Segoe UI', Roboto, sans-serif; }}
    
    /* Center and Style Logo at Top */
    .sidebar-logo-container {{
        display: flex;
        justify-content: center;
        padding-top: 10px;
        margin-bottom: 10px;
    }}
    .logo-3d {{
        width: 160px;
        transition: transform 0.8s ease-in-out;
        filter: drop-shadow(0 5px 15px rgba(0,0,0,0.3));
    }}
    .logo-3d:hover {{
        transform: rotateY(180deg) scale(1.05);
    }}

    /* Button Styling */
    div.stButton > button {{
        background: linear-gradient(90deg,#2563eb,#1e40af);
        color: white; border-radius: 12px; height: 3em; font-size: 16px;
        border: none; transition: all 0.25s ease; width: 100%;
    }}

    /* Hero Section */
    .hero {{
        background: white; color: #1f2a44; padding: 40px; border-radius: 20px;
        text-align: center; margin-bottom: 30px; border: 1px solid #e2e8f0;
    }}
</style>
""", unsafe_allow_html=True)

# ---------------- 4. SIDEBAR LOGO AT THE ABSOLUTE TOP ----------------
# Moving the logo call BEFORE any other sidebar content
if img_base64:
    st.sidebar.markdown(
        f'<div class="sidebar-logo-container"><img src="data:image/png;base64,{img_base64}" class="logo-3d"></div>', 
        unsafe_allow_html=True
    )

# Sidebar AI Assistant
try:
    client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    client = None

with st.sidebar:
    st.markdown("### 🤖 Career Copilot")
    with st.popover("💬 Chat with AI", use_container_width=True):
        chat_container = st.container(height=300)
        with chat_container:
            for message in st.session_state.messages:
                st.chat_message(message["role"]).markdown(message["content"])

        if prompt := st.chat_input("How can I help?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_container:
                st.chat_message("user").markdown(prompt)
                if client:
                    try:
                        with st.chat_message("assistant"):
                            stream = client.chat.completions.create(
                                model="llama-3.3-70b-versatile",
                                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                                stream=True,
                            )
                            response = st.write_stream(stream)
                            st.session_state.messages.append({"role": "assistant", "content": response})
                    except Exception:
                        st.error("Connection lost.")
                st.rerun()
            
    st.sidebar.divider()

# ---------------- 5. MAIN CONTENT ----------------
st.markdown("""
<div class="hero">
    <h1 style='margin:0; color:#2563eb;'>PlacementIQ Pro2</h1>
    <p style='font-size:1.2rem; color:#64748b;'>Precision AI for modern placement readiness</p>
</div>
""", unsafe_allow_html=True)

# ---------------- 6. INPUT METRICS ----------------
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 1. Academic & Skill Metrics")
    cgpa = st.slider("CGPA", 5.0, 10.0, 7.5)
    internship = st.selectbox("Internship Experience", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No")
    intern_val = internship # Defined for logic below
    projects = st.slider("Number of Projects", 0, 5, 2)
    communication = st.slider("Communication Skill (1-10)", 1, 10, 6)
    dsa_score = st.slider("DSA / Coding Skill (1-10)", 1, 10, 5)
    hackathons = st.slider("Hackathons / Certifications", 0, 5, 1)

with col2:
    st.markdown("### 2. Target Role & Resume")
    role_options = ["Software Engineer", "Python Developer", "Data Analyst", "ML Engineer", "DevOps Engineer", "Custom"]
    role = st.selectbox("Select Target Role", role_options)
    st.session_state.target_role = role
    
    job_description = st.text_area("Job Description Details", "Requires strong programming and problem solving.")
    uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
    
    if uploaded_file is not None:
        try:
            with pdfplumber.open(uploaded_file) as pdf:
                extracted_text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
                st.session_state.resume_text = extracted_text
            st.success("✅ Resume parsed!")
        except Exception:
            st.error("Could not read PDF.")

    resume_text = st.text_area("Parsed Resume Text", st.session_state.resume_text, height=150)
    st.session_state.resume_text = resume_text

# ---------------- 7. ANALYZE BUTTON & DASHBOARD ----------------
st.markdown("<br>", unsafe_allow_html=True)

if st.button("Analyze Profile Readiness", use_container_width=True):
    if not st.session_state.resume_text.strip():
        st.error("Please upload or paste your resume text to proceed.")
        st.stop()
    
    with st.spinner("Analyzing profile and computing insights..."):
        time.sleep(1.5) 
        
        # Skill Database for Matching
        SKILLS_DB = {
            "python": ["python"], "sql": ["sql", "mysql", "postgresql"],
            "machine learning": ["machine learning", "ml", "tensorflow"],
            "data analysis": ["data analysis", "pandas", "numpy"],
            "git": ["git", "github"], "java": ["java", "spring"],
            "react": ["react", "nextjs"], "docker": ["docker", "containers"],
            "c++": ["c++", "cpp"], "javascript": ["javascript", "js", "node"]
        }
        
        resume_clean = st.session_state.resume_text.lower()
        resume_skills = [s for s, kw in SKILLS_DB.items() if any(k in resume_clean for k in kw)]

        # 1. Resume Quality Scoring
        word_count = len(st.session_state.resume_text.split())
        numbers_found = sum(c.isdigit() for c in st.session_state.resume_text)
        resume_quality = min(word_count / 300, 1) * 4 + min(len(resume_skills) / 5, 1) * 4 + min(numbers_found / 15, 1) * 2
        resume_quality = round(resume_quality, 1)

        # 2. Probability Calculation
        probability = (cgpa * 4) + (intern_val * 15) + (len(resume_skills) * 5) + (projects * 4) + (dsa_score * 0.5)
        probability = round(max(5, min(probability, 98)), 1)

        # ---------------- DISPLAY RESULTS ----------------
        st.divider()
        st.markdown(f"""
            <div style="background: linear-gradient(90deg,#2563eb,#1e40af); color: white; padding: 20px; border-radius: 15px; text-align: center;">
                <h2 style='margin:0;'>Placement Readiness: {probability}%</h2>
            </div>
        """, unsafe_allow_html=True)
        
        st.progress(probability / 100)

        colA, colB, colC = st.columns(3)
        with colA: st.metric("Resume Quality", f"{resume_quality}/10")
        with colB: st.metric("Skills Detected", len(resume_skills))
        with colC: st.metric("Project Count", projects)
        
        # 3. Strength & Weakness Breakdown
        st.subheader("🧐 Why this score?")
        reasons = []
        if cgpa >= 8: reasons.append(f"✅ Strong Academic Performance (+{round(cgpa*1.2,1)}%)")
        if intern_val == 1: reasons.append("✅ Practical Experience from Internship (+15%)")
        if dsa_score >= 7: reasons.append("✅ Competitive DSA Proficiency (+5%)")
        if len(resume_skills) < 3: reasons.append("⚠️ Skill Gap: Add more core technologies (-10%)")
        
        for r in reasons:
            st.write(r)

        # 4. Visual Charts
        res_col_left, res_col_right = st.columns(2)
        with res_col_left:
            st.write("**Competency Levels**")
            chart_data = pd.DataFrame({
                "Metric": ["CGPA", "Projects", "Skills", "DSA"],
                "Score": [cgpa*10, projects*20, len(resume_skills)*20, dsa_score*10]
            })
            st.bar_chart(chart_data.set_index("Metric"))

        with res_col_right:
            st.write("**Target Company Readiness**")
            targets = {"FAANG": 1.3, "Tier-1 Startup": 1.1, "Service Based": 0.8}
            for comp, diff in targets.items():
                c_score = round(max(5, min(probability / diff, 95)), 1)
                st.write(f"**{comp}:** {c_score}% Match")
                st.progress(c_score / 100)

        # 5. Exact Next Steps
        st.subheader("🎯 Action Plan")
        if dsa_score < 7: st.info("• Practice 2 LeetCode Medium problems daily.")
        if intern_val == 0: st.info("• Focus on building 1 major Full-Stack project for your portfolio.")
        if len(resume_skills) < 4: st.info("• Learn and add cloud skills (Azure/AWS) to stay ahead.")

        st.balloons()

st.markdown("---")
st.markdown("<p style='text-align:center; opacity:0.6;'>PlacementIQ Pro2 | HackWave 2026</p>", unsafe_allow_html=True)