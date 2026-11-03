import os
from supabase import create_client, Client

# ⚠️ BURAYI KENDİ BİLGİLERİNLE DOLDUR ⚠️
SUPABASE_URL = "https://gisoxromyilwnxcizbmg.supabase.co"
SUPABASE_KEY = "sb_publishable_2hXuC5AQEWARh4vvwhKfpg_NnjKUxGh"

# Supabase istemcisini başlat
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def init_db():
    """Tablolar zaten Supabase üzerinde oluşturuldu."""
    print("Supabase veritabanına bağlanıldı.")
    pass