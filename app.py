import streamlit as st
import pdfplumber
import numpy as np
from groq import Groq
from sentence_transformers import SentenceTransformer
from pathlib import Path

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
DOCS_FOLDER = "docs"
GROQ_API_KEY = "API-KEY"
CHUNK_SIZE = 500

# ─────────────────────────────────────────
# CACHED RESOURCES
# ─────────────────────────────────────────
@st.cache_resource
def load_embedder():
    return SentenceTransformer("all-MiniLM-L6-v2")

@st.cache_resource
def load_groq():
    return Groq(api_key=GROQ_API_KEY)

embedder = load_embedder()
client = load_groq()

# ─────────────────────────────────────────
# CORE FUNCTIONS
# ─────────────────────────────────────────

def extract_text_from_pdfs(folder):
    all_chunks, all_sources = [], []
    for pdf_file in Path(folder).glob("*.pdf"):
        with pdfplumber.open(pdf_file) as pdf:
            full_text = ""
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
        for i in range(0, len(full_text), CHUNK_SIZE):
            chunk = full_text[i:i + CHUNK_SIZE].strip()
            if len(chunk) > 50:
                all_chunks.append(chunk)
                all_sources.append(pdf_file.name)
    return all_chunks, all_sources


def build_knowledge_base():
    chunks, sources = extract_text_from_pdfs(DOCS_FOLDER)
    if not chunks:
        return 0
    embeddings = embedder.encode(chunks)
    st.session_state.chunks = chunks
    st.session_state.sources = sources
    st.session_state.embeddings = embeddings
    return len(chunks)


def retrieve_relevant_chunks(query, n=5):
    if "embeddings" not in st.session_state or len(st.session_state.embeddings) == 0:
        return []
    query_emb = embedder.encode([query])[0]
    embeddings = st.session_state.embeddings
    dots = np.dot(embeddings, query_emb)
    norms = np.linalg.norm(embeddings, axis=1) * np.linalg.norm(query_emb)
    scores = dots / (norms + 1e-10)
    top_indices = np.argsort(scores)[::-1][:n]
    return [st.session_state.chunks[i] for i in top_indices]


def is_kb_ready():
    return "chunks" in st.session_state and len(st.session_state.chunks) > 0


def ask_focusdesk(query, exam_days=None, subject=""):
    chunks = retrieve_relevant_chunks(query)
    if not chunks:
        return "⚠️ No documents indexed yet. Click **Build Knowledge Base** in the sidebar first."

    context = "\n\n---\n\n".join(chunks)
    days_context = f"The student has {exam_days} days until their {subject} exam." if exam_days else ""

    prompt = f"""You are FocusDesk, an ADHD-friendly academic co-pilot for university students at Neil Gogte Institute of Technology (affiliated to Osmania University).

Your rules:
- NEVER give walls of text
- Always be specific and actionable
- End EVERY response with a single "⚡ YOUR NEXT ACTION:" line — one thing to do right now in the next 30 minutes
- Use bullet points, not paragraphs
- Be encouraging, not overwhelming
- Base answers ONLY on the provided university documents

{days_context}

UNIVERSITY DOCUMENTS:
{context}

STUDENT QUESTION: {query}

Respond in this exact format:
## 📚 What You Need To Know
[3-5 bullet points, most important first]

## 🎯 Priority Topics
[ranked list with why each matters, based on past paper frequency]

## 📅 Study Plan
[simple day-by-day or session breakdown]

⚡ YOUR NEXT ACTION: [one specific thing to do in the next 30 minutes]
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024
    )
    return response.choices[0].message.content


# ─────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None
if "last_response" not in st.session_state:
    st.session_state.last_response = None

# ─────────────────────────────────────────
# PAGE CONFIG & STYLES
# ─────────────────────────────────────────
st.set_page_config(page_title="FocusDesk", page_icon="✦", layout="wide")

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&display=swap');
  .stApp { background-color: #0e0e0e; color: #e8e8e8; }
  .main-header { font-family: 'Syne', sans-serif; font-size: 2.2rem; font-weight: 800; color: #c8f135; }
  .sub-header { font-size: 0.8rem; color: #555; letter-spacing: 2px; text-transform: uppercase; font-family: monospace; margin-bottom: 1.5rem; }
  .stTextInput > div > div > input { background-color: #161616 !important; color: #e8e8e8 !important; border: 1px solid #2a2a2a !important; border-radius: 10px !important; }
  .stButton > button { background-color: #c8f135 !important; color: #0e0e0e !important; border: none !important; border-radius: 8px !important; font-weight: 700 !important; }
  div[data-testid="stSidebar"] { background-color: #111 !important; border-right: 1px solid #1e1e1e; }
  .stMarkdown h2 { color: #c8f135; }
  .stMarkdown h3 { color: #3df0a0; }
  .stMarkdown li { color: #ccc; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("### ✦ FocusDesk")
    st.caption("Neil Gogte Institute of Technology")
    st.markdown("---")
    st.markdown("**⚙️ Build Knowledge Base**")
    st.caption("Run once after adding PDFs to /docs")

    if st.button("🔄 Build Knowledge Base"):
        with st.spinner("Reading and indexing your documents..."):
            count = build_knowledge_base()
        if count > 0:
            st.success(f"✅ Indexed {count} chunks!")
        else:
            st.error("❌ No PDFs found in /docs folder")

    if is_kb_ready():
        st.caption(f"📦 {len(st.session_state.chunks)} chunks ready")

    st.markdown("---")
    st.markdown("**📅 Exam Context**")
    exam_days = st.slider("Days until exam", 1, 30, 3)
    subject = st.text_input("Subject", placeholder="e.g. Data Structures")

# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
st.markdown('<div class="main-header">FocusDesk ✦</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI Academic Co-Pilot — NGIT · Osmania University</div>', unsafe_allow_html=True)

# Quick buttons
st.markdown("**Quick Questions:**")
c1, c2, c3, c4 = st.columns(4)
with c1:
    if st.button("📚 What to study today?"):
        st.session_state.pending_query = f"What should I study today if my {subject} exam is in {exam_days} days?"
with c2:
    if st.button("🎯 Top topics by frequency"):
        st.session_state.pending_query = f"What topics appear most in past {subject} papers?"
with c3:
    if st.button("📋 Important units"):
        st.session_state.pending_query = f"What are the most important units in {subject}?"
with c4:
    if st.button("⏱ 2-hour plan"):
        st.session_state.pending_query = f"Give me a 2-hour study plan for {subject} with {exam_days} days left."

st.markdown("---")

query = st.text_input(
    "Or ask anything directly...",
    placeholder="e.g. What should I study today if my exam is in 3 days?"
)
ask_btn = st.button("⚡ Ask FocusDesk")

# Determine query to run
current_query = None
if ask_btn and query:
    current_query = query
elif st.session_state.pending_query:
    current_query = st.session_state.pending_query
    st.session_state.pending_query = None

# Run
if current_query:
    if not is_kb_ready():
        st.warning("⚠️ Please build the knowledge base first using the sidebar button.")
    else:
        with st.spinner("Thinking..."):
            response = ask_focusdesk(current_query, exam_days=exam_days, subject=subject)
        st.session_state.last_response = {"q": current_query, "a": response}
        st.session_state.history.append({"q": current_query, "a": response})
elif not is_kb_ready():
    st.info("👆 First time? Click **Build Knowledge Base** in the sidebar to index your documents.")

# Show latest response
if st.session_state.last_response:
    st.markdown("---")
    st.markdown(f"**You asked:** {st.session_state.last_response['q']}")
    st.markdown("### ✦ FocusDesk says:")
    st.markdown(st.session_state.last_response["a"])

# History
if len(st.session_state.history) > 1:
    st.markdown("---")
    st.markdown("**Previous Questions:**")
    for item in reversed(st.session_state.history[:-1]):
        with st.expander(f"💬 {item['q']}"):
            st.markdown(item["a"])