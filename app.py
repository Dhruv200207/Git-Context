
import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000"
API_URL = f"{API_BASE}/ask"
INDEX_URL = f"{API_BASE}/index"

st.set_page_config(
    page_title="GitContext | Developer Copilot",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.stApp {
    background: #0b1020;
    color: #e5e7eb;
    font-family: 'Inter', sans-serif;
}

header[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    max-width: 1150px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

[data-testid="stSidebar"] {
    background: #101729;
    border-right: 1px solid #263249;
}

[data-testid="stSidebar"] * {
    color: #dbe4f0;
}

.hero {
    background: linear-gradient(120deg, #172554, #18213b 60%, #21183f);
    border: 1px solid #34466d;
    border-radius: 22px;
    padding: 30px;
    margin-bottom: 24px;
}

.hero-label {
    color: #93c5fd;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
}

.hero h1 {
    color: #ffffff;
    font-size: 38px;
    font-weight: 800;
    margin: 10px 0;
}

.hero p {
    color: #c4d2e8;
    font-size: 15px;
    margin-bottom: 0;
    line-height: 1.7;
}

.section-heading {
    color: #f1f5f9;
    font-size: 19px;
    font-weight: 700;
    margin: 22px 0 12px 0;
}

.feature-card {
    background: #111a2d;
    border: 1px solid #263752;
    border-radius: 15px;
    padding: 17px;
    min-height: 125px;
}

.feature-icon {
    font-size: 24px;
}

.feature-title {
    color: #f1f5f9;
    font-weight: 700;
    margin-top: 9px;
}

.feature-desc {
    color: #9caec8;
    font-size: 12px;
    margin-top: 5px;
    line-height: 1.6;
}

div[data-testid="stChatMessage"] {
    background: #111a2d;
    border: 1px solid #263752;
    border-radius: 15px;
    padding: 15px;
    margin-bottom: 12px;
}

.stChatInputContainer {
    border-color: #34466d !important;
}

.stChatInputContainer textarea {
    color: #f8fafc !important;
}

.stButton > button {
    background: #17243b;
    color: #e0eaff;
    border: 1px solid #34466d;
    border-radius: 12px;
    min-height: 43px;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    background: #24395e;
    border-color: #60a5fa;
    color: white;
}

div[data-testid="stMetric"] {
    background: #111a2d;
    border: 1px solid #263752;
    padding: 15px;
    border-radius: 13px;
}

div[data-testid="stMetricLabel"] {
    color: #9caec8;
}

hr {
    border-color: #263752;
}

.small-note {
    color: #8fa2bd;
    font-size: 12px;
    text-align: center;
    padding-top: 20px;
}
</style>
""", unsafe_allow_html=True)


# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("## 🧠 GitContext")
    st.caption("DEVELOPER COPILOT")
    st.divider()

    st.markdown("### Navigation")
    st.markdown("💬  Codebase Chat")
    st.markdown("🔎  Semantic Search")
    st.markdown("📚  Repository Insights")

    st.divider()

    st.markdown("### ⚙️ Backend Status")

    try:
        health_response = requests.get(
            f"{API_BASE}/health",
            timeout=3,
        )
        if health_response.ok:
            st.success("API Connected")
        else:
            st.warning("API is responding with an issue")
    except requests.exceptions.RequestException:
        st.error("API Offline")

    st.caption("Local development mode")

    st.divider()

    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.caption("Built with Streamlit • FastAPI • Qdrant • Groq")


# ---------------- HERO ----------------
st.markdown("""
<div class="hero">
    <div class="hero-label">AI-powered code intelligence</div>
    <h1>Understand your codebase.</h1>
    <p>
        Ask questions about your indexed GitHub repository.
        Find relevant code and get AI-generated explanations
        without manually searching through every file.
    </p>
</div>
""", unsafe_allow_html=True)


# -------- Repository Selector --------

st.markdown("## 📦 Repository Manager")
st.caption(
    "Connect a public GitHub repository and index its Python code."
)

with st.container(border=True):
    col1, col2 = st.columns(2)

    with col1:
        repo_owner = st.text_input(
            "GitHub Owner",
            placeholder="e.g. tiangolo",
            key="repo_owner",
        )

    with col2:
        repo_name = st.text_input(
            "Repository Name",
            placeholder="e.g. fastapi",
            key="repo_name",
        )

    st.warning(
        "Indexing a new repository replaces the current Qdrant index."
    )

    confirm_replace = st.checkbox(
        "I understand that the existing index will be replaced.",
        key="confirm_replace",
    )

    if st.button(
        "🚀 Index Repository",
        use_container_width=True,
        disabled=not confirm_replace,
    ):
        if not repo_owner.strip() or not repo_name.strip():
            st.error("Enter both GitHub owner and repository name.")

        else:
            try:
                with st.spinner(
                    "Fetching files, creating chunks and indexing..."
                ):
                    response = requests.post(
                        INDEX_URL,
                        json={
                            "owner": repo_owner.strip(),
                            "repo": repo_name.strip(),
                        },
                        timeout=300,
                    )

                if response.ok:
                    result = response.json()

                    st.success(
                        f"Indexed {result['repository']} successfully!"
                    )

                    metric1, metric2, metric3 = st.columns(3)

                    metric1.metric(
                        "Files Processed",
                        result["files_processed"],
                    )
                    metric2.metric(
                        "Chunks Created",
                        result["chunks_created"],
                    )
                    metric3.metric(
                        "Files Failed",
                        result["files_failed"],
                    )

                    st.info(
                        f"Branch: {result['branch']} | "
                        f"Files selected: {result['files_selected']}"
                    )

                    st.caption(
                        "Your next codebase question will use "
                        "the newly indexed repository."
                    )

                else:
                    try:
                        detail = response.json().get(
                            "detail", response.text
                        )
                    except ValueError:
                        detail = response.text

                    st.error(f"Indexing failed: {detail}")

            except requests.exceptions.Timeout:
                st.error(
                    "Indexing timed out. Check the backend terminal "
                    "before trying again."
                )

            except requests.exceptions.RequestException as error:
                st.error(
                    f"Could not connect to the GitContext API: {error}"
                )

# -------- End Repository Selector --------


# ---------------- FEATURE CARDS ----------------
st.markdown(
    '<div class="section-heading">Your developer workspace</div>',
    unsafe_allow_html=True,
)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🔍</div>
        <div class="feature-title">Semantic Search</div>
        <div class="feature-desc">
            Retrieve code chunks related to your question.
        </div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🧠</div>
        <div class="feature-title">AI Explanations</div>
        <div class="feature-desc">
            Understand code behaviour in natural language.
        </div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🐙</div>
        <div class="feature-title">GitHub Context</div>
        <div class="feature-desc">
            Ask questions about the repository you indexed.
        </div>
    </div>
    """, unsafe_allow_html=True)


# ---------------- CHAT ----------------
st.markdown(
    '<div class="section-heading">💬 Chat with your codebase</div>',
    unsafe_allow_html=True,
)

st.caption(
    "Try a suggested question or enter your own below."
)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Suggested prompts
p1, p2 = st.columns(2)

with p1:
    if st.button(
        "🔹 How does FastAPI validate requests?",
        use_container_width=True,
    ):
        st.session_state.pending_question = (
            "How does FastAPI validate request data?"
        )

with p2:
    if st.button(
        "🔹 Explain Python routing",
        use_container_width=True,
    ):
        st.session_state.pending_question = (
            "Explain how routing works in this codebase."
        )


# Show conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


def ask_backend(question):
    """Send a question to the FastAPI backend."""
    try:
        response = requests.post(
            API_URL,
            json={"question": question},
            timeout=120,
        )

        if response.ok:
            data = response.json()
            return data.get("answer", "The API returned no answer.")

        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text

        return f"**API Error ({response.status_code})**\n\n{detail}"

    except requests.exceptions.ConnectionError:
        return (
            "Cannot connect to the backend. Start FastAPI in another "
            "terminal using `python -m uvicorn src.api.main:app --reload`."
        )

    except requests.exceptions.Timeout:
        return (
            "The request timed out. Check the backend and try again."
        )

    except requests.exceptions.RequestException as error:
        return f"Request failed: {error}"


# Handle either typed or suggested question
typed_question = st.chat_input(
    "Ask about functions, classes, routing, or code behaviour..."
)

question = typed_question

if not question and "pending_question" in st.session_state:
    question = st.session_state.pop("pending_question")

if question:
    st.session_state.messages.append(
        {"role": "user", "content": question}
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching code and thinking..."):
            answer = ask_backend(question)

        st.markdown(answer)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )

st.markdown("""
<div class="small-note">
    GitContext · Codebase Intelligence · Local Development
</div>
""", unsafe_allow_html=True)
