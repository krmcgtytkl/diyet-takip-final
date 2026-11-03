import base64
import json
import requests
import os

# Önce Render'ın Environment Variable'ından oku, yoksa Streamlit Secrets'a bak
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    try:
        import streamlit as st
        GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    except:
        GROQ_API_KEY = ""

def analyze_food_image(image_bytes: bytes) -> dict:
    if not GROQ_API_KEY:
        return {"error": "API anahtarı bulunamadı. Render Environment Variables kısmını kontrol edin."}

    b64_image = base64.b64encode(image_bytes).decode("utf-8")
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "qwen/qwen3.8-27b",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Bu bir yemek fotoğrafı. Yemeğin adını, porsiyonunu ve tahmini kalori/makrolarını JSON formatında ver."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}}
                ]
            }
        ],
        "max_tokens": 300,
        "temperature": 0.2
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        content = content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except Exception as e:
        return {"error": f"Analiz hatası: {e}"}
