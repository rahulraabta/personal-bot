import streamlit as st
from groq import Groq
import json
import os
from io import BytesIO
from datetime import datetime
from functools import lru_cache
import pandas as pd
import random
import random
from pbi_questions import PBI_PRACTICAL_QUESTIONS, PBI_CONCEPT_QUESTIONS

# --- 1. CONFIG MUST BE FIRST ---
st.set_page_config(
    page_title="NexaCoach | AI-Powered Excellence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. PROFESSIONAL LIGHT THEME CSS (LeetCode/HackerRank Inspired) ---
st.markdown("""
<style>
/* System fonts first for instant render, Google Fonts load async */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
    /* === PROFESSIONAL LIGHT THEME === */
    --bg-primary: #ffffff;
    --bg-secondary: #f7f8fa;
    --bg-card: #ffffff;
    --border-color: #e2e8f0;
    --border-hover: #cbd5e1;
    
    /* Accent Colors (LeetCode Orange + HackerRank Green) */
    --accent-green: #2cbb5d;
    --accent-orange: #ffa116;
    --accent-blue: #0073e6;
    --accent-purple: #8b5cf6;
    --accent-cyan: #22d3ee;
    
    /* Difficulty Colors */
    --easy-green: #00b8a3;
    --medium-orange: #ffc01e;
    --hard-red: #ff375f;
    
    /* Text Colors */
    --text-primary: #1a1a1a;
    --text-secondary: #5c6370;
    --text-muted: #8b949e;
    
    /* Shadows & Effects */
    --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
    --shadow-md: 0 4px 12px rgba(0,0,0,0.08);
    --shadow-lg: 0 8px 24px rgba(0,0,0,0.12);
    --shadow-hover: 0 8px 30px rgba(44,187,93,0.15);
    
    /* Gradients */
    --gradient-primary: linear-gradient(135deg, #2cbb5d, #00b8a3);
    --gradient-accent: linear-gradient(135deg, #ffa116, #ff6b35);
}

.stApp {
    background: var(--bg-secondary) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: var(--text-primary);
}

#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ===== HERO SECTION ===== */
.hero-container {
    text-align: center;
    padding: 2rem 0 2.5rem 0;
    background: var(--bg-primary);
    border-bottom: 1px solid var(--border-color);
    margin-bottom: 1.5rem;
}

.hero-logo {
    font-size: 2.8rem;
    font-weight: 700;
    background: var(--gradient-primary);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.25rem;
}

.hero-tagline {
    font-size: 1rem;
    color: var(--text-secondary);
    font-weight: 400;
}

/* ===== MODE CARDS (Tab-like Navigation) ===== */
.stButton > button {
    background: var(--bg-card) !important;
    color: var(--text-secondary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 10px !important;
    padding: 0.75rem 1rem !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
    transition: all 0.2s ease !important;
    box-shadow: var(--shadow-sm) !important;
}

.stButton > button:hover {
    background: var(--bg-primary) !important;
    border-color: var(--accent-green) !important;
    color: var(--accent-green) !important;
    box-shadow: var(--shadow-md) !important;
    transform: translateY(-2px) !important;
}

.stButton > button:active, .stButton > button:focus {
    background: linear-gradient(135deg, #2cbb5d, #00b8a3) !important;
    color: white !important;
    border-color: var(--accent-green) !important;
}

/* ===== CHAT INTERFACE ===== */
.chat-container {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1.25rem;
    box-shadow: var(--shadow-sm);
}

.chat-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    background: var(--bg-secondary);
    border-radius: 10px;
    margin-bottom: 1rem;
}

.chat-avatar {
    width: 44px;
    height: 44px;
    border-radius: 10px;
    background: var(--gradient-primary);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.4rem;
    box-shadow: var(--shadow-sm);
}

.chat-title {
    color: var(--text-primary);
    font-weight: 600;
    font-size: 1.05rem;
}

.chat-subtitle {
    color: var(--text-secondary);
    font-size: 0.8rem;
    font-weight: 400;
}

/* Message Bubbles */
.message-ai {
    background: linear-gradient(135deg, rgba(44,187,93,0.08), rgba(0,184,163,0.08));
    border-left: 3px solid var(--accent-green);
    border-radius: 0 10px 10px 0;
    padding: 1rem 1.25rem;
    margin: 0.75rem 0;
    color: var(--text-primary);
    line-height: 1.6;
}

.message-user {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 10px;
    padding: 1rem 1.25rem;
    margin: 0.75rem 0;
    color: var(--text-primary);
    line-height: 1.6;
}

/* ===== SIDEBAR PANEL ===== */
.panel-container {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1.25rem;
    box-shadow: var(--shadow-sm);
}

.panel-title {
    color: var(--text-primary);
    font-weight: 600;
    font-size: 1rem;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid var(--border-color);
}

.discussion-point {
    background: rgba(44, 187, 93, 0.06);
    border-left: 3px solid var(--accent-green);
    padding: 0.75rem 1rem;
    margin: 0.5rem 0;
    border-radius: 0 8px 8px 0;
    color: var(--text-secondary);
    font-size: 0.9rem;
    transition: all 0.2s ease;
}

.discussion-point:hover {
    background: rgba(44, 187, 93, 0.12);
    color: var(--text-primary);
}

.tip-box {
    background: linear-gradient(135deg, rgba(255,161,22,0.08), rgba(255,107,53,0.08));
    border: 1px solid rgba(255,161,22,0.2);
    border-radius: 10px;
    padding: 1rem;
    margin-top: 1rem;
}

.tip-title {
    color: var(--accent-orange);
    font-weight: 600;
    font-size: 0.85rem;
    margin-bottom: 0.5rem;
}

.tip-text {
    color: var(--text-secondary);
    font-size: 0.85rem;
    line-height: 1.5;
}

/* ===== SESSION STATS ===== */
.stats-container {
    display: flex;
    justify-content: space-around;
    margin-top: 1.5rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border-color);
}

.stat-item {
    text-align: center;
}

.stat-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--accent-green);
}

.stat-label {
    font-size: 0.7rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-top: 0.25rem;
}

/* ===== GOLDEN VERSION / SOLUTION BOX ===== */
.golden-box {
    background: linear-gradient(135deg, rgba(255,161,22,0.08), rgba(255,193,30,0.08));
    border: 1px solid rgba(255,161,22,0.25);
    border-radius: 10px;
    padding: 1.25rem;
    margin-top: 0.5rem;
    color: var(--text-primary);
    line-height: 1.6;
}

.solution-box {
    background: linear-gradient(135deg, rgba(44,187,93,0.06), rgba(0,184,163,0.06));
    border: 1px solid rgba(44,187,93,0.2);
    border-radius: 10px;
    padding: 1.25rem;
    margin-top: 0.5rem;
}

/* ===== TEXT INPUTS ===== */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
    padding: 0.75rem 1rem !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--accent-green) !important;
    box-shadow: 0 0 0 3px rgba(44,187,93,0.15) !important;
}

/* ===== CODE BLOCKS (LeetCode-style) ===== */
.stCodeBlock, code, pre {
    font-family: 'JetBrains Mono', 'Fira Code', monospace !important;
    background: #1e1e1e !important;
    border-radius: 8px !important;
    border: 1px solid #333 !important;
}

/* ===== EXPANDER ===== */
.streamlit-expanderHeader {
    background: var(--bg-secondary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    font-weight: 500 !important;
}

.streamlit-expanderHeader:hover {
    background: var(--bg-card) !important;
    border-color: var(--accent-green) !important;
}

/* ===== DIFFICULTY BADGES ===== */
.difficulty-easy {
    background: rgba(0,184,163,0.12);
    color: var(--easy-green);
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
}

.difficulty-medium {
    background: rgba(255,192,30,0.15);
    color: #b89500;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
}

.difficulty-hard {
    background: rgba(255,55,95,0.12);
    color: var(--hard-red);
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
}

/* ===== VOICE TOGGLE ===== */
.voice-indicator {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(44,187,93,0.1);
    border: 1px solid rgba(44,187,93,0.25);
    border-radius: 20px;
    padding: 0.5rem 1rem;
    color: var(--accent-green);
    font-size: 0.85rem;
    font-weight: 500;
}

.voice-indicator.active {
    background: rgba(44,187,93,0.15);
    animation: voice-pulse 1.5s ease-in-out infinite;
}

@keyframes voice-pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(44,187,93,0.4); }
    50% { box-shadow: 0 0 0 8px rgba(44,187,93,0); }
}

/* ===== CHAT MESSAGE STYLING ===== */
[data-testid="stChatMessage"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
    padding: 1rem !important;
    margin: 0.5rem 0 !important;
}

/* ===== SIDEBAR TOGGLE ===== */
.stToggle label span {
    color: var(--text-primary) !important;
}

/* ===== RESPONSIVE ===== */
@media (max-width: 768px) {
    .hero-logo { font-size: 2.2rem; }
    .hero-tagline { font-size: 0.9rem; }
    .chat-header { padding: 0.5rem 0.75rem; }
    .panel-container { padding: 1rem; }
}

/* ===== SCROLLBAR (Subtle) ===== */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}

::-webkit-scrollbar-track {
    background: var(--bg-secondary);
}

::-webkit-scrollbar-thumb {
    background: var(--border-color);
    border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--text-muted);
}
</style>
""", unsafe_allow_html=True)


# --- 3. IMPORTS FOR VOICE ---
from streamlit_mic_recorder import speech_to_text
from gtts import gTTS

# --- 4. AUTHENTICATION ---
api_key = os.environ.get("GROQ_API_KEY") or os.environ.get("GOOGLE_API_KEY")

if not api_key:
    try:
        api_key = st.secrets.get("GROQ_API_KEY") or st.secrets.get("GOOGLE_API_KEY")
    except:
        pass

if not api_key:
    st.error("🔑 API Key missing. Please set GROQ_API_KEY in environment or .streamlit/secrets.toml")
    st.stop()

# --- 5. GROQ CLIENT SETUP (No cache to avoid stale keys) ---
client = Groq(api_key=api_key)

# --- 6. MODES CONFIGURATION ---
MODES = {
    "Business": {
        "icon": "💼",
        "role": "The Consultant",
        "color": "#8b5cf6",
        "system_instruction": """
ROLE: You are 'The Consultant', a Partner at McKinsey, BCG, or Bain with 15+ years of experience.
TASK: Conduct rigorous business case interviews covering:
- Market Sizing (TAM/SAM/SOM, top-down, bottom-up)
- Profitability Analysis (revenue vs cost breakdown)
- Market Entry Strategy (barriers, competition, positioning)
- M&A Evaluation (synergies, valuation, integration)
- Growth Strategy (organic vs inorganic, expansion)

STYLE: Be structured, push for MECE frameworks, challenge fuzzy logic.

OUTPUT FORMAT (JSON ONLY):
{
    "critique": "Sharp feedback on their framework and business acumen (2-3 sentences).",
    "discussion_points": ["Framework gap", "Quantitative angle", "Stakeholder consideration"],
    "golden_rewrite": "A structured, MECE response demonstrating consulting-grade thinking.",
    "next_question": "Next case question or deep-dive."
}
""",
        "initial_msg": "Your client is a mid-sized retail bank in Southeast Asia. Digital-only banks are capturing 20% of new customers annually. Should we launch our own digital bank, or improve our existing mobile app? Walk me through your approach.",
        "initial_points": ["Market analysis", "Competitive positioning", "Build vs Buy decision"],
    },
    "Soft Skills": {
        "icon": "🎯",
        "role": "The Mentor",
        "color": "#22d3ee",
        "system_instruction": """
ROLE: You are 'The Mentor', an executive coach who has advised Fortune 500 leaders.
TASK: Evaluate behavioral and soft skills:
- Leadership & Influence
- Communication & Executive Presence
- Conflict Resolution
- Emotional Intelligence
- Teamwork & Collaboration

STYLE: Use STAR method. Push for specific examples with measurable outcomes.

OUTPUT FORMAT (JSON ONLY):
{
    "critique": "Feedback on storytelling, impact, and leadership presence (2-3 sentences).",
    "discussion_points": ["Leadership dimension", "Communication skill", "Self-awareness opportunity"],
    "golden_rewrite": "An exemplary STAR response with specific metrics.",
    "next_question": "Next behavioral question."
}
""",
        "initial_msg": "Tell me about a time when you had to influence a decision without having formal authority. What was the situation, and what made your approach effective?",
        "initial_points": ["Influence without authority", "Stakeholder management", "Communication strategy"],
    },
    "SQL": {
        "icon": "🗄️",
        "role": "The Architect",
        "color": "#10b981",
        "system_instruction": """
ROLE: You are 'The Architect', a Principal Data Engineer at a FAANG company.
TASK: Test SQL skills with MEDIUM and HARD problems:
- Window Functions (RANK, ROW_NUMBER, LAG, LEAD)
- Complex JOINs and CTEs
- Aggregations and CASE statements
- Subqueries and query optimization

DIFFICULTY: Only MEDIUM or HARD. NO easy problems.

OUTPUT FORMAT (JSON ONLY):
{
    "critique": "Evaluate correctness, efficiency, style (2-3 sentences).",
    "discussion_points": ["Optimization opportunity", "Edge case", "Alternative approach"],
    "golden_rewrite": "Optimized SQL with comments.",
    "next_question": "Next challenge intro.",
    "problem_context": {
        "title": "Problem Title",
        "difficulty": "MEDIUM or HARD",
        "description": "Problem statement.",
        "schema": "CREATE TABLE statements.",
        "table_refs": "Markdown table showing 3-5 rows of sample data for each table.",
        "expected_output": "Sample expected output table.",
        "solution": "The complete SQL solution query with explanation.",
        "hints": "1-2 hints."
    }
}
""",
        "initial_msg": "Welcome to SQL Challenge. We focus on MEDIUM and HARD problems. Let's start.",
        "initial_context": {
            "title": "Consecutive Login Streak",
            "difficulty": "HARD",
            "description": "Find users with at least 3 consecutive login days. Return user_id and longest streak start date.",
            "schema": "Table: logins (user_id INT, login_date DATE)\nSample: (1,'2024-01-01'),(1,'2024-01-02'),(1,'2024-01-03'),(2,'2024-01-01'),(2,'2024-01-03')",
            "table_refs": "| user_id | login_date |\n|---|---|\n| 1 | 2024-01-01 |\n| 1 | 2024-01-02 |\n| 1 | 2024-01-03 |\n| 2 | 2024-01-01 |\n| 2 | 2024-01-03 |",
            "expected_output": "| user_id | streak_start | streak_length |\n|---------|--------------|---------------|\n| 1       | 2024-01-01   | 3             |",
            "solution": "WITH ranked AS (\n  SELECT user_id, login_date,\n    login_date - INTERVAL ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date) DAY AS grp\n  FROM logins\n),\nstreaks AS (\n  SELECT user_id, MIN(login_date) AS streak_start, COUNT(*) AS streak_length\n  FROM ranked\n  GROUP BY user_id, grp\n  HAVING COUNT(*) >= 3\n)\nSELECT * FROM streaks ORDER BY streak_length DESC;",
            "hints": "Use ROW_NUMBER with date arithmetic (Islands & Gaps pattern)"
        },
        "initial_points": ["Window functions", "Islands & Gaps pattern", "Date arithmetic"],
    },
    "Power BI": {
        "icon": "📊",
        "role": "The Analyst",
        "color": "#f59e0b",
        "system_instruction": """
ROLE: You are 'The Analyst', a Senior BI Developer and Power BI expert.
TASK: Test Power BI skills:
- Data Modeling (Star schema, relationships)
- DAX Functions (CALCULATE, FILTER, time intelligence)
- Visualization Best Practices
- Performance Optimization
- Row-Level Security

OUTPUT FORMAT (JSON ONLY):
{
    "critique": "Feedback on DAX, modeling, or visualization (2-3 sentences).",
    "discussion_points": ["DAX concept", "Model design", "Performance tip"],
    "golden_rewrite": "Correct DAX formula or approach with explanation.",
    "next_question": "Next Power BI scenario."
}
""",
        "initial_msg": "You're building a sales dashboard. The business wants 'Sales YTD' that resets each fiscal year (starting April 1). Current date context should apply. Write the DAX measure.",
        "initial_points": ["Time Intelligence DAX", "Fiscal year handling", "Context awareness"],
    },
    "Product Analysis": {
        "icon": "🚀",
        "role": "The PM Lead",
        "color": "#ec4899",
        "system_instruction": """
ROLE: You are 'The PM Lead', a Group Product Manager at Google/Meta/Amazon level.
TASK: Evaluate Product Analysis skills:
- Product Metrics (KPIs, north star)
- User Research (personas, journey mapping)
- Prioritization (RICE, ICE)
- A/B Testing (hypothesis, interpretation)
- Roadmap Planning
- Market Analysis

OUTPUT FORMAT (JSON ONLY):
{
    "critique": "Feedback on product thinking, metrics, prioritization (2-3 sentences).",
    "discussion_points": ["Metric to consider", "User segment to analyze", "Trade-off to evaluate"],
    "golden_rewrite": "Structured product analysis demonstrating PM-level thinking.",
    "next_question": "Next product scenario."
}
""",
        "initial_msg": "You're the PM for Instagram Stories. Engagement is flat YoY while TikTok grows 30%. The CEO asks: 'What's wrong and what should we do?' Walk me through how you'd diagnose this and propose solutions.",
        "initial_points": ["Metric deep-dive", "Competitive analysis", "Prioritization framework"],
    },
}
# --- 7. SESSION STATE ---
if "voice_mode" not in st.session_state:
    st.session_state.voice_mode = False

if "last_audio" not in st.session_state:
    st.session_state.last_audio = None

if "current_mode" not in st.session_state:
    st.session_state.current_mode = "Business"
    
@st.cache_data
def generate_sample_data():
    regions = ['North', 'South', 'East', 'West']
    products = ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Headset']
    segments = ['Consumer', 'Corporate', 'Home Office']
    
    data = []
    for _ in range(200):
        data.append({
            'Date': pd.Timestamp('2024-01-01') + pd.Timedelta(days=random.randint(0, 365)),
            'Region': random.choice(regions),
            'Product': random.choice(products),
            'Segment': random.choice(segments),
            'Sales': random.randint(100, 5000),
            'Profit': random.randint(10, 1000),
            'Discount': round(random.uniform(0, 0.3), 2)
        })
    return pd.DataFrame(data)

def render_visual(state, df):
    # Dynamic Aggregation
    if state["type"] == "KPI Card":
        if state['agg'] == "Sum":
            val = df[state['y']].sum()
        elif state['agg'] == "Avg":
            val = df[state['y']].mean()
        else:
            val = df[state['y']].count()
            
        prefix = "$" if state['y'] in ["Sales", "Profit", "Discount"] else ""
        st.markdown(f"""
        <div style="background: white; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <div style="color: #64748b; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.5px;">{state['agg']} of {state['y']}</div>
            <div style="color: #2cbb5d; font-size: 1.8rem; font-weight: 700;">{prefix}{val:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Grouping
        if state["agg"] == "Sum":
            chart_data = df.groupby(state['x'])[state['y']].sum().reset_index()
        elif state["agg"] == "Avg":
            chart_data = df.groupby(state['x'])[state['y']].mean().reset_index()
        else: # Count
            chart_data = df.groupby(state['x'])[state['y']].count().reset_index()
        
        # Rendering
        if state["type"] == "Bar Chart":
            st.bar_chart(chart_data, x=state['x'], y=state['y'], color="#2cbb5d")
        elif state["type"] == "Line Chart":
            st.line_chart(chart_data, x=state['x'], y=state['y'], color="#2cbb5d")
        elif state["type"] == "Donut Chart":
             # Fallback to bar chart as simple donut isn't native without extra libs
             st.bar_chart(chart_data, x=state['x'], y=state['y'], color="#ffa116")

if "session_start" not in st.session_state:
    st.session_state.session_start = datetime.now()

if "questions_answered" not in st.session_state:
    st.session_state.questions_answered = 0

if "sql_context" not in st.session_state:
    st.session_state.sql_context = MODES["SQL"]["initial_context"]

if "sql_context" not in st.session_state:
    st.session_state.sql_context = MODES["SQL"]["initial_context"]

if "pbi_data" not in st.session_state:
    st.session_state.pbi_data = generate_sample_data()

def init_mode_state(mode_name):
    hist_key = f"history_{mode_name}"
    points_key = f"points_{mode_name}"
    config = MODES[mode_name]

    if hist_key not in st.session_state:
        st.session_state[hist_key] = []
        initial_payload = {
            "critique": "Session starting. Let's see what you've got.",
            "discussion_points": config["initial_points"],
            "golden_rewrite": "",
            "next_question": config["initial_msg"]
        }
        if mode_name == "SQL":
            initial_payload["problem_context"] = config["initial_context"]
        elif mode_name == "SQL":
            initial_payload["case_context"] = config["initial_context"]
            
        st.session_state[hist_key].append({
            "role": "model", 
            "content": json.dumps(initial_payload)
        })
    
    if points_key not in st.session_state:
        st.session_state[points_key] = config["initial_points"].copy()
    
    return hist_key, points_key, config

# --- 8. HELPER FUNCTIONS ---
def text_to_speech(text):
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        audio_bytes = BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        return audio_bytes
    except Exception as e:
        return None

def get_session_duration():
    delta = datetime.now() - st.session_state.session_start
    minutes = int(delta.total_seconds() // 60)
    return f"{minutes}m"



# --- 9. HERO SECTION ---
st.markdown("""
<div class="hero-container">
    <div class="hero-logo">🧠 NexaCoach</div>
    <div class="hero-tagline">Your AI-Powered Path to Excellence</div>
</div>
""", unsafe_allow_html=True)

# --- 10. MODE SELECTION ---
cols = st.columns(len(MODES))
for i, (mode_name, mode_config) in enumerate(MODES.items()):
    with cols[i]:
        is_active = st.session_state.current_mode == mode_name
        active_class = "active" if is_active else ""
        
        if st.button(
            f"{mode_config['icon']}\n{mode_name.split()[0]}", 
            key=f"mode_{mode_name}",
            use_container_width=True
        ):
            if st.session_state.current_mode != mode_name:
                st.session_state.current_mode = mode_name
                st.rerun()

# Current mode
current_mode = st.session_state.current_mode
history_key, points_key, current_config = init_mode_state(current_mode)

# --- 11. MAIN LAYOUT ---
col1, col2 = st.columns([2, 1])

# --- RIGHT COLUMN: PANEL ---
with col2:
    if current_mode == "SQL":
        # SQL Coding Problem Panel
        st.markdown("""<div class="panel-container">
            <div class="panel-title">💻 SQL Challenge</div>
        </div>""", unsafe_allow_html=True)
        
        ctx = st.session_state.sql_context
        difficulty = ctx.get("difficulty", "MEDIUM")
        
        # Difficulty badge with proper styling
        if difficulty == "HARD":
            diff_badge = '<span class="difficulty-hard">🔴 HARD</span>'
        elif difficulty == "MEDIUM":
            diff_badge = '<span class="difficulty-medium">🟡 MEDIUM</span>'
        else:
            diff_badge = '<span class="difficulty-easy">🟢 EASY</span>'
        
        st.markdown(f"### {ctx.get('title', 'Problem')} {diff_badge}", unsafe_allow_html=True)
        st.markdown(ctx.get("description", ""))
        
        st.markdown("**📋 Schema:**")
        st.code(ctx.get("schema", ""), language="sql")
        
        if ctx.get("table_refs"):
             with st.expander("💾 Table Data Preview", expanded=False):
                 st.markdown(ctx.get("table_refs", ""))
        
        if ctx.get("expected_output"):
            with st.expander("📊 Expected Output", expanded=False):
                st.markdown(f"```\n{ctx.get('expected_output', '')}\n```")
        
        with st.expander("💡 Hints", expanded=False):
            st.info(ctx.get("hints", ""))
        
        # Show Solution - properly display SQL code
        solution = ctx.get("solution", "")
        if solution:
            with st.expander("✅ Solution", expanded=False):
                st.code(solution, language="sql")
    
    elif current_mode == "SQL":
        # SQL Case Study Panel
        st.markdown("""<div class="panel-container">
            <div class="panel-title">📈 Business Case</div>
        </div>""", unsafe_allow_html=True)
        
        ctx = st.session_state.sql_context
        st.markdown(ctx.get("scenario", ""))
        st.markdown("**Available Tables:**")
        st.code(ctx.get("schema", ""), language="sql")
        st.markdown(f"**Current Step:** {ctx.get('current_step', '1')}")
        if ctx.get("key_insight"):
            st.info(f"💡 **Key Insight:** {ctx.get('key_insight', '')}")
            
    elif current_mode == "Power BI":
        # Power BI Interview Panel
        st.markdown("""<div class="panel-container">
            <div class="panel-title">🎤 Interview Prep</div>
        </div>""", unsafe_allow_html=True)
        
        # --- SECTION 1: PRACTICAL CHALLENGE ---
        st.markdown("### 📊 Practical Challenge (Dataset)")
        st.info("Use the Visual Builder or DAX Studio to solve this using the loaded dataset.")
        
        p_q = PBI_PRACTICAL_QUESTIONS[st.session_state.pbi_prac_index]
        st.markdown(f"**Q: {p_q['question']}**")
        
        # Hint/Solution for Practical
        with st.expander("💡 Hint"):
            st.warning(p_q["hint"])
        with st.expander("✅ Solution Steps"):
            st.markdown(p_q["solution"])
            
        if st.button("Next Challenge ➡️", key="btn_prac_next", use_container_width=True):
             st.session_state.pbi_prac_index = (st.session_state.pbi_prac_index + 1) % len(PBI_PRACTICAL_QUESTIONS)
             # Sync Concept question with Practical question change
             st.session_state.pbi_concept_index = (st.session_state.pbi_concept_index + 1) % len(PBI_CONCEPT_QUESTIONS)
             st.rerun()

        st.markdown("---")
        
        # Dataset Context (Mini)
        with st.expander("💾 Dataset Preview", expanded=False):
            st.dataframe(st.session_state.pbi_data.head(5), hide_index=True)
            
        st.markdown("---")

        # --- SECTION 2: BONUS CONCEPT QUESTIONS ---
        st.markdown("### ⚡ Bonus: Rapid Fire")
        
        c_q = PBI_CONCEPT_QUESTIONS[st.session_state.pbi_concept_index]
        
        # Category Badge
        cat = c_q["category"]
        st.markdown(f"**Category:** `{cat}`")
        st.markdown(f"**Q: {c_q['question']}**")
        
        with st.expander("reveal answer"):
             st.markdown(c_q["solution"])
    else:
        # Discussion Focus Panel
        st.markdown(f"""
        <div class="panel-container">
            <div class="panel-title">🎯 Discussion Focus</div>
        </div>
        """, unsafe_allow_html=True)
        
        for point in st.session_state[points_key]:
            st.markdown(f"""<div class="discussion-point">{point}</div>""", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="tip-box">
            <div class="tip-title">💡 Pro Tip</div>
            <div class="tip-text">Focus on these areas in your response. The AI coach will provide specific feedback based on your answers.</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Session Stats
    st.markdown(f"""
    <div class="stats-container">
        <div class="stat-item">
            <div class="stat-value">{st.session_state.questions_answered}</div>
            <div class="stat-label">Questions</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">{get_session_duration()}</div>
            <div class="stat-label">Duration</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Voice Mode Toggle
    st.markdown("---")
    st.session_state.voice_mode = st.toggle("🎤 Voice Mode", value=st.session_state.voice_mode)
    
    if st.session_state.voice_mode:
        st.markdown("""<div class="voice-indicator active">🔊 Voice Active</div>""", unsafe_allow_html=True)
        if st.session_state.last_audio:
            st.audio(st.session_state.last_audio, format="audio/mp3", autoplay=True)
    
    # Reset Button
    st.markdown("")
    if st.button("🔄 Reset Session", use_container_width=True):
        if history_key in st.session_state: 
            del st.session_state[history_key]
        if points_key in st.session_state: 
            del st.session_state[points_key]
        st.session_state.questions_answered = 0
        st.session_state.session_start = datetime.now()
        if current_mode == "SQL":
            st.session_state.sql_context = MODES["SQL"]["initial_context"]
        elif current_mode == "SQL":
            st.session_state.sql_context = MODES["SQL"]["initial_context"]
        st.rerun()

# --- LEFT COLUMN: CHAT ---
with col1:
    # Chat Header
    st.markdown(f"""
    <div class="chat-header" style="background: rgba(255,255,255,0.05); border-radius: 12px; padding: 1rem; margin-bottom: 1rem;">
        <div class="chat-avatar">{current_config['icon']}</div>
        <div>
            <div class="chat-title">{current_config['role']}</div>
            <div class="chat-subtitle">{current_mode}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # POWER BI VISUAL BUILDER
    if "pbi_viz_state" not in st.session_state:
        st.session_state.pbi_viz_state = None
    
    if "pbi_dashboard" not in st.session_state:
        st.session_state.pbi_dashboard = []
        
    if "pbi_measures" not in st.session_state:
        st.session_state.pbi_measures = {}

    if "pbi_prac_index" not in st.session_state:
        st.session_state.pbi_prac_index = 0
        
    if "pbi_concept_index" not in st.session_state:
        st.session_state.pbi_concept_index = 0
        
    if current_mode == "Power BI":
        # --- 1. GLOBAL SLICERS ---
        st.markdown("### 🔍 Global Filters")
        f1, f2 = st.columns(2)
        with f1: 
            filter_region = st.multiselect("Region", ["North", "South", "East", "West"], default=["North", "South", "East", "West"])
        with f2:
            filter_segment = st.multiselect("Segment", ["Consumer", "Corporate", "Home Office"], default=["Consumer", "Corporate", "Home Office"])
        
        # Apply Filters
        filtered_df = st.session_state.pbi_data[
            (st.session_state.pbi_data["Region"].isin(filter_region)) & 
            (st.session_state.pbi_data["Segment"].isin(filter_segment))
        ].copy()
        
        # Calculate dynamic measures
        for m_name, m_func in st.session_state.pbi_measures.items():
            if m_func == "SUM": filtered_df[m_name] = filtered_df["Sales"] # Placeholder logic
            # In a real app we'd evaluate DAX here. For simulator we just add cols.
        
        st.markdown("---")

        # --- 2. DAX STUDIO ---
        with st.expander("𝑓𝑥 DAX Studio (Quick Measures)", expanded=False):
            d1, d2 = st.columns([2, 1])
            with d1: 
                measure_name = st.text_input("Measure Name", placeholder="e.g., Total Sales YTD")
                measure_formula = st.selectbox("Quick Measure Pattern", ["SUM", "AVERAGE", "YTD", "YoY %", "% of Total"])
                measure_col = st.selectbox("Base Column", ["Sales", "Profit", "Discount"])
            with d2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("➕ Create Measure", use_container_width=True):
                    if measure_name:
                        st.session_state.pbi_measures[measure_name] = {"formula": measure_formula, "col": measure_col}
                        st.success(f"Created measure: {measure_name}")
                        st.rerun()

        # --- 3. REPORT CANVAS (Visual Builder) ---
        with st.expander("🎨 Report Canvas", expanded=True):
            # Visual Builder Controls
            c1, c2, c3, c4 = st.columns(4)
            with c1: v_type = st.selectbox("Visual Type", ["Bar Chart", "Line Chart", "KPI Card", "Donut Chart"], key="v_type")
            
            # Dynamic Axis/Values based on Type
            axis_opts = ["Region", "Product", "Segment", "Date"]
            val_opts = ["Sales", "Profit", "Discount"] + list(st.session_state.pbi_measures.keys())
            
            with c2: x_val = st.selectbox("Axis / Category", axis_opts, key="v_x")
            with c3: y_val = st.selectbox("Values", val_opts, key="v_y")
            with c4: agg = st.selectbox("Aggregation", ["Sum", "Avg", "Count"], key="v_agg")
            
            b1, b2 = st.columns(2)
            with b1:
                if st.button("📊 Preview Visual", use_container_width=True):
                    st.session_state.pbi_viz_state = {"type": v_type, "x": x_val, "y": y_val, "agg": agg}
            with b2:
                if st.button("📌 Pin to Dashboard", use_container_width=True):
                    st.session_state.pbi_dashboard.append({"type": v_type, "x": x_val, "y": y_val, "agg": agg})
                    st.success("Pinned to Dashboard Grid!")
        
        # --- 4. DASHBOARD GRID LAYOUT ---
        st.markdown("### 🖥️ Dashboard Layout")
        
        # Preview Area
        if st.session_state.pbi_viz_state:
            st.info("Preview Mode (Pin to add to grid)")
            visual = st.session_state.pbi_viz_state
            render_visual(visual, filtered_df)
            st.markdown("---")
        
        # Pinned Visuals Grid
        if st.session_state.pbi_dashboard:
            grid_cols = st.columns(2)
            for i, visual in enumerate(st.session_state.pbi_dashboard):
                with grid_cols[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"**{visual['y']} by {visual['x']}**")
                        render_visual(visual, filtered_df)
                        if st.button("🗑️", key=f"del_{i}"):
                            st.session_state.pbi_dashboard.pop(i)
                            st.rerun()
                            
        st.markdown("---")
    
    # Chat Messages Container
    # Chat Messages
    history = st.session_state[history_key]
    for msg in history:
        if msg["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                if msg.get("type") == "code":
                    st.code(msg["content"], language="sql")
                else:
                    st.markdown(f'<div class="message-user">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            with st.chat_message("assistant", avatar=current_config['icon']):
                try:
                    data = json.loads(msg["content"])
                    
                    # Show the main question/scenario prominently
                    if data.get("next_question"):
                        st.markdown(f'### 💬 {current_config["role"]}')
                        st.markdown(data.get("next_question", ""))
                    
                    # Show case context for SQL Case Study
                    if current_mode == "SQL" and data.get("case_context"):
                        ctx = data["case_context"]
                        if ctx.get("scenario"):
                            st.info(ctx.get("scenario", ""))
                    
                    # Show problem context for SQL Coding
                    if current_mode == "SQL" and data.get("problem_context"):
                        ctx = data["problem_context"]
                        st.markdown(f"**Problem:** {ctx.get('title', '')}")
                        st.markdown(ctx.get('description', ''))
                    
                    # Show critique/feedback if not initial message
                    if data.get("critique") and "Session starting" not in data.get("critique", ""):
                        st.markdown(f'<div class="message-ai"><strong>Feedback:</strong> {data.get("critique", "")}</div>', unsafe_allow_html=True)
                    
                    # Show golden rewrite
                    if data.get("golden_rewrite"):
                        with st.expander("✨ The Golden Version"):
                            if current_mode == "SQL":
                                st.code(data.get("golden_rewrite"), language="sql")
                            else:
                                st.markdown(f'<div class="golden-box">{data.get("golden_rewrite")}</div>', unsafe_allow_html=True)
                    
                except:
                    st.write(msg["content"])
    
    # Voice Input
    if st.session_state.voice_mode:
        st.markdown("---")
        voice_text = speech_to_text(
            language='en',
            start_prompt="🎤 Click to speak",
            stop_prompt="⏹️ Stop",
            just_once=True,
            key=f'voice_{current_mode}'
        )
        if voice_text:
            user_input = voice_text
            st.success(f"📝 Captured: {user_input}")
        else:
            user_input = None
    else:
        voice_text = None
        user_input = None
    
    # Text/Code Input
    if current_mode == "SQL":
        with st.form("sql_form", clear_on_submit=True):
            code_input = st.text_area("💻 SQL Workspace", height=150, placeholder="SELECT * FROM ...")
            submit = st.form_submit_button("Submit Solution", use_container_width=True)
            if submit and code_input:
                user_input = code_input
    elif current_mode == "SQL":
        text_input = st.chat_input("Describe your approach or write SQL...")
        if text_input:
            user_input = text_input
    else:
        text_input = st.chat_input("Type your answer...")
        if text_input:
            user_input = text_input
    
    # Override with voice if available
    if voice_text:
        user_input = voice_text
    
    # Process Input
    if user_input:
        is_code = (current_mode == "SQL" and not voice_text)
        msg_type = "code" if is_code else "text"
        
        st.session_state[history_key].append({"role": "user", "content": user_input, "type": msg_type})
        st.session_state.questions_answered += 1
        
        # Generate Response (Optimized for speed)
        # Only include last 2 exchanges for context to reduce token processing
        recent_context = history[-2:] if len(history) >= 2 else history
        prompt = f"""{current_config['system_instruction']}

Context: {str(recent_context)}

User: {user_input}
"""
        
        with st.spinner(f"⚡ Generating response..."):
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": current_config['system_instruction']},
                        {"role": "user", "content": f"Context: {str(recent_context)}\n\nUser: {user_input}"}
                    ],
                    temperature=0.7,
                    max_tokens=1024,
                    response_format={"type": "json_object"}
                )
                
                response_text = response.choices[0].message.content.strip()
                if response_text.startswith("```"):
                    lines = response_text.split("\n")
                    response_text = "\n".join(lines[1:-1])
                
                data = json.loads(response_text)
                
                # Update state
                if "discussion_points" in data:
                    st.session_state[points_key] = data["discussion_points"]
                
                if current_mode == "SQL" and "problem_context" in data:
                    st.session_state.sql_context = data["problem_context"]
                
                if current_mode == "SQL" and "case_context" in data:
                    st.session_state.sql_context = data["case_context"]
                
                st.session_state[history_key].append({"role": "model", "content": json.dumps(data)})
                
                # Voice response
                if st.session_state.voice_mode:
                    speech_text = f"{data.get('critique', '')} {data.get('next_question', '')}"
                    audio = text_to_speech(speech_text)
                    if audio:
                        st.session_state.last_audio = audio
                else:
                    st.session_state.last_audio = None
                
                st.rerun()
                
            except json.JSONDecodeError:
                st.error("⚠️ Response parsing error. Please try again.")
            except Exception as e:
                st.error(f"⚠️ Error: {e}")

# --- FOOTER ---
st.markdown("""
<div style="text-align: center; padding: 2rem 0; margin-top: 2rem; border-top: 1px solid #e2e8f0; color: #8b949e; font-size: 0.85rem;">
    <span style="font-weight: 600; color: #2cbb5d;">NexaCoach</span> • Powered by AI • Built for Excellence
</div>
""", unsafe_allow_html=True)
