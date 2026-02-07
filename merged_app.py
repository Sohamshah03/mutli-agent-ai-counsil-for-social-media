"""
AI Marketing Council — SocialPulse Edition
Merged app combining the polished SocialPulse UI with real multi-agent backend.
Run:  streamlit run merged_app.py
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
import os
import sys
import time
import random
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.debate import DebateOrchestrator
from src.agents import load_agents

# ──────────────────────────────────────────────
# Page config & custom CSS (SocialPulse theme)
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="AI Marketing Council — SocialPulse",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
/* ---- global ---- */
[data-testid="stAppViewContainer"] {font-family: 'Inter', sans-serif;}
h1, h2, h3 {font-family: 'Space Grotesk', 'Inter', sans-serif;}

/* ---- sidebar brand ---- */
.brand-box {display:flex;align-items:center;gap:.5rem;padding:.25rem 0 1rem 0;}
.brand-icon {background:linear-gradient(135deg,#0ea5e9,#6366f1);color:#fff;width:36px;height:36px;
             border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:700;}
.brand-name {font-weight:700;font-size:1.2rem;color:inherit;}
.brand-sub  {font-size:.65rem;color:gray;margin-top:-2px;}

/* ---- stat card ---- */
.stat-card {border:1px solid rgba(128,128,128,.18);border-radius:12px;padding:18px 20px;
            background:var(--background-color);transition:box-shadow .2s;}
.stat-card:hover {box-shadow:0 4px 12px rgba(0,0,0,.06);}
.stat-title {font-size:.72rem;color:gray;text-transform:uppercase;letter-spacing:.5px;}
.stat-value {font-size:1.55rem;font-weight:700;margin:4px 0 2px;}
.stat-change-pos {font-size:.75rem;color:#22c55e;}
.stat-change-neg {font-size:.75rem;color:#ef4444;}

/* ---- agent card ---- */
.agent-card {border:1px solid rgba(128,128,128,.18);border-radius:12px;padding:16px 18px;
             margin-bottom:10px;transition:box-shadow .2s;}
.agent-card:hover {box-shadow:0 4px 12px rgba(0,0,0,.06);}
.agent-name {font-weight:700;font-size:1rem;}
.agent-role {font-size:.75rem;color:gray;margin-top:2px;}

/* ---- insight card ---- */
.insight-card {border-radius:12px;padding:16px;margin-bottom:10px;}
.insight-opportunity {border:1px solid rgba(14,165,233,.3);background:rgba(14,165,233,.05);}
.insight-warning     {border:1px solid rgba(245,158,11,.3);background:rgba(245,158,11,.05);}
.insight-success     {border:1px solid rgba(34,197,94,.3);background:rgba(34,197,94,.05);}

/* ---- chat ---- */
.chat-bubble-user {background:linear-gradient(135deg,#0ea5e9,#6366f1);color:#fff;padding:8px 14px;
                   border-radius:12px 12px 4px 12px;margin-left:auto;max-width:80%;font-size:.85rem;margin-bottom:6px;}
.chat-bubble-ai   {background:rgba(128,128,128,.12);padding:8px 14px;border-radius:12px 12px 12px 4px;
                   max-width:80%;font-size:.85rem;margin-bottom:6px;white-space:pre-wrap;}

/* ---- step progress ---- */
.step-badge {display:inline-flex;align-items:center;gap:6px;padding:4px 12px;border-radius:20px;
             font-size:.75rem;font-weight:600;margin:2px 4px 2px 0;}
.step-done    {background:rgba(34,197,94,.15);color:#22c55e;}
.step-active  {background:rgba(14,165,233,.15);color:#0ea5e9;animation:pulse 1.5s infinite;}
.step-pending {background:rgba(128,128,128,.1);color:gray;}

@keyframes pulse {
    0%, 100% {opacity:1;} 50% {opacity:.6;}
}

/* ---- score bar ---- */
.score-row {display:flex;justify-content:space-between;font-size:.75rem;margin-bottom:2px;}

/* ---- post card ---- */
.post-card {border:1px solid rgba(128,128,128,.18);border-radius:12px;padding:18px;margin-bottom:12px;}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Session state defaults
# ──────────────────────────────────────────────
DEFAULTS = {
    "logged_in": False,
    "auth_page": "login",
    "page": "Dashboard",
    "orchestrator": None,
    "agents_loaded": False,
    "iterations": [],
    "running_campaign": False,
    "campaign_step": 0,
    "chat_messages": [
        {"role": "assistant", "content": "Hey! I'm your AI marketing strategist. Ask me about campaign results, agent debates, or content strategy."}
    ],
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ──────────────────────────────────────────────
# Agent colour map
# ──────────────────────────────────────────────
AGENT_COLORS = {
    "viral_hunter": "#ef4444",
    "brand_guardian": "#3b82f6",
    "twitter_specialist": "#0ea5e9",
    "instagram_specialist": "#ec4899",
    "arbitrator": "#eab308",
}

AGENT_ICONS = {
    "viral_hunter": "🔥",
    "brand_guardian": "🛡️",
    "twitter_specialist": "𝕏",
    "instagram_specialist": "📸",
    "arbitrator": "⚖️",
}

# ──────────────────────────────────────────────
# Helper renderers
# ──────────────────────────────────────────────
def render_stat_card(title: str, value: str, change: str = "", positive: bool = True):
    cls = "stat-change-pos" if positive else "stat-change-neg"
    change_html = f'<div class="{cls}">{change}</div>' if change else ""
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-title">{title}</div>
        <div class="stat-value">{value}</div>
        {change_html}
    </div>
    """, unsafe_allow_html=True)


def render_progress_bar(label: str, score, max_val: int = 10):
    pct = min(int(score / max_val * 100), 100)
    st.markdown(f"""
    <div class="score-row"><span>{label}</span><span><b>{score}/{max_val}</b></span></div>
    """, unsafe_allow_html=True)
    st.progress(pct)


def render_agent_card(agent, icon: str = "🤖", color: str = "#0ea5e9"):
    st.markdown(f"""
    <div class="agent-card" style="border-left:4px solid {color};">
        <div style="display:flex;align-items:center;gap:8px;">
            <span style="font-size:1.4rem;">{icon}</span>
            <div>
                <div class="agent-name">{agent.name}</div>
                <div class="agent-role">{agent.role}</div>
            </div>
        </div>
        <div style="margin-top:8px;display:flex;gap:16px;font-size:.8rem;color:gray;">
            <span>Weight: <b style="color:inherit;">{agent.voting_weight:.2f}</b></span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def get_agent_icon(agent_id: str) -> str:
    return AGENT_ICONS.get(agent_id, "🤖")


def get_agent_color(agent_id: str) -> str:
    return AGENT_COLORS.get(agent_id, "#6b7280")


# ──────────────────────────────────────────────
# Chatbot (keyword-matched against real data)
# ──────────────────────────────────────────────
def get_chat_response(msg: str) -> str:
    lower = msg.lower()
    iterations = st.session_state.iterations

    if any(k in lower for k in ["result", "last", "campaign", "iteration"]):
        if iterations:
            last = iterations[-1]
            winner = last.get("decision", {}).get("winner", "N/A")
            score = last.get("engagement", {}).get("overall_score", 0)
            return f"The last campaign iteration was won by **{winner.replace('_', ' ').title()}** with an overall engagement score of **{score:.1f}/10**.\n\nWould you like me to break down the agent proposals?"
        return "No iterations have been run yet. Head to the **Campaign** page to start one!"

    if any(k in lower for k in ["agent", "weight", "who"]):
        if st.session_state.orchestrator:
            lines = []
            for aid, a in st.session_state.orchestrator.agents.items():
                if aid != "arbitrator":
                    lines.append(f"• **{a.name}** — weight {a.voting_weight:.2f}")
            return "Current agent roster:\n" + "\n".join(lines)
        return "Agents haven't been loaded yet."

    if any(k in lower for k in ["trend", "trending"]):
        if iterations:
            trends = iterations[-1].get("trends", [])[:5]
            if trends:
                return "Latest trending topics:\n" + "\n".join(f"• {t['topic']} ({t.get('volume','?')})" for t in trends)
        return "Run a campaign first to pull fresh trends!"

    if any(k in lower for k in ["content", "post", "caption"]):
        if iterations:
            content = iterations[-1].get("content", {})
            caption = content.get("caption", "N/A")
            return f"Latest generated caption ({content.get('platform','?').upper()}):\n\n{caption[:400]}"
        return "No content generated yet. Run a campaign to see AI-generated posts."

    return ("I can help with:\n"
            "• **Campaign results** — ask about the latest iteration\n"
            "• **Agent info** — current weights and roster\n"
            "• **Trends** — what's trending right now\n"
            "• **Content** — see generated posts\n\n"
            "Just ask away!")


# ═══════════════════════════════════════════════
# SYSTEM INIT
# ═══════════════════════════════════════════════
def initialize_system():
    """Load agents and orchestrator once."""
    if not st.session_state.agents_loaded:
        try:
            st.session_state.orchestrator = DebateOrchestrator()
            st.session_state.agents_loaded = True
        except Exception as e:
            st.error(f"Failed to initialize agent system: {e}")
            return False
    return True


# ═══════════════════════════════════════════════
# AUTH PAGES
# ═══════════════════════════════════════════════
def page_login():
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        st.markdown("")
        st.markdown("""
        <div style="text-align:center;margin-bottom:1.5rem;">
            <span style="background:linear-gradient(135deg,#0ea5e9,#6366f1);color:#fff;padding:10px 14px;
                         border-radius:12px;font-size:1.4rem;font-weight:700;">⚡</span>
            <span style="font-weight:700;font-size:1.6rem;margin-left:.6rem;">AI Marketing Council</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("#### Welcome back")
        st.caption("Sign in to access your campaign dashboard")

        with st.form("login_form"):
            email = st.text_input("Email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("Login", use_container_width=True, type="primary")
            if submitted:
                st.session_state.logged_in = True
                st.session_state.page = "Dashboard"
                st.rerun()

        st.markdown("")
        c1, c2 = st.columns([3, 2])
        with c2:
            if st.button("Sign up →", type="secondary"):
                st.session_state.auth_page = "signup"
                st.rerun()


def page_signup():
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        st.markdown("")
        st.markdown("""
        <div style="text-align:center;margin-bottom:1.5rem;">
            <span style="background:linear-gradient(135deg,#0ea5e9,#6366f1);color:#fff;padding:10px 14px;
                         border-radius:12px;font-size:1.4rem;font-weight:700;">⚡</span>
            <span style="font-weight:700;font-size:1.6rem;margin-left:.6rem;">AI Marketing Council</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("#### Create your account")
        st.caption("Start running AI-powered marketing campaigns")

        with st.form("signup_form"):
            email = st.text_input("Email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", placeholder="Create a password")
            confirm = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
            submitted = st.form_submit_button("Create Account", use_container_width=True, type="primary")
            if submitted:
                st.session_state.logged_in = True
                st.session_state.page = "Dashboard"
                st.rerun()

        st.markdown("")
        c1, c2 = st.columns([3, 2])
        with c2:
            if st.button("← Login", type="secondary"):
                st.session_state.auth_page = "login"
                st.rerun()


# ═══════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════
def render_sidebar():
    with st.sidebar:
        # Brand
        st.markdown("""
        <div class="brand-box">
            <div class="brand-icon">⚡</div>
            <div>
                <div class="brand-name">AI Marketing Council</div>
                <div class="brand-sub">Multi-Agent Campaign System</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # System status
        if st.session_state.agents_loaded:
            st.success("Agents Online", icon="🟢")
        else:
            st.warning("Agents Offline", icon="🟡")

        st.markdown("---")

        # Navigation
        pages = {
            "📊 Dashboard": "Dashboard",
            "🚀 Campaign":  "Campaign",
            "🗣️ Debate":    "Debate",
            "📝 Content":    "Content",
            "📈 Analytics":  "Analytics",
            "🔄 Compare":    "Compare",
        }
        for label, key in pages.items():
            btn_type = "primary" if st.session_state.page == key else "secondary"
            if st.button(label, use_container_width=True, type=btn_type, key=f"nav_{key}"):
                st.session_state.page = key
                st.rerun()

        st.markdown("---")

        # Agent weights (live)
        st.markdown("**Agent Weights**")
        if st.session_state.orchestrator:
            for aid, agent in st.session_state.orchestrator.agents.items():
                if aid != "arbitrator":
                    icon = get_agent_icon(aid)
                    color = get_agent_color(aid)
                    w = agent.voting_weight
                    bar_pct = int(min(w / 2.0, 1.0) * 100)
                    st.markdown(f"""
                    <div style="margin-bottom:6px;">
                        <div style="display:flex;justify-content:space-between;font-size:.78rem;">
                            <span>{icon} {agent.name}</span>
                            <span style="font-weight:600;">{w:.2f}</span>
                        </div>
                        <div style="background:rgba(128,128,128,.15);border-radius:8px;height:6px;margin-top:3px;">
                            <div style="background:{color};width:{bar_pct}%;height:100%;border-radius:8px;"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("---")
        st.caption(f"Iterations: **{len(st.session_state.iterations)}**")

        if st.button("🔄 Reset System", use_container_width=True, type="secondary"):
            st.session_state.orchestrator = DebateOrchestrator()
            st.session_state.iterations = []
            st.rerun()

        st.markdown("---")
        if st.button("🚪 Log out", use_container_width=True, type="secondary"):
            for k in DEFAULTS:
                st.session_state[k] = DEFAULTS[k]
            st.rerun()


# ═══════════════════════════════════════════════
# CHATBOT
# ═══════════════════════════════════════════════
def render_chatbot():
    with st.sidebar:
        st.markdown("---")
        with st.expander("💬 **AI Assistant**", expanded=False):
            for msg in st.session_state.chat_messages:
                if msg["role"] == "user":
                    st.markdown(f'<div class="chat-bubble-user">{msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-bubble-ai">{msg["content"]}</div>', unsafe_allow_html=True)

            if len(st.session_state.chat_messages) <= 1:
                prompts = [
                    "Show me the last campaign result",
                    "What are the agent weights?",
                    "What's trending right now?",
                    "Show me the latest generated content",
                ]
                for p in prompts:
                    if st.button(p, key=f"qp_{p}", use_container_width=True, type="secondary"):
                        st.session_state.chat_messages.append({"role": "user", "content": p})
                        st.session_state.chat_messages.append({"role": "assistant", "content": get_chat_response(p)})
                        st.rerun()

            with st.form("chat_form", clear_on_submit=True):
                user_input = st.text_input("Ask about your campaigns…", label_visibility="collapsed",
                                           placeholder="Ask about your campaigns…", key="chatbot_input")
                if st.form_submit_button("Send", use_container_width=True):
                    if user_input:
                        st.session_state.chat_messages.append({"role": "user", "content": user_input})
                        st.session_state.chat_messages.append({"role": "assistant", "content": get_chat_response(user_input)})
                        st.rerun()

            if len(st.session_state.chat_messages) > 1:
                if st.button("🗑️ Clear chat", key="clear_chat", use_container_width=True, type="secondary"):
                    st.session_state.chat_messages = [st.session_state.chat_messages[0]]
                    st.rerun()


# ═══════════════════════════════════════════════
# PAGE: DASHBOARD
# ═══════════════════════════════════════════════
def page_dashboard():
    st.info(
        "**Your AI Marketing Command Center** — "
        "Run multi-agent debates, generate optimised social media content, and watch your AI council learn and adapt across iterations.",
        icon="⚡",
    )
    col_btn = st.columns([5, 1])
    with col_btn[1]:
        if st.button("Run Campaign ↗", type="primary"):
            st.session_state.page = "Campaign"
            st.rerun()

    # ---- Quick stats ----
    n_iter = len(st.session_state.iterations)
    last_score = st.session_state.iterations[-1]["engagement"]["overall_score"] if n_iter else 0
    last_likes = st.session_state.iterations[-1]["engagement"]["likes"] if n_iter else 0
    last_sentiment = st.session_state.iterations[-1]["engagement"]["sentiment"] if n_iter else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_stat_card("Iterations Run", str(n_iter), f"+{n_iter} total" if n_iter else "No runs yet", n_iter > 0)
    with c2:
        render_stat_card("Last Engagement", f"{last_score:.1f}/10", "Overall score" if n_iter else "—", last_score >= 5)
    with c3:
        render_stat_card("Last Likes", f"{last_likes:,}" if n_iter else "—", "Simulated" if n_iter else "—")
    with c4:
        render_stat_card("Sentiment", f"{last_sentiment:.0%}" if n_iter else "—",
                         "Positive" if last_sentiment >= 0.6 else "Low", last_sentiment >= 0.6)

    st.markdown("")

    # ---- Agent roster ----
    st.markdown("##### 🤖 Agent Council")
    st.caption("Your autonomous marketing agents and their current voting weights")
    if st.session_state.orchestrator:
        cols = st.columns(4)
        idx = 0
        for aid, agent in st.session_state.orchestrator.agents.items():
            if aid == "arbitrator":
                continue
            with cols[idx % 4]:
                render_agent_card(agent, get_agent_icon(aid), get_agent_color(aid))
            idx += 1

    st.markdown("")

    # ---- Recent iterations ----
    if n_iter:
        st.markdown("##### 📋 Recent Campaigns")
        st.caption("Last iterations with outcomes")
        for i, it in enumerate(reversed(st.session_state.iterations[-5:]), 1):
            dec = it.get("decision", {})
            eng = it.get("engagement", {})
            winner = dec.get("winner", "—").replace("_", " ").title()
            score = eng.get("overall_score", 0)
            ts = it.get("timestamp", "")[:19].replace("T", " ")
            trend_color = "#22c55e" if score >= 6 else ("#eab308" if score >= 4 else "#ef4444")

            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([0.5, 3, 1.5, 1])
                with c1:
                    st.markdown(f"### {get_agent_icon(dec.get('winner', ''))}")
                with c2:
                    st.markdown(f"**{winner}** won the debate")
                    st.caption(ts)
                with c3:
                    st.metric("Score", f"{score:.1f}/10", label_visibility="collapsed")
                with c4:
                    st.markdown(
                        f"<span style='color:{trend_color};font-weight:600;font-size:.9rem;'>"
                        f"{'● Good' if score >= 6 else '● Fair' if score >= 4 else '● Low'}</span>",
                        unsafe_allow_html=True)
    else:
        st.markdown("")
        st.markdown(
            "<div style='text-align:center;padding:40px 0;color:gray;'>"
            "<div style='font-size:2rem;margin-bottom:8px;'>🚀</div>"
            "<div>No campaigns yet — head to <b>Campaign</b> to run your first one!</div>"
            "</div>",
            unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# PAGE: CAMPAIGN (Input)
# ═══════════════════════════════════════════════
def page_campaign():
    st.markdown("## 🚀 Run Campaign")
    st.caption("Configure your brand context and launch a multi-agent debate")

    col1, col2 = st.columns(2)

    with col1:
        brand_name = st.text_input("Brand Name", value="TechFlow AI", help="Your company or brand name")
        industry = st.selectbox("Industry", [
            "Technology / SaaS", "E-commerce", "Finance", "Healthcare", "Education", "Other"
        ])
        target_audience = st.text_area(
            "Target Audience",
            value="Busy professionals, startup founders, tech enthusiasts aged 25-45",
            height=100,
        )

    with col2:
        product_info = st.text_area(
            "Product / Campaign Info",
            value="Smart Scheduling Assistant — AI-powered calendar optimization that saves 5 hours per week",
            height=100,
        )
        use_api_trends = st.checkbox("Fetch Real-Time Trends", value=False,
                                     help="Uses Google Trends & Reddit APIs (slower)")
        generate_image = st.checkbox("Generate Post Image", value=False,
                                     help="AI image via Stable Diffusion (~30 s)")

    st.markdown("---")

    col_btn1, col_btn2, _ = st.columns([1, 1, 3])
    with col_btn1:
        run_clicked = st.button("🚀 Run Campaign", type="primary", use_container_width=True)
    with col_btn2:
        if st.button("📋 Load Example", use_container_width=True):
            st.toast("Example campaign values loaded!")

    if run_clicked:
        context = {
            "brand_name": brand_name,
            "industry": industry,
            "product_info": product_info,
            "target_audience": target_audience,
        }

        # Progress UI
        progress_placeholder = st.empty()
        status_placeholder = st.empty()

        steps = [
            ("📊 Fetching trends…", 0.10),
            ("💡 Agents proposing ideas…", 0.30),
            ("🗣️ Agents debating…", 0.55),
            ("⚖️ Arbitrator deciding…", 0.70),
            ("📝 Generating content…", 0.85),
            ("📈 Simulating engagement…", 0.92),
            ("🧠 Updating weights…", 0.97),
        ]

        def show_step(idx):
            html_parts = []
            for j, (label, _) in enumerate(steps):
                if j < idx:
                    html_parts.append(f'<span class="step-badge step-done">✓ {label}</span>')
                elif j == idx:
                    html_parts.append(f'<span class="step-badge step-active">● {label}</span>')
                else:
                    html_parts.append(f'<span class="step-badge step-pending">○ {label}</span>')
            progress_placeholder.markdown(
                '<div style="display:flex;flex-wrap:wrap;gap:4px;margin:12px 0;">' + "".join(html_parts) + '</div>',
                unsafe_allow_html=True,
            )
            status_placeholder.progress(steps[idx][1])

        try:
            show_step(0)
            result = st.session_state.orchestrator.run_campaign_iteration(
                context,
                use_api_trends=use_api_trends,
                generate_image=generate_image,
            )
            # Show final done state
            done_html = "".join(f'<span class="step-badge step-done">✓ {l}</span>' for l, _ in steps)
            progress_placeholder.markdown(
                '<div style="display:flex;flex-wrap:wrap;gap:4px;margin:12px 0;">' + done_html + '</div>',
                unsafe_allow_html=True,
            )
            status_placeholder.progress(1.0)

            st.session_state.iterations.append(result)
            st.success(f"Campaign iteration #{len(st.session_state.iterations)} complete!", icon="✅")
            st.balloons()
        except Exception as e:
            st.error(f"Error running campaign: {e}")


# ═══════════════════════════════════════════════
# PAGE: DEBATE
# ═══════════════════════════════════════════════
def page_debate():
    st.markdown("## 🗣️ Agent Debate Transcript")
    st.caption("See how your AI agents proposed, debated, and decided")

    if not st.session_state.iterations:
        st.markdown(
            "<div style='text-align:center;padding:60px 0;color:gray;'>"
            "<div style='font-size:2.5rem;margin-bottom:10px;'>🗣️</div>"
            "<div>No debates yet. Run a campaign first!</div></div>",
            unsafe_allow_html=True)
        return

    iteration_num = st.selectbox(
        "Select Iteration",
        range(1, len(st.session_state.iterations) + 1),
        format_func=lambda x: f"Iteration {x}",
        key="debate_iter",
    )
    iteration = st.session_state.iterations[iteration_num - 1]

    # ---- Trends ----
    st.markdown("##### 📊 Trending Topics Used")
    trends = iteration.get("trends", [])
    if trends:
        cols = st.columns(min(len(trends), 5))
        for i, trend in enumerate(trends[:5]):
            with cols[i]:
                vol = trend.get("volume", "?")
                vol_color = "#22c55e" if vol == "high" else ("#eab308" if vol == "medium" else "#6b7280")
                st.markdown(f"""
                <div class="stat-card" style="text-align:center;">
                    <div style="font-weight:600;font-size:.85rem;">{trend.get('topic','?')[:22]}</div>
                    <div style="color:{vol_color};font-size:.72rem;margin-top:4px;">● {vol}</div>
                </div>
                """, unsafe_allow_html=True)
    st.markdown("")

    # ---- Proposals ----
    st.markdown("##### 💡 Agent Proposals")
    proposals = iteration.get("proposals", {})
    for agent_id, proposal in proposals.items():
        agent = st.session_state.orchestrator.agents.get(agent_id)
        if agent:
            icon = get_agent_icon(agent_id)
            color = get_agent_color(agent_id)
            with st.expander(f"{icon} {agent.name} — Proposal", expanded=True):
                st.markdown(f"<div style='border-left:3px solid {color};padding-left:12px;'>"
                            f"<b>Weight:</b> {agent.voting_weight:.2f}</div>", unsafe_allow_html=True)
                st.markdown("")
                st.markdown(proposal)

    st.markdown("---")

    # ---- Critiques ----
    st.markdown("##### 🗣️ Agent Critiques")
    critiques = iteration.get("critiques", {})
    for agent_id, critique in critiques.items():
        agent = st.session_state.orchestrator.agents.get(agent_id)
        if agent:
            icon = get_agent_icon(agent_id)
            with st.expander(f"{icon} {agent.name} — Critique"):
                st.markdown(critique)

    st.markdown("---")

    # ---- Decision ----
    st.markdown("##### ⚖️ Arbitrator Decision")
    decision = iteration.get("decision", {})
    engagement = iteration.get("engagement", {})

    c1, c2, c3 = st.columns(3)
    with c1:
        winner = decision.get("winner", "N/A").replace("_", " ").title()
        winner_icon = get_agent_icon(decision.get("winner", ""))
        render_stat_card("Winner", f"{winner_icon} {winner}")
    with c2:
        render_stat_card("Confidence", f"{decision.get('confidence', 'N/A')}/10")
    with c3:
        render_stat_card("Engagement Score", f"{engagement.get('overall_score', 0):.1f}/10")

    st.markdown("")
    with st.container(border=True):
        st.markdown("**Reasoning**")
        st.markdown(decision.get("reasoning", "No reasoning provided"))
    with st.container(border=True):
        st.markdown("**Implementation Plan**")
        st.markdown(decision.get("implementation", "No implementation details"))


# ═══════════════════════════════════════════════
# PAGE: CONTENT
# ═══════════════════════════════════════════════
def page_content():
    st.markdown("## 📝 Generated Content")
    st.caption("AI-generated social media posts from your campaigns")

    if not st.session_state.iterations:
        st.markdown(
            "<div style='text-align:center;padding:60px 0;color:gray;'>"
            "<div style='font-size:2.5rem;margin-bottom:10px;'>📝</div>"
            "<div>No content yet. Run a campaign first!</div></div>",
            unsafe_allow_html=True)
        return

    iteration_num = st.selectbox(
        "Select Iteration",
        range(1, len(st.session_state.iterations) + 1),
        format_func=lambda x: f"Iteration {x}",
        key="content_iter",
    )
    iteration = st.session_state.iterations[iteration_num - 1]
    content = iteration.get("content", {})

    col_c1, col_c2 = st.columns([3, 2])

    with col_c1:
        st.markdown("##### 📄 Post Preview")
        platform = content.get("platform", "N/A").upper()
        plat_icon = {"TWITTER": "𝕏", "INSTAGRAM": "📸", "LINKEDIN": "💼"}.get(platform, "📱")

        with st.container(border=True):
            st.markdown(f"<div style='display:flex;align-items:center;gap:8px;margin-bottom:10px;'>"
                        f"<span style='font-size:1.4rem;'>{plat_icon}</span>"
                        f"<span style='font-weight:700;'>{platform}</span>"
                        f"<span style='color:gray;font-size:.8rem;'>· {content.get('posting_time', 'N/A')}</span>"
                        f"</div>", unsafe_allow_html=True)
            st.markdown(content.get("caption", "No caption generated"))
            st.markdown("")
            hashtags = content.get("hashtags", [])
            if hashtags:
                tag_html = " ".join(
                    f"<span style='display:inline-block;border:1px solid rgba(14,165,233,.3);color:#0ea5e9;"
                    f"border-radius:20px;padding:2px 10px;font-size:.78rem;margin:2px;'>{h}</span>"
                    for h in hashtags
                )
                st.markdown(tag_html, unsafe_allow_html=True)
            st.caption(f"{content.get('char_count', 0)} characters")

    with col_c2:
        st.markdown("##### 🖼️ Generated Image")
        image_path = content.get("image_path")
        if image_path and os.path.exists(image_path):
            st.image(image_path, use_container_width=True)
        else:
            st.markdown(
                "<div style='border:2px dashed rgba(128,128,128,.25);border-radius:12px;padding:60px 20px;"
                "text-align:center;color:gray;'>"
                "<div style='font-size:2rem;margin-bottom:8px;'>🖼️</div>"
                "No image generated for this iteration<br>"
                "<span style='font-size:.75rem;'>Enable image generation in Campaign settings</span>"
                "</div>",
                unsafe_allow_html=True)

    st.markdown("---")

    # ---- Engagement metrics ----
    st.markdown("##### 📈 Simulated Engagement")
    engagement = iteration.get("engagement", {})

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_stat_card("Likes", f"{engagement.get('likes', 0):,}", "Simulated", True)
    with c2:
        render_stat_card("Shares", f"{engagement.get('shares', 0):,}", "Simulated", True)
    with c3:
        render_stat_card("Comments", f"{engagement.get('comments', 0):,}", "Simulated", True)
    with c4:
        sent = engagement.get("sentiment", 0)
        render_stat_card("Sentiment", f"{sent:.0%}", "Positive" if sent >= 0.6 else "Low", sent >= 0.6)


# ═══════════════════════════════════════════════
# PAGE: ANALYTICS
# ═══════════════════════════════════════════════
def page_analytics():
    st.markdown("## 📈 Analytics & Learning")
    st.caption("Track how your AI council evolves over time")

    if not st.session_state.iterations:
        st.markdown(
            "<div style='text-align:center;padding:60px 0;color:gray;'>"
            "<div style='font-size:2.5rem;margin-bottom:10px;'>📈</div>"
            "<div>Run at least one campaign to see analytics.</div></div>",
            unsafe_allow_html=True)
        return

    # ---- Weight evolution ----
    st.markdown("##### 🎯 Agent Weight Evolution")
    st.caption("Watch agents gain or lose influence based on performance")

    weight_history = st.session_state.orchestrator.get_weight_history()
    if weight_history:
        fig_w = go.Figure()
        for aid, weights in weight_history.items():
            if not weights:
                continue
            agent = st.session_state.orchestrator.agents.get(aid)
            fig_w.add_trace(go.Scatter(
                x=list(range(1, len(weights) + 1)),
                y=weights,
                mode="lines+markers",
                name=agent.name if agent else aid,
                line=dict(width=3, color=get_agent_color(aid)),
                marker=dict(size=8),
            ))
        fig_w.update_layout(
            xaxis_title="Iteration", yaxis_title="Voting Weight",
            hovermode="x unified", height=380,
            margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(orientation="h"),
        )
        st.plotly_chart(fig_w, use_container_width=True)

    st.markdown("---")

    # ---- Engagement over time ----
    chart_l, chart_r = st.columns([3, 2])

    with chart_l:
        st.markdown("##### 📊 Engagement per Iteration")
        eng_data = []
        for i, it in enumerate(st.session_state.iterations, 1):
            e = it.get("engagement", {})
            eng_data.append({
                "Iteration": i,
                "Score": e.get("overall_score", 0),
                "Likes": e.get("likes", 0),
                "Shares": e.get("shares", 0),
            })
        df = pd.DataFrame(eng_data)
        fig_e = px.bar(df, x="Iteration", y="Score", color="Score",
                       color_continuous_scale=["#bfdbfe", "#0ea5e9", "#1d4ed8"],
                       text_auto=".1f")
        fig_e.update_layout(height=340, margin=dict(l=0, r=0, t=10, b=0), showlegend=False)
        st.plotly_chart(fig_e, use_container_width=True)

    with chart_r:
        st.markdown("##### 🏆 Winner Distribution")
        winners = [it.get("decision", {}).get("winner", "unknown") for it in st.session_state.iterations]
        wc = pd.Series(winners).value_counts()
        colors = [get_agent_color(name) for name in wc.index]
        fig_p = px.pie(
            values=wc.values,
            names=[n.replace("_", " ").title() for n in wc.index],
            color_discrete_sequence=colors,
        )
        fig_p.update_layout(height=340, margin=dict(l=0, r=0, t=10, b=10))
        st.plotly_chart(fig_p, use_container_width=True)

    st.markdown("---")

    # ---- Engagement breakdown ----
    st.markdown("##### 📊 Detailed Metrics")
    if len(st.session_state.iterations) >= 1:
        df_detail = pd.DataFrame(eng_data)
        df_melt = df_detail.melt(id_vars="Iteration", value_vars=["Likes", "Shares"],
                                  var_name="Metric", value_name="Count")
        fig_d = px.area(df_melt, x="Iteration", y="Count", color="Metric",
                        color_discrete_map={"Likes": "#0ea5e9", "Shares": "#22c55e"})
        fig_d.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="h"))
        st.plotly_chart(fig_d, use_container_width=True)


# ═══════════════════════════════════════════════
# PAGE: COMPARE
# ═══════════════════════════════════════════════
def page_compare():
    st.markdown("## 🔄 Iteration Comparison")
    st.caption("Compare two campaign iterations side-by-side")

    if len(st.session_state.iterations) < 2:
        st.markdown(
            "<div style='text-align:center;padding:60px 0;color:gray;'>"
            "<div style='font-size:2.5rem;margin-bottom:10px;'>🔄</div>"
            "<div>Run at least 2 campaigns to compare iterations.</div></div>",
            unsafe_allow_html=True)
        return

    c1, c2 = st.columns(2)
    with c1:
        iter1 = st.selectbox("First Iteration", range(1, len(st.session_state.iterations) + 1),
                              format_func=lambda x: f"Iteration {x}", key="cmp_1")
    with c2:
        iter2 = st.selectbox("Second Iteration", range(1, len(st.session_state.iterations) + 1),
                              format_func=lambda x: f"Iteration {x}", key="cmp_2",
                              index=min(1, len(st.session_state.iterations) - 1))

    if iter1 == iter2:
        st.warning("Select two different iterations to compare.")
        return

    comparison = st.session_state.orchestrator.compare_iterations(iter1 - 1, iter2 - 1)

    # ---- Summary cards ----
    st.markdown("##### Summary")
    m1, m2, m3 = st.columns(3)
    eng_diff = comparison["changes"]["engagement_diff"]
    with m1:
        changed = comparison["changes"]["winner_changed"]
        render_stat_card("Winner Changed", "Yes" if changed else "No",
                         "Different strategy" if changed else "Same winner", not changed)
    with m2:
        render_stat_card("Engagement Δ", f"{eng_diff:+.1f}",
                         "Improved" if eng_diff > 0 else ("Declined" if eng_diff < 0 else "Stable"),
                         eng_diff >= 0)
    with m3:
        render_stat_card("Learning", "Active" if abs(eng_diff) > 0.5 else "Stable",
                         "Weights shifting" if abs(eng_diff) > 0.5 else "Converging")

    st.markdown("---")

    # ---- Side-by-side ----
    col_a, col_b = st.columns(2)

    for col, iter_num, iter_key in [(col_a, iter1, "iteration_1"), (col_b, iter2, "iteration_2")]:
        with col:
            it_data = st.session_state.iterations[iter_num - 1]
            comp = comparison[iter_key]
            winner_id = comp["winner"] or "—"
            winner_name = winner_id.replace("_", " ").title()
            icon = get_agent_icon(winner_id)
            color = get_agent_color(winner_id)

            st.markdown(f"##### Iteration {iter_num}")
            with st.container(border=True):
                st.markdown(f"<div style='display:flex;align-items:center;gap:8px;margin-bottom:6px;'>"
                            f"<span style='font-size:1.3rem;'>{icon}</span>"
                            f"<span style='font-weight:700;color:{color};'>{winner_name}</span>"
                            f"</div>", unsafe_allow_html=True)
                st.markdown(f"**Engagement:** {comp['engagement']:.1f}/10")
                st.markdown("**Agent Weights:**")
                for aid, w in comp.get("weights", {}).items():
                    st.markdown(f"- {get_agent_icon(aid)} {aid.replace('_', ' ').title()}: **{w:.2f}**")

            content = it_data.get("content", {})
            caption = content.get("caption", "N/A")
            st.markdown("**Caption Preview:**")
            st.code(caption[:300] + ("…" if len(caption) > 300 else ""), language=None)


# ═══════════════════════════════════════════════
# MAIN ROUTING
# ═══════════════════════════════════════════════
def main():
    # ---- Auth gate ----
    if not st.session_state.logged_in:
        if st.session_state.auth_page == "signup":
            page_signup()
        else:
            page_login()
        return

    # ---- Initialize backend ----
    if not initialize_system():
        st.stop()

    # ---- Chrome ----
    render_sidebar()
    render_chatbot()

    # ---- Page router ----
    page = st.session_state.page
    router = {
        "Dashboard": page_dashboard,
        "Campaign":  page_campaign,
        "Debate":    page_debate,
        "Content":   page_content,
        "Analytics": page_analytics,
        "Compare":   page_compare,
    }
    router.get(page, page_dashboard)()


if __name__ == "__main__":
    main()
