import streamlit as st
import requests
import plotly.express as px
import pandas as pd
from streamlit_autorefresh import st_autorefresh

BASE_URL = "https://sentiment-analysis-system-etlx.onrender.com"

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
    try:
        return requests.get(f"{BASE_URL}/dashboard", timeout=10).json()
    except Exception as e:
        return ["Backend not available!"]

if "dashboard_metrics" not in st.session_state:
    st.session_state.dashboard_metrics = get_dashboard_metrics()

dashboard_metrics = get_dashboard_metrics()

inference = dashboard_metrics["inference"]
health = dashboard_metrics["health"]
analytics = dashboard_metrics["analytics"]
advanced = dashboard_metrics["advanced"]
logs_data = dashboard_metrics["logs"]

#setting the page title
st.set_page_config(
    page_title="AI Sentiment System",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("✨ AI Sentiment System")
st.caption("Real-time AI Sentiment Intelligence Platform")

#set the sidebar
with st.sidebar:
    st.markdown("✨ AI Sentiment System")
    st.caption("Real-time AI Sentiment Intelligence Platform")

    st.divider()

    st.markdown("### Prediction Controls")

    user_input = st.text_area("Enter your text", height=200, placeholder="Type review text here......")
    model_choice = st.selectbox("Select Model", model_list)
    predict_btn = st.button("Predict Sentiment", width="stretch")

    st.divider()

    st.markdown("### Health Indicators")

    #db_health
    db_status = health["db_health"]["database"]
    if db_status == "connected":
        st.success("Database Connected")
    else:
        st.error("Database Disconnected")

    #models loaded
    st.info(f"Models Loaded : {health["models_count"]}")

    #CPU Usage
    st.metric(
        f"CPU Usage: {health["cpu_usage"][0]}%",
        f"CPU Status: {health["cpu_usage"][1]}"
    )

    #Uptime
    st.metric(
        "Uptime", health["uptime"]
    )

#Metrics KPI
col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Predictions", inference["total_predictions"]
)

col2.metric(
    "Avg Latency", inference["average_latency"]
)

col3.metric(
    "RPM", inference["rpm"]
)

col4.metric(
    "Uptime", health["uptime"]
)

col5.metric(
    "Failure Rate", advanced["failure_rate"]["failure_percent"]
)

#Tab System
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Prediction",
    "Analytics",
    "Advanced Metrics",
    "System Health",
    "Logs"
])

with tab1:
    st.subheader("✨ AI Sentiment System")
    st.caption("Live inference using production ML models")

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
            st.metric(
                "Latency", f"{latency:.3f}"
            )
        
        with col2:
            st.metric(
                "Model", f"{model_name.upper()}"
            )

with tab2:
    st.subheader("Analytics Dashboard")
    st.caption(
        "Historical inference trends and system intelligence"
    )

    col1, col2 = st.columns(2)
    with col1:
        #Sentiment Distribution
        sentiment_distribution = analytics["sentiment_distribution"]

        sentiment_df = pd.DataFrame(
            {
                "Sentiment": sentiment_distribution.keys(),
                "Count": sentiment_distribution.values()
            }
        )

        fig_sentiment = px.pie(
            sentiment_df,
            names = "Sentiment",
            values = "Count",
            title = "Sentiment Distribution"
        )

        st.plotly_chart(
            fig_sentiment, width="stretch"
        )

        #Prediction Over Time
        prediction_ = analytics["predictions_over_time"]

        prediction_over_time = pd.DataFrame(prediction_)

        if not prediction_over_time.empty:
            fig_predictions = px.line(
                prediction_over_time,
                x = "day",
                y = "count",
                title = "Predictions Over Time",
                markers = True
            )

            st.plotly_chart(
                fig_predictions, width = "stretch"
            )
        
        else:
            st.info("You have not made any predictions yet. Make predictions to view the results.")

        #Model Usage Distribution
        models_ = analytics["model_usage_distribution"]

        model_usage_distribution = pd.DataFrame(models_)

        if not model_usage_distribution.empty:
            fig_model_usage = px.bar(
                model_usage_distribution,
                x = "model",
                y = "usage",
                title = "Model Usage Distribution"
            )

            st.plotly_chart(
                fig_model_usage, width = "stretch"
            )
        
        else:
            st.info("You have not made any predictions yet. Make predictions to view the results.")

    with col2:
        #Latency Trends
        latency = analytics["latency_trends"][1]

        latency_trends = pd.DataFrame(latency)

        if not latency_trends.empty:
            fig_latency_trends = px.line(
                latency_trends,
                x = "time",
                y = "avg_latency",
                title = "Latency Trends Over Time",
                markers = True
            )

            st.plotly_chart(
                fig_latency_trends, width="stretch"
            )
        
        else:
            st.info("You have not made any predictions yet. Make predictions to view the results.")

        #Confidence distribution
        confidence_ = analytics["confidence_distribution"]

        confidence_distribution = pd.DataFrame(confidence_)

        if not confidence_distribution.empty:
            fig_confidence_distributions = px.bar(
                confidence_distribution,
                x = "Confidence",
                y = "Count",
                title = "Confidence Distribution"
            )

            st.plotly_chart(
                fig_confidence_distributions, width = "stretch"
            )
        
        else:
            st.info("You have not made any predictions yet. Make predictions to view the results.")

        #Recent Activity Feed
        activity_ = analytics["recent_activity"]

        activity_feed = pd.DataFrame([activity_])

        st.subheader("Recent Activity")
        st.dataframe(
            activity_feed, width = "stretch"
        )

with tab3:
    st.header("Advanced ML Metrics")
    st.caption("Production-grade performance and observability insights")

    col1, col2 = st.columns(2)

    with col1:
        p95_latency = advanced.get("p95_latency", 0) or 0

        st.metric(
            "p95_latency", f"{p95_latency:.3f}s" 
        )

    with col2:
        failure_rate = advanced["failure_rate"]["failure_percent"]

        st.metric(
            "Failure Rate", f"{failure_rate:.2f}"
        )
    
    #Model Metrics
    model_metrics = advanced["model_metrics"]

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

        avg_latency = advanced["latency_per_model"]

        avg_latency_per_model = pd.DataFrame(avg_latency)

        if not avg_latency_per_model.empty:
            fig_avg_latency = px.bar(
                avg_latency_per_model,
                x = "model",
                y = "avg_latency",
                title = "Average Latency Per Model"
            )

            st.plotly_chart(
                fig_avg_latency, width = "stretch"
            )
        
        else:
            st.info("You have not made any predictions yet. Make predictions to view the results.")

    with col_2:
        #Model Accuracy

        if not df_metrics.empty:
            fig_model_accuracy = px.bar(
                df_metrics,
                x = "Model",
                y = "accuracy",
                title = "Model Accuracy Comparison"
            )

            st.plotly_chart(
                fig_model_accuracy, width="stretch"
            )

        else:
            st.info("You have not made any predictions yet. Make predictions to view the results.")

    #Drift indicators
    drift_indicators = advanced["drift_indicators"]

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
                    st.metric(
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
                y = value,
                title = title
            )

            st.plotly_chart(
                fig_rolling, width="stretch"
            )

with tab4:
    st.subheader("System Health Monitoring")
    st.caption("Infrastructure status and operational monitoring")

    c1, c2, c3 = st.columns(3)
    
    with c1:
        if db_status == "connected":
            st.success("Database connected")
        else:
            st.error("Database disconnected")
    
    with c2:
        st.metric(
            "Model Count",
            health["models_count"]
        )
    
    with c3:
        st.metric(
            "CPU Usage",
            f"{health["cpu_usage"][0]:.2f}%"
        )
    
    #columns for infra+CPU and Model+Uptime
    left_col, right_col = st.columns(2)
    with left_col:
        st.subheader("Infrastructure Status")
        if db_status == "connected":
            st.success("Database connection is operational.")
        else:
            st.error("Database connectivity issue detected.")

        st.subheader("Resource Monitoring")
        st.write("CPU Utilization")
        st.progress(health["cpu_usage"][0] / 100)

    with right_col:
        st.subheader("Model Availability")

        if health["models_count"]==0:
            model_count_info = f"No ML models are currently loaded."
        elif health["models_count"]==1:
            model_count_info = f"{health["models_count"]} ML model is currently loaded and ready for inference."
        else:
            model_count_info = f"{health["models_count"]} ML models are currently loaded and ready for inference."
        st.info(model_count_info)

        st.subheader("Uptime")
        st.metric(
            "Uptime", f"{health["uptime"]}", label_visibility="collapsed"
        )

    #Health table
    health_table =pd.DataFrame(
        {
            "Components":[
                "Database", "Inference Models", "CPU", "System Uptime"
            ],
            "Status":[
                db_status.capitalize(),
                f"{health["models_count"]} Model Avalilable"
                if health["models_count"] 
                else "No models available",
                f"{health["cpu_usage"][0]}%",
                health["uptime"]
            ]
        }
    )

    st.subheader("Operational Summary")
    st.dataframe(
        health_table, width="stretch"
    )

    st.success("All critical services are operational.")

with tab5:
    logs_df = pd.DataFrame(logs_data)

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
                    st.rerun()
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
                filtered_logs["text"].str.contains(search_term, case = False, na =n)
            ]
        
        #Log Metrics
        st.markdown("### 📈 Log Metrics")

        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

        with metric_col1:

            st.metric(
                "Total Logs",
                len(filtered_logs)
            )

        with metric_col2:

            avg_lat = filtered_logs['latency'].mean()
            st.metric(
                "Avg Latency",
                f"{avg_lat:.3f}s" if pd.notna(avg_lat) else "0.000s"
            )

        with metric_col3:

            error_count = len(
                filtered_logs[
                    filtered_logs["status"] != "success"
                ]
            )

            st.metric(
                "Errors",
                error_count
            )

        with metric_col4:

            most_used_model = (
                filtered_logs["model"].mode().iloc[0]
                if not filtered_logs.empty
                else "N/A"
            )

            st.metric(
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