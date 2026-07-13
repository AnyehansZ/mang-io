import streamlit as st
from utils.gmail import get_gmail_service, fetch_emails

st.set_page_config(page_title="Email AI Assistant", page_icon="📧", layout="wide")

if 'service' not in st.session_state:
    st.session_state.service = None
if 'emails' not in st.session_state:
    st.session_state.emails = []
if 'summarizer' not in st.session_state:
    st.session_state.summarizer = None
if 'search_index' not in st.session_state:
    st.session_state.search_index = None

st.title("📧 Email AI Assistant")

with st.sidebar:
    st.header("Connection")
    if st.session_state.service is None:
        if st.button("Connect to Gmail"):
            with st.spinner("Opening login window..."):
                st.session_state.service = get_gmail_service()
            st.rerun()
    else:
        st.success("Connected to Gmail")

    st.header("Fetch")
    max_results = st.slider("Number of emails", 5, 50, 20)
    if st.session_state.service and st.button("Fetch Emails"):
        with st.spinner(f"Fetching {max_results} emails..."):
            st.session_state.emails = fetch_emails(
                st.session_state.service,
                max_results=max_results,
                min_body_length=50
            )
        st.success(f"Fetched {len(st.session_state.emails)} emails")

if not st.session_state.service:
    st.info("Connect to Gmail from the sidebar to get started.")
    st.stop()

if not st.session_state.emails:
    st.info("Click 'Fetch Emails' in the sidebar.")
    st.stop()

tab_inbox, tab_summarize, tab_search = st.tabs(["Inbox", "Summarize", "Search"])

with tab_inbox:
    for email in st.session_state.emails:
        with st.expander(f"{email['subject']} — {email['sender']}"):
            st.caption(email['date'])
            st.write(email['body'][:1000])

with tab_summarize:
    if st.button("Summarize All"):
        if st.session_state.summarizer is None:
            with st.spinner("Loading summarization model (first run downloads ~1.6GB)..."):
                from summarize_inbox import load_summarizer
                st.session_state.summarizer = load_summarizer()

        tokenizer, model = st.session_state.summarizer
        from summarize_inbox import summarize

        for email in st.session_state.emails:
            with st.spinner(f"Summarizing: {email['subject']}"):
                summary = summarize(email['body'], tokenizer, model)
            st.markdown(f"**{email['subject']}**")
            st.write(summary)
            st.divider()

with tab_search:
    if st.session_state.search_index is None:
        if st.button("Build Search Index"):
            with st.spinner("Loading embedding model and indexing..."):
                from search_email import build_search_index
                st.session_state.search_index = build_search_index(st.session_state.emails)
            st.rerun()
    else:
        query = st.text_input("Search your inbox by meaning")
        if query:
            from search_email import search
            model, collection = st.session_state.search_index
            results = search(query, model, collection, top_k=5)

            if not results['ids'][0]:
                st.write("No matching emails found.")
            else:
                for i in range(len(results['ids'][0])):
                    metadata = results['metadatas'][0][i]
                    body = results['documents'][0][i]
                    distance = results['distances'][0][i] if 'distances' in results else None
                    relevance = max(0, int((1 - distance / 2) * 100)) if distance is not None else "?"

                    st.markdown(f"**{metadata['subject']}** — {relevance}% match")
                    st.caption(f"From: {metadata['sender']} · {metadata['date']}")
                    st.write(body[:200] + "...")
                    st.divider()