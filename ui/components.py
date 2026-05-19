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

def insights_card(title, content):
    st.markdown(f"""
    <div style="
        background: rgba(17,24,39,0.88);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 18px;
        padding: 1.4rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.25);
    ">
        <h4 style="margin-bottom:0.5rem; color:#F9FAFB;">
            {title}
        </h4>
        <p style="color:#D1D5DB; line-height:1.6; margin:0;">
            {content}
        </p>
    </div>
    """, unsafe_allow_html=True)

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
    <div class="mini-card">

        <div class="mini-card-title">
            {title}
        </div>

        <div class="mini-card-value">
            {value}
        </div>

    </div>
    """, unsafe_allow_html=True)