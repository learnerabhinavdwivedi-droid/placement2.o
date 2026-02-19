import streamlit as st
import pdfplumber
from openai import OpenAI

st.set_page_config(page_title="Certificate Verifier", page_icon="📜")
st.title("📜 Certificate & Resume Matcher")

# Pull resume data from the main page
resume_text = st.session_state.get("resume_text", "")

if not resume_text:
    st.warning("⚠️ Please upload your resume on the Main PlacementIQ Page first so we can verify against it!")
    st.stop()

st.info("Upload a certificate to verify if its skills/projects are properly highlighted in your resume.")
cert_file = st.file_uploader("Upload Certificate (PDF)", type=["pdf"])

if cert_file and st.button("Verify Alignment", type="primary"):
    with st.spinner("Cross-referencing certificate with resume..."):
        cert_text = ""
        with pdfplumber.open(cert_file) as pdf:
            for page in pdf.pages:
                cert_text += page.extract_text() + " "
        
        try:
            client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=st.secrets["GROQ_API_KEY"])
            prompt = f"""
            Analyze this certificate and the candidate's resume.
            Certificate Text: {cert_text[:500]}
            Resume Text: {resume_text[:1000]}
            
            Tell the user strictly in 3 short bullet points:
            1. What skill/project the certificate proves.
            2. If that skill is clearly mentioned in their resume.
            3. How they can improve their resume based on this certificate.
            """
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            st.success("Verification Complete!")
            st.markdown(response.choices[0].message.content)
        except Exception as e:
            st.error("Error connecting to AI API. Check your Groq Key in the .env file.")