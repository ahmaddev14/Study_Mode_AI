# streamlit_app.py
import streamlit as st
import os
import google.generativeai as genai
import PyPDF2
import docx

# ================== Page Config ==================
st.set_page_config(page_title="Study_mode AI", page_icon="📘", layout="wide")

# ================== API Key ==================
def get_api_key():
    if "GEMINI_API_KEY" in st.secrets:  # Streamlit Cloud secrets
        return st.secrets["GEMINI_API_KEY"]
    return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

API_KEY = get_api_key()
if not API_KEY:
    st.error("❌ Gemini API key not found. Add it in .streamlit/secrets.toml (local) or Streamlit Cloud → Secrets.")
else:
    genai.configure(api_key=API_KEY)

# ================== File Reader ==================
def extract_text(file):
    if file.type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text

    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(file)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text

    elif file.type in ["text/plain", "text/markdown"]:
        return file.read().decode("utf-8")

    else:
        return ""

# ================== Header ==================
st.markdown(
    """
    <div style='text-align:center; padding-top:12px;'>
      <h1 style='color:#1E88E5; font-size:36px; margin:0;'>📘 Study_mode AI</h1>
      <p style='color:#607D8B; margin-top:6px;'>Simple • Smart • Student-Friendly</p>
    </div>
    <hr style="border:1px solid #E0E0E0; margin: 12px 0;">
    """,
    unsafe_allow_html=True,
)

# ================== Sidebar ==================
with st.sidebar:
    st.markdown("<h3 style='color:#1E88E5'>⚙️ Controls</h3>", unsafe_allow_html=True)
    if st.button("Reset Chat", use_container_width=True):
        st.session_state.messages = []
        st.experimental_rerun()
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:gray; font-size:13px;'>✨ Made by <b>Ahmad Asif</b></p>", unsafe_allow_html=True)

# ================== Session State ==================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "file_text" not in st.session_state:
    st.session_state.file_text = ""

# ================== File Upload ==================
uploaded_file = st.file_uploader("📂 Upload study material", type=["pdf", "docx", "txt", "md"])
if uploaded_file:
    st.session_state.file_text = extract_text(uploaded_file)
    if st.session_state.file_text.strip():
        st.success(f"📂 {uploaded_file.name} uploaded and processed!")
    else:
        st.error("❌ Could not extract text from this file.")

# ================== Show Chat History ==================
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(f"👤 {msg['content']}")
    else:
        with st.chat_message("assistant"):
            st.markdown(f"🤖 {msg['content']}")

# ================== Chat Input ==================
if prompt := st.chat_input("💬 Ask your study question..."):
    # Add file content if uploaded
    if st.session_state.file_text.strip():
        full_prompt = f"Here is the study material:\n\n{st.session_state.file_text}\n\nQuestion: {prompt}"
    else:
        full_prompt = prompt

    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(f"👤 {prompt}")

    # Call Gemini
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(full_prompt)
        answer = response.text if hasattr(response, "text") else str(response)
    except Exception as e:
        answer = f"[API error] {e}"

    # Show assistant message
    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.markdown(f"🤖 {answer}")
