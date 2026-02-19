import streamlit as st
import requests
from openai import OpenAI

st.set_page_config(page_title="Developer Check", page_icon="💻", layout="wide")

# --- AI BOT SIDEBAR ---
with st.sidebar:
    st.markdown("### 🤖 Placement Assistant")
    with st.popover("💬 Ask AI", use_container_width=True):
        chat_container = st.container(height=300)
        if "messages" not in st.session_state:
            st.session_state.messages = []
        with chat_container:
            for msg in st.session_state.messages:
                st.chat_message(msg["role"]).markdown(msg["content"])
        if prompt := st.chat_input("Ask me anything..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").markdown(prompt)
            try:
                client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=st.secrets["GROQ_API_KEY"])
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                ).choices[0].message.content
                st.chat_message("assistant", avatar="✨").markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
            except Exception:
                st.error("Groq API error. Check .env file.")

# --- MAIN PAGE ---
st.title("💻 GitHub Developer Check")
st.markdown("Analyze your GitHub profile to see what recruiters think of your code.")

def analyze_github(username):
    url = f"https://api.github.com/users/{username}/repos"
    res = requests.get(url)
    if res.status_code == 200:
        repos = res.json()
        lang_stats = {}
        for r in repos:
            lang = r.get('language')
            if lang:
                lang_stats[lang] = lang_stats.get(lang, 0) + 1
        return sorted(lang_stats.items(), key=lambda x: x[1], reverse=True), len(repos)
    return None, 0

github_user = st.text_input("Enter GitHub Username", placeholder="e.g., torvalds")

if st.button("Run GitHub Analysis", type="primary") and github_user:
    with st.spinner("Scanning repositories..."):
        stats, total_repos = analyze_github(github_user)
        
        if stats is not None:
            st.markdown("### 📊 Portfolio Analysis")
            col1, col2 = st.columns(2)
            top_langs = [lang for lang, count in stats[:3]]
            
            with col1:
                st.success("✅ **Strengths**")
                st.write(f"**Top Tech Stack:** {', '.join(top_langs) if top_langs else 'N/A'}")
                st.write(f"**Project Count:** {total_repos} repositories")
                st.write("**Activity:** Active public profile")
                
            with col2:
                st.warning("⚠️ **Areas to Improve**")
                if total_repos < 5:
                    st.write("• **Portfolio Size:** Under 5 repos. Build more projects!")
                st.write("• **Documentation:** Ensure all top repos have a `README.md`.")
                st.write("• **Diversity:** Try contributing to open-source.")
                
            st.info(f"💡 **Next Step:** Your strongest language is **{top_langs[0] if top_langs else 'Coding'}**. Mention this prominently on your resume!")
        else:
            st.error("GitHub user not found or API rate limit reached.")