import streamlit as st

def load_global_styles():
    st.markdown("""
    <style>

    /* App Background */
    .stApp {
        background-color: #0B1020;
        color: #F3F4F6;
    }

    /* Main Content Padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
        max-width: 1450px;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid rgba(255,255,255,0.06);
    }

    /* Metric Cards */
    .metric-card {
        background: rgba(17,24,39,0.88);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 18px;
        padding: 1.4rem;
        margin-bottom: 1rem;

        box-shadow:
            0 4px 20px rgba(0,0,0,0.25);

        backdrop-filter: blur(12px);

        transition: 0.2s ease;
    }

    /* Card Hover */
    .metric-card:hover {
        border: 1px solid rgba(99,102,241,0.45);
        transform: translateY(-2px);
    }

    /* Section Headers */
    .section-header {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }

    /* Section Description */
    .section-subtext {
        color: #9CA3AF;
        margin-bottom: 2rem;
    }

    /* Internal Section Titles */
    .section-subtitle {
        font-size: 1.15rem;
        font-weight: 600;
        color: #F3F4F6;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }

    /* Section Subtitle Description */
    .section-subtitle-subtext {
        color: #9CA3AF;
        font-size: 0.92rem;
        line-height: 1.5;
        margin-bottom: 1.2rem;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab"] {
        font-size: 1rem;
        font-weight: 600;
    }

    /* Buttons */
    .stButton button {
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.08);
        background-color: #1F2937;
        color: white;
        padding: 0.6rem 1rem;
    }

    /* Inputs */
    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox div {
        border-radius: 12px !important;
    }

    </style>
    """, unsafe_allow_html=True)