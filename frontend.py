import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:8000"

# ── Page Config — MUST be first ──────────────────────────────
st.set_page_config(
    page_title="DocMind AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════
# CUSTOM CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg:          #080b12;
    --bg2:         #0d1117;
    --bg3:         #111827;
    --card:        #131b2e;
    --card2:       #1a2540;
    --accent:      #4f8ef7;
    --accent2:     #7b61ff;
    --glow:        rgba(79,142,247,0.18);
    --glow2:       rgba(123,97,255,0.18);
    --txt:         #e2e8f8;
    --txt2:        #8895b3;
    --txt3:        #4a5568;
    --border:      rgba(255,255,255,0.06);
    --border2:     rgba(79,142,247,0.35);
    --success:     #10b981;
    --warning:     #f59e0b;
    --error:       #f87171;
    --radius:      14px;
    --radius-sm:   8px;
    --shadow:      0 4px 24px rgba(0,0,0,0.4);
}

/* ── Base ─────────────────────────────────────────────────── */
* { box-sizing: border-box; margin: 0; padding: 0; }

html, body, .stApp {
    background: var(--bg) !important;
    font-family: 'DM Sans', sans-serif !important;
    color: var(--txt) !important;
}

#MainMenu, footer, header, .stDeployButton { display: none !important; }

::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--accent); border-radius: 99px; }

/* ── Sidebar ──────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 1.6rem 1.2rem 1.2rem !important;
}

/* ── Main block container ─────────────────────────────────── */
.main .block-container {
    padding: 0 2.5rem 1rem 2.5rem !important;
    max-width: 860px !important;
}

/* ── Buttons ──────────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
    color: #fff !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    padding: 0.6rem 1.2rem !important;
    width: 100% !important;
    letter-spacing: 0.01em !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 0 18px var(--glow) !important;
    cursor: pointer !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 0 28px var(--glow) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── File Uploader ────────────────────────────────────────── */
[data-testid="stFileUploader"] section {
    background: var(--card) !important;
    border: 1.5px dashed var(--border2) !important;
    border-radius: var(--radius) !important;
    transition: all 0.2s !important;
}
[data-testid="stFileUploader"] section:hover {
    background: var(--card2) !important;
    border-color: var(--accent) !important;
    box-shadow: 0 0 20px var(--glow) !important;
}
[data-testid="stFileUploader"] section p,
[data-testid="stFileUploader"] section span { color: var(--txt2) !important; font-size: 0.82rem !important; }
[data-testid="stFileUploader"] section button {
    background: var(--card2) !important;
    color: var(--accent) !important;
    border: 1px solid var(--border2) !important;
    border-radius: var(--radius-sm) !important;
    font-size: 0.78rem !important;
}

/* ── Chat Input ───────────────────────────────────────────── */
[data-testid="stChatInput"] {
    background: var(--bg2) !important;
    border-top: 1px solid var(--border) !important;
    padding: 1rem 2.5rem 1.2rem !important;
}
[data-testid="stChatInput"] > div {
    background: var(--card) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 12px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stChatInput"] > div:focus-within {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--glow) !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: var(--txt) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    caret-color: var(--accent) !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: var(--txt3) !important; }
[data-testid="stChatInput"] button {
    background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
    border-radius: 8px !important;
    color: white !important;
}

/* ── Chat Messages ────────────────────────────────────────── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 0.3rem 0 !important;
}

/* ── Alerts ───────────────────────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: var(--radius-sm) !important;
    font-size: 0.83rem !important;
}

/* ── Spinner ──────────────────────────────────────────────── */
.stSpinner > div > div { border-top-color: var(--accent) !important; }

/* ── Divider ──────────────────────────────────────────────── */
hr { border-color: var(--border) !important; margin: 1.2rem 0 !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════
if "messages" not in st.session_state:
    st.session_state.messages = []
if "ingested" not in st.session_state:
    st.session_state.ingested = []

# Load ingested file list from backend on first page load
# so it persists even after browser refresh
if "docs_loaded" not in st.session_state:
    try:
        resp = requests.get(f"{BACKEND_URL}/documents", timeout=5)
        if resp.status_code == 200:
            st.session_state.ingested = resp.json().get("documents", [])
    except Exception:
        pass  # backend not running yet — silently skip
    st.session_state.docs_loaded = True


# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:

    # ── Branding ──────────────────────────────────────────────
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;padding-bottom:1.4rem;border-bottom:1px solid rgba(255,255,255,0.06);margin-bottom:1.4rem">
        <div style="width:40px;height:40px;background:linear-gradient(135deg,#4f8ef7,#7b61ff);border-radius:10px;
                    display:flex;align-items:center;justify-content:center;font-size:19px;box-shadow:0 0 16px rgba(79,142,247,0.4)">
            🧠
        </div>
        <div>
            <div style="font-family:'Syne',sans-serif;font-size:1.15rem;font-weight:800;color:#e2e8f8;letter-spacing:-0.02em">
                DocMind
            </div>
            <div style="font-size:0.62rem;color:#4f8ef7;background:rgba(79,142,247,0.12);padding:2px 7px;
                        border-radius:4px;font-weight:600;letter-spacing:0.08em;display:inline-block;margin-top:1px">
                RAG · AI
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Upload Section ─────────────────────────────────────────
    st.markdown("""
    <div style="font-size:0.62rem;font-weight:600;text-transform:uppercase;letter-spacing:0.12em;
                color:#4a5568;margin-bottom:0.7rem">
        📂 &nbsp; Upload Documents
    </div>
    """, unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "PDF files",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if uploaded_files:
        st.markdown(f"""
        <div style="font-size:0.75rem;color:#8895b3;margin:0.5rem 0 0.7rem;padding-left:2px">
            {len(uploaded_files)} file(s) ready to upload
        </div>
        """, unsafe_allow_html=True)

        if st.button("⬆  Upload & Process"):
            for uf in uploaded_files:
                files = {"file": (uf.name, uf.getvalue(), "application/pdf")}
                with st.spinner(f"Processing {uf.name}…"):
                    try:
                        resp = requests.post(f"{BACKEND_URL}/upload", files=files, timeout=60)
                        if resp.status_code == 200:
                            result = resp.json()
                            if result.get("status") == "duplicate":
                                st.warning(f"Already ingested: {uf.name}")
                            else:
                                if uf.name not in st.session_state.ingested:
                                    st.session_state.ingested.append(uf.name)
                                st.success(f"✓ {uf.name}")
                        else:
                            st.error(f"Failed: {uf.name}")
                    except requests.exceptions.ConnectionError:
                        st.error("Cannot connect to backend. Is it running?")

    # ── Ingested Documents List ───────────────────────────────
    if st.session_state.ingested:
        st.markdown("""
        <div style="font-size:0.62rem;font-weight:600;text-transform:uppercase;letter-spacing:0.12em;
                    color:#4a5568;margin:1.5rem 0 0.7rem">
            ✅ &nbsp; Ingested
        </div>
        """, unsafe_allow_html=True)

        for fname in st.session_state.ingested:
            short = fname if len(fname) <= 24 else fname[:21] + "…"
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:8px;padding:0.5rem 0.7rem;
                        background:#131b2e;border:1px solid rgba(255,255,255,0.06);
                        border-radius:8px;margin-bottom:5px">
                <div style="width:6px;height:6px;background:#10b981;border-radius:50%;flex-shrink:0"></div>
                <span style="font-size:0.76rem;color:#8895b3;font-family:'JetBrains Mono',monospace;
                             white-space:nowrap;overflow:hidden;text-overflow:ellipsis"
                      title="{fname}">{short}</span>
            </div>
            """, unsafe_allow_html=True)

    # ── Clear Chat ─────────────────────────────────────────────
    if st.session_state.messages:
        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
        st.divider()
        if st.button("🗑  Clear Chat"):
            st.session_state.messages = []
            st.rerun()

    # ── Footer ─────────────────────────────────────────────────
    st.markdown("""
    <div style="position:fixed;bottom:1.2rem;left:0;right:0;width:260px;padding:0 1.2rem;
                font-size:0.68rem;color:#2d3748;text-align:center">
        Powered by Ollama · ChromaDB · LangChain
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# MAIN — CHAT INTERFACE
# ══════════════════════════════════════════════════════════════

# ── Page Header ───────────────────────────────────────────────
st.markdown("""
<div style="padding: 2.2rem 0 1.4rem">
    <div style="font-family:'Syne',sans-serif;font-size:2.1rem;font-weight:800;
                color:#e2e8f8;letter-spacing:-0.03em;line-height:1.1">
        Ask your documents
    </div>
    <div style="font-size:0.88rem;color:#8895b3;margin-top:0.4rem;font-weight:300">
        Upload PDFs and get instant, sourced answers from your files.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Always-visible Document Manager ───────────────────────────
with st.expander(
    f"📂  Documents  {'· ' + str(len(st.session_state.ingested)) + ' ingested' if st.session_state.ingested else '· upload to get started'}",
    expanded=not st.session_state.messages
):

    # ── Upload area ────────────────────────────────────────────
    st.markdown("""
    <div style="font-size:0.72rem;color:#8895b3;margin-bottom:0.6rem">
        Upload one or more PDFs. Ingestion runs in background — wait ~15s before querying.
    </div>
    """, unsafe_allow_html=True)

    main_files = st.file_uploader(
        "Drop PDFs here",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        key="main_uploader"
    )

    if main_files:
        st.markdown(f"<div style='font-size:0.73rem;color:#8895b3;margin:0.3rem 0 0.4rem'>{len(main_files)} file(s) selected</div>",
                    unsafe_allow_html=True)
        if st.button("⬆  Upload & Process", key="main_upload_btn"):
            for uf in main_files:
                files = {"file": (uf.name, uf.getvalue(), "application/pdf")}
                with st.spinner(f"Processing {uf.name}…"):
                    try:
                        resp = requests.post(f"{BACKEND_URL}/upload", files=files, timeout=60)
                        if resp.status_code == 200:
                            result = resp.json()
                            if result.get("status") == "duplicate":
                                st.warning(f"Already ingested: {uf.name}")
                            else:
                                if uf.name not in st.session_state.ingested:
                                    st.session_state.ingested.append(uf.name)
                                st.success(f"✅ {uf.name} — ingestion running in background.")
                        else:
                            st.error(f"Failed: {uf.name}")
                    except requests.exceptions.ConnectionError:
                        st.error("❌ Cannot reach backend. Run:  uvicorn main:app --reload")

    # ── Ingested documents list with delete buttons ─────────────
    if st.session_state.ingested:
        st.markdown("""
        <div style="font-size:0.65rem;font-weight:600;text-transform:uppercase;
                    letter-spacing:0.1em;color:#4a5568;margin:1rem 0 0.5rem">
            Ingested Documents
        </div>
        """, unsafe_allow_html=True)

        for i, fname in enumerate(list(st.session_state.ingested)):
            short = fname if len(fname) <= 36 else fname[:33] + "…"
            col_name, col_del = st.columns([9, 1])

            with col_name:
                st.markdown(f"""
                <div style="background:#0d1117;border:1px solid rgba(255,255,255,0.07);
                            border-radius:8px;padding:0.5rem 0.8rem;
                            display:flex;align-items:center;gap:8px">
                    <div style="width:6px;height:6px;background:#10b981;
                                border-radius:50%;flex-shrink:0"></div>
                    <span style="font-size:0.75rem;color:#8895b3;
                                 font-family:'JetBrains Mono',monospace"
                          title="{fname}">{short}</span>
                </div>
                """, unsafe_allow_html=True)

            with col_del:
                if st.button("🗑", key=f"del_{i}_{fname}", help=f"Delete {fname}"):
                    try:
                        del_resp = requests.delete(
                            f"{BACKEND_URL}/document/{fname}",
                            timeout=30
                        )
                        if del_resp.status_code == 200:
                            st.session_state.ingested.remove(fname)
                            st.success(f"🗑 '{fname}' deleted.")
                            st.rerun()
                        else:
                            st.error(f"Delete failed: {del_resp.text}")
                    except requests.exceptions.ConnectionError:
                        st.error("Cannot reach backend.")

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)


# ── Chat History ───────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🧠"):

        # Message bubble styling
        if msg["role"] == "user":
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,rgba(79,142,247,0.15),rgba(123,97,255,0.15));
                        border:1px solid rgba(79,142,247,0.2);border-radius:12px 12px 2px 12px;
                        padding:0.8rem 1.1rem;display:inline-block;max-width:100%;
                        font-size:0.9rem;color:#e2e8f8;line-height:1.6">
                {msg["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="font-size:0.9rem;color:#e2e8f8;line-height:1.7;padding:0.2rem 0">
                {msg["content"]}
            </div>
            """, unsafe_allow_html=True)

            # Source cards (shown under assistant messages)
            if msg.get("sources"):
                st.markdown("""
                <div style="font-size:0.68rem;font-weight:600;text-transform:uppercase;
                            letter-spacing:0.1em;color:#4a5568;margin:0.9rem 0 0.5rem">
                    Sources
                </div>
                """, unsafe_allow_html=True)

                cols = st.columns(min(len(msg["sources"]), 3))
                for i, (col, src) in enumerate(zip(cols, msg["sources"][:3])):
                    fname = src.get("file", "Unknown")
                    page  = src.get("page", "?")
                    pg    = page + 1 if isinstance(page, int) else page
                    short = fname.split("/")[-1]
                    short = short if len(short) <= 22 else short[:19] + "…"
                    with col:
                        st.markdown(f"""
                        <div style="background:#0d1117;border:1px solid rgba(255,255,255,0.07);
                                    border-radius:8px;padding:0.6rem 0.8rem">
                            <div style="font-size:0.7rem;font-weight:600;color:#4f8ef7;
                                        margin-bottom:2px">#{i+1}</div>
                            <div style="font-size:0.72rem;color:#8895b3;font-family:'JetBrains Mono',monospace;
                                        white-space:nowrap;overflow:hidden;text-overflow:ellipsis"
                                 title="{fname}">{short}</div>
                            <div style="font-size:0.68rem;color:#4a5568;margin-top:2px">Page {pg}</div>
                        </div>
                        """, unsafe_allow_html=True)


# ── Chat Input (sticky at bottom) ─────────────────────────────
if prompt := st.chat_input("Ask anything about your documents…"):

    # Append and display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,rgba(79,142,247,0.15),rgba(123,97,255,0.15));
                    border:1px solid rgba(79,142,247,0.2);border-radius:12px 12px 2px 12px;
                    padding:0.8rem 1.1rem;display:inline-block;max-width:100%;
                    font-size:0.9rem;color:#e2e8f8;line-height:1.6">
            {prompt}
        </div>
        """, unsafe_allow_html=True)

    # Get and display assistant response
    with st.chat_message("assistant", avatar="🧠"):
        with st.spinner("Searching your documents…"):
            try:
                resp = requests.post(
                    f"{BACKEND_URL}/query",
                    json={"query": prompt},
                    timeout=120
                )
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to backend. Make sure FastAPI is running.")
                st.stop()

        if resp.status_code == 200:
            result  = resp.json()
            answer  = result.get("answer", "No answer returned.")
            sources = result.get("sources", [])

            # Answer
            st.markdown(f"""
            <div style="font-size:0.9rem;color:#e2e8f8;line-height:1.7;padding:0.2rem 0">
                {answer}
            </div>
            """, unsafe_allow_html=True)

            # Source cards
            if sources:
                st.markdown("""
                <div style="font-size:0.68rem;font-weight:600;text-transform:uppercase;
                            letter-spacing:0.1em;color:#4a5568;margin:0.9rem 0 0.5rem">
                    Sources
                </div>
                """, unsafe_allow_html=True)

                cols = st.columns(min(len(sources), 3))
                for i, (col, src) in enumerate(zip(cols, sources[:3])):
                    fname = src.get("file", "Unknown")
                    page  = src.get("page", "?")
                    pg    = page + 1 if isinstance(page, int) else page
                    short = fname.split("/")[-1]
                    short = short if len(short) <= 22 else short[:19] + "…"
                    with col:
                        st.markdown(f"""
                        <div style="background:#0d1117;border:1px solid rgba(255,255,255,0.07);
                                    border-radius:8px;padding:0.6rem 0.8rem">
                            <div style="font-size:0.7rem;font-weight:600;color:#4f8ef7;
                                        margin-bottom:2px">#{i+1}</div>
                            <div style="font-size:0.72rem;color:#8895b3;font-family:'JetBrains Mono',monospace;
                                        white-space:nowrap;overflow:hidden;text-overflow:ellipsis"
                                 title="{fname}">{short}</div>
                            <div style="font-size:0.68rem;color:#4a5568;margin-top:2px">Page {pg}</div>
                        </div>
                        """, unsafe_allow_html=True)

            # Save to history
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": sources
            })

        elif resp.status_code == 404:
            st.error("No documents ingested yet — please upload a PDF first.")
        else:
            st.error(f"Error {resp.status_code}: {resp.text}")