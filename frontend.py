import os
import uuid
from datetime import datetime

import streamlit as st
from langchain_core.messages import HumanMessage
from langgraph.types import Command

from graph import app
from state import default_state

st.set_page_config(
    page_title="GoBeyond — Travel Planner",
    page_icon="assets/favicon.ico" if os.path.exists("assets/favicon.ico") else None,
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, .stApp {
    font-family: 'Inter', sans-serif;
    background: #050b14;
    color: #e0edf8;
}

.hero {
    position: relative;
    border-radius: 20px;
    overflow: hidden;
    height: 280px;
    margin-bottom: 2rem;
    box-shadow: 0 8px 40px rgba(0,0,0,0.6);
}
.hero img {
    width: 100%; height: 100%;
    object-fit: cover;
    filter: brightness(0.25) saturate(1.1);
}
.hero-content {
    position: absolute; inset: 0;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    text-align: center; padding: 2rem;
}
.hero-badge {
    font-size: 0.72rem; font-weight: 700; letter-spacing: 0.2em;
    text-transform: uppercase; color: #7ab8f5;
    background: rgba(58,123,213,0.15);
    border: 1px solid rgba(58,123,213,0.4);
    border-radius: 20px; padding: 0.28rem 1rem;
    margin-bottom: 1rem; display: inline-block;
}
.hero-title {
    font-size: 2.8rem; font-weight: 800; color: #fff;
    margin: 0 0 0.6rem; letter-spacing: -0.02em;
}
.hero-sub {
    font-size: 0.97rem; color: #8aaccc;
    max-width: 520px; line-height: 1.65;
}

.dest-wrap {
    border-radius: 10px; overflow: hidden;
    position: relative; height: 90px;
}
.dest-wrap img { width: 100%; height: 100%; object-fit: cover; filter: brightness(0.45); }
.dest-label {
    position: absolute; bottom: 8px; left: 0; right: 0;
    text-align: center; color: #fff;
    font-size: 0.78rem; font-weight: 600; letter-spacing: 0.03em;
}

.section-label {
    font-size: 0.74rem; font-weight: 700;
    letter-spacing: 0.13em; text-transform: uppercase;
    color: #4a8cc0; margin-bottom: 0.5rem;
}

.result-card {
    background: linear-gradient(160deg, #0b1826 0%, #091320 100%);
    border: 1px solid #1e3a5c;
    border-left: 3px solid #3a7bd5;
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    line-height: 1.8; color: #bdd4ec;
    font-size: 0.91rem; margin-bottom: 0.8rem;
}

.final-card {
    background: linear-gradient(160deg, #0c1e35 0%, #081625 100%);
    border: 1px solid #1e4a7a;
    border-left: 3px solid #2a9d6e;
    border-radius: 14px; padding: 1.8rem;
    line-height: 1.85; color: #c5e8d8; font-size: 0.93rem;
}

.approval-banner {
    background: #0d1e32;
    border: 1px solid #1e3d60;
    border-left: 3px solid #c97a10;
    border-radius: 12px; padding: 1.2rem 1.6rem;
    margin: 1.2rem 0;
}
.approval-title {
    font-size: 1rem; font-weight: 700;
    color: #c97a10; margin-bottom: 0.4rem;
}

.metrics {
    display: flex; gap: 0.8rem; margin: 1.4rem 0;
}
.metric {
    flex: 1; background: #0c1624;
    border: 1px solid #1a2e44; border-radius: 10px;
    padding: 0.9rem 1rem; text-align: center;
}
.metric-val { font-size: 1.7rem; font-weight: 800; color: #4ea8f0; }
.metric-lbl { font-size: 0.7rem; color: #4a7a96; margin-top: 0.15rem;
              text-transform: uppercase; letter-spacing: 0.1em; }

.sec-line {
    display: flex; align-items: center; gap: 0.5rem;
    margin: 1.8rem 0 0.7rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #162030;
}
.sec-line span { font-size: 1rem; font-weight: 600; color: #d8ecf8; }

.save-bar {
    background: #0c1624; border: 1px solid #1a2e44;
    border-radius: 8px; padding: 0.7rem 1rem;
    color: #6a9ab8; font-size: 0.84rem; margin-top: 0.4rem;
}

section[data-testid="stSidebar"] {
    background: #080e18 !important;
    border-right: 1px solid #0f1c2c !important;
}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label { color: #7aA0be !important; }
.sidebar-title { color: #d0e8f8 !important; font-size: 0.88rem;
                 font-weight: 600; margin: 1rem 0 0.45rem; }
.sidebar-chip {
    background: #0d1a2b; border: 1px solid #162840;
    border-radius: 6px; padding: 0.35rem 0.7rem;
    margin-bottom: 0.3rem; font-size: 0.78rem; color: #5a8faf;
}
.agent-step {
    display: flex; align-items: center; gap: 0.4rem;
    padding: 0.35rem 0; border-bottom: 1px solid #0f1c2c;
    font-size: 0.8rem; color: #6a9ab8;
}
.step-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: #3a7bd5; flex-shrink: 0;
}

div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #1256b0 0%, #0c3d82 100%) !important;
    color: #fff !important; border: none !important;
    border-radius: 10px !important; padding: 0.8rem 2rem !important;
    font-size: 1rem !important; font-weight: 600 !important;
    width: 100% !important; letter-spacing: 0.01em !important;
    box-shadow: 0 0 24px rgba(18,86,176,0.35) !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stButton"] > button:hover {
    box-shadow: 0 0 40px rgba(18,86,176,0.6) !important;
    transform: translateY(-1px) !important;
}

.stTextArea textarea {
    background: #091320 !important; border: 1px solid #182e44 !important;
    border-radius: 8px !important; color: #d8ecf8 !important;
    font-size: 0.93rem !important;
}
.stTextArea textarea:focus {
    border-color: #2a6bbf !important;
    box-shadow: 0 0 0 2px rgba(42,107,191,0.2) !important;
}
input[type="text"], .stTextInput input {
    background: #0d1a2b !important; border: 1px solid #162840 !important;
    border-radius: 7px !important; color: #d8ecf8 !important;
}
.stTextInput label, .stTextArea label {
    color: #4a8cc0 !important; font-size: 0.76rem !important;
    font-weight: 600 !important; letter-spacing: 0.08em !important;
}

.stMarkdown p, .stMarkdown li { color: #b8d4e8 !important; }
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #e0f0ff !important; }

div[data-testid="stDownloadButton"] > button {
    background: #112840 !important; color: #d8ecf8 !important;
    border: 1px solid #1a3a58 !important; border-radius: 8px !important;
}
.stAlert { background: #0d1a2b !important; border-radius: 8px !important; }
section[data-testid="stSidebar"] hr { border-color: #0f1c2c !important; }
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


if "thread_id" not in st.session_state:
    st.session_state.thread_id = f"guest_{uuid.uuid4().hex[:8]}"
if "waiting_for_approval" not in st.session_state:
    st.session_state.waiting_for_approval = False
if "latest_result" not in st.session_state:
    st.session_state.latest_result = None
if "collected" not in st.session_state:
    st.session_state.collected = {}


with st.sidebar:
    st.markdown("<div class='sidebar-title'>GoBeyond</div>", unsafe_allow_html=True)
    st.markdown("<div style='color:#3a6a8a;font-size:0.76rem;margin-bottom:0.8rem;'>Multi-Agent Travel Planner</div>", unsafe_allow_html=True)
    st.markdown("---")

    user_id = st.text_input("User ID", value="traveller", help="Session ID — keeps history between queries")

    col_new, col_clear = st.columns(2)
    with col_new:
        if st.button("New Session", use_container_width=True):
            st.session_state.thread_id            = f"{user_id}_{uuid.uuid4().hex[:8]}"
            st.session_state.waiting_for_approval = False
            st.session_state.latest_result        = None
            st.session_state.collected            = {}
            st.rerun()
    with col_clear:
        if st.button("Clear", use_container_width=True):
            st.session_state.latest_result        = None
            st.session_state.waiting_for_approval = False
            st.session_state.collected            = {}
            st.rerun()

    st.caption(f"Thread: `{st.session_state.thread_id}`")
    st.markdown("---")

    st.markdown("<div class='sidebar-title'>Stack</div>", unsafe_allow_html=True)
    for tech in ["LangGraph", "Groq / LLaMA 3.3 70B", "Supabase PostgreSQL",
                 "Tavily MCP", "AviationStack MCP", "OpenWeatherMap MCP"]:
        st.markdown(f"<div class='sidebar-chip'>{tech}</div>", unsafe_allow_html=True)

    st.markdown("<div class='sidebar-title'>Pipeline</div>", unsafe_allow_html=True)
    for name in ["Supervisor", "Flight Agent", "Hotel Agent", "Weather Agent",
                 "Budget Agent", "Itinerary Agent", "Human Review", "Final Agent"]:
        st.markdown(f"<div class='agent-step'><div class='step-dot'></div>{name}</div>", unsafe_allow_html=True)


st.markdown("""
<div class="hero">
    <img src="https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=1400&q=80" alt="travel"/>
    <div class="hero-content">
        <div class="hero-badge">Multi-Agent AI System</div>
        <div class="hero-title">GoBeyond</div>
        <div class="hero-sub">
            Eight agents working in sequence — flights, hotels, weather, budget, and a full itinerary
            that you review before it's finalized.
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


DESTINATIONS = [
    ("Tokyo",   "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=300&q=70"),
    ("Paris",   "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=300&q=70"),
    ("Bangkok", "https://images.unsplash.com/photo-1508009603885-50cf7c579365?w=300&q=70"),
    ("Rome",    "https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=300&q=70"),
    ("Dubai",   "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=300&q=70"),
]
for col, (name, url) in zip(st.columns(5), DESTINATIONS):
    with col:
        st.markdown(f"""
        <div class="dest-wrap">
            <img src="{url}" alt="{name}"/>
            <div class="dest-label">{name}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


QUICK = ["7-day Japan under 2 Lakhs", "5-day Paris trip", "Dubai weekend", "10-day Bali"]
qcols = st.columns(len(QUICK))
quick_fill = st.session_state.get("quick_fill", "")
for qc, label in zip(qcols, QUICK):
    with qc:
        if st.button(label, key=f"q_{label}"):
            st.session_state.quick_fill = label
            quick_fill = label

st.markdown("<div class='section-label'>Describe your trip</div>", unsafe_allow_html=True)
user_query = st.text_area(
    "",
    value=quick_fill,
    placeholder="e.g. 7-day Japan trip with flights and hotels under 2 lakhs",
    height=100,
    label_visibility="collapsed",
)

config = {"configurable": {"thread_id": st.session_state.thread_id}}


if st.button("Plan My Trip", use_container_width=True):
    if not user_query.strip():
        st.warning("Enter a travel request first.")
    else:
        st.session_state.thread_id            = f"{user_id}_{uuid.uuid4().hex[:8]}"
        config                                = {"configurable": {"thread_id": st.session_state.thread_id}}
        st.session_state.waiting_for_approval = False
        st.session_state.latest_result        = None
        st.session_state.collected            = {
            "flight_results": "", "hotel_results": "", "weather_results": "",
            "budget_results": "", "itinerary": "", "final_response": "",
            "supervisor_reasoning": "", "selected_agents": [], "llm_calls": 0,
        }

        with st.spinner("Agents are working on your plan..."):
            try:
                result = app.invoke(default_state(user_query, user_id), config=config)
                st.session_state.latest_result       = result
                st.session_state.waiting_for_approval = "__interrupt__" in result
                c = st.session_state.collected
                c["supervisor_reasoning"] = result.get("supervisor_reasoning", "")
                c["selected_agents"]      = result.get("selected_agents", [])
                c["flight_results"]       = result.get("flight_results", "")
                c["hotel_results"]        = result.get("hotel_results", "")
                c["weather_results"]      = result.get("weather_results", "")
                c["budget_results"]       = result.get("budget_results", "")
                c["llm_calls"]            = result.get("llm_calls", 0)
                if "__interrupt__" in result:
                    c["itinerary"] = result["__interrupt__"][0].value.get("draft_itinerary", result.get("itinerary", ""))
                else:
                    c["itinerary"]      = result.get("itinerary", "")
                    c["final_response"] = result.get("final_response", "")
            except Exception as exc:
                st.error(f"Error: {exc}")
                st.exception(exc)


result = st.session_state.get("latest_result")
c      = st.session_state.get("collected", {})

if result:
    if c.get("supervisor_reasoning"):
        st.markdown("<div class='sec-line'><span>Supervisor</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='result-card'>{c['supervisor_reasoning']}</div>", unsafe_allow_html=True)
        if c.get("selected_agents"):
            st.markdown("**Agents selected:** " + " · ".join(f"`{a}`" for a in c["selected_agents"]))

    if c.get("flight_results") or c.get("hotel_results"):
        col1, col2 = st.columns(2)
        with col1:
            if c.get("flight_results"):
                st.markdown("<div class='sec-line'><span>Flights</span></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='result-card'>{c['flight_results']}</div>", unsafe_allow_html=True)
            if c.get("weather_results"):
                st.markdown("<div class='sec-line'><span>Weather</span></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='result-card'>{c['weather_results']}</div>", unsafe_allow_html=True)
        with col2:
            if c.get("hotel_results"):
                st.markdown("<div class='sec-line'><span>Hotels</span></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='result-card'>{c['hotel_results']}</div>", unsafe_allow_html=True)
            if c.get("budget_results"):
                st.markdown("<div class='sec-line'><span>Budget</span></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='result-card'>{c['budget_results']}</div>", unsafe_allow_html=True)

    if c.get("itinerary"):
        st.markdown("<div class='sec-line'><span>Draft Itinerary</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='result-card'>{c['itinerary']}</div>", unsafe_allow_html=True)

    num_agents = len(c.get("selected_agents", [])) + 1
    st.markdown(f"""
    <div class="metrics">
        <div class="metric"><div class="metric-val">{num_agents}</div><div class="metric-lbl">Agents</div></div>
        <div class="metric"><div class="metric-val">{c.get('llm_calls', 0)}</div><div class="metric-lbl">LLM Calls</div></div>
        <div class="metric"><div class="metric-val">Live</div><div class="metric-lbl">Memory</div></div>
    </div>
    """, unsafe_allow_html=True)


if st.session_state.get("waiting_for_approval"):
    st.markdown("""
    <div class="approval-banner">
        <div class="approval-title">Review Required</div>
        <div style="color:#8aaec8;font-size:0.88rem;">
            Look at the draft itinerary above and either approve it or send it back with notes.
        </div>
    </div>
    """, unsafe_allow_html=True)

    approved_choice = st.radio(
        "Your decision:",
        ["Approve", "Request changes"],
        horizontal=True,
        key="approval_radio",
    )
    approved = approved_choice == "Approve"
    feedback = ""
    if not approved:
        feedback = st.text_area(
            "What should be changed?",
            placeholder="e.g. Remove the temple tour on day 3, keep the budget under 1.5 lakhs.",
            height=90,
            key="approval_feedback",
        )

    if st.button("Submit", use_container_width=True, type="primary"):
        with st.spinner("Updating your plan..."):
            try:
                final_result = app.invoke(
                    Command(resume={"approved": approved, "feedback": feedback}),
                    config={"configurable": {"thread_id": st.session_state.thread_id}},
                )
                st.session_state.latest_result        = final_result
                st.session_state.waiting_for_approval = False
                st.session_state.collected["final_response"] = final_result.get("final_response", "")
                st.session_state.collected["llm_calls"]      = final_result.get("llm_calls", 0)
                st.rerun()
            except Exception as exc:
                st.error(f"Error: {exc}")
                st.exception(exc)


final_response = c.get("final_response", "") or (result or {}).get("final_response", "")
if final_response:
    st.markdown("<div class='sec-line'><span>Final Travel Plan</span></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='final-card'>{final_response}</div>", unsafe_allow_html=True)

    timestamp    = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename     = f"gobeyond_plan_{timestamp}.md"
    save_dir     = os.path.join(os.path.dirname(__file__), "travel_plans")
    os.makedirs(save_dir, exist_ok=True)

    file_content = f"""# GoBeyond Travel Plan

**Query:** {user_query}
**Date:** {datetime.now().strftime("%Y-%m-%d %H:%M")}
**User:** {user_id}

---

## Flights
{c.get('flight_results') or 'N/A'}

---

## Hotels
{c.get('hotel_results') or 'N/A'}

---

## Weather
{c.get('weather_results') or 'N/A'}

---

## Budget
{c.get('budget_results') or 'N/A'}

---

## Itinerary
{c.get('itinerary') or 'N/A'}

---

## Final Plan
{final_response}
"""
    with open(os.path.join(save_dir, filename), "w", encoding="utf-8") as fh:
        fh.write(file_content)

    dl_col, info_col = st.columns([1, 3])
    with dl_col:
        st.download_button("Download Plan", data=file_content, file_name=filename, mime="text/markdown", use_container_width=True)
    with info_col:
        st.markdown(f"<div class='save-bar'>Saved to travel_plans/{filename}</div>", unsafe_allow_html=True)
