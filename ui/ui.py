import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

BASE_URL = "https://sentiment-analysis-system-etlx.onrender.com"

st.set_page_config(layout="wide")
st.title("Text Classification Model")
l_col,c_col,r_col=st.columns([1.5,4,1.5])

@st.cache_data(ttl=60)
def get_models():
    try:
        return requests.get(f"{BASE_URL}/models", timeout=5).json()
    except:
        return ["Backend not available!"]

model_list=get_models()

with c_col:
    user_input=st.text_area("Enter your text")
    model_choice=st.selectbox("Select Model", model_list)

    if st.button("Predict"):
        if user_input.strip()=="":
            st.write("Please enter some text!!")
        
        else:
            response=requests.post(
                f"{BASE_URL}/predict",
                json={"text":user_input, "model":model_choice}
            )

            if response.status_code != 200:
                st.error(f"Backend failed (Status {response.status_code})")
                st.text(response.text)
                st.stop()

            try:
                result = response.json()
            except:
                st.error("Invalid response from backend")
                st.text(response.text)
                st.write("Raw response:", response.text)
                st.stop()

            label_map = {
                0: "Negative",
                1: "Neutral",
                2: "Positive"
            }

            if "prediction" in result:
                st.success(f"Prediction: {label_map[result['prediction']]}")

                score=result.get("confidence_scores", [])

                st.subheader("Confidence Scores")

                line = "    ".join(
                    [f"{label_map[i]}: {round(s*100, 2)}%" for i, s in enumerate(score)]
                )
                st.write(line)

                df=pd.DataFrame({
                    "Sentiment":["Negative", "Neutral", "Positive"],
                    "Score":score
                })

                st.bar_chart(df.set_index("Sentiment"), width="stretch")
            
            else:
                st.error(f"Backend Error: {result['error']}")

with l_col:
    st.subheader("Logs")

    try:
        response=requests.get(f"{BASE_URL}/logs")
        logs=response.json()

        df_logs=pd.DataFrame(logs)

        if len(df_logs)>0 and "prediction" in df_logs.columns:
            df_logs["prediction"] = df_logs["prediction"]
            st.dataframe(df_logs)
        else:
            "No logs yet!"
    
    except:
        st.info("No logs yet!")

    #---------------------------#

    st.subheader("Overall Sentiment Trend")
    try:
        response = requests.get(f"{BASE_URL}/analytics")

        if response.status_code == 200:
            avg = response.json()

            for k, v in avg.items():
                st.write(f"{k}: {round(100*v,2)}%")

            df_avg = pd.DataFrame({
                "Sentiment": ["Negative", "Neutral", "Positive"],
                "Score": [avg["Negative"], avg["Neutral"], avg["Positive"]]
            })

            st.bar_chart(df_avg.set_index("Sentiment"), width="stretch")

        else:
            st.error("Backend error")

    except:
        st.warning("Analytics not available yet")

with r_col:
    st.subheader("Prediction Distribution")

    response = requests.get(f"{BASE_URL}/count_predictions")
    preds=response.json()

    if len(preds)==0:
        st.info("No predictions yet!")
    else:
        counts=pd.Series(preds).value_counts(normalize=True)

        for k, v in counts.items():
            st.write(f"{k} = {round(100*v, 2)}%")
        
        plt.style.use("dark_background")

        fig, ax = plt.subplots()
        counts.plot.pie(
            autopct='%1.1f%%',
            colors=["#ff4b4b", "#ffaa00", "#00cc96"],
            ax=ax
        )

        ax.set_ylabel("")
        fig.patch.set_alpha(0)

        st.pyplot(fig)

        #Average Latency
        st.subheader("Average Latency Per Model")

        response = requests.get(f"{BASE_URL}/avg_latency")
        avg_lat = response.json()

        df=pd.DataFrame(avg_lat)
        st.bar_chart(df[["model", "avg_latency"]].set_index("model"))