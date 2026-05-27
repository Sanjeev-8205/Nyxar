import streamlit as st

def metric_card(title, value, delta=None):
    delta_html = f'<p style="color:#10B981; margin:4px 0 0 0;">{delta}</p>' if delta else ""

    st.markdown(f"""
    <div style="
        background: rgba(17,24,39,0.88);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 18px;
        padding: 1.4rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.25);
        min-height: 120px;
        background: linear-gradient(180deg, rgba(17,24,39,1), rgba(8,12,24,1));
    ">
        <p style="color:#9CA3AF; font-size:0.9rem; margin:0 0 8px 0;">
            {title}
        </p>
        <h2 style="margin:0; color:#F9FAFB;">
            {value}
        </h2>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

def status_card(title, status, color):
    st.markdown(f"""
    <div style="
        background: rgba(17,24,39,0.88);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 18px;
        padding: 1.4rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.25);
    ">
        <div style="
            display:flex;
            justify-content:space-between;
            align-items:center;
        ">
            <span style="color:#F9FAFB;">{title}</span>
            <span style="color:{color}; font-weight:600;">
                ● {status}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

#'def insights_card(title, content): st.markdown(f""" <div style=" background: rgba(17,24,39,0.88); border: 1px solid rgba(255,255,255,0.06); border-radius: 18px; padding: 1.4rem; margin-bottom: 1rem; box-shadow: 0 4px 20px rgba(0,0,0,0.25); "> <h4 style="margin-bottom:0.5rem; color:#F9FAFB;"> {title} </h4> <p style="color:#D1D5DB; line-height:1.6; margin:0;"> {content} </p> </div> """, unsafe_allow_html=True)'

def insights_card(title, content, level="activity"):

    severity_styles = {
        "inference": "#3B82F6",   # blue
        "activity": "#6B7280",    # neutral
        "anomaly": "#F59E0B",     # amber
        "health": "#10B981",      # green
    }

    accent = severity_styles.get(level, "#6B7280")

    card_html = f"""<div style="background:rgba(17,24,39,0.88);border:1px solid rgba(255,255,255,0.06);border-left:3px solid {accent};border-radius:18px;padding:1.6rem 1.5rem;margin-bottom:1.2rem;box-shadow:0 4px 20px rgba(0,0,0,0.25);"><h4 style="margin:0 0 0.85rem 0;color:#F9FAFB;font-size:1.05rem;font-weight:700;">{title}</h4><p style="color:#D1D5DB;line-height:1.85;font-size:0.95rem;margin:0;">{content}</p></div>"""
    st.markdown(card_html, unsafe_allow_html=True)

def hero_header(title):
    st.markdown(f"""
    <div style="
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
        color: #F9FAFB;
    ">
        {title}
    </div>
    """, unsafe_allow_html=True)

def hero_subtext(text):
    st.markdown(f"""
    <div style="
        color: #9CA3AF;
        margin-bottom: 2rem;
        max-width: 950px;
    ">
        {text}
    </div>
    """, unsafe_allow_html=True)

def subtitle(title):
    st.markdown(f"""
    <div style="
        font-size: 1.15rem;
        font-weight: 600;
        color: #F3F4F6;
        margin-top: 1rem;
        margin-bottom: 1rem;
    ">
        {title}
    </div>
    """, unsafe_allow_html=True)

def subtitle_subtext(text):
    st.markdown(f"""
    <div style="
        color: #9CA3AF;
        font-size: 0.92rem;
        line-height: 1.5;
        margin-bottom: 1.2rem;
    ">
        {text}
    </div>
    """, unsafe_allow_html=True)

def chart_container(fig, title, subtitle=None):
    fig.update_layout(height=350)

    with st.container(border=True):

        st.markdown(f"""
        <div style="
            font-size:1.1rem;
            font-weight:700;
            margin-bottom:0.3rem;
        ">
            {title}
        </div>
        """, unsafe_allow_html=True)

        if subtitle:

            st.markdown(f"""
            <div style="
                color:#9CA3AF;
                font-size:0.92rem;
                margin-bottom:1rem;
            ">
                {subtitle}
            </div>
            """, unsafe_allow_html=True)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

def mini_card(title, value):
    st.markdown(f"""
    <div style="
        background: rgba(17,24,39,0.65);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 14px;
        padding: 1rem;
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
    ">
        <div style="
            color: #9CA3AF;
            font-size: 0.9rem;
            margin-bottom: 0.35rem;
        ">
            {title}
        </div>
        <div style="
            font-size: 1.2rem;
            font-weight: 600;
            color: #F3F4F6;
        ">
            {value}
        </div>
    </div>
    """, unsafe_allow_html=True)

def platform_status_card(status_data):
    card_html = f"""<div style="background:linear-gradient(135deg,rgba(17,24,39,0.96),rgba(10,15,30,0.96));border:1px solid rgba(255,255,255,0.06);border-left:4px solid {status_data['color']};border-radius:20px;padding:1.5rem;margin-top:1rem;box-shadow:0 8px 30px rgba(0,0,0,0.35);"><div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:1rem;"><div style="width:14px;height:14px;border-radius:50%;background:{status_data['color']};box-shadow:0 0 12px {status_data['color']};"></div><span style="color:#F9FAFB;font-size:1rem;font-weight:700;">{status_data['status']}</span></div><p style="color:#D1D5DB;line-height:1.7;font-size:0.93rem;margin:0;">{status_data['message']}</p></div>"""
    st.markdown(card_html, unsafe_allow_html=True)

def apply_button_style():
    st.markdown(f"""<style>div.stButton > button {{height: 4.1rem; margin-top: 1.75rem; border-radius: 14px; font-size: 1.2rem; font-weight: 600;}}</style>""", unsafe_allow_html=True)