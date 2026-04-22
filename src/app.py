import streamlit as st
import pandas as pd
import subprocess
from pathlib import Path
import json

st.set_page_config(page_title="Intelligent Password Estimator", layout="wide")

st.title("🔐 Intelligent Password Estimator")
st.write("Run AI-powered password analysis and view results.")

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------
# Upload Section
# -----------------------------
st.header("📤 Upload Dataset")
uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.success("Dataset uploaded successfully!")
    st.subheader("📊 Preview")
    st.dataframe(df.head())

    # Save uploaded file
    input_path = RAW_DIR / "uploaded_dataset.csv"
    df.to_csv(input_path, index=False)

    # Run pipeline
    if st.button("🚀 Run Full Analysis"):
        st.info("Running pipeline... please wait ⏳")

        result = subprocess.run(
            ["py", "main.py", "--raw-input", str(input_path.resolve())],
            cwd=str(BASE_DIR / "src"),
            capture_output=True,
            text=True
        )

        st.subheader("📜 Logs")
        st.text_area("Pipeline Output", result.stdout, height=300)

        if result.returncode == 0:
            st.success("✅ Analysis completed!")
        else:
            st.error("❌ Error occurred")
            st.text(result.stderr)

# -----------------------------
# Results Section
# -----------------------------
st.header("📂 Results")

# Generated Passwords
generated_file = PROCESSED_DIR / "generated_passwords.csv"
if generated_file.exists():
    st.subheader("🔑 Generated Passwords")
    gen_df = pd.read_csv(generated_file)

    st.dataframe(gen_df.head(20))

    st.download_button(
        "⬇ Download Generated Passwords",
        gen_df.to_csv(index=False),
        file_name="generated_passwords.csv"
    )

# Metrics
metrics_file = PROCESSED_DIR / "metrics.json"
if metrics_file.exists():
    st.subheader("📊 Metrics")
    with open(metrics_file) as f:
        metrics = json.load(f)
    st.json(metrics)

# Chart
chart_file = PROCESSED_DIR / "accuracy_lift.png"
if chart_file.exists():
    st.subheader("📈 Accuracy Chart")
    st.image(str(chart_file))

# If nothing exists
if not generated_file.exists():
    st.warning("No results yet. Run analysis first.")