import streamlit as st
import json
from openai import OpenAI

st.set_page_config(page_title="AI Mock Test", page_icon="🧠", layout="wide")

# --- AI BOT SIDEBAR ---
try:
    client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    client = None

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
            if client:
                try:
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                    ).choices[0].message.content
                    st.chat_message("assistant", avatar="✨").markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.rerun()
                except Exception:
                    st.error("API error.")
            else:
                st.error("API Key missing.")

# --- INITIALIZE TEST STATES ---
# We need to lock the questions in memory so they don't disappear when the user clicks an answer
if "mcq_test_data" not in st.session_state:
    st.session_state.mcq_test_data = None
if "test_submitted" not in st.session_state:
    st.session_state.test_submitted = False

# --- MAIN PAGE ---
st.title("🧠 Interactive AI Mock Test")
st.write("Test your knowledge instantly. The AI will generate multiple-choice questions based on your resume stack.")

target_role = st.session_state.get("target_role", "Software Engineer")
user_skills = st.session_state.get("extracted_skills", [])

if not user_skills:
    st.warning("⚠️ We didn't detect any skills from your session. Go to the Home Page and click 'Analyze Profile' first!")
    user_skills = ["Python", "Data Structures", "Problem Solving"] 

st.info(f"**Target Role:** {target_role} | **Detected Stack:** {', '.join(user_skills)}")

# --- GENERATE TEST BUTTON ---
if st.button("Generate Custom HackWave Test", type="primary"):
    with st.spinner("AI is compiling your interactive test..."):
        try:
            # We ask the LLM to reply strictly in JSON format
            prompt = f"""
            You are a technical interviewer for the role of {target_role}. 
            The candidate knows: {', '.join(user_skills)}.
            Generate a 3-question Multiple Choice Test to check their knowledge.
            
            You MUST reply strictly with a valid JSON object in this exact format. Do not add markdown blocks like ```json or any other text.
            {{
                "questions": [
                    {{
                        "question": "Question text here",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "correct_answer": "Option A",
                        "explanation": "Explanation of why this is correct."
                    }}
                ]
            }}
            """
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            
            raw_content = response.choices[0].message.content.strip()
            
            # Clean up just in case the LLM adds markdown tags
            if raw_content.startswith("```json"):
                raw_content = raw_content[7:-3].strip()
            elif raw_content.startswith("```"):
                raw_content = raw_content[3:-3].strip()

            # Parse JSON and save to session state
            test_data = json.loads(raw_content)
            st.session_state.mcq_test_data = test_data["questions"]
            st.session_state.test_submitted = False # Reset test status
            st.rerun() # Refresh the page to show the test
            
        except Exception as e:
            st.error(f"Failed to generate test. The AI might have returned invalid format. Try again! Error: {e}")

# --- DISPLAY THE INTERACTIVE TEST ---
if st.session_state.mcq_test_data:
    st.markdown("---")
    st.markdown("### 📝 Your Custom Assessment")
    
    # We use a form so the page doesn't reload on every single radio button click
    with st.form("mcq_form"):
        user_answers = {}
        for i, q in enumerate(st.session_state.mcq_test_data):
            st.markdown(f"**Q{i+1}: {q['question']}**")
            # Radio button for options
            user_answers[i] = st.radio("Select your answer:", q["options"], key=f"q_{i}", index=None)
            st.markdown("<br>", unsafe_allow_html=True)
            
        submit_test = st.form_submit_button("Submit Test & View Results")
        
        if submit_test:
            st.session_state.test_submitted = True
            st.session_state.user_answers = user_answers

# --- DISPLAY RESULTS BELOW TEST ---
if st.session_state.test_submitted:
    st.markdown("---")
    st.markdown("### 📊 Test Results")
    
    score = 0
    total = len(st.session_state.mcq_test_data)
    
    # Calculate score
    for i, q in enumerate(st.session_state.mcq_test_data):
        if st.session_state.user_answers.get(i) == q["correct_answer"]:
            score += 1
            
    # Show big metric
    st.metric(label="Final Score", value=f"{score} / {total}")
    st.progress(score / total)
    
    if score == total:
        st.success("Perfect Score! You are highly prepared for this role.")
    elif score > 0:
        st.warning("Good attempt! Review the explanations below to improve.")
    else:
        st.error("Needs work! Don't worry, read the explanations to learn the concepts.")

    st.markdown("#### Detailed Review")
    for i, q in enumerate(st.session_state.mcq_test_data):
        user_choice = st.session_state.user_answers.get(i)
        correct_choice = q["correct_answer"]
        
        with st.expander(f"Q{i+1}: {q['question']}", expanded=True):
            st.write(f"**Your Answer:** {user_choice}")
            if user_choice == correct_choice:
                st.success(f"**Correct!** {correct_choice}")
            else:
                st.error(f"**Wrong.** The correct answer was: {correct_choice}")
                
            st.info(f"**Explanation:** {q['explanation']}")