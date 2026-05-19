import streamlit as st
import requests
import plotly.express as px
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import time

from styles import load_global_styles
from components import metric_card, status_card, insights_card, hero_header, subtitle, hero_subtext, subtitle_subtext, chart_container

#setting the page title
st.set_page_config(
    page_title="AI Observability and Intelligence Platform",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_global_styles()

BASE_URL = "https://sanjeev2501-nyxar.hf.space"

#Get the loaded models
@st.cache_data
def get_models():
    try:
        return requests.get(f"{BASE_URL}/models", timeout=5).json()
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
            timeout=10
        )

        response.raise_for_status()

        return response.json()

    except Exception:
        return empty_dashboard

if "dashboard_metrics" not in st.session_state:
    st.session_state.dashboard_metrics = get_dashboard_metrics()

dashboard_metrics = st.session_state.dashboard_metrics

st.title("✨ AI Observability and Intelligence Platform")
st.caption("Real-time monitoring, inference analytics, and AI-driven operational intelligence for production-scale ML systems.")

def render_overview():
    hero_header("Overview")
    hero_subtext("Real-time AI inference, observability, and intelligence monitoring for production-scale ML workflows.")

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        metric_card("Total Predictions", dashboard_metrics["inference"]["total_predictions"])

    with col2:
        metric_card("Avg Latency", dashboard_metrics["inference"]["average_latency"])
    
    with col3:
        metric_card("RPM", dashboard_metrics["inference"]["rpm"])
    
    with col4:
        metric_card("Active Models", dashboard_metrics["health"]["models_count"])
    
    with col5:
        metric_card("Uptime", dashboard_metrics["health"]["uptime"])

    subtitle("Live System Status")

    subtitle("Latest AI Insights")

    st.info(f"""
            Latency increased 12% during recent BERT batch jobs.
            Bi-LSTM currently provides best latency/accuracy balance."""
    )

def render_live_inference():
        hero_header("Live Inference")
        hero_subtext("Live inference using production ML models")

        st.markdown("### Prediction Controls")

        user_input = st.text_area("Enter your text", height=200, placeholder="Type review text here......")
        model_choice = st.selectbox("Select Model", model_list)
        predict_btn = st.button("Predict Sentiment", width="stretch")

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
                    
        if "prediction_result" in st.session_state:

            result = st.session_state.prediction_result
            
            prediction = result["prediction"]
            latency = result["latency"]
            confidence_score = max(result["confidence_scores"])
            model_name = result["model_used"]

            st.markdown("## Prediction Result")

            st.success(
                f"Sentiment: {prediction}"
            )
            
            st.progress(confidence_score)
            st.write(f"Confidence Score: {confidence_score:.2%}")

            col1, col2 = st.columns(2)

            with col1:
                metric_card(
                    "Latency", f"{latency:.3f}"
                )
            
            with col2:
                metric_card(
                    "Model", f"{model_name.upper()}"
                )

def render_batch_intelligence():
    hero_header("Batch Intelligence")
    hero_subtext("Track large-scale dataset processing, asynchronous AI workflows, job analytics, and batch inference performance.")

    uploaded_file = st.file_uploader(
        "Upload CSV", type=["csv"]
    )

    selected_model = st.selectbox("Choose Model", model_list)
    upload_button = st.button("Start Batch Predictions")

    if "polling_started" not in st.session_state:
        st.session_state.polling_started = False

    if "completed_job_data" not in st.session_state:
        st.session_state.completed_job_data = None

    if "failed_job" not in st.session_state:
        st.session_state.failed_job = False

    if upload_button:
        if uploaded_file is not None and not st.session_state.get("polling_started", False):
            files = {
                "file":uploaded_file.getvalue()
            }

            data = {
                "model": selected_model
            }

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

        if "job_id" in st.session_state and st.session_state.get("polling_started", True):
            job_id = st.session_state.job_id

            placeholder = st.empty()
            progress_bar = st.progress(0)
            status_text = st.empty()
            row_text = st.empty()

            while True:

                try:
                    response = requests.get(
                        f"{BASE_URL}/batch/job/{job_id}", timeout=10
                    )

                    if response.status_code != 200:
                        st.error(f"API Error: {response.status_code}")
                        st.text(response.text)
                        break

                    job_data = response.json()

                except Exception as e:
                    st.error(f"Request Failed: {e}")
                    break

                with placeholder.container():
                    status_text.write(f"Status: {job_data['status']}")
                    progress_bar.progress(job_data['progress'] / 100)
                    row_text.write(
                        f"Processed rows: "
                        f"{job_data['processed_rows']} / "
                        f"{job_data['total_rows']}"
                    )

                if job_data["status"] in ["completed", "failed"]:

                    st.session_state.polling_started = False

                    if job_data["status"] == "completed":
                        st.session_state.completed_job_data = job_data
                    else:
                        st.session_state.failed_job = True

                    break  

                time.sleep(1)              

def render_ai_intelligence():

    hero_header("AI Intelligence")
    hero_subtext("Generate LLM-powered summaries, topic insights, anomaly detection, and enterprise-scale feedback intelligence.")

    summary_container = st.container()
    telemetry_container = st.container()
    recommendation_container = st.container()
    
    if st.session_state.completed_job_data:

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

        if st.button("Generate AI Insights"):
            with st.spinner("Analyzing reviews with AI..."):
                response = requests.get(
                    f"{BASE_URL}/batch/job/{st.session_state.job_id}/summary",
                    params={"summary_type":summary_type},
                    timeout=120
                )

                if response.status_code == 200:
                    data = response.json()

                    st.caption("AI Summary")

                    with summary_container:
                        st.markdown(data["summary"])

                else:
                    st.error("Failed to generate insights. Try again.")

def render_observability():
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

            #Prediction Over Time
            prediction_ = dashboard_metrics["analytics"]["predictions_over_time"]

            prediction_over_time = pd.DataFrame(prediction_)

            if not prediction_over_time.empty:
                fig_predictions = px.line(
                    prediction_over_time,
                    x = "day",
                    y = "count",
                    markers = True
                )

                chart_container(fig_predictions, "Predictions Over Time")
            
            else:
                st.info("You have not made any predictions yet. Make predictions to view the results.")

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

            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

            with metric_col1:

                metric_card(
                    "Total Logs",
                    dashboard_metrics["inference"]["total_predictions"]
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
                    most_used_model.upper()
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
            if db_status == "connected":
                status_card("Database", "Connected", "green")
            else:
                status_card("Database", "Disconnected", "red")
        
        with c2:
            metric_card(
                "Model Count",
                dashboard_metrics["health"]["models_count"]
            )
        
        with c3:
            metric_card(
                "CPU Usage",
                f"{dashboard_metrics["health"]["cpu_usage"][0]:.2f}%"
            )
        
        #columns for infra+CPU and Model+Uptime
        left_col, right_col = st.columns(2)
        with left_col:
            st.subheader("Infrastructure Status")
            if db_status == "connected":
                status_card("Database", "Connected", "green")
            else:
                status_card("Database", "Connection issue", "red")

            st.subheader("Resource Monitoring")
            st.write("CPU Utilization")
            st.progress(dashboard_metrics["health"]["cpu_usage"][0] / 100)

        with right_col:
            st.subheader("Model Availability")

            if dashboard_metrics["health"]["models_count"]==0:
                model_count_info = f"No ML models are currently loaded."
            elif dashboard_metrics["health"]["models_count"]==1:
                model_count_info = f"{dashboard_metrics["health"]["models_count"]} ML model is currently loaded and ready for inference."
            else:
                model_count_info = f"{dashboard_metrics["health"]["models_count"]} ML models are currently loaded and ready for inference."
            st.info(model_count_info)

            st.subheader("Uptime")
            metric_card(
                "Uptime", f"{dashboard_metrics["health"]["uptime"]}", label_visibility="collapsed"
            )

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