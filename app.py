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

# Ensure session state variables exist
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "target_role" not in st.session_state:
    st.session_state.target_role = "Software Engineer"
if "extracted_skills" not in st.session_state:
    st.session_state.extracted_skills = []
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

# ---------------- 3. GLOBAL STYLES (Pinned Logo & Modern Buttons) ----------------
st.markdown(f"""
<style>
    html, body, [class*="css"] {{ font-family: 'Segoe UI', Roboto, sans-serif; }}
    
    /* Center and Style Logo */
    .sidebar-logo-container {{
        display: flex;
        justify-content: center;
        padding-top: 20px;
        margin-bottom: -10px;
    }}
    .logo-3d {{
        width: 180px;
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
    div.stButton > button:hover {{
        transform: translateY(-2px); box-shadow: 0 8px 20px rgba(37, 99, 235, 0.3);
    }}

    /* Hero Section */
    .hero {{
        background: white; color: #1f2a44; padding: 40px; border-radius: 20px;
        text-align: center; margin-bottom: 30px; border: 1px solid #e2e8f0;
    }}
</style>
""", unsafe_allow_html=True)

# ---------------- 4. SIDEBAR (LOGO AT TOP) ----------------
# Force the logo to the absolute top of the sidebar
if img_base64:
    st.sidebar.markdown(
        f'<div class="sidebar-logo-container"><img src="data:image/png;base64,{img_base64}" class="logo-3d"></div>', 
        unsafe_allow_html=True
    )
else:
    st.sidebar.title("PlacementIQ Pro")

st.sidebar.markdown("---")

# AI Assistant in Sidebar
try:
    client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    client = None

with st.sidebar:
    st.markdown("### 🤖 Career Copilot")
    with st.popover("💬 Chat with Placement Assistant", use_container_width=True):
        chat_container = st.container(height=300)
        with chat_container:
            for message in st.session_state.messages:
                st.chat_message(message["role"]).markdown(message["content"])

        if prompt := st.chat_input("Ask about interviews, DSA, or resume tips..."):
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
    st.sidebar.info("Use the navigation above to explore LinkedIn Audit and Test Series.")

# ---------------- 5. MAIN CONTENT ----------------
st.markdown("""
<div class="hero">
    <h1 style='margin:0; color:#2563eb;'>PlacementIQ Pro2</h1>
    <p style='font-size:1.2rem; color:#64748b;'>Precision AI for modern placement readiness</p>
</div>
""", unsafe_allow_html=True)

# Main Input Layout
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### 📊 Academic Profile")
    cgpa = st.slider("Current CGPA", 5.0, 10.0, 7.5, step=0.1)
    internship = st.radio("Internship Experience", ["No", "Yes"], horizontal=True)
    intern_val = 1 if internship == "Yes" else 0
    projects = st.number_input("Major Projects", 0, 10, 2)
    dsa_score = st.select_slider("Coding Proficiency", options=range(1, 11), value=5)

with col2:
    st.markdown("### 🎯 Targeting")
    role = st.selectbox("Target Role", ["Software Engineer", "Data Scientist", "DevOps Engineer", "Cloud Architect", "Frontend Developer", "Custom"])
    st.session_state.target_role = role
    
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    
    if uploaded_file:
        with pdfplumber.open(uploaded_file) as pdf:
            text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
            st.session_state.resume_text = text
            st.success("Resume processed!")

    resume_text = st.text_area("Resume Content Preview", st.session_state.resume_text, height=150)

# ---------------- 6. ANALYSIS ----------------
if st.button("Run Placement Audit"):
    if not resume_text:
        st.warning("Please upload a resume to get accurate insights.")
    else:
        with st.spinner("Analyzing match accuracy..."):
            time.sleep(1)
            # Dummy logic for display (Update with your actual model logic)
            ready_score = min(98, (cgpa * 8) + (intern_val * 15) + (projects * 5))
            
            st.markdown(f"## Overall Readiness: {ready_score}%")
            st.progress(ready_score / 100)
            
            # Use your existing logic for skill breakdowns and company targets here...
            st.balloons()