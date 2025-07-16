import streamlit as st
import google.generativeai as genai
# ==== CSS ====
def load_css(file_path):
    with open(file_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load the custom style
load_css("style.css")



st.set_page_config(page_title="THESIS-X | Hypothesis Falsifier", layout="centered")

# ==== Header ====
st.markdown('<h1 class="logo">THESIS-X</h1>', unsafe_allow_html=True)
st.markdown('<p class="tagline">Ask any topic and get a critique-ready hypothesis assessment.</p>', unsafe_allow_html=True)

# ==== Gemini API Key ====
api_key = st.secrets.get("GEMINI_API_KEY") or st.text_input("Enter Gemini API Key", type="password", label_visibility="collapsed")
if api_key:
    genai.configure(api_key=api_key)

# ==== Handle Input ====
if "show_result" not in st.session_state:
    st.session_state.show_result = False



# === Hypothesis Entry Page ===
if not st.session_state.show_result:
    uploaded_file = st.file_uploader("📄 Upload Hypothesis (.txt)", type=["txt"])

    with st.container():
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        col1, col2 = st.columns([6, 1])
        with col1:
            user_hypothesis = st.text_input("Enter hypothesis", label_visibility="collapsed", placeholder="Enter hypothesis here...")
        with col2:
            submit = st.button("➤", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if api_key and (uploaded_file or (submit and user_hypothesis.strip())):
        if uploaded_file:
            st.session_state.hypothesis_text = uploaded_file.read().decode("utf-8").strip()
        else:
            st.session_state.hypothesis_text = user_hypothesis.strip()

        st.session_state.show_result = True
        st.rerun()

# === Result Page ===
if st.session_state.show_result and api_key:
    st.subheader("Your Hypothesis")
    st.code(st.session_state.hypothesis_text)

    prompt = f"""
You are a scientific assistant AI tasked with falsifying hypotheses.
Given the following hypothesis:

\"\"\"{st.session_state.hypothesis_text}\"\"\"

Your tasks are:
1. Identify logical flaws or weaknesses, if any.
2. Present known theories, historical data, or principles that might contradict it.
3. Suggest a possible experimental design or observation that could test (falsify) this hypothesis.
4. Play devil’s advocate: argue as if trying to disprove it rigorously.
5. Suggest how this hypothesis could be refined to be more robust or testable.

Make the output structured with **headings** and examples.
"""

    try:
        model = genai.GenerativeModel("models/gemma-3-27b-it")
        with st.spinner("Falsifying hypothesis..."):
            response = model.generate_content(prompt)
        st.success(" Analysis complete")
        st.markdown(response.text)
    except Exception as e:
        st.error(f" Error: {e}")
