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
    st.markdown(f"""<style>div.stButton > button {{height: 2.2rem; margin-top: 1.75rem; border-radius: 14px; font-size: 1.2rem; font-weight: 600;}}</style>""", unsafe_allow_html=True)

def render_model_info(model_name, model_info):
    st.markdown(f"""<div style="display:inline-flex;align-items:center;gap:0.4rem;margin-top:0.2rem;margin-bottom:0.8rem;background:rgba(59,130,246,0.08);border:1px solid rgba(59,130,246,0.2);border-radius:8px;padding:0.35rem 0.75rem;color:#93C5FD;font-size:0.85rem;font-weight:500;">⚡ {model_info[model_name]}</div>""", unsafe_allow_html=True)

def inference_output_card(
    sentiment=None,
    confidence=None,
    severity=None,
    model=None,
    runtime=None,
    certainty=None
):

    if sentiment is None:

        with st.container(border=True):

            st.markdown("""<div style="font-size:1.1rem;font-weight:700;margin-bottom:0.3rem;">Inference Output</div>""", unsafe_allow_html=True)

            st.markdown("""<div style="color:#9CA3AF;font-size:0.92rem;margin-bottom:1rem;">Prediction intelligence unavailable</div>""", unsafe_allow_html=True)

            st.markdown("""<div style="min-height:320px;display:flex;flex-direction:column;justify-content:center;"><div style="color:#F3F4F6;font-size:2.2rem;font-weight:800;margin-bottom:1rem;">Awaiting Inference</div><div style="color:#9CA3AF;font-size:1rem;line-height:1.7;">Run inference to generate<br>prediction intelligence.</div></div>""", unsafe_allow_html=True)

    else:

        sentiment_color = {
            "POSITIVE": "#10B981",
            "NEGATIVE": "#EF4444",
            "NEUTRAL": "#F59E0B"
        }.get(sentiment.upper(), "#F3F4F6")

        certainty_bg = {
            "HIGH CERTAINTY": "rgba(16,185,129,0.15)",
            "MODERATE CERTAINTY": "rgba(245,158,11,0.15)",
            "LOW CONFIDENCE": "rgba(239,68,68,0.15)"
        }.get(certainty, "rgba(255,255,255,0.08)")

        certainty_color = {
            "HIGH CERTAINTY": "#10B981",
            "MODERATE CERTAINTY": "#F59E0B",
            "LOW CONFIDENCE": "#EF4444"
        }.get(certainty, "#E5E7EB")

        with st.container(border=True):

            st.markdown("""<div style="font-size:1.1rem;font-weight:700;margin-bottom:0.3rem;">Inference Output</div>""", unsafe_allow_html=True)

            st.markdown("""<div style="color:#9CA3AF;font-size:0.92rem;margin-bottom:1.5rem;">Live prediction intelligence</div>""", unsafe_allow_html=True)

            st.markdown(f"""<div style="color:{sentiment_color};font-size:3rem;font-weight:800;letter-spacing:0.03em;margin-bottom:1.5rem;">{sentiment.upper()}</div>""", unsafe_allow_html=True)

            st.markdown(f"""<div style="display:inline-block;background:{certainty_bg};color:{certainty_color};padding:0.45rem 0.9rem;border-radius:999px;font-size:0.8rem;font-weight:700;margin-bottom:2rem;">{certainty}</div>""", unsafe_allow_html=True)

            c1, c2 = st.columns(2)

            with c1:
                st.markdown(f"""<div style="border:1px solid rgba(255,255,255,0.08);border-radius:14px;padding:1rem;background-color:#081028;margin-bottom:1rem;"><div style="color:#9CA3AF;font-size:0.82rem;margin-bottom:0.35rem;">Confidence</div><div style="color:#F3F4F6;font-size:1.35rem;font-weight:700;">{confidence}</div></div>""", unsafe_allow_html=True)

            with c2:
                st.markdown(f"""<div style="border:1px solid rgba(255,255,255,0.08);border-radius:14px;padding:1rem;background-color:#081028;margin-bottom:1rem;"><div style="color:#9CA3AF;font-size:0.82rem;margin-bottom:0.35rem;">Runtime</div><div style="color:#F3F4F6;font-size:1.35rem;font-weight:700;">{runtime}</div></div>""", unsafe_allow_html=True)

            c3, c4 = st.columns(2)

            with c3:
                st.markdown(f"""<div style="border:1px solid rgba(255,255,255,0.08);border-radius:14px;padding:1rem;background-color:#081028;"><div style="color:#9CA3AF;font-size:0.82rem;margin-bottom:0.35rem;">Severity</div><div style="color:#F3F4F6;font-size:1.35rem;font-weight:700;">{severity}</div></div>""", unsafe_allow_html=True)

            with c4:
                st.markdown(f"""<div style="border:1px solid rgba(255,255,255,0.08);border-radius:14px;padding:1rem;background-color:#081028;"><div style="color:#9CA3AF;font-size:0.82rem;margin-bottom:0.35rem;">Model</div><div style="color:#F3F4F6;font-size:1.1rem;font-weight:700;">{model}</div></div>""", unsafe_allow_html=True)
                
def render_confidence_analysis_card(fig=None):

    if fig is None:
        with st.container(border=True):
            st.markdown("""<div style="font-size:1.1rem;font-weight:700;margin-bottom:0.3rem;">Confidence Analysis</div>""", unsafe_allow_html=True)
            st.markdown("""<div style="color:#9CA3AF;font-size:0.92rem;margin-bottom:1rem;">Probability distribution unavailable</div>""", unsafe_allow_html=True)
            st.markdown("""<div style="min-height:320px;display:flex;flex-direction:column;justify-content:center;"><div style="color:#F3F4F6;font-size:1.8rem;font-weight:700;margin-bottom:1rem;">Analysis Unavailable</div><div style="color:#9CA3AF;font-size:1rem;line-height:1.7;">Probability distribution will appear<br>after inference execution.</div></div>""", unsafe_allow_html=True)

    else:
        fig.update_layout(
            height=180,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis_title=None,
            yaxis_title=None,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            bargap=0.55
        )

        fig.update_traces(
            textposition="outside",
            marker_line_width=0
        )

        chart_container(fig=fig, title="Confidence Analysis", subtitle="Probability Distribution")