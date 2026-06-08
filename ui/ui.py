import streamlit as st
import requests
import plotly.express as px
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import time
from collections import Counter
from datetime import datetime

from styles import load_global_styles
from components import (metric_card, status_card, insights_card, platform_status_card,
                        hero_header, subtitle, hero_subtext, subtitle_subtext, 
                        chart_container, apply_button_style, render_model_info, apply_container_background, 
                        inference_output_card, render_confidence_analysis_card, telemetry_card,
                        render_trace_card, render_trace_placeholder, render_pipeline_summary,
                        input_analysis_metrics_card, text_complexity_header, text_complexity_header_placeholder,
                        ai_insight_card, progress_bar_modified, batch_job_overview_header,
                        dataset_intelligence_card, prediction_distribution_card,
                        processing_analytics_card, processing_breakdown_card, 
                        render_trace_placeholder_batch_inference, batch_trace_row, batch_trace_header, batch_ai_insight_card,
                        summary_description_card, render_section_card, render_intelligence_sections, render_recommendations_card, render_metadata_card,
                        render_opportunity_assessment, render_risk_assessment, render_confidence_assessment)

#setting the page title
st.set_page_config(
    page_title="AI Observability and Intelligence Platform",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_global_styles()
apply_button_style()
apply_container_background()
progress_bar_modified()

BASE_URL = "https://sanjeev2501-nyxar.hf.space"

#Get the loaded models
@st.cache_data
def get_models():
    try:
        return requests.get(f"{BASE_URL}/models", timeout=30).json()
    except:
        return ["Backend not available!"]
    
model_list = get_models()

#dashboard_metrics

@st.cache_data(ttl=15)
def get_dashboard_metrics():

    empty_dashboard = {
        "inference": {
            "total_predictions": 0,
            "average_latency": 0,
            "rpm": 0
        },

        "health": {
            "db_health": {
                "database": "disconnected"
            },

            "models_count": 0,

            "cpu_usage": [0, "Unknown"],

            "uptime": "Unavailable"
        },

        "analytics": {
            "sentiment_distribution": {},
            "predictions_over_time": [],
            "model_usage_distribution": [],
            "latency_trends": [None, []],
            "confidence_distribution": [],
            "recent_activity": {}
        },

        "advanced": {
            "failure_rate": {
                "failure_percent": 0
            },

            "p95_latency": 0,

            "model_metrics": {},

            "latency_per_model": [],

            "drift_indicators": {}
        },

        "logs": []
    }

    try:
        response = requests.get(
            f"{BASE_URL}/dashboard",
            timeout=30
        )

        response.raise_for_status()

        return response.json()

    except Exception:
        return empty_dashboard

if "dashboard_metrics" not in st.session_state:
    st.session_state.dashboard_metrics = get_dashboard_metrics()

dashboard_metrics = st.session_state.dashboard_metrics

# =========================
# SESSION STATE INIT
# =========================

if "completed_job_data" not in st.session_state:
    st.session_state.completed_job_data = None

if "polling_started" not in st.session_state:
    st.session_state.polling_started = False

if "failed_job" not in st.session_state:
    st.session_state.failed_job = False

if "prediction_result" not in st.session_state:
    st.session_state.prediction_result = None

if "job_id" not in st.session_state:
    st.session_state.job_id = None

if "ai_summary" not in st.session_state:
    st.session_state.ai_summary = None

st.title("✨ AI Observability and Intelligence Platform")
st.caption("Real-time monitoring, inference analytics, and AI-driven operational intelligence for production-scale ML systems.")

def render_overview():

    dashboard_metrics = st.session_state.dashboard_metrics

    hero_header("Overview")
    hero_subtext("Real-time AI inference, observability, and intelligence monitoring for production-scale ML workflows.")

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        metric_card("Total Predictions", dashboard_metrics["inference"]["inference_metrics"]["total_predictions"])

    with col2:
        metric_card("Avg Latency", f"{dashboard_metrics["inference"]["inference_metrics"]["average_latency"]}ms")
    
    with col3:
        metric_card("RPM", dashboard_metrics["inference"]["inference_metrics"]["rpm"])
    
    with col4:
        metric_card("Active Models", dashboard_metrics["health"]["models_count"])
    
    with col5:
        metric_card("Uptime", dashboard_metrics["health"]["uptime"])

    le_col, ri_col = st.columns([1.7,1])

    with le_col:
        t1, t2, t3 = st.tabs([
            "Latency Over Time",
            "Request Volume",
            "Throughput Trend"
        ])

        with t1:
            #Latency Trends
            latency = dashboard_metrics["analytics"]["latency_trends"][1]

            latency_trends = pd.DataFrame(latency)

            if not latency_trends.empty:
                fig_latency_trends = px.line(
                    latency_trends,
                    x = "time",
                    y = "avg_latency",
                    markers = True
                )

                chart_container(fig_latency_trends, "Latency Trends Over Time")
            
            else:
                st.info("No data yet.")

        platform_status = requests.get(f"{BASE_URL}/platform_status")

        if platform_status.status_code == 200:
            data = platform_status.json()
            platform_status_card(data)
        
        else:
            platform_status_card({
                "status": "DATA UNAVAILABLE",
                "message": "Platform status could not be retrieved. Service may be temporarily unavailable.",
                "color": "#EF4444"
            })
        
        with t2:
            #Requests Per Hour
            requests_per_hour = dashboard_metrics["analytics"]["predictions_over_time"][1]

            rph = pd.DataFrame(requests_per_hour)

            if not rph.empty:
                fig_rph = px.line(
                    rph,
                    x = "hour",
                    y = "count",
                    markers = True
                )

                chart_container(fig_rph, "Requests Per Hour")
            
            else:
                st.info("You have not made any predictions yet. Make predictions to view the results.")

        with t3:
            #Throughput Per Hour
            throughput_per_hour = dashboard_metrics["analytics"]["throughput_per_hour"]

            tph = pd.DataFrame(throughput_per_hour)

            if not tph.empty:
                fig_tph = px.line(
                    tph,
                    x = "hour",
                    y = "throughput",
                    markers = True
                )

                chart_container(fig_tph, "Throughput Per Hour")

    with ri_col:
        
        left_col, right_col = st.columns([1.5, 0.5])
        with left_col:
            st.subheader("System Insights")

        with right_col:
            if st.button("🔄", help="Click to refresh insights."):
                response = requests.post(f"{BASE_URL}/overview_insights/refresh")
                if response.status_code == 200:
                    st.toast("Insights refreshed!", icon="✅")
                    st.rerun()
                else:
                    st.toast("Failed to refresh insights.", icon="❌")

        response = requests.get(f"{BASE_URL}/overview_insights")

        if response.status_code == 200:
            data = response.json()
            insights = data.get("ai_insights", {})

            inference = insights.get("inference_insights") or "Insights not available yet."
            activity = insights.get("recent_activity") or "Insights not available yet."
            anomaly = insights.get("anomaly_detection") or "Insights not available yet."
            health = insights.get("health_metrics") or "Insights not available yet."

            insights_card("Inference", inference, level="inference")
            insights_card("Recent Activity", activity, level="activity")
            insights_card("Anomaly Detection", anomaly, level="anomaly")
            insights_card("Health", health, level="health")

        else:
            insights_card("AI Insights", "Unable to load insights. Please try again later.")

def render_live_inference():
        
        dashboard_metrics = st.session_state.dashboard_metrics
        hero_header("Live Inference")
        hero_subtext("Live inference using ML models")

        with st.container(border=True):

            st.markdown("### Inference Control Center")

            user_input = st.text_area("Enter review text for live inference...", height=200, placeholder="Type review text here......")
            st.markdown("##### &nbsp;")

            c1, c2 = st.columns([1.5,0.5])
            with c1:
                model_choice = st.selectbox("Inference Engine", model_list)

                MODEL_INFO = {
                    "RoBERTa Transformer": "High Quality • Low Single-Inference Latency",
                    "Bi-LSTM": "Moderate Quality • Higher Inference Latency",
                    "Logistic Regression": "Fastest Inference • Lightweight Model"
                }

                #render _model_info
                render_model_info(model_choice, MODEL_INFO)
                
            with c2:
                predict_btn = st.button("Run Inference", width="stretch")
            

        if predict_btn:
            if not user_input.strip():
                st.warning("Enter some text for prediction")
            else:
                with st.spinner("Running model inference......."):
                    response = requests.post(
                        f"{BASE_URL}/predict",
                        json={"text":user_input, "model":model_choice}
                    )

                    try:
                        result = response.json()
                    
                        st.session_state.prediction_result = result

                        #clear old dashboarb cache
                        get_dashboard_metrics.clear()
                        st.session_state.dashboard_metrics = get_dashboard_metrics()
                        dashboard_metrics = st.session_state.dashboard_metrics
                    
                    except Exception as e:
                        st.error(
                            f"Prediction failed: {str(e)}"
                        )
                    
        col1, col2 = st.columns(2)
        if st.session_state.prediction_result is not None:

            result = st.session_state.prediction_result
            
            prediction = result["prediction"]
            latency = result["latency"]
            confidence_score = max(result["confidence_scores"])
            model_name = result["model_used"]
            probability_scores = [f"{score:.2%}" for score in result["confidence_scores"]]
            certainty = result["certainty"]

            with col1:
                inference_output_card(
                    sentiment=prediction, confidence=confidence_score, certainty=certainty
                )
            
            with col2:

                fig = px.bar(
                    x=probability_scores,
                    y=["Negative", "Neutral", "Positive"],
                    orientation="h",
                    text=[f"{score}" for score in probability_scores],
                    color=["Negative", "Neutral", "Positive"],
                    color_discrete_map={
                        "Negative": "#EF4444",
                        "Neutral": "#F59E0B",
                        "Positive": "#10B981"
                    }
                )

                render_confidence_analysis_card(fig=fig)
        
        else:
            with col1:
                inference_output_card()
            with col2:
                render_confidence_analysis_card()  

        col1, col2, col3 = st.columns([1,1,1.2])
        if st.session_state.prediction_result is not None:
            all_metrics = dashboard_metrics["inference"]["inference_row_metrics"]
            
            with col1:
                telemetry_card(
                    title="Latency",
                    primary=f"{all_metrics["latency_ms"]} ms",
                    secondary=f"p95: {(dashboard_metrics["advanced"]["p95_latency"])*1000} ms",
                    tertiary=all_metrics["latency_label"],
                    accent="#3B82F6"
                )
            
            with col2:
                telemetry_card(
                    title="Throughput",
                    primary=f"{all_metrics["rpm"]} RPM",
                    secondary=all_metrics["throughput_label"],
                    tertiary=all_metrics["processing_time"],
                    accent="#10B981"
                )
            
            with col3:
                telemetry_card(
                    title="Model Metadata",
                    primary=f"{all_metrics["model_name"]}",
                    secondary=all_metrics["model_family"],
                    tertiary=all_metrics["model_runtime"],
                    accent="#8B5CF6"
                )

        else:
            with col1:
                telemetry_card(title="Latency")
            with col2:
                telemetry_card(title="Throughput")
            with col3:
                telemetry_card(title="Model Metadata")
        
        if st.session_state.prediction_result is not None:

            result = st.session_state.prediction_result
            model = result["model_used"]
            st.markdown("<div style='margin-top: 1rem'></div>", unsafe_allow_html=True)
            with st.container(border=True):
                trace = result["trace"]
                
                if model == "Bi-LSTM":
                    stages=4
                    cols = st.columns([4,1,4,1,4,1,4])
                else:
                    stages=3
                    cols = st.columns([4,1,4,1,4])

                for i, item in enumerate(trace):

                    # Card column
                    with cols[i * 2]:
                        render_trace_card(
                            step=item["step"],
                            duration_ms=item["duration_ms"]
                        )

                    # Arrow column (except after last card)
                    if i < len(trace) - 1:
                        with cols[i * 2 + 1]:
                            st.markdown('<div style="text-align:center;font-size:2rem;color:#64748B;margin-top:55px;">→</div>', unsafe_allow_html=True)

                render_pipeline_summary(result["total_time"])

        else:
            render_trace_placeholder()
        
        #Last row
        c1, c2 = st.columns([1, 1.6])
        with c1:
            with st.container(border=True):

                if st.session_state.prediction_result is not None:

                    results = st.session_state.prediction_result

                    text_complexity_header()

                    words = results["words"]
                    chars = results["characters"]
                    sentences = results["sentences"]
                    complexity = results["complexity"]

                else:

                    text_complexity_header_placeholder()

                    words = "--"
                    chars = "--"
                    sentences = "--"
                    complexity = "--"

                col1, col2 = st.columns(2)

                with col1:
                    input_analysis_metrics_card("Words", words)
                    input_analysis_metrics_card("Characters", chars)

                with col2:
                    input_analysis_metrics_card("Sentences", sentences)
                    input_analysis_metrics_card("Complexity", complexity)

        with c2:
            with st.container(border=True):

                st.markdown("""<div style="font-size:1.1rem;font-weight:700;margin-bottom:0.3rem;">AI Prediction Insights</div>""", unsafe_allow_html=True)

                st.markdown("""<div style="color:#9CA3AF;font-size:0.92rem;margin-bottom:1rem;">Analysis of key signals influencing prediction</div>""", unsafe_allow_html=True)

                if st.session_state.prediction_result is not None:
                    result = st.session_state.prediction_result
                    insight = result["insight"]

                    ai_insight_card(insight=insight)

                else:

                    st.markdown(
                        '<div style="min-height:272.5px;display:flex;align-items:center;justify-content:center;text-align:center;"><div><div style="color:#F3F4F6;font-size:1.4rem;font-weight:700;margin-bottom:1rem;">Awaiting Analysis</div><div style="color:#9CA3AF;font-size:1rem;line-height:1.8;">Run inference to generate<br>AI-powered prediction insights.</div></div></div>',
                        unsafe_allow_html=True
                    )

def render_batch_intelligence():

    dashboard_metrics = st.session_state.dashboard_metrics

    hero_header("Batch Intelligence")
    hero_subtext("Track large-scale dataset processing, asynchronous AI workflows, job analytics, and batch inference performance.")

    with st.container(border=True):
        uploaded_file = st.file_uploader(
            "Upload CSV", type=["csv"]
        )

        selected_model = st.selectbox("Select Model", model_list)
        upload_button = st.button("Start Batch Processing")

        if "polling_started" not in st.session_state:
            st.session_state.polling_started = False

        if "completed_job_data" not in st.session_state:
            st.session_state.completed_job_data = None

        if "failed_job" not in st.session_state:
            st.session_state.failed_job = False
        
        if "last_job_data" not in st.session_state:
            st.session_state.last_job_data = None
        
        if "file_size" not in st.session_state:
            st.session_state.file_size = None

        if upload_button:
            if uploaded_file is not None and not st.session_state.get("polling_started", False):
                files = {
                    "file":uploaded_file.getvalue()
                }

                data = {
                    "model": selected_model
                }

                file_size_bytes = uploaded_file.size
                def format_file_size(size_bytes):
                    if size_bytes < 1024:
                        return f"{size_bytes} B"
                    elif size_bytes < 1024**2:
                        return f"{size_bytes / 1024:.2f} KB"
                    elif size_bytes < 1024**3:
                        return f"{size_bytes / (1024**2):.2f} MB"
                    else:
                        return f"{size_bytes / (1024**3):.2f} GB"
                    
                st.session_state.file_size = format_file_size(file_size_bytes)

                response = requests.post(
                    f"{BASE_URL}/batch/upload",
                    params={"model": selected_model},
                    files={
                        "file":(
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            "text/csv"
                        )
                    }
                )

                job_id = response.json()['job_id']

                st.session_state.job_id = job_id
                st.session_state.polling_started = True
                time.sleep(1)

    if not st.session_state.job_id and not st.session_state.polling_started:
        with st.container(border=True):
            batch_job_overview_header()
            st.progress(0)

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                input_analysis_metrics_card("Total Rows", "--")
            with c2:
                input_analysis_metrics_card("Processed Rows", "--")
            with c3:
                input_analysis_metrics_card("Throughput", "-- Rows/Sec")
            with c4:
                input_analysis_metrics_card("Status", "WAITING")

    elif "job_id" in st.session_state and st.session_state.polling_started:
        job_id = st.session_state.job_id

        placeholder = st.empty()

        while True:

            try:
                response = requests.get(
                    f"{BASE_URL}/batch/job/{job_id}", timeout=30
                )

                if response.status_code != 200:
                    st.error(f"API Error: {response.status_code}")
                    st.text(response.text)
                    break

                st.session_state.last_job_data = response.json()

            except Exception as e:
                st.error(f"Request Failed: {e}")
                break

            with placeholder.container(border=True):
                batch_job_overview_header()
                st.progress(st.session_state.last_job_data['progress'] / 100)

                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    input_analysis_metrics_card("Total Rows", st.session_state.last_job_data['total_rows'])
                with c2:
                    input_analysis_metrics_card("Processed Rows", st.session_state.last_job_data['processed_rows'])
                with c3:
                    if st.session_state.last_job_data['processed_rows']:
                        input_analysis_metrics_card("Throughput", f"{int((st.session_state.last_job_data['processed_rows'])/st.session_state.last_job_data['processing_time'])} Rows/Sec")
                    else:
                        input_analysis_metrics_card("Throughput", "0 Rows/Sec")
                with c4:
                    input_analysis_metrics_card("Status", st.session_state.last_job_data["status"].upper())

            if st.session_state.last_job_data["status"] in ["completed", "failed"]:

                st.session_state.polling_started = False

                if st.session_state.last_job_data["status"] == "completed":
                    st.session_state.completed_job_data = st.session_state.last_job_data
                else:
                    st.session_state.failed_job = True

                break

            time.sleep(1)

    elif st.session_state.last_job_data is not None:
        with st.container(border=True):
            batch_job_overview_header()
            st.progress(st.session_state.last_job_data['progress'] / 100)

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                input_analysis_metrics_card("Total Rows", st.session_state.last_job_data['total_rows'])
            with c2:
                input_analysis_metrics_card("Processed Rows", st.session_state.last_job_data['processed_rows'])
            with c3:
                if st.session_state.last_job_data['processed_rows']:
                    input_analysis_metrics_card("Throughput", f"{int((st.session_state.last_job_data['processed_rows'])/st.session_state.last_job_data['processing_time'])} Rows/Sec")
                else:
                    input_analysis_metrics_card("Throughput", "0 Rows/Sec")
            with c4:
                input_analysis_metrics_card("Status", st.session_state.last_job_data["status"].upper())

    c1, c2 = st.columns(2)
    with c1:
        if not st.session_state.job_id:
            dataset_intelligence_card()
        else:
            results = st.session_state.last_job_data
            dataset_intelligence_card(rows=results["total_rows"], columns=results["all_columns"], file_size=st.session_state.file_size, model=results["model_name"], text_column=results["text_column"])
    with c2:
        if st.session_state.completed_job_data:
            response = requests.get(f"{BASE_URL}/batch/job/{st.session_state.job_id}/results", timeout=30)

            if response.status_code == 200:
                data = response.json()
                results = data["results"]

                sentiments = [r["prediction"] for r in results]
                sentiments_count = Counter(sentiments)

                prediction_distribution_card(
                    state="completed",
                    negative_count=sentiments_count.get("0", 0),
                    neutral_count=sentiments_count.get("1", 0),
                    positive_count=sentiments_count.get("2", 0),
                    total_rows=len(sentiments)
                )
            
            else:
                st.error("Unexpected Error Occured") 

        else:
            prediction_distribution_card()

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        if st.session_state.completed_job_data:
            def format_duration(seconds):
                if seconds < 1:
                    return f"{seconds * 1000:.0f} ms"
                return f"{seconds:.2f} sec"
            
            data = st.session_state.completed_job_data
            processing_analytics_card(
                ml_processing_time=format_duration(data["ml_processing_time"]), db_time=format_duration(data["db_time"]),
                overhead_time=format_duration(data["overhead_time"]), total_runtime=format_duration(data["processing_time"]),
                model_name=data["model_name"]
            )
        
        else:
            processing_analytics_card()
    
    with c2:
        if st.session_state.completed_job_data:
            data = st.session_state.completed_job_data
            processing_breakdown_card(
                ml_processing_time=data["ml_processing_time"], db_time=data["db_time"], overhead_time=data["overhead_time"], state="completed"
            )

        else:
            processing_breakdown_card()

    #Pipeline
    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    c1, c2 = st.columns([1.25,2])
    with c1:
        if st.session_state.completed_job_data is not None:
            
            result = st.session_state.completed_job_data
            model = result["model_name"]

            completed_at = datetime.fromisoformat(result["completed_at"])
            created_at = datetime.fromisoformat(result["created_at"])
            total_time = (completed_at - created_at).total_seconds()

            if model == "Logistic Regression":
                trace = [
                    {
                        "step": "Upload",
                        "duration": result["upload_time"]
                    },
                    {
                        "step": "Dataset Validation",
                        "duration": result["validation_time"]
                    },
                    {
                        "step": "Text Preprocessing",
                        "duration": result["text_preprocessing_time"]
                    },
                    {
                        "step": "Vectorization",
                        "duration": result["vectorization_time"]
                    },
                    {
                        "step": "Logistic Batch Prediction",
                        "duration": result["inference_time"]
                    },
                    {
                        "step": "Database",
                        "duration":result["db_time"]
                    }
                ]
            
            elif model == "Bi-LSTM":
                trace = [
                    {
                        "step": "Upload",
                        "duration": result["upload_time"]
                    },
                    {
                        "step": "Dataset Validation",
                        "duration": result["validation_time"]
                    },
                    {
                        "step": "Text Preprocessing",
                        "duration": result["text_preprocessing_time"]
                    },
                    {
                        "step": "Tokenization",
                        "duration": result["tokenization_time"]
                    },
                    {
                        "step": "Sequence Padding",
                        "duration": result["sequence_padding_time"]
                    },
                    {
                        "step": "Bi-LSTM Batch Prediction ",
                        "duration": result["inference_time"]
                    },
                    {
                        "step": "Database",
                        "duration":result["db_time"]
                    }
                ]

            elif model == "RoBERTa Transformer":
                trace = [
                    {
                        "step": "Upload",
                        "duration": result["upload_time"]
                    },
                    {
                        "step": "Dataset Validation",
                        "duration": result["validation_time"]
                    },
                    {
                        "step": "Text Preprocessing",
                        "duration": result["text_preprocessing_time"]
                    },
                    {
                        "step": "Tokenization",
                        "duration": result["tokenization_time"]
                    },
                    {
                        "step": "Onnx Batch Prediction",
                        "duration": result["inference_time"]
                    },
                    {
                        "step": "Database",
                        "duration":result["db_time"]
                    }
                ]

            with st.container(border=True):
                
                batch_trace_header()
                max_duration = max(item["duration"] for item in trace)

                for i, item in enumerate(trace):
                    duration_ms = item["duration"] * 1000
                    is_bottleneck = item["duration"] == max_duration

                    if is_bottleneck:
                        dot, color, glow, weight = "💥", "#A855F7", "0 0 10px #A855F7, 0 0 20px #A855F7", "700"
                        
                    else:
                        dot, color, glow, weight = "●", "#14B8A6", "0 0 6px rgba(20,184,166,0.5)", "500"
                    
                    batch_trace_row(dot, color, glow, weight, duration_ms, item["step"], show_connector=i<len(trace) - 1)
                
                st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

        else:
            render_trace_placeholder_batch_inference()

    with c2:
        #'''with st.container(border=True):
        #   st.markdown("""<div style="font-size:1.1rem;font-weight:700;margin-bottom:0.3rem;">Operational Insights</div>""", unsafe_allow_html=True)
        #
        #  st.markdown("""<div style="color:#9CA3AF;font-size:0.92rem;margin-bottom:1rem;">AI-generated assessment of batch execution efficiency and processing performance.</div>""", unsafe_allow_html=True)
        #
        #    raw_insights = None
        #    for _ in range(10):  # retry up to 10 times
        #        response = requests.get(f"{BASE_URL}/batch/job/{st.session_state.job_id}")
        #        data = response.json()
        #        raw_insights = data.get("insight")
        #        if raw_insights:
        #            break
        #        time.sleep(2)
        #
        #        if raw_insights:
        #            ai_insight_card(insight=raw_insights["insight"])
        #        else:
        #            st.markdown('<div style="min-height:272.5px;display:flex;align-items:center;justify-content:center;text-align:center;"><div><div style="color:#F3F4F6;font-size:1.4rem;font-weight:700;margin-bottom:1rem;">Please wait.......</div><div style="color:#9CA3AF;font-size:1rem;line-height:1.8;">Insights are being generated.</div></div></div>', unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("""<div style="font-size:1.1rem;font-weight:700;margin-bottom:0.3rem;">Operational Insights</div>""", unsafe_allow_html=True)
            st.markdown("""<div style="color:#9CA3AF;font-size:0.92rem;margin-bottom:1rem;">AI-generated assessment of batch execution efficiency and processing performance.</div>""", unsafe_allow_html=True)

            raw_insights = None
            placeholder = st.empty()
            placeholder.markdown("""<style>@keyframes pulse{0%,100%{opacity:1;}50%{opacity:0.4;}}.pulse{animation:pulse 1.5s ease-in-out infinite;}</style><div style="min-height:272.5px;display:flex;align-items:center;justify-content:center;text-align:center;"><div><div class="pulse" style="color:#F3F4F6;font-size:1.4rem;font-weight:700;margin-bottom:1rem;">Generating Insights...</div><div style="color:#9CA3AF;font-size:1rem;line-height:1.8;">AI is analyzing pipeline performance.</div></div></div>""", unsafe_allow_html=True)

            for _ in range(10):
                response = requests.get(f"{BASE_URL}/batch/job/{st.session_state.job_id}")
                data = response.json()
                raw_insights = data.get("insight")
                if raw_insights:
                    break
                time.sleep(2)

            with placeholder.container():
                if raw_insights:
                    batch_ai_insight_card(insight=raw_insights["insight"])
                else:
                    st.markdown('<div style="min-height:272.5px;display:flex;align-items:center;justify-content:center;text-align:center;"><div><div style="color:#F3F4F6;font-size:1.4rem;font-weight:700;margin-bottom:1rem;">Oops. Unexpected error occured</div><div style="color:#9CA3AF;font-size:1rem;line-height:1.8;">Insights could not be generated.</div></div></div>', unsafe_allow_html=True)

def render_ai_intelligence():

    dashboard_metrics = st.session_state.dashboard_metrics

    @st.dialog("AI Intelligence Summary", width="large")
    def show_summary():
        st.markdown(st.session_state.ai_summary)

    with st.container(border=True):
        hero_header("AI Intelligence")
        hero_subtext("Generate LLM-powered summaries, topic insights, and enterprise-scale feedback intelligence.")

    #telemetry_container = st.container()
    #recommendation_container = st.container()
    
    with st.container(border=True):
        st.markdown("### Intelligence Control Center")

        st.markdown('<div style="color:#9CA3AF;font-size:1rem;line-height:1.8;margin-top:-0.25rem;margin-bottom:1rem;">Choose the depth of analysis to generate from batch prediction results.</div>',unsafe_allow_html=True,)

        SUMMARY_MAPPING = {
            "Executive Summary": "executive",
            "Detailed Report": "detailed",
            "Full Report(Both)": "full"
        }

        selected_option = st.radio(
            "Summary Type",
            [
                "Executive Summary",
                "Detailed Report",
                "Full Report(Both)"
            ],
            horizontal=True,
            help = "Executive: 30 seconds read | Detailed: Full Breakdown | Full: Both"
        )

        summary_type = SUMMARY_MAPPING[selected_option]
        st.session_state.summary_type = selected_option

        #Description of the summary types
        descriptions = {
            "Executive Summary":
                "Quick overview of key findings, sentiment trends, and major themes (~30 second read).",

            "Detailed Report":
                "Comprehensive analysis of customer strengths, pain points, sentiment drivers, emerging themes, and strategic opportunities.",

            "Full Report(Both)":
                "Includes both the Executive Summary and Detailed Report for complete intelligence coverage."
        }

        summary_description_card(title=st.session_state.summary_type, description=descriptions[selected_option])

        if st.button("Generate AI Insights"):
            if not st.session_state.completed_job_data:
                st.toast("Run a batch prediction before generating AI insights.", icon="⚠️")

            else:
                with st.spinner("Analyzing reviews with AI..."):
                    response = requests.get(
                        f"{BASE_URL}/batch/job/{st.session_state.job_id}/summary",
                        params={"summary_type":summary_type},
                        timeout=120
                    )

                    if response.status_code == 200:
                        data = response.json()

                        st.write(data)
                        st.session_state.ai_summary = data["summary"]["executive_summary"]
                        st.toast("AI insights generated sucessfully.", icon="✅")

                    else:
                        st.error("Failed to generate insights. Try again.")

        if st.session_state.ai_summary:
            if st.session_state.summary_type == "Full Report(Both)":
                summary_type="Full Report"
            else:
                summary_type = st.session_state.summary_type

            st.divider()
            st.markdown(f'<div style="font-size:0.75rem;font-weight:600;letter-spacing:1px;color:#94A3B8;text-transform:uppercase;">REPORT GENERATED</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="color:#E5E7EB;margin-top:0.5rem;margin-bottom:0rem;"> {summary_type} generated successfully and is ready for view or download.</div>', unsafe_allow_html=True)

            c1, c2 = st.columns(2)

            with c1:
                if st.button(f"📄 View {summary_type}", width="stretch"):
                    show_summary()
            
            with c2:
                st.markdown("<div style='height:27.4px;'></div>", unsafe_allow_html=True)
                st.download_button(
                    f"📥 Download {summary_type}",
                    st.session_state.ai_summary,
                    file_name="ai_summary.md",
                    mime="text/markdown",
                    width="stretch"
                )

    
    if not st.session_state.ai_summary:
        with st.container(border=True):
            st.markdown("""<div style="min-height:320px;display:flex;align-items:center;justify-content:center;text-align:center;"><div><div style="font-size:2rem;margin-bottom:1rem;filter:drop-shadow(0 0 10px rgba(255,255,255,0.2));">🧠</div><div style="color:#F3F4F6;font-size:1.4rem;font-weight:700;margin-bottom:1rem;">Awaiting Intelligence Generation</div><div style="color:#9CA3AF;font-size:1rem;line-height:1.8;max-width:650px;">Generate an AI-powered intelligence report from completed batch analysis.<br><br>The report will automatically organize findings into relevant analytical sections and provide structured insights based on the observed patterns within the dataset.</div></div></div>""", unsafe_allow_html=True)

    else:
        with st.container(border=True):
            response = requests.get(f"/batch/job/{st.session_state.job_id}/summary")

            if response.status_code == 200:
                data=response.json()
                summary_data = data["summary"]

            else:
                st.error("Response timed out. No response from the server.")

            render_intelligence_sections(summary_data["sections"])

            if st.session_state.summary_type == "Full Report(Both)":
                c1, c2 = st.columns(2)
                with c1:
                    render_opportunity_assessment(summary_data["opportunity_assessment"])
                with c2:
                    render_risk_assessment(summary_data["risk_assesssment"])
                render_confidence_assessment(summary_data["confidence_assessment"])

            render_recommendations_card(summary_data["recommendations"])
            render_metadata_card(summary_data["report_metadata"])

def render_observability():

    dashboard_metrics = st.session_state.dashboard_metrics

    obs_tab1, obs_tab2, obs_tab3, obs_tab4 = st.tabs([
        "Overview",
        "Performance",
        "Logs",
        "Infrastructure"
    ])

    with obs_tab1:
        subtitle("Analytics Dashboard")
        subtitle_subtext("Historical inference trends and system intelligence")

        col1, col2 = st.columns(2)
        with col1:
            #Sentiment Distribution
            sentiment_distribution = dashboard_metrics["analytics"]["sentiment_distribution"]

            sentiment_df = pd.DataFrame(
                {
                    "Sentiment": sentiment_distribution.keys(),
                    "Count": sentiment_distribution.values()
                }
            )

            fig_sentiment = px.pie(
                sentiment_df,
                names = "Sentiment",
                values = "Count"
            )

            chart_container(fig_sentiment, "Sentiment Distribution")

            #Model Usage Distribution
            models_ = dashboard_metrics["analytics"]["model_usage_distribution"]

            model_usage_distribution = pd.DataFrame(models_)

            if not model_usage_distribution.empty:
                fig_model_usage = px.bar(
                    model_usage_distribution,
                    x = "model",
                    y = "usage"
                )

                chart_container(fig_model_usage, "Model Usage Distribution")
            
            else:
                st.info("You have not made any predictions yet. Make predictions to view the results.")

        with col2:
            #Prediction Over Time
            prediction_ = dashboard_metrics["analytics"]["predictions_over_time"][0]

            prediction_over_time = pd.DataFrame(prediction_)

            if not prediction_over_time.empty:
                fig_predictions = px.line(
                    prediction_over_time,
                    x = "day",
                    y = "count",
                    markers = True
                )

                chart_container(fig_predictions, "Predictions Per Day")
            
            else:
                st.info("You have not made any predictions yet. Make predictions to view the results.")

            #Confidence distribution
            confidence_ = dashboard_metrics["analytics"]["confidence_distribution"]

            confidence_distribution = pd.DataFrame(confidence_)

            if not confidence_distribution.empty:
                fig_confidence_distributions = px.bar(
                    confidence_distribution,
                    x = "Confidence",
                    y = "Count"
                )

                chart_container(fig_confidence_distributions, "Confidence Distribution")
            
            else:
                st.info("You have not made any predictions yet. Make predictions to view the results.")

            #Recent Activity Feed
            activity_ = dashboard_metrics["analytics"]["recent_activity"]

            activity_feed = pd.DataFrame([activity_])

            st.subheader("Recent Activity")
            st.dataframe(
                activity_feed, width = "stretch"
            )

    with obs_tab2:
        subtitle("Advanced ML Metrics")
        subtitle_subtext("Production-grade performance and observability insights")

        col1, col2 = st.columns(2)

        with col1:
            p95_latency = dashboard_metrics["advanced"].get("p95_latency", 0) or 0

            metric_card(
                "p95_latency", f"{p95_latency:.3f}s" 
            )

        with col2:
            failure_rate = dashboard_metrics["advanced"]["failure_rate"]["failure_percent"]

            metric_card(
                "Failure Rate", f"{failure_rate:.2f}"
            )
        
        #Model Metrics
        model_metrics = dashboard_metrics["advanced"]["model_metrics"]

        df_metrics = pd.DataFrame(model_metrics).T.reset_index()
        df_metrics = df_metrics.rename(columns={"index":"Model"})

        st.subheader("Model Performance Comparison")

        if not df_metrics.empty:
            st.dataframe(df_metrics, width="stretch")
        else:
            st.info("You have not made any predictions yet. Make predictions to view the results.")

        # Columns for latency and accuracy
        col_1, col_2 = st.columns(2)

        with col_1:
        #Avg latency per model

            avg_latency = dashboard_metrics["advanced"]["latency_per_model"]

            avg_latency_per_model = pd.DataFrame(avg_latency)

            if not avg_latency_per_model.empty:
                fig_avg_latency = px.bar(
                    avg_latency_per_model,
                    x = "model",
                    y = "avg_latency"
                )

                chart_container(fig_avg_latency, "Average Latency Per Model")
            
            else:
                st.info("You have not made any predictions yet. Make predictions to view the results.")

        with col_2:
            #Model Accuracy

            if not df_metrics.empty:
                fig_model_accuracy = px.bar(
                    df_metrics,
                    x = "Model",
                    y = "accuracy"
                )

                chart_container(fig_model_accuracy, "Model Accuracy Comparison")

            else:
                st.info("You have not made any predictions yet. Make predictions to view the results.")

        #Drift indicators
        drift_indicators = dashboard_metrics["advanced"]["drift_indicators"]

        if not drift_indicators:
            st.info("You have not made any predictions yet. Make predictions to view drift data.")

        else:
            shift_data = {
                key:value for key, value in drift_indicators.items() if "shift" in key
            }

            rolling_data = {
                key:value for key, value in drift_indicators.items() if "rolling" in key
            }

            time_stamp = drift_indicators["timestamp"]

            ##KPIs
            if shift_data:
                st.subheader("Drift Indicators")
                drift_cols = st.columns(len(shift_data))

                for col, (metric, value) in zip(drift_cols, shift_data.items()):
                    with col:
                        metric_card(
                            metric.replace("_", " ").title(),
                            f"{value:.2f}"
                        )
            else:
                st.info("Not enough data available to calculate drift shifts yet.")
            
            ##Visualization of rolling drifts
            for metric, value in rolling_data.items():
                if "text" in metric:
                    title = f"Input Length Trends"
                elif "sentiment" in metric:
                    title = f"Sentiment Trends"
                else:
                    title = f"Model Confidence Trends"

                fig_rolling = px.line(
                    x = time_stamp,
                    y = value
                )

                chart_container(fig_rolling, title)

    with obs_tab3:
        logs_df = pd.DataFrame(dashboard_metrics["logs"])

        if logs_df.empty:
            st.info("No logs available yet. Make predictions to populate inference logs.")
        else:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### Filters")
            with col2:
                refresh_col1, refresh_col2 = st.columns(2)

                with refresh_col1:
                    if st.button("🔄 Refresh"):
                        get_dashboard_metrics.clear()
                        st.session_state.dashboard_metrics = get_dashboard_metrics()
                        dashboard_metrics = st.session_state.dashboard_metrics

                with refresh_col2:
                    auto_refresh = st.toggle("Auto Refresh", help="Refreshes dashboard every 10 seconds")
                    if auto_refresh:
                        st_autorefresh(interval=10000, key="refresh")

            filter_col1, filter_col2, filter_col3 = st.columns(3)

            with filter_col1:
                selected_model_filter = st.selectbox(
                    "Model Filter",
                    ["All"] + list(logs_df["model"].unique())
                )

            with filter_col2:
                selected_status_filter = st.selectbox(
                    "Status Filter",
                    ["All"] + list(logs_df["status"].unique())
                )
            
            with filter_col3:
                search_term = st.text_input(
                    "Search Prediction"
                )

            filtered_logs = logs_df.copy()

            if selected_model_filter!= "All":
                filtered_logs = filtered_logs[
                    filtered_logs["model"] == selected_model_filter
                ]
            
            if selected_status_filter!= "All":
                filtered_logs = filtered_logs[
                    filtered_logs["status"] == selected_status_filter
                ]
            
            if search_term:
                filtered_logs = filtered_logs[
                    filtered_logs["text"].str.contains(search_term, case = False, na =False)
                ]
            
            #Log Metrics
            st.markdown("### 📈 Log Metrics")

            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns([1,1,1,2])

            with metric_col1:

                metric_card(
                    "Total Logs",
                    dashboard_metrics["inference"]["inference_metrics"]["total_predictions"]
                )

            with metric_col2:

                avg_lat = filtered_logs['latency'].mean()
                metric_card(
                    "Avg Latency",
                    f"{avg_lat:.3f}s" if pd.notna(avg_lat) else "0.000s"
                )

            with metric_col3:

                error_count = len(
                    filtered_logs[
                        filtered_logs["status"] != "success"
                    ]
                )

                metric_card(
                    "Errors",
                    error_count
                )

            with metric_col4:

                most_used_model = (
                    filtered_logs["model"].mode().iloc[0]
                    if not filtered_logs.empty
                    else "N/A"
                )

                metric_card(
                    "Most Used Model",
                    most_used_model
                )

            # Centerpiece - Main Logs
            st.markdown("### Inference Logs")

            if filtered_logs.empty:
                st.warning("No logs match the selected filters.")
            else:
                st.dataframe(
                    filtered_logs,
                    width="stretch",
                    height=400
                )

            # recent failures section
            failure_logs = filtered_logs[
                filtered_logs["status"] == "failure"
            ]

            st.markdown("### Recent Failures")
            if failure_logs.empty:
                st.success("No recent failures detected.")
            else:
                st.dataframe(
                    failure_logs, width="stretch"
                )

            #System Events
            st.markdown("### System Events")
            system_events = [
                "Model registry initialized",
                "Database connection established",
                "Inference service operational",
                "Analytics pipeline refreshed"
            ]

            for event in system_events:
                st.info(event)

    with obs_tab4:
        hero_header("System Health Monitoring")
        hero_subtext("Infrastructure status and operational monitoring")

        db_status = dashboard_metrics["health"]["db_health"]["database"]

        c1, c2, c3 = st.columns(3)
        
        with c1:
            if dashboard_metrics["health"]["models_count"]==0:
                model_count_info = f"No Active Models"
            elif dashboard_metrics["health"]["models_count"]==1:
                model_count_info = f"{dashboard_metrics["health"]["models_count"]} Active Model"
            else:
                model_count_info = f"{dashboard_metrics["health"]["models_count"]} Active Models"

            metric_card("Model Availability", model_count_info)
        
        with c2:
            metric_card(
                "Uptime", f"{dashboard_metrics["health"]["uptime"]}"
            )

        with c3:
            metric_card(
                "CPU Usage",
                f"{dashboard_metrics["health"]["cpu_usage"][0]:.2f}%"
            )
        
        left_col, right_col = st.columns(2)
        with left_col:
            if db_status == "connected":
                status_card("Database", "Connected", "green")
            else:
                status_card("Database", "Connection issue", "red")

        with right_col:
            with st.container(border=True):
                st.write("CPU Utilization")
                st.progress(dashboard_metrics["health"]["cpu_usage"][0] / 100)
                st.caption(f"{dashboard_metrics["health"]["cpu_usage"][0]}% utilization")

        #Health table
        health_table =pd.DataFrame(
            {
                "Components":[
                    "Database", "Inference Models", "CPU", "System Uptime"
                ],
                "Status":[
                    db_status.capitalize(),
                    f"{dashboard_metrics["health"]["models_count"]} Model Avalilable"
                    if dashboard_metrics["health"]["models_count"] 
                    else "No models available",
                    f"{dashboard_metrics["health"]["cpu_usage"][0]}%",
                    dashboard_metrics["health"]["uptime"]
                ]
            }
        )

        st.subheader("Operational Summary")
        st.dataframe(
            health_table, width="stretch"
        )

        st.success("All critical services are operational.")

#set the sidebar
with st.sidebar:
    st.markdown("✨ AI Sentiment System")
    st.caption("Real-time AI Sentiment Intelligence Platform")

    st.divider()

    page = st.radio(
        "Platform",
        [
            "Overview",
            "Live Inference",
            "Batch Intelligence",
            "AI Intelligence",
            "Observability"
        ],
        index=0)

#--------------------------------------#
#-------------Page Routing-------------#
if page=="Overview":
    render_overview()

elif page=="Live Inference":
    render_live_inference()

elif page=="Batch Intelligence":
    render_batch_intelligence()

elif page=="AI Intelligence":
    render_ai_intelligence()

elif page=="Observability":
    render_observability()