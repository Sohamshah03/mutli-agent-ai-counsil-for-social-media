"""
SocialPulse AI — Social Media Manager
Streamlit conversion of the Next.js SocialPulse app.
Run:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time, textwrap, random
from datetime import datetime

# ──────────────────────────────────────────────
# Page config & custom CSS
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="SocialPulse AI - Social Media Manager",
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
.brand-icon {background:#0ea5e9;color:#fff;width:32px;height:32px;border-radius:8px;
             display:flex;align-items:center;justify-content:center;font-size:16px;}
.brand-name {font-weight:700;font-size:1.15rem;color:inherit;}

/* ---- stat card ---- */
.stat-card {border:1px solid rgba(128,128,128,.2);border-radius:10px;padding:16px 18px;
            background:var(--background-color);}
.stat-title {font-size:.75rem;color:gray;}
.stat-value {font-size:1.5rem;font-weight:700;}
.stat-change-pos {font-size:.75rem;color:#22c55e;}
.stat-change-neg {font-size:.75rem;color:#ef4444;}

/* ---- post row ---- */
.post-row {border:1px solid rgba(128,128,128,.2);border-radius:10px;padding:12px 14px;
           margin-bottom:8px;display:flex;align-items:center;gap:12px;}

/* ---- insight card ---- */
.insight-card {border-radius:10px;padding:14px;margin-bottom:10px;}
.insight-opportunity {border:1px solid rgba(14,165,233,.3);background:rgba(14,165,233,.05);}
.insight-warning {border:1px solid rgba(245,158,11,.3);background:rgba(245,158,11,.05);}
.insight-success {border:1px solid rgba(34,197,94,.3);background:rgba(34,197,94,.05);}

/* ---- chat ---- */
.chat-bubble-user {background:#0ea5e9;color:#fff;padding:8px 12px;border-radius:10px;
                   margin-left:auto;max-width:80%;font-size:.875rem;margin-bottom:6px;}
.chat-bubble-ai {background:rgba(128,128,128,.15);padding:8px 12px;border-radius:10px;
                 max-width:80%;font-size:.875rem;margin-bottom:6px;white-space:pre-wrap;}

/* ---- score bar ---- */
.score-row {display:flex;justify-content:space-between;font-size:.75rem;margin-bottom:2px;}
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
    "chat_open": False,
    "chat_messages": [
        {"role": "assistant", "content": "Hey! I'm your AI social media strategist. Ask me anything about your content strategy, trending topics, or let me help you create posts."}
    ],
    "ig_selected_reel": 0,
    "yt_selected_short": 0,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ──────────────────────────────────────────────
# Mock Data
# ──────────────────────────────────────────────
ENGAGEMENT_DATA = pd.DataFrame({
    "day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    "Instagram": [4200, 3800, 5100, 4700, 6200, 7100, 6800],
    "YouTube":   [3800, 4100, 3600, 5200, 4800, 6200, 5800],
    "X":         [2100, 2400, 3200, 2800, 3600, 4100, 3900],
})

PERFORMANCE_DATA = pd.DataFrame({
    "type": ["Reels", "Stories", "Shorts", "Tweets", "Threads", "Carousels"],
    "engagement": [8200, 5400, 7100, 4300, 3800, 6500],
})

RECENT_POSTS = [
    {"platform": "Instagram", "icon": "📸", "title": "5 Tips for Better Content", "engagement": "12.4K", "time": "2h ago", "trend": "+24%"},
    {"platform": "YouTube",   "icon": "▶️", "title": "How I Grew to 100K",       "engagement": "8.7K",  "time": "5h ago", "trend": "+18%"},
    {"platform": "X",         "icon": "𝕏",  "title": "The content strategy no one...", "engagement": "3.2K", "time": "8h ago", "trend": "+42%"},
]

MOCK_REELS = [
    {"id": 1, "title": "5 Editing Tricks You Need",      "views": "245K",  "likes": "18.2K", "comments": "432",  "audio": "Trending Audio #1", "duration": "0:28", "hookScore": 94, "captionScore": 88, "hashtagScore": 76,
     "aiSummary": "This reel performed exceptionally well due to its strong opening hook that immediately captures attention. The use of trending audio boosted discoverability by 340%. The quick-cut editing style maintained viewer retention above 85% through the entire video."},
    {"id": 2, "title": "Morning Routine for Creators",    "views": "189K",  "likes": "14.7K", "comments": "287",  "audio": "Lo-fi Beats",       "duration": "0:45", "hookScore": 82, "captionScore": 91, "hashtagScore": 85,
     "aiSummary": "Strong performance driven by relatable content and excellent caption strategy. The caption used a curiosity gap that drove 42% more saves than average. Hashtag mix of niche + broad tags helped reach new audiences."},
    {"id": 3, "title": "How to Go Viral in 2026",         "views": "512K",  "likes": "38.4K", "comments": "1.2K", "audio": "Original Audio",    "duration": "0:58", "hookScore": 97, "captionScore": 95, "hashtagScore": 90,
     "aiSummary": "Your top performing reel this month. The problem-solution hook format drove 97% retention in the first 3 seconds. Educational content with actionable tips generated massive save and share rates. This content format should be replicated."},
    {"id": 4, "title": "Behind the Scenes",               "views": "98K",   "likes": "7.8K",  "comments": "156",  "audio": "Chill Vibes",       "duration": "0:32", "hookScore": 71, "captionScore": 68, "hashtagScore": 72,
     "aiSummary": "Average performance. The hook could be stronger — consider starting with the most visually interesting moment. Caption was too long and lacked a clear CTA. Consider adding more niche-specific hashtags."},
    {"id": 5, "title": "Gear I Use Daily",                "views": "156K",  "likes": "11.3K", "comments": "345",  "audio": "Tech Review Beat",  "duration": "0:41", "hookScore": 88, "captionScore": 82, "hashtagScore": 79,
     "aiSummary": "Good performance with product-focused content. The list format keeps viewers watching. Consider adding text overlays for each item to boost accessibility and engagement. Audio choice was relevant and trending."},
    {"id": 6, "title": "Reply to @user: Best camera?",    "views": "203K",  "likes": "15.1K", "comments": "892",  "audio": "Reply Audio",       "duration": "0:22", "hookScore": 91, "captionScore": 87, "hashtagScore": 81,
     "aiSummary": "Reply videos consistently perform well for your account. The short duration and direct answer format led to high completion rates. Comment engagement was 3x your average, indicating strong community building."},
]

MOCK_SHORTS = [
    {"id": 1, "title": "This AI Tool Changes Everything", "views": "1.2M",  "likes": "45.2K", "duration": "0:58", "seoScore": 92, "titleScore": 95, "thumbnailCTR": 14.2, "hookRetention": 89,
     "aiInsight": "Exceptional performance driven by a strong curiosity-gap title and trending topic. The first 3 seconds feature a dramatic reveal that retains 89% of viewers. SEO optimization is excellent with relevant keywords in title and description."},
    {"id": 2, "title": "Stop Using ChatGPT Wrong",        "views": "876K",  "likes": "32.1K", "duration": "0:45", "seoScore": 88, "titleScore": 91, "thumbnailCTR": 12.8, "hookRetention": 85,
     "aiInsight": "The negative framing in the title creates a knowledge gap that drives clicks. The thumbnail with bold text and contrasting colors achieved above-average CTR. Consider adding timestamps in the description for better SEO."},
    {"id": 3, "title": "5 Apps You NEED in 2026",         "views": "654K",  "likes": "24.8K", "duration": "0:52", "seoScore": 85, "titleScore": 88, "thumbnailCTR": 11.5, "hookRetention": 82,
     "aiInsight": "List format performs consistently well. The CAPS emphasis on 'NEED' adds urgency. Each app is shown for the right duration to maintain engagement. Tags could be more specific to improve discoverability."},
    {"id": 4, "title": "I Built This in 24 Hours",        "views": "432K",  "likes": "18.9K", "duration": "0:48", "seoScore": 78, "titleScore": 84, "thumbnailCTR": 10.2, "hookRetention": 79,
     "aiInsight": "Time-challenge format engages viewers. The build process is shown in satisfying fast-motion. SEO could improve with more descriptive keywords. Consider A/B testing thumbnail styles for this content type."},
]

MOCK_TWEETS = [
    {"id": 1, "content": "The best content strategy isn't about posting more. It's about posting smarter.\n\nHere's what I mean:\n\n- Quality > Quantity\n- Consistency > Frequency\n- Community > Followers\n\nFocus on these 3 and watch your growth accelerate.", "likes": "4.2K", "retweets": "1.8K", "replies": "234", "time": "2h"},
    {"id": 2, "content": "I spent $0 on ads and grew from 0 to 50K followers in 6 months.\n\nThe secret? Threads.\n\nHere's the exact formula I used (bookmark this):", "likes": "8.7K", "retweets": "3.2K", "replies": "567", "time": "5h"},
    {"id": 3, "content": "Hot take: AI won't replace creators.\n\nBut creators who use AI will replace those who don't.\n\nThe tools are free. The knowledge is free. The only cost is your time to learn them.", "likes": "12.1K", "retweets": "5.4K", "replies": "892", "time": "1d"},
    {"id": 4, "content": "90% of people consume content.\n9% engage with content.\n1% create content.\n\nBe in the 1%.", "likes": "6.3K", "retweets": "2.7K", "replies": "345", "time": "1d"},
    {"id": 5, "content": "The algorithm doesn't owe you anything.\n\nBut it rewards:\n- Consistency\n- Engagement\n- Value\n\nFocus on what you can control.", "likes": "3.8K", "retweets": "1.4K", "replies": "189", "time": "2d"},
]

GENERATED_TWEETS = [
    "The biggest lie in content creation? That you need to be original.\n\nYou don't. You need to be authentic.\n\nRemix ideas. Add your perspective. That's how you stand out.",
    "I analyzed 1,000 viral tweets.\n\nThe pattern? It's not luck.\n\n1. Start with a bold claim\n2. Back it with data or story\n3. End with a takeaway\n\nSimple, but most people skip step 2.",
    "Unpopular opinion: Engagement farming is destroying X.\n\nReal growth comes from real conversations.\n\nStop asking \"What's your favorite...\" and start sharing what you actually know.",
]

GENERATED_THREAD = [
    "I went from 0 to 50K followers in 6 months without spending a dime on ads.\n\nHere's the exact playbook I followed (bookmark this thread):",
    "Step 1: Niche Down Hard\n\nI didn't try to be everything to everyone. I picked ONE topic and went deep.\n\nResult: My content attracted the right audience instead of random followers.",
    "Step 2: The 3-1-1 Posting Formula\n\n- 3 value posts (teach something)\n- 1 personal story (build connection)\n- 1 engagement post (build community)\n\nThis ratio kept my feed balanced and growing.",
    "Step 3: Reply Strategy\n\nI spent 30 min/day replying to larger accounts in my niche.\n\nNot \"great post!\" but thoughtful, value-added replies that made people click my profile.",
    "Step 4: Thread Thursdays\n\nEvery Thursday, I posted a deep-dive thread.\n\nThreads get 3x more engagement than single tweets for educational content.\n\nThis alone drove 40% of my growth.",
    "That's the playbook.\n\nNo secrets. No shortcuts.\n\nJust consistent execution of a simple strategy.\n\nIf this was helpful, follow me @alexcreator for more content growth tips.",
]

MOCK_CAPTIONS = [
    "The best content strategy is the one you actually stick to.\n\nHere's my framework:\n1. Plan your week in 30 minutes\n2. Batch create 5 pieces of content\n3. Schedule everything in advance\n4. Engage for 15 min after posting\n\nSimple? Yes. Effective? Absolutely.\n\nSave this for later.",
    "I asked 50 top creators their #1 growth tip.\n\nThe answer was unanimous: Consistency beats perfection.\n\nStop waiting for the perfect post. Start sharing your journey today.\n\nYour future self will thank you.",
    "Unpopular opinion: You don't need 100K followers to make an impact.\n\nI've seen creators with 5K followers:\n- Land brand deals\n- Build communities\n- Change lives\n\nFocus on depth, not width.",
]

MOCK_HOOKS = [
    "Nobody's talking about this, but it changed everything for me...",
    "I spent 6 months testing this so you don't have to",
    "The #1 mistake I see creators making in 2026",
    "What if I told you this takes 5 minutes?",
    "Stop scrolling. This is the sign you've been waiting for.",
]

MOCK_HASHTAGS = [
    "#ContentCreator", "#SocialMediaTips", "#CreatorEconomy", "#GrowOnInstagram",
    "#DigitalMarketing", "#ContentStrategy", "#InstagramGrowth", "#CreatorLife",
    "#SocialMediaMarketing", "#ContentCreation", "#MarketingTips", "#ViralContent",
]

AI_INSIGHTS = [
    {"type": "opportunity", "platform": "Instagram", "icon": "📸",
     "title": "Carousel posts are trending in your niche",
     "description": "Your niche has seen a 42% increase in carousel engagement this week. Consider creating a carousel post about your top-performing topic.",
     "impact": "High", "timeframe": "This week"},
    {"type": "warning", "platform": "YouTube", "icon": "▶️",
     "title": "Shorts upload frequency dropped",
     "description": "You posted 3 fewer Shorts this week compared to last week. Consistent posting is key to algorithmic visibility.",
     "impact": "Medium", "timeframe": "Immediate"},
    {"type": "opportunity", "platform": "X", "icon": "𝕏",
     "title": "Thread engagement is 3x higher than single tweets",
     "description": "Your thread posts consistently outperform single tweets. Increase thread frequency to 3-4 per week for optimal growth.",
     "impact": "High", "timeframe": "Next 2 weeks"},
    {"type": "success", "platform": "Instagram", "icon": "📸",
     "title": "Engagement rate hit all-time high",
     "description": "Your engagement rate of 5.2% is 72% above the average for creators with similar follower counts. Keep up the interactive content.",
     "impact": "Positive", "timeframe": "Ongoing"},
]

WEEKLY_GROWTH = pd.DataFrame({
    "week": ["W1", "W2", "W3", "W4", "W5", "W6"],
    "Followers":  [2400, 3100, 2800, 4200, 3600, 5100],
    "Engagement": [3200, 4100, 3800, 5200, 4800, 6400],
    "Reach":      [18000, 22000, 19500, 31000, 27000, 38000],
})

PLATFORM_STRENGTHS = pd.DataFrame({
    "subject":    ["Reach", "Engagement", "Growth", "Virality", "Consistency", "Community"],
    "Instagram":  [85, 78, 70, 88, 72, 80],
    "YouTube":    [72, 80, 85, 76, 90, 70],
    "X":          [65, 70, 75, 82, 68, 88],
})

BEST_POSTING_TIMES = [
    {"platform": "Instagram", "times": ["6:00 AM", "12:00 PM", "7:00 PM"], "bestDay": "Saturday"},
    {"platform": "YouTube",   "times": ["2:00 PM", "5:00 PM", "8:00 PM"], "bestDay": "Thursday"},
    {"platform": "X",         "times": ["8:00 AM", "12:00 PM", "6:00 PM"], "bestDay": "Tuesday"},
]

CONTENT_MIX = [
    {"type": "Educational",        "percentage": 35, "performance": 92},
    {"type": "Entertainment",      "percentage": 25, "performance": 78},
    {"type": "Behind-the-scenes",  "percentage": 20, "performance": 85},
    {"type": "Promotional",        "percentage": 10, "performance": 62},
    {"type": "Community",          "percentage": 10, "performance": 88},
]

CONNECTED_ACCOUNTS = [
    {"platform": "Instagram",    "handle": "@creator_studio", "connected": True, "followers": "184.2K"},
    {"platform": "YouTube",      "handle": "@techvision",     "connected": True, "followers": "342K"},
    {"platform": "X (Twitter)",  "handle": "@alexcreator",    "connected": True, "followers": "92.4K"},
]

# ──────────────────────────────────────────────
# Chatbot mock response logic
# ──────────────────────────────────────────────
MOCK_RESPONSES = {
    "default":
        "I'd be happy to help with your social media strategy! I can analyze trends, generate content ideas, optimize captions, and provide insights across Instagram, YouTube, and X. What would you like to work on?",
    "reel":
        "Based on the engagement data, this reel performed well due to several factors: 1) Strong hook in the first 3 seconds, 2) Trending audio that boosted discoverability, 3) High save rate indicating valuable content, and 4) Optimal posting time during peak audience activity.",
    "hooks":
        "Here are some high-performing hooks for your YouTube Short:\n\n1. \"Nobody talks about this, but...\"\n2. \"I tested this for 30 days and here's what happened\"\n3. \"Stop doing [X] if you want [result]\"\n4. \"The secret that top creators don't share\"\n5. \"You've been doing [X] wrong this whole time\"",
    "post":
        "Based on your recent performance data, I recommend posting a carousel on Instagram about your top-performing topic. The best time to post would be between 6-8 PM when your audience is most active. Focus on educational content since your last 3 highest-performing posts were all educational.",
    "caption":
        "Here's an optimized caption:\n\n\"Most people skip this step. But it's the #1 reason your content isn't growing.\n\nHere's the framework I use:\n\n1. Hook them in 3 seconds\n2. Deliver unexpected value\n3. End with a clear CTA\n\nSave this for later.\"\n\nThis uses proven viral patterns: open loop, numbered list, and a save-trigger CTA.",
}


def get_ai_response(msg: str) -> str:
    lower = msg.lower()
    if "reel" in lower or "perform" in lower:
        return MOCK_RESPONSES["reel"]
    if "hook" in lower or "youtube" in lower:
        return MOCK_RESPONSES["hooks"]
    if "post" in lower or "next" in lower:
        return MOCK_RESPONSES["post"]
    if "caption" in lower or "viral" in lower or "optimize" in lower:
        return MOCK_RESPONSES["caption"]
    return MOCK_RESPONSES["default"]


# ──────────────────────────────────────────────
# Helper renderers
# ──────────────────────────────────────────────
def render_stat_card(title: str, value: str, change: str, positive: bool = True):
    cls = "stat-change-pos" if positive else "stat-change-neg"
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-title">{title}</div>
        <div class="stat-value">{value}</div>
        <div class="{cls}">{change}</div>
    </div>
    """, unsafe_allow_html=True)


def render_progress_bar(label: str, score: int, max_val: int = 100):
    pct = int(score / max_val * 100)
    st.markdown(f"""
    <div class="score-row"><span>🎯 {label}</span><span><b>{score}/{max_val}</b></span></div>
    """, unsafe_allow_html=True)
    st.progress(pct)


# ═══════════════════════════════════════════════
# AUTH PAGES
# ═══════════════════════════════════════════════
def page_login():
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        st.markdown("")
        st.markdown("""
        <div style="text-align:center;margin-bottom:1.5rem;">
            <span style="background:#0ea5e9;color:#fff;padding:8px 12px;border-radius:10px;font-size:1.25rem;">⚡</span>
            <span style="font-weight:700;font-size:1.5rem;margin-left:.5rem;">SocialPulse</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### Welcome back")
        st.caption("Sign in to your account to continue")

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
            if st.button("Sign up →", type="tertiary"):
                st.session_state.auth_page = "signup"
                st.rerun()


def page_signup():
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        st.markdown("")
        st.markdown("""
        <div style="text-align:center;margin-bottom:1.5rem;">
            <span style="background:#0ea5e9;color:#fff;padding:8px 12px;border-radius:10px;font-size:1.25rem;">⚡</span>
            <span style="font-weight:700;font-size:1.5rem;margin-left:.5rem;">SocialPulse</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### Create your account")
        st.caption("Start managing your social media with AI")

        with st.form("signup_form"):
            email = st.text_input("Email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", placeholder="Create a password")
            confirm  = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
            st.markdown("**Preferred Platforms**")
            c1, c2, c3 = st.columns(3)
            with c1:
                ig = st.checkbox("Instagram")
            with c2:
                yt = st.checkbox("YouTube")
            with c3:
                xp = st.checkbox("X (Twitter)")
            submitted = st.form_submit_button("Create Account", use_container_width=True, type="primary")
            if submitted:
                st.session_state.logged_in = True
                st.session_state.page = "Dashboard"
                st.rerun()

        st.markdown("")
        c1, c2 = st.columns([3, 2])
        with c2:
            if st.button("← Login", type="tertiary"):
                st.session_state.auth_page = "login"
                st.rerun()


# ═══════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div class="brand-box">
            <div class="brand-icon">⚡</div>
            <div class="brand-name">SocialPulse</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**Platform**")
        pages_main = {
            "📊 Dashboard": "Dashboard",
            "📸 Instagram":  "Instagram",
            "▶️ YouTube":    "YouTube",
            "𝕏  X (Twitter)": "X",
        }
        for label, key in pages_main.items():
            if st.sidebar.button(label, use_container_width=True,
                                 type="primary" if st.session_state.page == key else "tertiary"):
                st.session_state.page = key
                st.rerun()

        st.markdown("---")
        st.markdown("**AI Tools**")
        pages_ai = {
            "✨ AI Post Generator": "AI Generator",
            "📈 Insights":         "Insights",
        }
        for label, key in pages_ai.items():
            if st.sidebar.button(label, use_container_width=True,
                                 type="primary" if st.session_state.page == key else "tertiary"):
                st.session_state.page = key
                st.rerun()

        st.markdown("---")
        if st.sidebar.button("⚙️ Settings", use_container_width=True,
                             type="primary" if st.session_state.page == "Settings" else "tertiary"):
            st.session_state.page = "Settings"
            st.rerun()

        st.markdown("---")
        if st.sidebar.button("🚪 Log out", use_container_width=True, type="tertiary"):
            st.session_state.logged_in = False
            st.session_state.auth_page = "login"
            st.rerun()


# ═══════════════════════════════════════════════
# AI CHATBOT (sidebar expander or popover‑like)
# ═══════════════════════════════════════════════
def render_chatbot():
    with st.sidebar:
        st.markdown("---")
        with st.expander("💬 **AI Assistant**", expanded=st.session_state.chat_open):
            # Messages
            for msg in st.session_state.chat_messages:
                if msg["role"] == "user":
                    st.markdown(f'<div class="chat-bubble-user">{msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-bubble-ai">{msg["content"]}</div>', unsafe_allow_html=True)

            # Quick prompts (show only if 1 message)
            if len(st.session_state.chat_messages) <= 1:
                prompts = [
                    "Why did this reel perform well?",
                    "Generate hooks for my YouTube Short",
                    "What should I post next?",
                    "Optimize this caption for virality",
                ]
                for p in prompts:
                    if st.button(p, key=f"qp_{p}", use_container_width=True, type="tertiary"):
                        st.session_state.chat_messages.append({"role": "user", "content": p})
                        st.session_state.chat_messages.append({"role": "assistant", "content": get_ai_response(p)})
                        st.rerun()

            user_input = st.chat_input("Ask me anything...", key="chatbot_input")
            if user_input:
                st.session_state.chat_messages.append({"role": "user", "content": user_input})
                st.session_state.chat_messages.append({"role": "assistant", "content": get_ai_response(user_input)})
                st.rerun()

            if len(st.session_state.chat_messages) > 1:
                if st.button("🗑️ Clear chat", key="clear_chat", use_container_width=True, type="tertiary"):
                    st.session_state.chat_messages = [st.session_state.chat_messages[0]]
                    st.rerun()


# ═══════════════════════════════════════════════
# PAGE: DASHBOARD
# ═══════════════════════════════════════════════
def page_dashboard():
    # Banner
    st.info(
        "**Your AI Social Media Command Center** — "
        "Analyze trends, optimize content, and manage posting across platforms. "
        "AI-powered insights to help you create high-performing content for Instagram, YouTube, and X.",
        icon="⚡",
    )
    col_btn = st.columns([5, 1])
    with col_btn[1]:
        if st.button("Start Creating ↗", type="primary"):
            st.session_state.page = "AI Generator"
            st.rerun()

    # Stat cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_stat_card("Total Followers", "247.3K", "+12.5% this month", True)
    with c2:
        render_stat_card("Total Views", "1.2M", "+8.2% this week", True)
    with c3:
        render_stat_card("Engagement Rate", "4.8%", "+0.3% from last week", True)
    with c4:
        render_stat_card("Total Likes", "89.4K", "-2.1% this week", False)

    st.markdown("")

    # Charts
    chart_left, chart_right = st.columns([4, 3])

    with chart_left:
        st.markdown("##### Cross-Platform Engagement")
        st.caption("Daily engagement across all platforms")
        df_melt = ENGAGEMENT_DATA.melt(id_vars="day", var_name="Platform", value_name="Engagement")
        fig = px.area(df_melt, x="day", y="Engagement", color="Platform",
                      color_discrete_map={"Instagram": "#0ea5e9", "YouTube": "#ec4899", "X": "#22c55e"})
        fig.update_layout(height=320, margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="h"))
        st.plotly_chart(fig, use_container_width=True)

    with chart_right:
        st.markdown("##### Content Performance")
        st.caption("Engagement by content type")
        fig2 = px.bar(PERFORMANCE_DATA, x="type", y="engagement", color_discrete_sequence=["#0ea5e9"])
        fig2.update_layout(height=320, margin=dict(l=0, r=0, t=10, b=0), showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    # Recent posts
    st.markdown("##### Recent Posts")
    st.caption("Latest content across all platforms")
    for post in RECENT_POSTS:
        c1, c2, c3, c4 = st.columns([0.5, 4, 1.5, 1])
        with c1:
            st.markdown(f"### {post['icon']}")
        with c2:
            st.markdown(f"**{post['title']}**  \n`{post['platform']}` · {post['time']}")
        with c3:
            st.metric(label="Engagement", value=post["engagement"], label_visibility="collapsed")
        with c4:
            st.markdown(f"<span style='color:#22c55e;font-weight:600'>{post['trend']}</span>", unsafe_allow_html=True)
        st.markdown("---")


# ═══════════════════════════════════════════════
# PAGE: INSTAGRAM
# ═══════════════════════════════════════════════
def page_instagram():
    st.markdown("## 📸 Instagram")
    st.caption("Analyze accounts, track performance, and get AI insights")

    # Search
    col_s, col_b = st.columns([4, 1])
    with col_s:
        st.text_input("Search public Instagram accounts...", key="ig_search", label_visibility="collapsed", placeholder="Search public Instagram accounts...")
    with col_b:
        st.button("Search", key="ig_search_btn")

    # Account overview
    st.markdown("---")
    c1, c2, c3, c4, c5, c6 = st.columns([2, 1.5, 1, 1, 1, 1])
    with c1:
        st.markdown("### 🟣 Creator Studio")
        st.caption("@creator_studio")
    with c2:
        pass
    with c3:
        st.metric("Followers", "184.2K")
    with c4:
        st.metric("Engagement", "5.2%")
    with c5:
        st.metric("Virality ⚡", "87")
    with c6:
        st.metric("Trend 📈", "92")

    st.markdown("---")

    # Reel grid + insights
    grid_col, insight_col = st.columns([3, 2])

    with grid_col:
        st.markdown("##### Feed")
        st.caption("Recent reels and posts — click to view AI insights")
        cols = st.columns(3)
        for idx, reel in enumerate(MOCK_REELS):
            with cols[idx % 3]:
                selected = st.session_state.ig_selected_reel == idx
                border_color = "#0ea5e9" if selected else "rgba(128,128,128,.2)"
                st.markdown(f"""
                <div style="border:2px solid {border_color};border-radius:10px;padding:10px;margin-bottom:10px;">
                    <div style="background:rgba(128,128,128,.1);border-radius:6px;padding:30px;text-align:center;color:gray;">▶ {reel['duration']}</div>
                    <p style="font-size:.8rem;font-weight:600;margin-top:6px;">{reel['title']}</p>
                    <p style="font-size:.65rem;color:gray;">👁 {reel['views']}  ❤ {reel['likes']}  💬 {reel['comments']}</p>
                    <p style="font-size:.65rem;color:gray;">🎵 {reel['audio']}</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button("View Insights", key=f"ig_reel_{idx}", use_container_width=True, type="tertiary"):
                    st.session_state.ig_selected_reel = idx
                    st.rerun()

    with insight_col:
        st.markdown("##### ✨ Post Insights")
        st.caption("AI analysis for selected post")
        reel = MOCK_REELS[st.session_state.ig_selected_reel]
        st.markdown(f"**{reel['title']}**")
        st.markdown(f"`{reel['views']} views` · `{reel['likes']} likes`")
        st.markdown("")
        render_progress_bar("Hook Strength", reel["hookScore"])
        render_progress_bar("Caption Effectiveness", reel["captionScore"])
        render_progress_bar("Hashtag Effectiveness", reel["hashtagScore"])
        st.markdown("")
        st.markdown("**✨ AI Summary**")
        st.markdown(f"<div style='font-size:.85rem;color:gray;line-height:1.6'>{reel['aiSummary']}</div>",
                    unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# PAGE: YOUTUBE
# ═══════════════════════════════════════════════
def page_youtube():
    st.markdown("## ▶️ YouTube")
    st.caption("Analyze channels, optimize Shorts, and generate content")

    col_s, col_b = st.columns([4, 1])
    with col_s:
        st.text_input("Search public YouTube channels...", key="yt_search", label_visibility="collapsed", placeholder="Search public YouTube channels...")
    with col_b:
        st.button("Search", key="yt_search_btn")

    # Channel overview
    st.markdown("---")
    c1, c2, c3, c4 = st.columns([3, 1.5, 1.5, 1.5])
    with c1:
        st.markdown("### 🔴 TechVision")
        st.caption("@techvision")
    with c2:
        st.metric("Subscribers", "342K")
    with c3:
        st.metric("Avg Views", "48.7K")
    with c4:
        st.metric("Shorts Score 📈", "88")

    st.markdown("---")

    tab_overview, tab_tools = st.tabs(["Shorts Feed", "AI Tools"])

    with tab_overview:
        grid_col, insight_col = st.columns([3, 2])
        with grid_col:
            st.markdown("##### Shorts")
            st.caption("Recent Shorts performance")
            cols = st.columns(2)
            for idx, short in enumerate(MOCK_SHORTS):
                with cols[idx % 2]:
                    selected = st.session_state.yt_selected_short == idx
                    border_color = "#0ea5e9" if selected else "rgba(128,128,128,.2)"
                    st.markdown(f"""
                    <div style="border:2px solid {border_color};border-radius:10px;padding:10px;margin-bottom:10px;">
                        <div style="background:rgba(128,128,128,.1);border-radius:6px;padding:40px;text-align:center;color:gray;">▶ {short['duration']}</div>
                        <p style="font-size:.8rem;font-weight:600;margin-top:6px;">{short['title']}</p>
                        <p style="font-size:.65rem;color:gray;">👁 {short['views']}  👍 {short['likes']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("View Insights", key=f"yt_short_{idx}", use_container_width=True, type="tertiary"):
                        st.session_state.yt_selected_short = idx
                        st.rerun()

        with insight_col:
            st.markdown("##### ✨ Video Insights")
            st.caption("AI analysis for selected Short")
            short = MOCK_SHORTS[st.session_state.yt_selected_short]
            st.markdown(f"**{short['title']}**")
            st.markdown(f"`{short['views']} views` · `{short['likes']} likes`")
            st.markdown("")
            render_progress_bar("SEO Score", short["seoScore"])
            render_progress_bar("Title Effectiveness", short["titleScore"])
            render_progress_bar("Thumbnail CTR", int(short["thumbnailCTR"]), 20)
            render_progress_bar("Hook Retention", short["hookRetention"])
            st.markdown("")
            st.markdown("**✨ AI Insight**")
            st.markdown(f"<div style='font-size:.85rem;color:gray;line-height:1.6'>{short['aiInsight']}</div>",
                        unsafe_allow_html=True)

    with tab_tools:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### 📝 Title Generator")
            st.caption("Generate optimized titles for Shorts")
            st.text_input("Topic or keyword", placeholder="e.g., AI productivity tools", key="yt_title_topic")
            if st.button("Generate Titles", key="yt_gen_titles"):
                pass
            st.markdown("""
            **Generated Titles:**
            1. This AI Tool Will 10x Your Productivity
            2. Stop Wasting Time — Use These AI Tools Instead
            3. The AI Productivity Stack That Changed My Life
            """)
        with c2:
            st.markdown("##### 📄 Description Generator")
            st.caption("SEO-optimized video descriptions")
            st.text_input("Video topic", placeholder="e.g., 5 must-have apps for 2026", key="yt_desc_topic")
            if st.button("Generate Description", key="yt_gen_desc"):
                pass
            st.text_area("Generated description", value="Discover the 5 must-have apps that will transform your workflow in 2026! From AI-powered tools to productivity boosters, these apps are changing the game.\n\n#productivity #apps #2026 #tech", height=120, key="yt_desc_out", disabled=True)

        c3, c4 = st.columns(2)
        with c3:
            st.markdown("##### 🏷️ Tags Generator")
            st.caption("Discover high-performing tags")
            st.text_input("Video topic", placeholder="e.g., tech review", key="yt_tag_topic")
            if st.button("Generate Tags", key="yt_gen_tags"):
                pass
            tags = ["tech", "review", "2026", "gadgets", "trending", "productivity", "AI", "apps", "must-have", "tools"]
            st.markdown(" ".join([f"`{t}`" for t in tags]))
        with c4:
            st.markdown("##### 🖼️ Thumbnail Text")
            st.caption("Attention-grabbing thumbnail copy")
            st.text_input("Video topic", placeholder="e.g., budget setup tour", key="yt_thumb_topic")
            if st.button("Generate Text", key="yt_gen_thumb"):
                pass
            st.markdown("""
            **Thumbnail Text Ideas:**
            1. BUDGET SETUP < $500
            2. YOU NEED THIS
            3. $0 → $500 SETUP
            """)


# ═══════════════════════════════════════════════
# PAGE: X (Twitter)
# ═══════════════════════════════════════════════
def page_x():
    st.markdown("## 𝕏 X (Twitter)")
    st.caption("Analyze accounts, track tweets, and generate viral content")

    col_s, col_b = st.columns([4, 1])
    with col_s:
        st.text_input("Search public X accounts...", key="x_search", label_visibility="collapsed", placeholder="Search public X accounts...")
    with col_b:
        st.button("Search", key="x_search_btn")

    # Account overview
    st.markdown("---")
    c1, c2, c3, c4 = st.columns([3, 1.5, 1.5, 1.5])
    with c1:
        st.markdown("### 🔵 Alex Creator")
        st.caption("@alexcreator")
    with c2:
        st.metric("Followers", "92.4K")
    with c3:
        st.metric("Following", "1,247")
    with c4:
        st.metric("Avg Engagement 📈", "3.8%")

    st.markdown("---")

    tab_feed, tab_single, tab_thread = st.tabs(["Tweet Feed", "Tweet Generator", "Thread Generator"])

    with tab_feed:
        for tweet in MOCK_TWEETS:
            with st.container(border=True):
                c1, c2 = st.columns([0.3, 5])
                with c1:
                    st.markdown("### 🔵")
                with c2:
                    st.markdown(f"**Alex Creator** `@alexcreator` · {tweet['time']}")
                    st.markdown(tweet["content"])
                    st.markdown(f"💬 {tweet['replies']}    🔁 {tweet['retweets']}    ❤️ {tweet['likes']}")

    with tab_single:
        gen_col, result_col = st.columns(2)
        with gen_col:
            st.markdown("##### ✨ Generate Tweets")
            st.caption("Create viral single tweets with AI")
            st.text_input("Topic", placeholder="e.g., content creation tips", key="x_tweet_topic")
            st.selectbox("Tone", ["Viral", "Professional", "Casual", "Educational", "Funny"], key="x_tweet_tone")
            st.button("✨ Generate Tweets", key="x_gen_tweets")
        with result_col:
            st.markdown("##### Generated Tweets")
            st.caption("Click Copy to copy any tweet")
            for i, tweet in enumerate(GENERATED_TWEETS):
                with st.container(border=True):
                    st.markdown(f"<div style='font-size:.85rem;line-height:1.6;white-space:pre-wrap'>{tweet}</div>", unsafe_allow_html=True)
                    if st.button("📋 Copy", key=f"copy_tweet_{i}"):
                        st.toast(f"Tweet {i+1} copied!")

    with tab_thread:
        gen_col, result_col = st.columns(2)
        with gen_col:
            st.markdown("##### ⚡ Thread Generator")
            st.caption("Create engaging tweet threads")
            st.text_area("Thread topic", placeholder="e.g., How I grew to 50K followers in 6 months", key="x_thread_topic", height=100)
            st.selectbox("Number of tweets", [4, 6, 8, 10], index=1, key="x_thread_count")
            st.button("✨ Generate Thread", key="x_gen_thread")
        with result_col:
            st.markdown("##### Generated Thread")
            st.caption("Preview your thread")
            for i, tweet in enumerate(GENERATED_THREAD):
                c_num, c_text = st.columns([0.3, 5])
                with c_num:
                    st.markdown(f"<div style='background:#0ea5e9;color:#fff;width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:.8rem;font-weight:700;'>{i+1}</div>", unsafe_allow_html=True)
                    if i < len(GENERATED_THREAD) - 1:
                        st.markdown("<div style='width:2px;height:40px;background:rgba(128,128,128,.3);margin:0 auto'></div>", unsafe_allow_html=True)
                with c_text:
                    with st.container(border=True):
                        st.markdown(f"<div style='font-size:.85rem;white-space:pre-wrap'>{tweet}</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# PAGE: AI GENERATOR
# ═══════════════════════════════════════════════
def page_ai_generator():
    st.markdown("## ✨ AI Post Generator")
    st.caption("Create high-performing content with AI assistance")

    tab_captions, tab_hooks, tab_hashtags = st.tabs(["Captions", "Hooks", "Hashtags"])

    with tab_captions:
        input_col, result_col = st.columns(2)
        with input_col:
            st.markdown("##### 🪄 Generate Captions")
            st.caption("Create engaging captions for any platform")
            platform = st.selectbox("Platform", ["📸 Instagram", "▶️ YouTube", "𝕏 X (Twitter)"], key="aig_platform")
            topic = st.text_input("Topic", placeholder="e.g., content creation tips for beginners", key="aig_topic")
            tone = st.selectbox("Tone", ["Inspirational", "Educational", "Casual", "Professional", "Funny"], key="aig_tone")
            context = st.text_area("Additional context (optional)", placeholder="Add any specific details, key points, or brand voice notes...", key="aig_context", height=80)
            st.button("✨ Generate Captions", key="aig_gen_captions", use_container_width=True, type="primary")
        with result_col:
            st.markdown("##### Generated Captions")
            st.caption("Click Copy to copy a caption")
            for i, caption in enumerate(MOCK_CAPTIONS):
                with st.container(border=True):
                    st.markdown(f"<div style='font-size:.85rem;white-space:pre-wrap;line-height:1.6'>{caption}</div>", unsafe_allow_html=True)
                    c1, c2 = st.columns([3, 1])
                    plat_label = platform.split(" ", 1)[1] if " " in platform else platform
                    with c1:
                        st.caption(f"`{plat_label}` · {len(caption)} characters")
                    with c2:
                        if st.button("📋 Copy", key=f"aig_copy_cap_{i}"):
                            st.toast(f"Caption {i+1} copied!")

    with tab_hooks:
        input_col, result_col = st.columns(2)
        with input_col:
            st.markdown("##### ✨ Hook Generator")
            st.caption("Generate attention-grabbing hooks for your content")
            st.text_input("Content topic", placeholder="e.g., productivity tips", key="aig_hook_topic")
            st.selectbox("Content type", ["Reel / Short", "Carousel", "Thread", "Single Post"], key="aig_hook_type")
            st.button("✨ Generate Hooks", key="aig_gen_hooks")
        with result_col:
            st.markdown("##### Generated Hooks")
            st.caption("Click Copy to copy any hook")
            for i, hook in enumerate(MOCK_HOOKS):
                with st.container(border=True):
                    c1, c2, c3 = st.columns([0.3, 4, 0.5])
                    with c1:
                        st.markdown(f"<div style='background:#0ea5e9;color:#fff;width:24px;height:24px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:.75rem;font-weight:700;'>{i+1}</div>", unsafe_allow_html=True)
                    with c2:
                        st.markdown(hook)
                    with c3:
                        if st.button("📋", key=f"aig_copy_hook_{i}"):
                            st.toast(f"Hook {i+1} copied!")

    with tab_hashtags:
        input_col, result_col = st.columns(2)
        with input_col:
            st.markdown("##### ✨ Hashtag Generator")
            st.caption("Find the best hashtags for maximum reach")
            st.text_input("Post topic", placeholder="e.g., social media marketing", key="aig_hash_topic")
            st.selectbox("Number of hashtags", [5, 12, 20, 30], index=1, key="aig_hash_count")
            st.button("✨ Generate Hashtags", key="aig_gen_hashtags")
        with result_col:
            st.markdown("##### Generated Hashtags")
            c_top_1, c_top_2 = st.columns([3, 1])
            with c_top_2:
                if st.button("📋 Copy All", key="aig_copy_all_hash"):
                    st.toast("All hashtags copied!")
            st.caption("Click individual tags or copy all")
            # Render tags as a flow
            tag_html = " ".join(
                [f"<span style='display:inline-block;border:1px solid rgba(128,128,128,.3);border-radius:20px;padding:4px 12px;font-size:.8rem;margin:3px;cursor:pointer;'>{t}</span>"
                 for t in MOCK_HASHTAGS]
            )
            st.markdown(tag_html, unsafe_allow_html=True)


# ═══════════════════════════════════════════════
# PAGE: INSIGHTS
# ═══════════════════════════════════════════════
def page_insights():
    st.markdown("## 📈 Insights")
    st.caption("AI-powered analytics and recommendations across all platforms")

    # AI recommendations
    st.markdown("##### ✨ AI Recommendations")
    cols = st.columns(2)
    for i, ins in enumerate(AI_INSIGHTS):
        with cols[i % 2]:
            css_class = f"insight-{ins['type']}"
            badge_color = "#ef4444" if ins["type"] == "warning" else ("#22c55e" if ins["type"] == "success" else "#0ea5e9")
            st.markdown(f"""
            <div class="insight-card {css_class}">
                <div style="display:flex;justify-content:space-between;align-items:start;margin-bottom:6px;">
                    <div>
                        <span style="font-size:.7rem;color:gray;">{ins['icon']} {ins['platform']}</span><br>
                        <span style="font-weight:600;font-size:.9rem;">{ins['title']}</span>
                    </div>
                    <span style="background:{badge_color};color:#fff;padding:2px 8px;border-radius:8px;font-size:.7rem;">{ins['impact']}</span>
                </div>
                <p style="font-size:.8rem;color:gray;line-height:1.5;">{ins['description']}</p>
                <p style="font-size:.7rem;color:gray;margin-top:4px;">🕐 {ins['timeframe']}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("")

    # Charts
    chart_left, chart_right = st.columns([4, 3])

    with chart_left:
        st.markdown("##### Weekly Growth")
        st.caption("Followers, engagement, and reach over time")
        df_melt = WEEKLY_GROWTH.melt(id_vars="week", var_name="Metric", value_name="Value")
        fig = px.area(df_melt, x="week", y="Value", color="Metric",
                      color_discrete_map={"Followers": "#0ea5e9", "Engagement": "#22c55e", "Reach": "#ec4899"})
        fig.update_layout(height=320, margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="h"))
        st.plotly_chart(fig, use_container_width=True)

    with chart_right:
        st.markdown("##### Platform Strengths")
        st.caption("Comparative analysis across platforms")
        fig_radar = go.Figure()
        categories = PLATFORM_STRENGTHS["subject"].tolist()
        for plat, color in [("Instagram", "#0ea5e9"), ("YouTube", "#ec4899"), ("X", "#22c55e")]:
            values = PLATFORM_STRENGTHS[plat].tolist()
            fig_radar.add_trace(go.Scatterpolar(r=values + [values[0]], theta=categories + [categories[0]],
                                                fill="toself", name=plat, line=dict(color=color), opacity=0.3))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                                height=320, margin=dict(l=30, r=30, t=10, b=10),
                                legend=dict(orientation="h"))
        st.plotly_chart(fig_radar, use_container_width=True)

    # Bottom row
    col_times, col_mix = st.columns(2)

    with col_times:
        st.markdown("##### 📅 Best Posting Times")
        st.caption("Optimal times based on your audience activity")
        for item in BEST_POSTING_TIMES:
            with st.container(border=True):
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.markdown(f"**{item['platform']}**")
                    st.caption(f"Best day: {item['bestDay']}")
                with c2:
                    st.markdown(" · ".join([f"`{t}`" for t in item["times"]]))

    with col_mix:
        st.markdown("##### 🎯 Content Mix")
        st.caption("Recommended distribution & performance")
        for item in CONTENT_MIX:
            c1, c2, c3 = st.columns([2, 3, 1])
            with c1:
                st.markdown(f"**{item['type']}**")
            with c2:
                st.progress(item["percentage"])
            with c3:
                st.markdown(f"`{item['performance']}/100`")


# ═══════════════════════════════════════════════
# PAGE: SETTINGS
# ═══════════════════════════════════════════════
def page_settings():
    st.markdown("## ⚙️ Settings")
    st.caption("Manage your account, connections, and preferences")

    tab_profile, tab_connections, tab_notifications = st.tabs(["Profile", "Connections", "Notifications"])

    with tab_profile:
        st.markdown("##### 👤 Profile Information")
        st.caption("Update your personal details")
        col_avatar, _ = st.columns([1, 4])
        with col_avatar:
            st.markdown("""
            <div style="background:#0ea5e9;color:#fff;width:64px;height:64px;border-radius:50%;
                        display:flex;align-items:center;justify-content:center;font-size:1.25rem;font-weight:700;">SP</div>
            """, unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.text_input("First Name", value="Social", key="set_fname")
        with c2:
            st.text_input("Last Name", value="Pulse", key="set_lname")
        st.text_input("Email", value="hello@socialpulse.ai", key="set_email")
        st.text_input("Bio", value="AI-powered social media manager", key="set_bio")
        if st.button("Save Changes", key="set_save", type="primary"):
            st.toast("✅ Profile saved!")

        st.markdown("---")
        st.markdown("##### 🔒 Security")
        st.caption("Manage your password and security settings")
        st.text_input("Current Password", type="password", placeholder="Enter current password", key="set_cur_pw")
        st.text_input("New Password", type="password", placeholder="Enter new password", key="set_new_pw")
        if st.button("Update Password", key="set_pw_btn"):
            st.toast("✅ Password updated!")

    with tab_connections:
        st.markdown("##### 🔗 Connected Accounts")
        st.caption("Manage your connected social media accounts")
        for acc in CONNECTED_ACCOUNTS:
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 1, 1])
                with c1:
                    st.markdown(f"**{acc['platform']}**  \n`{acc['handle']}`")
                with c2:
                    st.markdown(f"`{acc['followers']}`")
                with c3:
                    if acc["connected"]:
                        st.markdown("<span style='color:#22c55e;font-weight:600;font-size:.85rem;'>✅ Connected</span>", unsafe_allow_html=True)
                    else:
                        st.button("Connect", key=f"conn_{acc['platform']}")

    with tab_notifications:
        st.markdown("##### 🔔 Notification Preferences")
        st.caption("Choose what notifications you receive")

        st.markdown("**Performance Alerts**")
        st.toggle("Viral post alerts", value=True, key="notif_viral")
        st.toggle("Engagement drops", value=True, key="notif_drops")
        st.toggle("Weekly performance summary", value=True, key="notif_weekly")

        st.markdown("**AI Recommendations**")
        st.toggle("Content suggestions", value=True, key="notif_suggestions")
        st.toggle("Trending topics", value=False, key="notif_trending")
        st.toggle("Best time to post reminders", value=True, key="notif_posttime")

        st.markdown("**Account**")
        st.toggle("Email updates", value=True, key="notif_email")
        st.toggle("Security alerts", value=True, key="notif_security")


# ═══════════════════════════════════════════════
# MAIN ROUTING
# ═══════════════════════════════════════════════
def main():
    # Not logged in → show auth
    if not st.session_state.logged_in:
        if st.session_state.auth_page == "signup":
            page_signup()
        else:
            page_login()
        return

    # Logged in → sidebar + page
    render_sidebar()
    render_chatbot()

    page = st.session_state.page
    if page == "Dashboard":
        page_dashboard()
    elif page == "Instagram":
        page_instagram()
    elif page == "YouTube":
        page_youtube()
    elif page == "X":
        page_x()
    elif page == "AI Generator":
        page_ai_generator()
    elif page == "Insights":
        page_insights()
    elif page == "Settings":
        page_settings()
    else:
        page_dashboard()


if __name__ == "__main__":
    main()
