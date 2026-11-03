import base64
import json
import requests
import os
import re

# Anahtarı sadece Render'ın Environment Variable'ından oku
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def analyze_food_image(image_bytes: bytes) -> dict:
    if not GROQ_API_KEY:
        return {"error": "API anahtarı bulunamadı. Lütfen Render'daki Environment Variables ayarlarını kontrol edin."}

    # Görseli base64 formatına çevir
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
                        "text": "Bu bir yemek fotoğrafı. Lütfen aşağıdaki adımları kesinlikle uygula:\n1. Yemeğin adını belirle.\n2. Tabaktaki porsiyonun ne kadar büyük olduğunu tahmin et (küçük, orta, büyük).\n3. Bu porsiyon boyutuna göre GERÇEKÇİ bir kalori ve makro tahmini yap. Sakın ortalama bir değer verme, fotoğraftaki tabağın boyutunu ve yemek miktarını dikkate al.\nSadece şu JSON formatında cevap ver: {\"food_name\": \"yemek adı\", \"portion_size\": \"küçük/orta/büyük\", \"calories\": 250, \"protein_g\": 10, \"carbs_g\": 30, \"fat_g\": 15}"
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
        # reasoning_effort SATIRINI SİLDİK! Çünkü Groq'ta hata veriyor.
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        message = result["choices"][0]["message"]
        
        # Cevabı önce content'ten, yoksa reasoning'den al (Qwen modeli düşünme modunda cevabı buraya yazıyor)
        content = message.get("content") or message.get("reasoning") or ""
        print(f"Groq'tan gelen ham cevap: {content}") # Render loglarında görmek için
        
        # JSON'u bulmak için regex kullan (metin içinde JSON varsa çıkarır)
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            content = json_match.group(0)
        else:
            return {"error": f"Model JSON döndürmedi. Gelen cevap: {content[:200]}"}
        
        data = json.loads(content)
        
        # Eksik alanları varsayılan değerlerle doldur
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
