# 🔐 Password Intelligence Engine (CipherSense)

AI-powered password analysis and generation system using NLP, Streamlit, and Docker.

---

## 🚀 Features

- Password preprocessing and cleaning  
- Keyword extraction using YAKE  
- Password generation  
- Evaluation metrics  
- Streamlit dashboard  
- Docker support  

---

## ▶️ Run Locally

py -m venv .venv  
.venv\Scripts\activate  
pip install -r requirements.txt  
cd src  
py -m streamlit run app.py  

---

## 🐳 Run with Docker

docker build -t password-estimator .  
docker run -p 8501:8501 password-estimator  

Open: http://localhost:8501