import streamlit as st
import pdfplumber
import os
import google.generativeai as genai
import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path
from google import genai

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
DOCS_FOLDER = "docs"
GEMINI_API_KEY = "AIzaSyB3J5-vVP02sAti_KL7bzp4fnhmbxGD8pw"  # 🔑 Replace this
COLLECTION_NAME = "focusdesk"
CHUNK_SIZE = 500  # characters per chunk

# ─────────────────────────────────────────
# SETUP
# ─────────────────────────────────────────
genai.configure(api_key=GEMINI_API_KEY)
gemini = genai.GenerativeModel("gemini-1.5-flash")
embedder = SentenceTransformer("all-MiniLM-L6-v2")
chroma_client = chromadb.PersistentClient(path="./chroma_store")

# ─────────────────────────────────────────
# FUNCTIONS
# ─────────────────────────────────────────

def extract_text_from_pdfs(folder):
    """Extract all text from PDFs in the docs folder."""
    all_chunks = []
    all_sources = []
    for pdf_file in Path(folder).glob("*.pdf"):
        with pdfplumber.open(pdf_file) as pdf:
            full_text = ""
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
        # Chunk the text
        for i in range(0, len(full_text), CHUNK_SIZE):
            chunk = full_text[i:i + CHUNK_SIZE].strip()
            if len(chunk) > 50:  # skip tiny chunks
                all_chunks.append(chunk)
                all_sources.append(pdf_file.name)
    return all_chunks, all_sources


def build_knowledge_base():
    """Embed all PDF chunks and store in ChromaDB."""
    try:
        chroma_client.delete_collection(COLLECTION_NAME)
    except:
        pass
    collection = chroma_client.create_collection(COLLECTION_NAME)
    chunks, sources = extract_text_from_pdfs(DOCS_FOLDER)
    if not chunks:
        return 0
    embeddings = embedder.encode(chunks).tolist()
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"source": src} for src in sources]
    collection.add(documents=chunks, embeddings=embeddings, ids=ids, metadatas=metadatas)
    return len(chunks)


def get_collection():
    """Get the ChromaDB collection."""
    try:
        return chroma_client.get_collection(COLLECTION_NAME)
    except:
        return None


def retrieve_relevant_chunks(query, n=5):
    """Find the most relevant chunks for a query."""
    collection = get_collection()
    if not collection:
        return []
    query_embedding = embedder.encode([query]).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=n)
    return results["documents"][0] if results["documents"] else []


def ask_focusdesk(query, exam_days=None):
    """Send query + relevant context to Gemini and get a structured response."""
    chunks = retrieve_relevant_chunks(query)
    if not chunks:
        return "⚠️ No documents found. Please build the knowledge base first."

    context = "\n\n---\n\n".join(chunks)
    days_context = f"The student has {exam_days} days until their exam." if exam_days else ""

    prompt = f"""You are FocusDesk, an ADHD-friendly academic co-pilot for university students.

Your rules:
- NEVER give walls of text
- Always be specific and actionable
- Structure every response with clear sections
- End EVERY response with a single "⚡ YOUR NEXT ACTION:" line — one thing to do right now
- Use bullet points, not paragraphs
- Be encouraging, not overwhelming

{days_context}

UNIVERSITY DOCUMENTS (use ONLY this to answer):
{context}

STUDENT QUESTION: {query}

Respond in this exact format:
## 📚 What You Need To Know
[3-5 bullet points, most important first]

## 🎯 Priority Topics
[ranked list with why each matters]

## 📅 Suggested Study Plan
[simple day-by-day breakdown if relevant]

⚡ YOUR NEXT ACTION: [one single specific thing to do in the next 30 minutes]
"""

    response = gemini.generate_content(prompt)
    return response.text


# ─────────────────────────────────────────
# STREAMLIT UI
# ─────────────────────────────────────────

st.set_page_config(
    page_title="FocusDesk",
    page_icon="✦",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&display=swap');

    .stApp { background-color: #0e0e0e; color: #e8e8e8; }

    .main-header {
        font-family: 'Syne', sans-serif;
        font-size: 2.2rem;
        font-weight: 800;
        color: #c8f135;
        margin-bottom: 0;
    }

    .sub-header {
        font-size: 0.85rem;
        color: #555;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 2rem;
        font-family: monospace;
    }

    .next-action-box {
        background: linear-gradient(135deg, rgba(200,241,53,0.08), rgba(61,240,160,0.04));
        border: 1px solid rgba(200,241,53,0.3);
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 1.5rem;
    }

    .stTextInput > div > div > input {
        background-color: #161616 !important;
        color: #e8e8e8 !important;
        border: 1px solid #2a2a2a !important;
        border-radius: 10px !important;
        font-size: 14px !important;
    }

    .stButton > button {
        background-color: #c8f135 !important;
        color: #0e0e0e !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        padding: 0.5rem 1.5rem !important;
    }

    .stButton > button:hover {
        opacity: 0.85 !important;
    }

    .stMarkdown h2 { color: #c8f135; font-size: 1rem; }
    .stMarkdown h3 { color: #3df0a0; font-size: 0.95rem; }
    .stMarkdown li { color: #ccc; margin-bottom: 4px; }
    .stMarkdown strong { color: #fff; }

    div[data-testid="stSidebar"] {
        background-color: #111 !important;
        border-right: 1px solid #1e1e1e;
    }

    .stSelectbox label, .stSlider label, .stNumberInput label {
        color: #888 !important;
        font-size: 12px !important;
        font-family: monospace !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
    }
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ──
with st.sidebar:
    st.markdown("### ✦ FocusDesk")
    st.markdown("---")

    st.markdown("**📍 University**")
    st.caption("Neil Gogte Institute of Technology")

    st.markdown("---")
    st.markdown("**⚙️ Admin: Build Knowledge Base**")
    st.caption("Run once after adding new documents to /docs")

    if st.button("🔄 Build Knowledge Base"):
        with st.spinner("Reading your documents..."):
            count = build_knowledge_base()
        if count > 0:
            st.success(f"✅ Indexed {count} chunks from your documents!")
        else:
            st.error("❌ No PDFs found in /docs folder")

    collection = get_collection()
    if collection:
        try:
            st.caption(f"📦 {collection.count()} chunks indexed")
        except:
            st.caption("📦 Knowledge base ready")

    st.markdown("---")
    st.markdown("**📅 Exam Context**")
    exam_days = st.slider("Days until exam", 1, 30, 3)
    subject = st.text_input("Subject", placeholder="e.g. Data Structures")

# ── MAIN ──
st.markdown('<div class="main-header">FocusDesk ✦</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI Academic Co-Pilot — Neil Gogte Institute of Technology</div>', unsafe_allow_html=True)

# Quick action chips
st.markdown("**Quick Questions:**")
col1, col2, col3, col4 = st.columns(4)
quick_query = None
with col1:
    if st.button("📚 What to study today?"):
        quick_query = f"What should I study today if my {subject} exam is in {exam_days} days?"
with col2:
    if st.button("🎯 Top topics by frequency"):
        quick_query = f"What topics appear most frequently in past {subject} papers?"
with col3:
    if st.button("📋 Important units"):
        quick_query = f"What are the most important units in the {subject} syllabus?"
with col4:
    if st.button("⏱ 2-hour session plan"):
        quick_query = f"Give me a focused 2-hour study plan for {subject} with {exam_days} days left."

st.markdown("---")

# Chat input
query = st.text_input(
    "Ask anything about your exams, syllabus, or past papers...",
    value=quick_query if quick_query else "",
    placeholder="e.g. What should I study today if my exam is in 3 days?"
)

ask_col, _ = st.columns([1, 5])
with ask_col:
    ask_btn = st.button("⚡ Ask FocusDesk")

# Response
if ask_btn and query:
    with st.spinner("Thinking..."):
        response = ask_focusdesk(
            query,
            exam_days=exam_days if exam_days else None
        )
    st.markdown("---")
    st.markdown("### ✦ FocusDesk says:")
    st.markdown(response)

elif not collection and not ask_btn:
    st.info("👆 First time? Click **'Build Knowledge Base'** in the sidebar to index your documents.")

# Chat history (session state)
if "history" not in st.session_state:
    st.session_state.history = []

if ask_btn and query:
    st.session_state.history.append({"q": query, "a": response})

if st.session_state.history:
    st.markdown("---")
    st.markdown("**Previous Questions This Session:**")
    for item in reversed(st.session_state.history[:-1]):
        with st.expander(f"💬 {item['q']}"):
            st.markdown(item["a"])