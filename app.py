import streamlit as st
from datetime import date
import auth
import meals as meal_mod
import random
import datetime
from database import init_db
from calories import calorie_target
from foods_data import FOOD_DATABASE
import streamlit.components.v1 as components
import os

# --- SAYFA AYARLARI VE HAFIZA ---
st.set_page_config(page_title="KCTFIT", page_icon="🥗", layout="wide")

# Session state başlangıç değerleri
if "user" not in st.session_state:
    st.session_state.user = None
if "show_profile" not in st.session_state:
    st.session_state.show_profile = False
if "karsilama_mesaji" not in st.session_state:
    st.session_state.karsilama_mesaji = None

# --- iOS TARZI ÖZEL CSS ---
st.markdown("""
<style>
    /* Genel font ve arka plan */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Ana butonlar (iOS mavi) */
    .stButton>button {
        background-color: #007AFF;
        color: white;
        border-radius: 12px;
        border: none;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        background-color: #0056b3;
        transform: scale(1.02);
    }
    
    /* Giriş kutuları (input) */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>select {
        border-radius: 10px;
        border: 1px solid #C7C7CC;
        background-color: #FFFFFF !important;
        color: #000000 !important;
        padding: 10px;
    }
    
    /* Metrik kartları (Bembeyaz iOS kart görünümü) */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF !important;
        border-radius: 16px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border: 1px solid #E5E5EA;
    }
    
    /* Kart içindeki yazılar koyu gri */
    div[data-testid="stMetricLabel"] {
        color: #8E8E93 !important; 
        font-weight: 600;
    }
    
    /* Kart içindeki büyük rakamlar simsiyah */
    div[data-testid="stMetricValue"] {
        color: #000000 !important; 
        font-weight: 700;
        font-size: 1.4rem !important;
    }
    
    /* --- HAP (PILL) MENÜ TASARIMI --- */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #E5E5EA; 
        border-radius: 50px;       
        padding: 5px;              
        gap: 5px;                  
        display: flex;
        flex-wrap: nowrap;         
        overflow-x: auto;          
        scrollbar-width: none;     
    }
    
    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {
        display: none;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 50px;
        color: #8E8E93;
        padding: 8px 16px;
        font-weight: 600;
        border: none;
        white-space: nowrap;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #007AFF;
    }

    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important; 
        color: #007AFF !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1); 
    }
    
    .stTabs [data-baseweb="tab-highlight"] {
        display: none;
    }

    /* --- ÖZEL METRİK KART RENKLERİ --- */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) div[data-testid="stMetric"] {
        background-color: #FFF3E0 !important; border: 1px solid #FFCC80 !important;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) div[data-testid="stMetricValue"] { color: #E65100 !important; }

    div[data-testid="stHorizontalBlock"] > div:nth-child(2) div[data-testid="stMetric"] {
        background-color: #E8F5E9 !important; border: 1px solid #A5D6A7 !important;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) div[data-testid="stMetricValue"] { color: #1B5E20 !important; }

    div[data-testid="stHorizontalBlock"] > div:nth-child(3) div[data-testid="stMetric"] {
        background-color: #F3E5F5 !important; border: 1px solid #CE93D8 !important;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(3) div[data-testid="stMetricValue"] { color: #6A1B9A !important; }

    div[data-testid="stHorizontalBlock"] > div:nth-child(4) div[data-testid="stMetric"] {
        background-color: #E3F2FD !important; border: 1px solid #90CAF9 !important;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(4) div[data-testid="stMetricValue"] { color: #0D47A1 !important; }

    /* Mobilde tam ekran görünüm için kenar boşluklarını sıfırla */
    .block-container {
        padding-left: 0rem !important;
        padding-right: 0rem !important;
        padding-top: 2rem !important;
        max-width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)

# Veritabanını her açılışta garanti et
init_db()

# Karşılama Cümleleri
KARSILAMA_CUMLELERI = [
    "Hoş geldin {isim}! Bugün fit olmak için harika bir gün! 💪",
    "Merhaba {isim}! Hedefine bir adım daha yaklaşmaya hazır mısın? 🚀",
    "Selam {isim}! Bugün kendin için ne yapacaksın? 🌟",
    "Hoş geldin {isim}! Sağlıklı yaşam yolculuğun devam ediyor. 🌿",
    "Merhaba {isim}! Bugün de harika işler başaracaksın, eminim! 🔥",
    "Selam {isim}! Kendine iyi bak, çünkü sen bunu hak ediyorsun. 💚",
    "Hoş geldin {isim}! Bugün attığın adımlar yarının güçlü seni olacak. ⭐",
]

# --- YARDIMCI FONKSİYONLAR ---
MOTIVASYON_CUMLELERI = [
    "Bugün kendin için harika bir şey yapıyorsun! 🌟",
    "Küçük adımlar büyük değişimler yaratır. Devam et! 🚀",
    "Sağlıklı yaşam bir yarış değil, bir yolculuktur. Keyfini çıkar! 🌿",
    "Bugünkü çaban, yarınki güçlü senin temelidir. 💪",
    "Kendine inan, çünkü sen bunu başarabilecek güçtesin. 🔥",
    "Her yeni gün, yeniden başlamak için bir fırsattır. ☀️",
    "Vücuduna iyi bak, o senin tek evin. 🏡",
    "İstikrar, mükemmellikten daha önemlidir. Harika gidiyorsun! ✨",
    "Bugün attığın her adım, hedefine bir adım daha yaklaşman demek. 🎯",
    "Kendinle gurur duy, bu yolda ilerliyorsun! 👏"
]

def get_random_motivation():
    return random.choice(MOTIVASYON_CUMLELERI)

def get_combined_foods(user_id):
    foods = {k: v for k, v in FOOD_DATABASE.items()}
    custom = meal_mod.get_custom_foods(user_id)
    for c in custom:
        foods[f"⭐ {c['name']} (Kendi)"] = {"cal": c["calories"], "pro": c["protein"], "carb": c["carbs"], "fat": c["fat"]}
    return foods

def show_login_page():
    st.title("🥗 KCTFIT")
    st.caption("👨‍💻 Geliştirici: **Kerim Çağatay Toklu** | 📱 KCTFIT v1.0")
    st.markdown("### *Sağlıklı yaşam burada başlıyor...*")
    
    tab1, tab2 = st.tabs(["Giriş Yap", "Kayıt Ol"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Kullanıcı adı")
            password = st.text_input("Şifre", type="password")
            submitted = st.form_submit_button("Giriş Yap")
            
        if submitted:
            user = auth.login(username, password)
            if user:
                st.session_state.user = dict(user)
                karsilama = random.choice(KARSILAMA_CUMLELERI).format(isim=user['display_name'])
                st.session_state.karsilama_mesaji = karsilama
                st.rerun()
            else:
                st.error("Kullanıcı adı veya şifre hatalı.")
                
    with tab2:
        with st.form("register_form"):
            new_username = st.text_input("Kullanıcı adı (benzersiz)")
            new_display = st.text_input("Görünen ad")
            new_password = st.text_input("Şifre (en az 4 karakter)", type="password")
            new_password2 = st.text_input("Şifre (tekrar)", type="password")
            submitted = st.form_submit_button("Kayıt Ol")
            
        if submitted:
            if new_password != new_password2:
                st.error("Şifreler eşleşmiyor.")
            else:
                ok, msg = auth.register(new_username, new_password, new_display)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)

def show_profile_setup(user):
    st.title("👤 Profilini Düzenle")
    st.caption("Kalori hedefini ve kişisel bilgilerini buradan güncelleyebilirsin.")
    
    with st.form("profile_form"):
        yeni_isim = st.text_input("Görünen Adınız", value=user['display_name'])
        st.divider()
        
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Yaş", 10, 100, int(user["age"] or 30))
            height = st.number_input("Boy (cm)", 100, 230, int(user["height_cm"] or 170))
        with col2:
            gender = st.selectbox("Cinsiyet", ["kadın", "erkek"], index=0 if (user["gender"] or "kadın") == "kadın" else 1)
            weight = st.number_input("Kilo (kg)", 30.0, 250.0, float(user["weight_kg"] or 70.0), 0.5)
            
        activity = st.selectbox("Günlük hareket seviyesi", ["hareketsiz", "az", "orta", "çok", "aşırı"], index=["hareketsiz", "az", "orta", "çok", "aşırı"].index(user["activity_level"] or "az"))
        goal = st.selectbox("Hedefin", ["kilo ver", "koru", "kilo al"], index=["kilo ver", "koru", "kilo al"].index(user["goal"] or "kilo ver"))
        st.divider()
        st.write("**🔐 Hesap Bilgilerini Değiştir**")
        st.caption("Sadece değiştirmek istediğiniz alanı doldurun, diğerlerini boş bırakın.")
        
        col_user, col_pass = st.columns(2)
        with col_user:
            yeni_kullanici_adi = st.text_input("Yeni Kullanıcı Adı", value="", help="Küçük harf ve rakam kullanın.")
        with col_pass:
            yeni_sifre = st.text_input("Yeni Şifre", type="password", value="", help="En az 4 karakter.")
        submitted = st.form_submit_button("Değişiklikleri Kaydet", type="primary")

    if submitted:
        if yeni_isim.strip() and yeni_isim.strip() != user['display_name']:
            meal_mod.update_display_name(user["id"], yeni_isim.strip())
            st.session_state.user["display_name"] = yeni_isim.strip()
            user["display_name"] = yeni_isim.strip()
            
        target = calorie_target(weight, height, age, gender, activity, goal)
        auth.update_profile(
            user["id"], age=age, gender=gender, height_cm=height, weight_kg=weight,
            activity_level=activity, goal=goal, daily_calorie_target=target,
        )
        st.session_state.user.update({
            "age": age, "gender": gender, "height_cm": height, "weight_kg": weight,
            "activity_level": activity, "goal": goal, "daily_calorie_target": target,
        })
        
        st.session_state.show_profile = False
        st.success(f"Profiliniz başarıyla güncellendi! Günlük hedef: {target} kcal")
        # Kullanıcı adı ve şifre güncellemesi
        if yeni_kullanici_adi or yeni_sifre:
            ok, msg = auth.update_credentials(user["id"], yeni_kullanici_adi, yeni_sifre)
            if ok:
                st.success(msg)
                if yeni_kullanici_adi:
                    st.session_state.user["username"] = yeni_kullanici_adi.strip().lower()
            else:
                st.error(msg)
        st.rerun()

def show_home(user):
    # --- SOL MENÜ (SIDEBAR) ---
    with st.sidebar:
        bas_harfler = "".join([word[0].upper() for word in user['display_name'].split() if word])
        if len(bas_harfler) > 2:
            bas_harfler = bas_harfler[:2]
            
        st.markdown(f"""
        <div style="text-align: center; padding: 15px 0;">
            <div style="width: 70px; height: 70px; background-color: #007AFF; color: white; 
                        border-radius: 50%; display: flex; align-items: center; 
                        justify-content: center; font-size: 28px; font-weight: bold; 
                        margin: 0 auto 10px auto; box-shadow: 0 4px 10px rgba(0,122,255,0.3);">
                {bas_harfler}
            </div>
            <h3 style="margin: 0; color: #000000;">{user['display_name']}</h3>
            <p style="color: #8E8E93; margin: 5px 0 0 0; font-size: 14px;">@{user['username']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        st.metric("🎯 Günlük Kalori Hedefi", f"{user['daily_calorie_target'] or '—'} kcal")
        st.divider()
        
        if st.button("⚙️ Profili Düzenle", use_container_width=True):
            st.session_state.show_profile = True
            st.rerun()
            
        if st.button("🚪 Çıkış Yap", use_container_width=True):
            st.session_state.user = None
            st.rerun()
            
        st.divider()
        with st.expander("🛠️ Hesap ve Veri Yönetimi"):
            st.caption("Dikkat! Buradaki işlemler geri alınamaz.")
            
            with st.expander("🗑️ Veri Temizleme"):
                if st.button("Bugünkü Tüm Verileri Sil", use_container_width=True):
                    meal_mod.clear_today_data(user["id"])
                    st.success("Bugünkü veriler başarıyla silindi!")
                    st.rerun()
                    
                if st.button("TÜM Geçmişi Sil", type="primary", use_container_width=True):
                    meal_mod.clear_all_data(user["id"])
                    st.warning("Tüm geçmiş verileriniz silindi! Hesabınız duruyor.")
                    st.rerun()
                    
            with st.expander("⚠️ Hesabımı Sil"):
                st.warning("Dikkat! Bu işlem geri alınamaz. Tüm verileriniz ve hesabınız kalıcı olarak silinir.")
                onay = st.checkbox("Hesabımı kalıcı olarak silmek istiyorum.")
                
                if st.button("Hesabı Sil", type="primary", use_container_width=True, disabled=not onay):
                    meal_mod.delete_user_account(user["id"])
                    st.session_state.user = None
                    st.success("Hesabınız ve tüm verileriniz silindi.")
                    st.rerun()

    if st.session_state.show_profile:
        show_profile_setup(user)
        return

    # --- ANA SAYFA İÇERİĞİ ---
    st.title("🥗 Bugünkü Özet")
    
    if st.session_state.get("karsilama_mesaji"):
        st.success(st.session_state.karsilama_mesaji)
        del st.session_state.karsilama_mesaji
        
    st.info(f"💡 **Günün Mesajı:** {get_random_motivation()}")

    summary = meal_mod.get_today_summary(user["id"])
    target = user["daily_calorie_target"] or 0
    water_ml = meal_mod.get_today_water(user["id"]) 
    net = summary["total_eaten"] - summary["total_burned"]
    remaining = target - net

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Alınan", f"{int(summary['total_eaten'])} kcal")
    col2.metric("Yakılan", f"{int(summary['total_burned'])} kcal")
    
    if remaining < 700:
        col3.metric("⚠️ Kalan (Açık Azalıyor!)", f"{int(remaining)} kcal", delta="Hedefin altında!", delta_color="inverse")
    else:
        col3.metric("Kalan", f"{int(remaining)} kcal")
        
    col4.metric("Su", f"{water_ml} ml")
    
    if target > 0:
        st.progress(max(0.0, min(1.0, net / target)), text=f"Kalori Hedefi: %{int((net/target)*100)}")

    st.divider()
    
    tab_ai, tab_meal, tab_water, tab_act, tab_weight, tab_measure, tab_chart = st.tabs(
        ["📸 Fotoğraftan Ekle", "🍽️ Yemekler", "💧 Su", "🏃 Aktiviteler", "⚖️ Kilo", "📏 Ölçüler", "📊 Raporlar"]
    )

    # --- 0. FOTOĞRAFTAN EKLE ---
    with tab_ai:
        st.subheader("📸 Yemek Fotoğrafından Kalori Tahmini")
        st.caption("Yemeğin fotoğrafını çek/yükle, yapay zeka tahmini yapsın.")
        
        uploaded = st.file_uploader("Fotoğraf seç", type=["jpg", "jpeg", "png", "webp"], key="food_photo")
        
        if uploaded is not None:
            st.image(uploaded, caption="Yüklenen fotoğraf", width="stretch")
            if st.button("🔍 Analiz Et", type="primary"):
                with st.spinner("Analiz ediliyor..."):
                    try:
                        import food_ai
                        result = food_ai.analyze_food_image(uploaded.getvalue())
                        st.session_state.ai_result = result
                    except Exception as e:
                        st.session_state.ai_result = {"error": f"Hata: {e}"}
        
        result = st.session_state.get("ai_result")
        if result:
            if "error" in result:
                st.error(result["error"])
            else:
                st.success(f"**{result.get('food_name', '?')}**")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Kalori", f"{int(result.get('calories', 0))} kcal")
                c2.metric("Protein", f"{result.get('protein_g', 0)} g")
                c3.metric("Karb.", f"{result.get('carbs_g', 0)} g")
                c4.metric("Yağ", f"{result.get('fat_g', 0)} g")
                
                with st.form("ai_confirm_form"):
                    f_name = st.text_input("Yemek adı", value=result.get("food_name", ""))
                    f_meal = st.selectbox("Öğün", ["Kahvaltı", "Öğle", "Akşam", "Ara Öğün"])
                    cc1, cc2, cc3, cc4 = st.columns(4)
                    f_cal = cc1.number_input("Kalori", 0.0, 5000.0, float(result.get("calories", 0)), 10.0)
                    f_pro = cc2.number_input("Protein (g)", 0.0, 500.0, float(result.get("protein_g", 0)), 1.0)
                    f_carb = cc3.number_input("Karb. (g)", 0.0, 500.0, float(result.get("carbs_g", 0)), 1.0)
                    f_fat = cc4.number_input("Yağ (g)", 0.0, 500.0, float(result.get("fat_g", 0)), 1.0)
                    confirmed = st.form_submit_button("✅ Günlüğe Ekle", type="primary")
                    
                if confirmed:
                    meal_mod.add_meal(user["id"], f_meal, f_name.strip(), f_cal, f_pro, f_carb, f_fat, source="foto")
                    st.session_state.ai_result = None
                    st.success(f"{f_name} günlüğe eklendi!")
                    st.rerun()

    # --- 1. YEMEK EKLE ---
    with tab_meal:
        st.subheader("Bugün Yediklerim")
        if summary["meals"]:
            for m in summary["meals"]:
                c1, c2 = st.columns([5, 1])
                emoji = "🍽️"
                if m['meal_type'] == "Kahvaltı": emoji = "🍳"
                elif m['meal_type'] == "Öğle": emoji = "🍲"
                elif m['meal_type'] == "Akşam": emoji = "🍽️"
                elif m['meal_type'] == "Ara Öğün": emoji = "🍎"
                
                c1.write(f"{emoji} **{m['food_name']}** — {int(m['calories'])} kcal")
                if c2.button("🗑️", key=f"del_meal_{m['id']}"):
                    meal_mod.delete_meal(m["id"])
                    st.rerun()
        else:
            st.info("Henüz yemek eklenmedi.")

        st.divider()
        st.write("**Yeni Yemek Ekle**")
        
        tum_yemekler = get_combined_foods(user["id"])
        yemek_secimi = st.selectbox("Hazır Yemekler", ["Kendim Gireceğim"] + list(tum_yemekler.keys()))
        
        varsayilan_cal, varsayilan_pro, varsayilan_carb, varsayilan_fat = 0.0, 0.0, 0.0, 0.0
        if yemek_secimi != "Kendim Gireceğim":
            secili = tum_yemekler[yemek_secimi]
            varsayilan_cal = float(secili["cal"])
            varsayilan_pro = float(secili["pro"])
            varsayilan_carb = float(secili["carb"])
            varsayilan_fat = float(secili["fat"])

        with st.form("meal_form", clear_on_submit=True):
            default_name = yemek_secimi if yemek_secimi != "Kendim Gireceğim" else ""
            food_name = st.text_input("Yemek adı", value=default_name)
            meal_type = st.selectbox("Öğün", ["Kahvaltı", "Öğle", "Akşam", "Ara Öğün"])
            c1, c2, c3, c4 = st.columns(4)
            calories = c1.number_input("Kalori", 0.0, 5000.0, varsayilan_cal, 10.0)
            protein = c2.number_input("Protein (g)", 0.0, 500.0, varsayilan_pro, 1.0)
            carbs = c3.number_input("Karb. (g)", 0.0, 500.0, varsayilan_carb, 1.0)
            fat = c4.number_input("Yağ (g)", 0.0, 500.0, varsayilan_fat, 1.0)
            
            col_save, col_add = st.columns(2)
            save_custom = col_save.form_submit_button("⭐ Yemeği Listeye Kaydet")
            submitted = col_add.form_submit_button("Ekle", type="primary")
            
        if submitted or save_custom:
            if not food_name.strip() or calories <= 0:
                st.error("Yemek adı ve kalori gerekli.")
            else:
                meal_mod.add_meal(user["id"], meal_type, food_name.strip(), calories, protein, carbs, fat)
                if save_custom:
                    meal_mod.add_custom_food(user["id"], food_name.strip(), calories, protein, carbs, fat)
                    st.success(f"{food_name} hem günlüğe eklendi hem de listene kaydedildi!")
                else:
                    st.success(f"{food_name} eklendi!")
                st.rerun()

    # --- 2. SU TAKİBİ ---
    with tab_water:
        st.subheader("💧 Su Tüketimi")
        
        if water_ml == 0:
            st.warning("💧 **Bugün henüz su içmedin!** Sağlığın için bir bardak su içmeyi unutma. 🚰")
        
        st.write(f"Bugün toplam **{water_ml} ml** su içtiniz. (Hedef: ~2000 ml)")
        
        su_orani = min(1.0, water_ml / 2000.0)
        st.progress(su_orani, text=f"Hedefin %{int(su_orani*100)}'i")
        
        st.divider()
        st.write("**Hızlı Ekle**")
        
        col1, col2 = st.columns(2)
        if col1.button("🥛 1 Bardak (200ml)", use_container_width=True):
            meal_mod.add_water(user["id"], 200)
            st.rerun()
        if col2.button("🍵 Büyük Bardak (300ml)", use_container_width=True):
            meal_mod.add_water(user["id"], 300)
            st.rerun()
            
        col3, col4 = st.columns(2)
        if col3.button("🥤 Şişe (500ml)", use_container_width=True):
            meal_mod.add_water(user["id"], 500)
            st.rerun()
        if col4.button("🚰 1 Litre", use_container_width=True):
            meal_mod.add_water(user["id"], 1000)
            st.rerun()
            
        st.divider()
        
        if st.button("↩️ Son Eklenen 1 Bardağı Geri Al (200ml)", use_container_width=True):
            meal_mod.remove_water(user["id"], 200)
            st.rerun()

        if water_ml >= 2000 and "konfeti_gosterildi" not in st.session_state:
            st.balloons()
            st.session_state.konfeti_gosterildi = True

    # --- 3. AKTİVİTE ---
    with tab_act:
        st.subheader("Bugün Aktivitelerim")
        if summary["activities"]:
            for a in summary["activities"]:
                c1, c2 = st.columns([5, 1])
                act_emoji = "🏃"
                if "Yürüyüş" in a['activity_name']: act_emoji = "🚶"
                elif "Koşu" in a['activity_name']: act_emoji = "🏃‍♂️"
                elif "Bisiklet" in a['activity_name']: act_emoji = "🚴"
                elif "Yüzme" in a['activity_name']: act_emoji = "🏊"
                elif "Ağırlık" in a['activity_name']: act_emoji = "💪"
                elif "Pilates" in a['activity_name'] or "Yoga" in a['activity_name']: act_emoji = "🧘"
                
                c1.write(f"{act_emoji} **{a['activity_name']}** — {a['duration_min']} dk, {int(a['calories_burned'])} kcal")
                if c2.button("🗑️", key=f"del_act_{a['id']}"):
                    meal_mod.delete_activity(a["id"])
                    st.rerun()
        else:
            st.info("Henüz aktivite eklenmedi.")
        st.divider()
        weight = user["weight_kg"] or 70
        with st.form("activity_form", clear_on_submit=True):
            activity_name = st.selectbox("Aktivite", list(meal_mod.ACTIVITY_BURN_PER_KG_PER_MIN.keys()))
            duration = st.number_input("Süre (dk)", 1, 600, 30)
            est = weight * duration * meal_mod.ACTIVITY_BURN_PER_KG_PER_MIN[activity_name]
            st.caption(f"Tahmini yakım: **{int(est)} kcal**")
            submitted = st.form_submit_button("Ekle")
        if submitted:
            burn = weight * duration * meal_mod.ACTIVITY_BURN_PER_KG_PER_MIN[activity_name]
            meal_mod.add_activity(user["id"], activity_name, duration, burn)
            st.rerun()

    # --- 4. KİLO ---
    with tab_weight:
        st.subheader("⚖️ Kilo Takibi")
        
        stats = meal_mod.get_weight_stats(user["id"])
        
        if stats:
            c1, c2, c3 = st.columns(3)
            c1.metric("Başlangıç Kilosu", f"{stats['ilk_kilo']} kg")
            c2.metric("Son Kilo", f"{stats['son_kilo']} kg")
            
            fark = stats['fark']
            if fark < 0:
                c3.metric("Toplam Değişim", f"{fark:.1f} kg", delta=f"{fark:.1f} kg (Tebrikler! 🎉)", delta_color="normal")
            elif fark > 0:
                c3.metric("Toplam Değişim", f"{fark:.1f} kg", delta=f"+{fark:.1f} kg", delta_color="inverse")
            else:
                c3.metric("Toplam Değişim", "0.0 kg")
                
            st.write("**Kilo Değişim Grafiği**")
            st.line_chart({"Kilo (kg)": {r["date"]: r["weight_kg"] for r in stats['gecmis']}})
            
        else:
            st.info("Henüz kilo kaydı yok. Aşağıdan ilk kilonu ekleyebilirsin.")
        
        st.divider()
        st.write("**Yeni Kilo Kaydı Ekle**")
        
        with st.form("weight_form", clear_on_submit=True):
            w_date = st.date_input("Tarih", value=date.today())
            w_kg = st.number_input("Kilo (kg)", 30.0, 250.0, float(user["weight_kg"] or 70.0), 0.1)
            submitted = st.form_submit_button("Kaydet")
            
        if submitted:
            meal_mod.add_weight(user["id"], w_kg, w_date)
            st.success(f"{w_date} için {w_kg} kg kaydedildi.")
            st.rerun()

    # --- 5. VÜCUT ÖLÇÜLERİ ---
    with tab_measure:
        st.subheader("📏 Vücut Ölçüleri")
        st.caption("Bel, göğüs, kalça gibi ölçülerinizi kaydedin. Değişimi görmek motivasyonunuzu artıracaktır.")
        
        measurements = meal_mod.get_measurements(user["id"])
        
        if measurements:
            st.write("**Geçmiş Ölçüleriniz**")
            for m in measurements:
                st.write(f"📅 {m['date']} — Bel: {m['waist']} cm, Göğüs: {m['chest']} cm, Kalça: {m['hips']} cm")
            
            son = measurements[-1]
            c1, c2, c3, c4, c5, c6 = st.columns(6)
            c1.metric("Bel", f"{son['waist']} cm" if son['waist'] else "-")
            c2.metric("Göğüs", f"{son['chest']} cm" if son['chest'] else "-")
            c3.metric("Kalça", f"{son['hips']} cm" if son['hips'] else "-")
            c4.metric("Kol", f"{son['biceps']} cm" if son['biceps'] else "-")
            c5.metric("Bacak", f"{son['thigh']} cm" if son['thigh'] else "-")
            c6.metric("Boyun", f"{son['neck']} cm" if son['neck'] else "-")
        else:
            st.info("Henüz ölçü kaydı yok. Aşağıdan ilk ölçülerinizi ekleyebilirsiniz.")
        
        st.divider()
        st.write("**Yeni Ölçü Kaydı Ekle**")
        
        with st.form("measure_form", clear_on_submit=True):
            m_date = st.date_input("Tarih", value=date.today())
            c1, c2, c3 = st.columns(3)
            neck = c1.number_input("Boyun (cm)", 0.0, 100.0, 0.0, 0.5)
            chest = c2.number_input("Göğüs (cm)", 0.0, 200.0, 0.0, 0.5)
            waist = c3.number_input("Bel (cm)", 0.0, 200.0, 0.0, 0.5)
            
            c4, c5, c6 = st.columns(3)
            hips = c4.number_input("Kalça (cm)", 0.0, 200.0, 0.0, 0.5)
            biceps = c5.number_input("Kol (cm)", 0.0, 100.0, 0.0, 0.5)
            thigh = c6.number_input("Bacak (cm)", 0.0, 150.0, 0.0, 0.5)
            
            submitted = st.form_submit_button("Kaydet", type="primary")
            
        if submitted:
            meal_mod.add_measurement(user["id"], str(m_date), neck, chest, waist, hips, biceps, thigh)
            st.success("Ölçüleriniz kaydedildi!")
            st.rerun()

    # --- 6. RAPORLAR ---
    with tab_chart:
        st.subheader("📊 Analiz ve Raporlar")

        # --- HAFTALIK ÖZET VE AÇIK KARTI ---
        
        # --- HAFTALIK ÖZET VE AÇIK KARTI (Pazartesi'den Bugüne) ---
        haftalik_ozet = meal_mod.get_this_week_summary(user["id"])
        toplam_alinan = haftalik_ozet["eaten"]
        toplam_yakilan = haftalik_ozet["burned"]
        gecen_gun = haftalik_ozet["days_passed"]
        
        haftalik_hedef = target * gecen_gun
        haftalik_acik = toplam_alinan - (haftalik_hedef + toplam_yakilan)
        
        if haftalik_acik <= 0:
            acik_mesaji = f"🔥 **Harika!** Bu hafta (Pazartesi'den bugüne) **{abs(int(haftalik_acik))} kcal** açık verdin."
        else:
            acik_mesaji = f"⚠️ **Dikkat!** Bu hafta **{int(haftalik_acik)} kcal** fazla aldın."
            
        st.info(f"""
        🎉 **Bu Haftanın Özeti (Pazartesi'den Bugüne)**
        
        Bu hafta toplam **{int(toplam_alinan)} kcal** aldın ve **{int(toplam_yakilan)} kcal** yaktın. 
        ({gecen_gun} günlük veri)
        
        {acik_mesaji}
        """)
        st.divider()
        rapor_tipi = st.radio("Rapor Tipi", ["Son 7 Gün", "Aylık Rapor"], horizontal=True)
        
        if rapor_tipi == "Son 7 Gün":
            data = meal_mod.get_last_7_days(user["id"])
            labels = [d["date"].strftime("%d.%m") for d in data]
            
            total_eaten = sum(d["eaten"] for d in data)
            total_burned = sum(d["burned"] for d in data)
            
            c1, c2 = st.columns(2)
            c1.metric("Ortalama Alınan", f"{int(total_eaten/7)} kcal/gün")
            c2.metric("Ortalama Yakılan", f"{int(total_burned/7)} kcal/gün")
            
            st.write("**Günlük Kalori Akışı**")
            st.bar_chart({
                "Alınan": {l: d["eaten"] for l, d in zip(labels, data)},
                "Yakılan": {l: d["burned"] for l, d in zip(labels, data)},
            })
            
            st.divider()
            st.write("**Günlük Ortalama Makro Besinler**")
            macro = meal_mod.get_macro_summary_last_7_days(user["id"])
            
            mc1, mc2, mc3 = st.columns(3)
            mc1.metric("Protein", f"{int(macro['protein'])} g/gün")
            mc2.metric("Karbonhidrat", f"{int(macro['carbs'])} g/gün")
            mc3.metric("Yağ", f"{int(macro['fat'])} g/gün")
            
            st.bar_chart({
                "Miktar (g)": {
                    "Protein": macro["protein"],
                    "Karbonhidrat": macro["carbs"],
                    "Yağ": macro["fat"]
                }
            })
            
        else:
            st.write("**Geçmiş Ayları İncele**")
            bugun = date.today()
            yillar = list(range(bugun.year, bugun.year - 3, -1))
            secilen_yil = st.selectbox("Yıl Seçin", yillar)
            
            aylar = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", 
                     "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
            secilen_ay_adi = st.selectbox("Ay Seçin", aylar)
            secilen_ay = aylar.index(secilen_ay_adi) + 1
            
            aylik_data = meal_mod.get_monthly_summary(user["id"], secilen_yil, secilen_ay)
            
            if aylik_data:
                st.success(f"{secilen_ay_adi} {secilen_yil} ayına ait verileriniz aşağıdadır:")
                
                aylik_toplam_alinan = sum(d["eaten"] for d in aylik_data)
                aylik_toplam_yakilan = sum(d["burned"] for d in aylik_data)
                gun_sayisi = len(aylik_data)
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Toplam Alınan", f"{int(aylik_toplam_alinan)} kcal")
                col2.metric("Toplam Yakılan", f"{int(aylik_toplam_yakilan)} kcal")
                col3.metric("Günlük Ortalama", f"{int(aylik_toplam_alinan/gun_sayisi)} kcal")
                
                st.write("**Aylık Kalori Grafiği**")
                labels = [d["date"].split("-")[2] for d in aylik_data]
                st.bar_chart({
                    "Alınan": {l: d["eaten"] for l, d in zip(labels, aylik_data)},
                    "Yakılan": {l: d["burned"] for l, d in zip(labels, aylik_data)},
                })
                
                st.divider()
                st.write("**Günlük Ortalama Makro Besinler (Aylık)**")
                macro_aylik = meal_mod.get_macro_summary_monthly(user["id"], secilen_yil, secilen_ay)
                
                mac1, mac2, mac3 = st.columns(3)
                mac1.metric("Protein", f"{int(macro_aylik['protein'])} g/gün")
                mac2.metric("Karbonhidrat", f"{int(macro_aylik['carbs'])} g/gün")
                mac3.metric("Yağ", f"{int(macro_aylik['fat'])} g/gün")
                
            else:
                st.info(f"{secilen_ay_adi} {secilen_yil} ayında henüz hiçbir kayıt bulunmuyor.")
                
        # --- VÜCUT ÖLÇÜLERİ GRAFİĞİ ---
        st.divider()
        st.write("**📏 Vücut Ölçüleri Değişimi (Son 6 Ay)**")
        
        today = date.today()
        alti_ay_once = today - datetime.timedelta(days=180)
        
        olcu_data = meal_mod.get_measurements_for_chart(user["id"])
        
        if olcu_data:
            filtered = [r for r in olcu_data if r["date"] >= str(alti_ay_once)]
            
            if filtered:
                chart_data = {
                    "Bel (cm)": {r["date"]: r["waist"] for r in filtered if r["waist"]},
                    "Göğüs (cm)": {r["date"]: r["chest"] for r in filtered if r["chest"]},
                    "Kalça (cm)": {r["date"]: r["hips"] for r in filtered if r["hips"]},
                    "Kol (cm)": {r["date"]: r["biceps"] for r in filtered if r["biceps"]},
                }
                st.line_chart(chart_data)
            else:
                st.info("Son 6 ayda kaydedilmiş ölçü bulunmuyor.")
        else:
            st.info("Henüz hiç ölçü kaydı yok. '📏 Ölçüler' sekmesinden ekleyebilirsiniz.")

# --- ALT BİLGİ (FOOTER) ---
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #8E8E93; font-size: 12px; padding-bottom: 20px;'>
        🥗 <b>KCTFIT</b> | Geliştirici: <b>Kerim Çağatay Toklu</b> (@kct)
    </div>
    """, 
    unsafe_allow_html=True
)

# Ana akış
user = st.session_state.user
if user is None:
    show_login_page()
elif not user.get("daily_calorie_target"):
    show_profile_setup(user)
else:
    show_home(user)
