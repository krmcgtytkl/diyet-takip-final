import base64
import json
import requests
import os
import re

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def analyze_food_image(image_bytes: bytes) -> dict:
    """Yemek fotoğrafını Groq API ile analiz eder, kalori ve makro tahmini döndürür."""
    if not GROQ_API_KEY:
        return {"error": "API anahtarı bulunamadı."}

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
                    {
                        "type": "text", 
                        "text": "Bu bir yemek fotoğrafı. Sadece şu JSON formatında cevap ver, başka hiçbir şey yazma: {\"food_name\": \"yemek adı\", \"calories\": 250, \"protein_g\": 10, \"carbs_g\": 30, \"fat_g\": 15}"
                    },
                    {
                        "type": "image_url", 
                        "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}
                    }
                ]
            }
        ],
        "max_tokens": 300,
        "temperature": 0.1
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        message = result["choices"][0]["message"]
        content = message.get("content") or message.get("reasoning") or ""
        print(f"Groq'tan gelen ham cevap: {content}")
        
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            content = json_match.group(0)
        else:
            return {"error": f"Model JSON döndürmedi. Gelen: {content[:200]}"}
        
        data = json.loads(content)
        
        return {
            "food_name": data.get("food_name", "Bilinmeyen Yemek"),
            "calories": data.get("calories", 0),
            "protein_g": data.get("protein_g", 0),
            "carbs_g": data.get("carbs_g", 0),
            "fat_g": data.get("fat_g", 0)
        }
        
    except json.JSONDecodeError as e:
        return {"error": f"JSON ayrıştırma hatası. Gelen: {content[:200]}"}
    except Exception as e:
        return {"error": f"Analiz hatası: {e}"}


def get_food_data_by_name(food_name: str) -> dict:
    """Yemek adını Groq API'ye göndererek kalori ve makro değerlerini tahmin eder."""
    if not GROQ_API_KEY:
        return {"error": "API anahtarı bulunamadı."}

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
                "content": f"'{food_name}' yemeği için 1 porsiyonun ortalama kalori, protein, karbonhidrat ve yağ değerlerini tahmin et. Sadece şu JSON formatında cevap ver, başka hiçbir şey yazma: {{\"calories\": 250, \"protein_g\": 10, \"carbs_g\": 30, \"fat_g\": 15}}"
            }
        ],
        "max_tokens": 150,
        "temperature": 0.1
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        message = result["choices"][0]["message"]
        content = message.get("content") or message.get("reasoning") or ""
        print(f"Groq'tan gelen ham cevap (isimle): {content}")
        
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            content = json_match.group(0)
        else:
            return {"error": f"Model JSON döndürmedi. Gelen: {content[:200]}"}
        
        data = json.loads(content)
        return {
            "calories": float(data.get("calories", 0)),
            "protein_g": float(data.get("protein_g", 0)),
            "carbs_g": float(data.get("carbs_g", 0)),
            "fat_g": float(data.get("fat_g", 0))
        }
        
    except json.JSONDecodeError as e:
        return {"error": f"JSON ayrıştırma hatası. Gelen: {content[:200]}"}
    except Exception as e:
        return {"error": f"Analiz hatası: {e}"}
