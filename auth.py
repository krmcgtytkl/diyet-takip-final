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
            return response.data[0]
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

def update_credentials(user_id, new_username=None, new_password=None):
    """Kullanıcının adını ve/veya şifresini günceller."""
    updates = {}
    if new_username and new_username.strip():
        updates["username"] = new_username.strip().lower()
    if new_password and new_password.strip():
        updates["password_hash"] = _hash(new_password)
        
    if not updates:
        return False, "Değiştirilecek bir bilgi girilmedi."
        
    try:
        # Kullanıcı adı başkası tarafından alınmış mı kontrol et
        if "username" in updates:
            existing = supabase.table("users").select("id").eq("username", updates["username"]).execute()
            if existing.data and existing.data[0]["id"] != user_id:
                return False, "Bu kullanıcı adı zaten alınmış."
        
        supabase.table("users").update(updates).eq("id", user_id).execute()
        return True, "Bilgileriniz başarıyla güncellendi."
    except Exception as e:
        return False, f"Güncelleme hatası: {e}"

def login_with_username(username):
    """Çerezden gelen kullanıcı adı ile giriş yapar (şifre kontrolü olmadan)."""
    try:
        response = supabase.table("users").select("*").eq("username", username).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Otomatik giriş hatası: {e}")
        return None
