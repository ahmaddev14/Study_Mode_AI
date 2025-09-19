import streamlit as st
import os
import google.generativeai as genai

# --- Page Config
st.set_page_config(page_title="Ahmad Study_Mode AI", page_icon="📘", layout="wide")

# --- Get API key
def get_api_key():
    if "GEMINI_API_KEY" in st.secrets:
        return st.secrets["GEMINI_API_KEY"]
    return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

API_KEY = get_api_key()

if not API_KEY:
    st.error("❌ Gemini API key not found. Add it in `.streamlit/secrets.toml` or env vars.")
else:
    genai.configure(api_key=API_KEY)

# --- Header
st.markdown(
    """
    <div style='text-align: center; padding: 10px;'>
        <h1 style='color: #2196F3; font-weight: 700; font-size: 38px; margin-bottom: 5px;'>
            📘 Study_Mode AI
        </h1>
        <p style='color: #607D8B; font-size: 18px; margin-top:0;'>
            Simple • Smart • Student-Friendly
        </p>
    </div>
    <hr style="border:1px solid #E0E0E0; margin: 15px 0;">
    """,
    unsafe_allow_html=True,
)

# --- File Upload (clean, no text label)
uploaded_file = st.file_uploader("", type=["pdf", "docx", "txt", "md"], label_visibility="collapsed")

if uploaded_file:
    st.success(f"📂 `{uploaded_file.name}` uploaded successfully!")

# --- Sidebar (minimal & student-friendly)
with st.sidebar:
    st.markdown(
        """
        <div style='text-align: center;'>
            <h3 style='color:#2196F3; font-size:20px;'>⚙️ Controls</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    enable_ref = st.toggle("External References", value=True)

    if st.button("Reset Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown(
        """
        <hr style="border:0.5px solid #E0E0E0;">
        <p style='text-align:center; color:gray; font-size:13px;'>
            ✨ Made by <b>Ahmad Asif</b>
        </p>
        """,
        unsafe_allow_html=True,
    )

# --- Chat State
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Display Messages
for msg in st.session_state.messages:
    role, content = msg["role"], msg["content"]
    if role == "user":
        st.chat_message("user").markdown(f"👤 {content}")
    else:
        st.chat_message("assistant").markdown(f"🤖 {content}")

# --- Chat Input
if question := st.chat_input("💬 Ask your study question..."):
    st.session_state.messages.append({"role": "user", "content": question})
    st.chat_message("user").markdown(f"👤 {question}")

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(question)
        answer = response.text

        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.chat_message("assistant").markdown(f"🤖 {answer}")

    except Exception as e:
        st.error(f"⚠️ Error: {e}")
