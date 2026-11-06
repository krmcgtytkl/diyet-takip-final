import hashlib
from database import supabase

def _hash(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def register(username: str, password: str, display_name: str = ""):
    username = username.strip().lower()
    if not username or not password:
        return False, "Kullanıcı adı ve şifre boş olamaz."
    if len(password) < 4:
        return False, "Şifre en az 4 karakter olmalı."
    
    try:
        # Kullanıcı adı zaten var mı kontrol et
        existing = supabase.table("users").select("id").eq("username", username).execute()
        if existing.data:
            return False, "Bu kullanıcı adı zaten alınmış."
        
        # Yeni kullanıcı ekle
        response = supabase.table("users").insert({
            "username": username,
            "password_hash": _hash(password),
            "display_name": display_name or username
        }).execute()
        
        if response.data:
            return True, "Kayıt başarılı! Şimdi giriş yapabilirsin."
        else:
            return False, "Kayıt sırasında bir hata oluştu."
    except Exception as e:
        return False, f"Hata: {e}"

def login(username: str, password: str):
    username = username.strip().lower()
    try:
        response = supabase.table("users").select("*").eq("username", username).eq("password_hash", _hash(password)).execute()
        if response.data:
            user = response.data[0]
            # Kullanıcı aktif mi kontrol et (varsayılan True'dur, eğer False ise giriş yapamaz)
            if user.get("is_active") is False:
                return None  # Banlanmış kullanıcı giriş yapamaz
            return user
        return None
    except Exception as e:
        print(f"Giriş hatası: {e}")
        return None

def update_profile(user_id: int, **fields):
    if not fields:
        return
    try:
        supabase.table("users").update(fields).eq("id", user_id).execute()
    except Exception as e:
        print(f"Profil güncelleme hatası: {e}")
