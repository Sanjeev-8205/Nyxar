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

def chart_container(fig, title, subtitle=None, height=350):
    fig.update_layout(height = height)

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
    certainty=None
):

    if sentiment is None:

        with st.container(border=True):

            st.markdown("""<div style="font-size:1.1rem;font-weight:700;margin-bottom:0.3rem;">Inference Output</div>""", unsafe_allow_html=True)

            st.markdown("""<div style="color:#9CA3AF;font-size:0.92rem;margin-bottom:1rem;">Prediction intelligence unavailable</div>""", unsafe_allow_html=True)

            st.markdown("""<div style="min-height:320px;display:flex;flex-direction:column;justify-content:center;"><div style="color:#F3F4F6;font-size:1.8rem;font-weight:700;margin-bottom:1rem;">Awaiting Inference</div><div style="color:#9CA3AF;font-size:1rem;line-height:1.7;">Run inference to generate<br>prediction intelligence.</div></div>""", unsafe_allow_html=True)

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

            st.markdown("""<div style="color:#9CA3AF;font-size:0.92rem;margin-bottom:0.65rem;">Live prediction intelligence</div>""", unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"""<div style="color:{sentiment_color};font-size:3rem;font-weight:800;letter-spacing:0.03em;margin-bottom:0.65rem;">{sentiment.upper()}</div>""", unsafe_allow_html=True)

                st.markdown(f"""<div style="display:inline-block;background:{certainty_bg};color:{certainty_color};padding:0.45rem 0.9rem;border-radius:999px;font-size:0.8rem;font-weight:700;margin-bottom:0.5rem;">{certainty}</div>""", unsafe_allow_html=True)

            with col2:
                confidence_color = (
                    "#10B981" if confidence >= 0.70
                    else "#F59E0B" if confidence >= 0.40
                    else "#EF4444"
                )

                st.markdown(f"""<div style="text-align:right;"><div style="color:{confidence_color};font-size:3rem;font-weight:800;line-height:0.9; margin-top:1.1rem">{confidence:.0%}</div><div style="color:#9CA3AF;font-size:0.75rem;font-weight:700;letter-spacing:0.15em;text-transform:uppercase;margin-top:0.6rem;">Confidence</div></div>""", unsafe_allow_html=True)

            st.markdown(f"""<div style="text-align:center;margin-top:0.2rem;margin-bottom:1rem;"><svg width="220" height="120" viewBox="0 0 180 100"><path d="M20 90 A70 70 0 0 1 160 90" fill="none" stroke="rgba(255,255,255,0.12)" stroke-width="12" stroke-linecap="round"/><path d="M20 90 A70 70 0 0 1 160 90" fill="none" stroke="{'#10B981' if confidence>=0.7 else '#F59E0B' if confidence>=0.4 else '#EF4444'}" stroke-width="12" stroke-linecap="round" pathLength="100" stroke-dasharray="{confidence*100} 100"/><text x="90" y="70" text-anchor="middle" fill="#F3F4F6" font-size="24" font-weight="700">{confidence:.0%}</text></svg></div>""", unsafe_allow_html=True)
            
            st.markdown("""<div style="height:1.2rem;"></div>""", unsafe_allow_html=True)

def render_confidence_analysis_card(fig=None):

    if fig is None:
        with st.container(border=True):
            st.markdown("""<div style="font-size:1.1rem;font-weight:700;margin-bottom:0.3rem;">Confidence Analysis</div>""", unsafe_allow_html=True)
            st.markdown("""<div style="color:#9CA3AF;font-size:0.92rem;margin-bottom:1rem;">Probability distribution unavailable</div>""", unsafe_allow_html=True)
            st.markdown("""<div style="min-height:320px;display:flex;flex-direction:column;justify-content:center;"><div style="color:#F3F4F6;font-size:1.8rem;font-weight:700;margin-bottom:1rem;">Analysis Unavailable</div><div style="color:#9CA3AF;font-size:1rem;line-height:1.7;">Probability distribution will appear<br>after inference execution.</div></div>""", unsafe_allow_html=True)

    else:
        fig.update_layout(
            height=140,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis_title="Confidence Score (%)",
            yaxis_title=None,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            bargap=0.45,
            xaxis=dict(range=[0, 100]),
            yaxis=dict(
                tickfont=dict(size=14)
            )
        )

        fig.update_traces(
            textposition="outside",
            marker_line_width=0
        )

        chart_container(fig=fig, title="Confidence Analysis", subtitle="Probability Distribution", height=267)

def telemetry_card(
    title=None,
    primary=None,
    secondary=None,
    tertiary=None,
    accent="#3B82F6"
):

    if primary is None:

        card_html = """
        <div style="background:linear-gradient(180deg,rgba(17,24,39,0.96),rgba(8,12,24,0.96));border:1px solid rgba(255,255,255,0.06);border-left:4px solid #374151;border-radius:18px;padding:1.35rem 1.4rem;min-height:180px;box-shadow:0 4px 20px rgba(0,0,0,0.25);">
            <div style="color:#9CA3AF;font-size:0.78rem;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:1rem;">Telemetry Unavailable</div>
            <div style="color:#F9FAFB;font-size:2rem;font-weight:800;line-height:1.1;margin-bottom:1.2rem;">--</div>
            <div style="color:#D1D5DB;font-size:0.9rem;margin-bottom:0.45rem;">Awaiting Inference</div>
            <div style="color:#9CA3AF;font-size:0.85rem;">No telemetry available</div>
        </div>
        """

    else:

        card_html = f"""
        <div style="background:linear-gradient(180deg,rgba(17,24,39,0.96),rgba(8,12,24,0.96));border:1px solid rgba(255,255,255,0.06);border-left:4px solid {accent};border-radius:18px;padding:1.35rem 1.4rem;min-height:180px;box-shadow:0 4px 20px rgba(0,0,0,0.25);">
            <div style="color:#9CA3AF;font-size:0.78rem;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:1rem;">{title}</div>
            <div style="color:#F9FAFB;font-size:2rem;font-weight:800;line-height:1.1;margin-bottom:1.2rem;">{primary}</div>
            <div style="color:#D1D5DB;font-size:0.9rem;margin-bottom:0.45rem;">{secondary}</div>
            <div style="color:#9CA3AF;font-size:0.85rem;">{tertiary}</div>
        </div>
        """

    st.markdown(card_html, unsafe_allow_html=True)

def apply_container_background():
    st.markdown(f"""<style>.st-emotion-cache-1gz5zxc,div[data-testid="stVerticalBlockBorderWrapper"]{{background:linear-gradient(180deg,rgba(17,24,39,0.96),rgba(8,12,24,0.96))!important;border:1px solid rgba(255,255,255,0.06)!important;border-radius:18px!important;box-shadow:0 4px 20px rgba(0,0,0,0.25)!important;}}</style>""", unsafe_allow_html=True)

def render_total_time(total_time_ms):
    st.markdown(f'<div style="font-size:1.1rem;"><b>Total Pipeline Time:</b> {total_time_ms:.1f} ms</div>', unsafe_allow_html=True)

def render_trace_placeholder():
    st.markdown("<div style='margin-top: 1rem'></div>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown('<div style="text-align:center;padding:1rem 0;"><h4>Awaiting inference execution...</h4><p>Execution stages and timing telemetry<br>will appear after prediction.</p></div>', unsafe_allow_html=True)

def render_trace_card(step, duration_ms):
    html = f'<div style="text-align:center;padding:16px;border-radius:12px;border:1px solid rgba(148,163,184,0.15);background:linear-gradient(135deg, rgba(15,23,42,0.85), rgba(2,6,23,0.95));"><div style="font-size:0.75rem;font-weight:600;letter-spacing:1px;color:#94A3B8;margin-bottom:8px;">{step.upper()}</div><div style="color:#10B981;font-size:0.85rem;margin-bottom:10px;">✓ COMPLETED</div><div style="font-size:1.8rem;font-weight:700;color:white;">{duration_ms:.1f}</div><div style="font-size:0.8rem;color:#94A3B8;">ms</div></div>'
    st.markdown(html, unsafe_allow_html=True)

def render_pipeline_summary(total_time_ms):
    st.markdown(f'<div style="text-align:center;padding:10px;"><div style="font-size:0.75rem;letter-spacing:2px;color:#94A3B8;">TOTAL PIPELINE TIME</div><div style="font-size:2.2rem;font-weight:700;color:white;">{total_time_ms} ms</div><div style="font-size:0.9rem;color:#10B981;">Pipeline execution complete</div></div>', unsafe_allow_html=True)

def input_analysis_metrics_card(label, value):
    
    html = f'<div style="text-align:center;padding:16px;border-radius:12px;border:1px solid rgba(148,163,184,0.15);background:linear-gradient(135deg,rgba(15,23,42,0.85),rgba(2,6,23,0.95));margin-bottom: 1rem;height:120px;display:flex;flex-direction:column;justify-content:center;"><div style="font-size:0.75rem;font-weight:600;letter-spacing:1px;color:#94A3B8;margin-bottom:10px;text-transform:uppercase;">{label}</div><div style="font-size:1.8rem;font-weight:700;color:white;line-height:1;">{value}</div></div>'
    st.markdown(html, unsafe_allow_html=True)

def text_complexity_header():
    st.markdown("""<div style="font-size:1.1rem;font-weight:700;margin-bottom:0.3rem;">Text Complexity</div>""", unsafe_allow_html=True)

    st.markdown("""<div style="color:#9CA3AF;font-size:0.92rem;margin-bottom:1rem;">Input content analysis</div>""", unsafe_allow_html=True)

def text_complexity_header_placeholder():
    st.markdown("""<div style="font-size:1.1rem;font-weight:700;margin-bottom:0.3rem;">Text Complexity</div>""", unsafe_allow_html=True)

    st.markdown("""<div style="color:#9CA3AF;font-size:0.92rem;margin-bottom:1rem;">Input content analysis not available</div>""", unsafe_allow_html=True)

def ai_insight_card(insight):

    html = f'<div style="background:linear-gradient(135deg,rgba(15,23,42,0.95),rgba(2,6,23,0.95));border:1px solid rgba(148,163,184,0.15);border-left:4px solid rgba(226,232,240,0.85);border-radius:16px;padding:1.5rem;margin-top:1rem;box-shadow:0 0 20px rgba(226,232,240,0.06);"><div style="color:#F8FAFC;font-size:0.95rem;font-weight:700;margin-bottom:1rem;text-shadow:0 0 10px rgba(226,232,240,0.25);">✦ AI Insight Summary</div><div style="color:#E5E7EB;font-size:1rem;line-height:1.9;">{insight}</div></div>'
    st.markdown(html, unsafe_allow_html=True)