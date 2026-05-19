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
                
    /* Streamlit Containers */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(17,24,39,0.88) !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: 18px !important;
        padding: 1rem !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.25) !important;
        backdrop-filter: blur(12px) !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid rgba(255,255,255,0.06);
    }

    /* Metrics Card */
    div[data-testid="stMarkdownContainer"] .metric-card {
        background: rgba(17,24,39,0.88) !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: 18px !important;
        padding: 1.4rem !important;
        margin-bottom: 1rem !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.25) !important;
        backdrop-filter: blur(12px) !important;
        transition: 0.2s ease !important;
    }

    /* Metrics Card Hover */
    div[data-testid="stMarkdownContainer"] .metric-card:hover {
        border: 1px solid rgba(99,102,241,0.45) !important;
        transform: translateY(-2px) !important;
    }           
                
    /* Mini Card */
    .mini-card {
        background: rgba(17,24,39,0.65) !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
        border-radius: 14px !important;
        padding: 1rem !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }
                
    /* Mini Card Title */
    .mini-card-title {
        color: #9CA3AF !important;
        font-size: 0.9rem !important;
        margin-bottom: 0.35rem !important;
    }


    /* Mini Card Value */
    .mini-card-value {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: #F3F4F6 !important;
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