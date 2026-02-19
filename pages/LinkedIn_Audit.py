import streamlit as st
import time

st.set_page_config(page_title="LinkedIn Audit", page_icon="💼", layout="wide")

st.title("💼 LinkedIn Profile Optimizer")
st.write("Recruiters heavily source candidates from LinkedIn. Let's make sure your profile is fully optimized.")

st.markdown("### Profile Metrics")

col1, col2 = st.columns(2)

with col1:
    li_url = st.text_input("LinkedIn Profile URL", placeholder="linkedin.com/in/yourname")
    is_custom_url = st.checkbox("Did you customize your profile URL? (Removed the random numbers)")
    li_headline = st.selectbox("How is your Headline formatted?", [
        "Just my current title (e.g., Student at XYZ College)",
        "Title + Core Skills (e.g., B.Tech CSE | Python | React)",
        "Value Proposition (e.g., Building Scalable Systems | Incoming SDE)"
    ])
    has_about = st.checkbox("Do you have an 'About' summary longer than 3 sentences?")

with col2:
    li_conn = st.number_input("How many connections do you have?", min_value=0, step=50, value=150)
    has_featured = st.checkbox("Do you have projects linked in your 'Featured' section?")
    has_recs = st.checkbox("Do you have at least 2 written Recommendations?")
    has_photo = st.checkbox("Do you have a professional headshot AND a background banner?")

if st.button("Generate Profile Audit", type="primary"):
    with st.spinner("Analyzing LinkedIn Profile components..."):
        time.sleep(1.5)
        
        score = 0
        improvements = []
        
        # Scoring Logic
        if is_custom_url: score += 10
        else: improvements.append("Customize your URL to make it clean and professional.")
        
        if "Skills" in li_headline or "Value Proposition" in li_headline: score += 20
        else: improvements.append("Update your headline to include your target role and top skills.")
        
        if has_about: score += 15
        else: improvements.append("Write a detailed 'About' section highlighting your journey.")
        
        if li_conn >= 500: score += 20
        elif li_conn >= 150: score += 10
        else: improvements.append(f"Grow your network. You currently have {li_conn}, aim for 500+.")
        
        if has_featured: score += 15
        else: improvements.append("Pin your best GitHub repos to your 'Featured' section.")
        
        if has_recs: score += 10
        else: improvements.append("Ask for written recommendations.")
        
        if has_photo: score += 10
        else: improvements.append("Add a professional headshot and banner.")

        # Display Results
        st.markdown("---")
        
        # UI Layout for Audit and Summary
        res_col1, res_col2 = st.columns([1, 1.5])

        with res_col1:
            st.markdown(f"### Profile Strength: {score}/100")
            st.progress(score / 100)
            
            if score >= 85:
                st.success("🌟 All-Star Profile!")
            elif score >= 60:
                st.info("👍 Good Profile.")
            else:
                st.warning("⚠️ Action Needed.")
                
            st.markdown("#### 📝 Optimization Checklist")
            for item in improvements:
                st.write(f"❌ {item}")

        with res_col2:
            # NEW: Work Summary Section (The 'Same Stuff' from the Image)
            st.markdown("### 📄 Resume-Work Alignment Summary")
            with st.container(border=True):
                st.markdown(f"**Candidate:** {li_url.split('/')[-1] if li_url else 'User'}")
                st.info("Based on your profile and project data, here is your professional narrative:")
                
                # These can be dynamically generated later using an LLM API
                st.markdown("""
                * **Cloud & Infrastructure:** Strong foundation in **Azure Solutions Architecture** and DevOps workflows.
                * **DevOps Excellence:** Expertise in **CI/CD pipelines**, automation, and Infrastructure as Code.
                * **Cloud-Native Dev:** Specialized in **Kubernetes (CKAD)** for scalable application deployment.
                * **Key Project:** Leading development on **PlacementIQ Pro2**, showcasing full-stack and AI integration skills.
                * **Strategic Goal:** Optimized for roles requiring a blend of **Architecture, DevOps, and Containerization**.
                """)
                
                st.button("Download Summary as PDF", key="dl_summary")

        st.markdown("---")
        st.markdown("### 🎁 Bonus: Ready-to-Use LinkedIn Post")
        st.code("Excited to share my latest project: PlacementIQ Pro2! 🚀\nI just built an AI platform using Streamlit & Python to help students crack placements.\nLet me know what you think in the comments! 👇\n#HackWave2026 #Coding #Placement #Tech", language="text")