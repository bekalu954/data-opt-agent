"""
Data Optimization Assistant - Team Web App
Built with Streamlit + Google Gemini 2.0 Flash
Share the URL with your team - no installation required.
"""

import streamlit as st
from google import genai
from google.genai import types
import time

# ── Page Configuration ───────────────────────────────────────────
st.set_page_config(
    page_title="Data Optimization Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── API Key ───────────────────────────────────────────────────────
# Try secrets.toml first, then fall back to direct entry
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    GEMINI_API_KEY = None

if not GEMINI_API_KEY:
    st.warning("API key not found in secrets. Please enter it below to continue.")
    GEMINI_API_KEY = st.text_input(
        "Enter your Gemini API Key:",
        type="password",
        placeholder="Paste your API key here..."
    )
    if not GEMINI_API_KEY:
        st.stop()

# ── System Prompt ─────────────────────────────────────────────────
SYSTEM_PROMPT = """
## CRITICAL RULE: ProjectWise Version Questions

MANDATORY: When ANY user asks about ProjectWise Explorer version,
ProjectWise Administrator version, or any ProjectWise component version:
1. ALWAYS reference the Bentley ProjectWise Version Support Matrix as the PRIMARY source
2. ALWAYS include this URL:
   https://docs.bentley.com/LiveContent/web/ProjectWise%20Version%20Support%20Matrix-vlatest/Guide/en/topics/2809885/GUID-1A2E193F-C3D9-4709-92A2-E5B9301B5946.html
3. Do NOT answer using ONLY the FAQ PDF - the Version Support Matrix is authoritative
4. You may supplement with FAQ content but always direct users to the above URL

---

## Role and Identity

You are the Data Optimization Team Assistant, a shared internal AI agent built to
support the Data Optimization team. You act as a knowledgeable, reliable, and structured
partner for all data-related tasks, analysis, documentation, and decision-making.

---

## Core Capabilities

- Accept and execute custom user-defined task prompts
- Analyze, summarize, and extract insights from documents
- Answer questions about Data Optimization processes and cloud upgrades
- Support Python and SQL code generation and pipeline optimization
- Maintain awareness of team context and ProjectWise environment

---

## Public Documentation References

ACTIVE RETRIEVAL REQUIRED: When questions fall under any category below,
retrieve live content from the corresponding URL and answer from it.

### 1. ProjectWise Version Support Matrix
- When to use: Version questions, compatibility, upgrade planning
- URL: https://docs.bentley.com/LiveContent/web/ProjectWise%20Version%20Support%20Matrix-vlatest/Guide/en/topics/2809885/GUID-1A2E193F-C3D9-4709-92A2-E5B9301B5946.html

### 2. ProjectWise Cloud Readme v2025
- When to use: Cloud deployment, new features, PW Cloud compatibility
- URL: https://docs.bentley.com/LiveContent/web/ProjectWise%20Cloud-v2025/ReadMe/en/topics/757583/c-PW-Readme-Introduction.html

### 3. ProjectWise Design Integration Readme v2025
- When to use: PWDI server requirements, design integration queries
- URL: https://docs.bentley.com/LiveContent/web/ProjectWise%20Design%20Integration-v2025/ReadMe/en/topics/1688349/c-PWDI-Readme.html

### 4. ProjectWise Administrator Help v2025
- When to use: Admin config, datasource setup, licensing, troubleshooting
- URL: https://docs.bentley.com/LiveContent/web/ProjectWise%20Administrator-v2025/Help/en/topics/1688349/GUID-69C4F050-35CF-4663-9D34-C9B84BF5E065.html

### 5. GreenBook Best Practices KB0020014
- When to use: Best practices, architecture decisions, security hardening
- URL: https://bentleysystems.service-now.com/community?id=kb_article_view&sysparm_article=KB0020014

---

## Behavioral Guidelines

- Accuracy First: Base responses on verified information. State uncertainty clearly.
- Structured Output: Use headings, bullets, tables, and code blocks as appropriate.
- Team-First Language: Use the team, we, our process.
- For Bentley version and compatibility questions: Always reference the live Bentley
  documentation URLs above. These are more authoritative than the internal FAQ document.
"""

# ── Initialize Gemini Client ──────────────────────────────────────
@st.cache_resource
def get_client(api_key):
    return genai.Client(api_key=api_key)

# ── Sidebar ───────────────────────────────────────────────────────
with st.sidebar:
    st.title("Data Optimization\nAssistant")
    st.markdown("---")
    st.markdown("**Quick Topics:**")

    if st.button("📋 ProjectWise Version Info"):
        st.session_state["quick_question"] = (
            "What version of ProjectWise Explorer and Administrator are we currently using?"
        )
    if st.button("☁️ Cloud Upgrade Process"):
        st.session_state["quick_question"] = (
            "What is the ProjectWise cloud upgrade process?"
        )
    if st.button("📊 Datasource Statistics"):
        st.session_state["quick_question"] = (
            "Give me an overview of our datasource statistics."
        )
    if st.button("🔧 Admin Best Practices"):
        st.session_state["quick_question"] = (
            "What are the best practices for ProjectWise administration?"
        )

    st.markdown("---")

    if st.button("🗑️ Clear Conversation"):
        st.session_state["messages"] = []
        st.session_state["history"] = []
        st.rerun()

    st.markdown("---")
    st.markdown("**Bentley Documentation:**")
    st.markdown(
        "[📖 Version Support Matrix](https://docs.bentley.com/LiveContent/web/"
        "ProjectWise%20Version%20Support%20Matrix-vlatest/Guide/en/topics/2809885/"
        "GUID-1A2E193F-C3D9-4709-92A2-E5B9301B5946.html)"
    )
    st.markdown(
        "[☁️ Cloud Readme v2025](https://docs.bentley.com/LiveContent/web/"
        "ProjectWise%20Cloud-v2025/ReadMe/en/topics/757583/c-PW-Readme-Introduction.html)"
    )
    st.markdown(
        "[🔧 Administrator Help v2025](https://docs.bentley.com/LiveContent/web/"
        "ProjectWise%20Administrator-v2025/Help/en/topics/1688349/"
        "GUID-69C4F050-35CF-4663-9D34-C9B84BF5E065.html)"
    )
    st.markdown(
        "[📘 GreenBook Best Practices](https://bentleysystems.service-now.com/"
        "community?id=kb_article_view&sysparm_article=KB0020014)"
    )

    st.markdown("---")
    st.caption("Powered by Gemini 2.0 Flash")

# ── Main Interface ────────────────────────────────────────────────
st.title("📊 Data Optimization Assistant")
st.caption("Your team's shared AI agent for ProjectWise, data pipelines, and documentation.")

# ── Session State ─────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "history" not in st.session_state:
    st.session_state["history"] = []
if "quick_question" not in st.session_state:
    st.session_state["quick_question"] = None

# ── Welcome Message ───────────────────────────────────────────────
if not st.session_state["messages"]:
    with st.chat_message("assistant"):
        st.markdown(
            "👋 **Hello! I am your Data Optimization Team Assistant.**\n\n"
            "I can help you with:\n"
            "- 📋 **ProjectWise versions** — Explorer, Administrator, compatibility\n"
            "- ☁️ **Cloud upgrade processes** — migration planning and requirements\n"
            "- 🔧 **Admin tasks** — datasource setup, user management, licensing\n"
            "- 📊 **Data optimization** — pipeline analysis, SQL and Python code\n"
            "- 📘 **Best practices** — Bentley GreenBook recommendations\n\n"
            "Use the quick-topic buttons on the left, or type your question below!"
        )

# ── Display Chat History ──────────────────────────────────────────
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── Send Message Function ─────────────────────────────────────────
def send_message(prompt):
    client = get_client(GEMINI_API_KEY)

    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        start_time = time.time()
        placeholder = st.empty()
        full_response = ""

        try:
            # Build conversation history for context
            contents = []
            for msg in st.session_state["history"]:
                contents.append(
                    types.Content(
                        role=msg["role"],
                        parts=[types.Part(text=msg["content"])]
                    )
                )
            contents.append(
                types.Content(
                    role="user",
                    parts=[types.Part(text=prompt)]
                )
            )

            # Stream the response
            response = client.models.generate_content_stream(
                            model="gemini-1.5-flash",
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.2,
                    max_output_tokens=2048,
                )
            )

            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    placeholder.markdown(full_response + "▌")

            elapsed = time.time() - start_time
            placeholder.markdown(full_response)
            st.caption(f"Response time: {elapsed:.1f}s")

        except Exception as e:
            full_response = f"Error: {str(e)}\n\nPlease check your API key and try again."
            placeholder.markdown(full_response)

    # Save to history
    st.session_state["messages"].append(
        {"role": "assistant", "content": full_response}
    )
    st.session_state["history"].append({"role": "user", "content": prompt})
    st.session_state["history"].append({"role": "model", "content": full_response})

# ── Handle Quick Question Buttons ─────────────────────────────────
if st.session_state["quick_question"]:
    prompt = st.session_state["quick_question"]
    st.session_state["quick_question"] = None
    send_message(prompt)
    st.rerun()

# ── Chat Input ────────────────────────────────────────────────────
if prompt := st.chat_input(
    "Ask me anything about ProjectWise, data optimization, or your team processes..."
):
    send_message(prompt)
