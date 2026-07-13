# mang-io

**mang-io** is a local-first, open-source email assistant that fetches, summarizes, and semantically searches your inbox using AI models that run entirely on your own machine. No cloud AI APIs, no paid services, no email data leaving your computer.

> ⚠️ **Status: Early development (V1 prototype).** Core features work, but the sign-in experience is not yet "friendly enough" for a non-technical user. Read the [Authentication Challenge](#the-authentication-challenge) section before you set this up — it explains why.

---

## What it does

- **Fetch** — Pull recent emails from your Gmail inbox
- **Summarize** — Condense long emails into short summaries using a local AI model (no data sent anywhere)
- **Search** — Find emails by meaning, not just keywords, using semantic vector search
- **Manage / Draft / Send** *(in progress)* — Reply to, draft, and organize emails from the tool itself

---

## The Authentication Challenge

This is the single biggest open problem in mang-io right now, and it's worth being upfront about it.

A tool like this ideally works the way people expect from any modern app: click "Sign in with Google," approve access, done. **That is not currently possible for an open-source, self-hosted, in-development project like this one**, for reasons outside our control — both realistic approaches to Gmail access come with real friction.

### Option 1: Google OAuth (Gmail API) — what mang-io uses today
This is Google's official, most secure method. But it comes with a catch: Gmail scopes are tiered by sensitivity, and reading or managing mail (`gmail.readonly`, `gmail.modify`) falls into Google's **restricted scope** tier — the same tier as apps that need a full security audit before the public can use them.

What that means in practice:
- Every user currently needs to create their own Google Cloud project and OAuth credentials (`credentials.json`) before they can use mang-io at all.
- For mang-io to offer a single "Sign in with Google" button to the public, the project itself would need to pass Google's verification process for restricted scopes, which includes a hosted privacy policy, a demo video, and a third-party **CASA security assessment** — plus annual re-certification.
- That process is realistic for a funded company, not a solo open-source tool in active development.
- **The workaround:** because each self-hosted instance of mang-io technically serves fewer than 100 users (just you), it is exempt from verification entirely. This is why the current setup asks you to create your own small Google Cloud project rather than mang-io hosting one centrally.

### Option 2: IMAP/SMTP with a Gmail App Password
The simpler alternative: skip Google Cloud entirely, use an app password with standard IMAP/SMTP.

- No Cloud Console, no OAuth screen, no verification — just a one-time 16-character password generated in your Google Account settings (requires 2-Step Verification).
- Trade-off: this only works for **personal Gmail accounts**, not Workspace/school/work accounts unless an admin explicitly allows it.
- Trade-off: app passwords are unscoped — one password can read, send, and delete, unlike OAuth's fine-grained permissions.

**Bottom line:** until mang-io either passes Google's restricted-scope review (unlikely at this stage) or standardizes fully on app passwords with proper local encryption, initial setup will require a few extra manual steps beyond "sign in and go." This README will be updated the moment that changes.

---

## Requirements

- Python 3.12
- ~4GB RAM minimum (developed and tested on a ThinkPad L470, 16GB RAM, dual-core i5-6300U, no GPU)
- No GPU required — all models run on CPU
- Internet connection for first-time model downloads only; fully offline after that

## AI Models Used

| Model | Purpose | Size | Runs via |
|---|---|---|---|
| `all-MiniLM-L6-v2` | Converts email text into meaning-vectors for semantic search | ~90 MB | `sentence-transformers` |
| `facebook/bart-large-cnn` | Summarizes long email bodies into short summaries | ~1.6 GB | `transformers` (`AutoTokenizer` + `AutoModelForSeq2SeqLM`) |

Both models download automatically the first time they're used and are cached locally afterward — no repeated downloads, no internet required once cached.

---

## Setup (current, OAuth-based)

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a project → enable the **Gmail API**
3. Configure the OAuth consent screen → External → add scope `gmail.readonly` (or `gmail.modify` if using write features)
4. Add yourself as a test user
5. Create an OAuth Client ID → Desktop app → download the JSON → rename it to `credentials.json`
6. Place `credentials.json` in the project root
7. Run any script — the first run opens a browser for login; a `token.json` is saved so future runs don't require logging in again

```bash
pip install -r requirements.txt
python fetch_email.py
```

---

## Project Structure

```
mang-io/
├── utils/
│   └── gmail.py           # Shared OAuth login, fetch, and parsing logic
├── fetch_email.py          # Fetch and display recent emails
├── summarize_inbox.py      # Fetch + AI summarization pipeline
├── search_email.py         # Fetch + semantic search over inbox
├── ai-model.py              # Standalone summarization test harness
├── app.py                   # Streamlit dashboard (Inbox / Summarize / Search)
├── credentials.json         # Your Google OAuth credentials (not committed)
├── token.json                # Auto-generated session token (not committed)
└── requirements.txt
```

---

## Design Philosophy

- **Local-first** — all AI inference happens on your machine; your emails are never sent to a third-party AI API
- **Modular** — each feature is a self-contained script; working code isn't rewritten in place, new features get new files
- **Low dependency** — no Docker, no external database servers, no paid services
- **Transparent** — built to be read and understood line by line, not a black box

---

## Roadmap

- [ ] Streamlit UI polish and unified entry point
- [ ] Auto-clustering emails by topic
- [ ] RAG-style chat over inbox content
- [ ] Daily digest view
- [ ] Draft and send support
- [ ] Simplified, safer credential handling (evaluating encrypted local storage vs. OS keychain)
- [ ] Outlook / IMAP-generic provider support

---

## Contributing

This project is in active early development and open to contributions, feedback, and issue reports — especially around the authentication experience described above, which is the current top priority.

## License

Open source. *(Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/)*