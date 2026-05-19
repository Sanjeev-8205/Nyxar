import streamlit as st

def metric_card(title, value, delta=None):
    st.markdown(f"""
    <div class="metric-card">
                
        <p style="color:#9CA3AF;font-size:0.9rem;">
            {title}
        </p>

        <h2 style="margin:0;">
            {value}
        </h2>

        <p style="color:#10B981">
            {delta if delta else ""}
        </p>

    </div>
    """, unsafe_allow_html=True)

def status_card(title, status, color):

    st.markdown(f"""
    <div class="metric-card">

        <div style="
            display:flex;
            justify-content:space-between;
            align-items:center;
        ">

            <span>{title}</span>

            <span style="
                color:{color};
                font-weight:600;
            ">
                ● {status}
            </span>

        </div>

    </div>
    """, unsafe_allow_html=True)

def insights_card(title, content):

    st.markdown(f"""
    <div class="metric-card">

        <h4 style="margin-bottom:0.5rem;">
            {title}
        </h4>

        <p style="
            color:#D1D5DB;
            line-height:1.6;
        ">
            {content}
        </p>

    </div>
    """, unsafe_allow_html=True)

def hero_header(title):
    st.markdown(f"""
    <div class="section-header">
        {title}
    </div>
    """, unsafe_allow_html=True)

def hero_subtext(text):
    st.markdown(f"""
    <div class="section-subtext">
        {text}
    </div>
    """)

def subtitle(title):
    st.markdown(f"""
    <div class="section-subtitle">
        {title}
    </div>
    """, unsafe_allow_html=True)

def subtitle_subtext(text):
    st.markdown(f"""
        <div class="section-subtitle-subtext">
            {text}
        </div>
    """, unsafe_allow_html=True)

def chart_container(title, fig, subtitle=None):

    st.markdown(f"""
    <div class="metric-card">

        <div style="
            margin-bottom: 1rem;
        ">

            <div style="
                font-size: 1.1rem;
                font-weight: 700;
                color: white;
            ">
                {title}
            </div>

            <div style="
                color: #9CA3AF;
                font-size: 0.92rem;
                margin-top: 0.25rem;
            ">
                {subtitle if subtitle else ""}
            </div>

        </div>
    """, unsafe_allow_html=True)

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.markdown("</div>", unsafe_allow_html=True)