import base64
import json
import requests
import os

# API anahtarını Streamlit Secrets'tan veya ortam değişkeninden güvenli bir şekilde oku
try:
    import streamlit as st
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

def analyze_food_image(image_bytes: bytes) -> dict:
    """Yemek fotoğrafını Groq API ile analiz eder, kalori ve makro tahmini döndürür."""
    if not GROQ_API_KEY:
        return {"error": "API anahtarı bulunamadı. Lütfen Streamlit Secrets ayarlarını kontrol edin."}

    # Görseli base64 formatına çevir
    b64_image = base64.b64encode(image_bytes).decode("utf-8")
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "qwen/qwen3.8-27b",  # Groq'un güncel görsel modeli
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Bu bir yemek fotoğrafı. Lütfen şu adımları izle: 1. Yemeğin adını belirle. 2. Tabaktaki porsiyonun ne kadar büyük olduğunu tahmin et (küçük, orta, büyük). 3. Bu bilgilere göre gerçekçi bir kalori ve makro tahmini yap. Sadece şu JSON formatında cevap ver: {\"food_name\": \"yemek adı\", \"portion_size\": \"küçük/orta/büyük\", \"calories\": 250, \"protein_g\": 10, \"carbs_g\": 30, \"fat_g\": 15}"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{b64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300,
        "temperature": 0.2
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        # JSON formatını temizle
        content = content.replace("```json", "").replace("```", "").strip()
        data = json.loads(content)
        return data
    except Exception as e:
        return {"error": f"Analiz hatası: {e}"}