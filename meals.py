from datetime import date, timedelta
from database import supabase

ACTIVITY_BURN_PER_KG_PER_MIN = {
    "Yürüyüş (hafif)":     0.05,
    "Yürüyüş (tempolu)":   0.08,
    "Koşu":                0.14,
    "Bisiklet":            0.10,
    "Yüzme":               0.12,
    "Ağırlık antrenmanı":  0.06,
    "HIIT":                0.15,
    "Pilates / Yoga":      0.04,
    "Dans":                0.07,
    "Ev işleri":           0.05,
}

def add_meal(user_id, meal_type, food_name, calories, protein=0.0, carbs=0.0, fat=0.0, source="manuel"):
    try:
        supabase.table("meal_entries").insert({
            "user_id": user_id, "date": str(date.today()), "meal_type": meal_type,
            "food_name": food_name, "calories": float(calories), "protein": float(protein),
            "carbs": float(carbs), "fat": float(fat), "source": source
        }).execute()
    except Exception as e:
        print(f"Yemek ekleme hatası: {e}")

def delete_meal(meal_id):
    try:
        supabase.table("meal_entries").delete().eq("id", meal_id).execute()
    except Exception as e:
        print(f"Yemek silme hatası: {e}")

def add_activity(user_id, activity_name, duration_min, calories_burned, source="manuel"):
    try:
        supabase.table("activity_entries").insert({
            "user_id": user_id, "date": str(date.today()), "activity_name": activity_name,
            "duration_min": int(duration_min), "calories_burned": float(calories_burned), "source": source
        }).execute()
    except Exception as e:
        print(f"Aktivite ekleme hatası: {e}")

def delete_activity(activity_id):
    try:
        supabase.table("activity_entries").delete().eq("id", activity_id).execute()
    except Exception as e:
        print(f"Aktivite silme hatası: {e}")

def add_weight(user_id, weight_kg, on_date=None):
    on_date = on_date or date.today()
    try:
        existing = supabase.table("weight_logs").select("id").eq("user_id", user_id).eq("date", str(on_date)).execute()
        if existing.data:
            supabase.table("weight_logs").update({"weight_kg": float(weight_kg)}).eq("id", existing.data[0]["id"]).execute()
        else:
            supabase.table("weight_logs").insert({"user_id": user_id, "date": str(on_date), "weight_kg": float(weight_kg)}).execute()
    except Exception as e:
        print(f"Kilo ekleme hatası: {e}")

def get_today_summary(user_id):
    try:
        meals_res = supabase.table("meal_entries").select("*").eq("user_id", user_id).eq("date", str(date.today())).order("id", desc=True).execute()
        act_res = supabase.table("activity_entries").select("*").eq("user_id", user_id).eq("date", str(date.today())).order("id", desc=True).execute()
        meals = meals_res.data or []
        activities = act_res.data or []
        total_eaten = sum(m["calories"] for m in meals)
        total_burned = sum(a["calories_burned"] for a in activities)
        return {"meals": meals, "activities": activities, "total_eaten": total_eaten, "total_burned": total_burned}
    except Exception as e:
        print(f"Özet hatası: {e}")
        return {"meals": [], "activities": [], "total_eaten": 0, "total_burned": 0}

def get_last_7_days(user_id):
    result = []
    for i in range(6, -1, -1):
        d = date.today() - timedelta(days=i)
        try:
            eaten_res = supabase.table("meal_entries").select("calories").eq("user_id", user_id).eq("date", str(d)).execute()
            burned_res = supabase.table("activity_entries").select("calories_burned").eq("user_id", user_id).eq("date", str(d)).execute()
            eaten = sum(m["calories"] for m in eaten_res.data) if eaten_res.data else 0
            burned = sum(a["calories_burned"] for a in burned_res.data) if burned_res.data else 0
            result.append({"date": d, "eaten": eaten, "burned": burned})
        except Exception as e:
            print(f"7 günlük veri hatası: {e}")
            result.append({"date": d, "eaten": 0, "burned": 0})
    return result

def get_weight_history(user_id):
    try:
        res = supabase.table("weight_logs").select("date, weight_kg").eq("user_id", user_id).order("date", desc=False).execute()
        return res.data or []
    except Exception as e:
        print(f"Kilo geçmişi hatası: {e}")
        return []

def get_weight_stats(user_id, hedef_kilo=None):
    try:
        res = supabase.table("weight_logs").select("date, weight_kg").eq("user_id", user_id).order("date", desc=False).execute()
        rows = res.data or []
        if not rows:
            return None
        ilk_kilo = rows[0]["weight_kg"]
        son_kilo = rows[-1]["weight_kg"]
        return {"ilk_kilo": ilk_kilo, "son_kilo": son_kilo, "fark": son_kilo - ilk_kilo, "gecmis": rows}
    except Exception as e:
        print(f"Kilo istatistik hatası: {e}")
        return None

def add_custom_food(user_id, name, cal, pro, carb, fat):
    try:
        supabase.table("custom_foods").insert({"user_id": user_id, "name": name, "calories": cal, "protein": pro, "carbs": carb, "fat": fat}).execute()
    except Exception as e:
        print(f"Özel yemek ekleme hatası: {e}")

def get_custom_foods(user_id):
    try:
        res = supabase.table("custom_foods").select("*").eq("user_id", user_id).order("name", desc=False).execute()
        return res.data or []
    except Exception as e:
        print(f"Özel yemek getirme hatası: {e}")
        return []

def add_water(user_id, amount_ml):
    try:
        existing = supabase.table("water_logs").select("id, amount_ml").eq("user_id", user_id).eq("date", str(date.today())).execute()
        if existing.data:
            new_amount = existing.data[0]["amount_ml"] + amount_ml
            supabase.table("water_logs").update({"amount_ml": new_amount}).eq("id", existing.data[0]["id"]).execute()
        else:
            supabase.table("water_logs").insert({"user_id": user_id, "date": str(date.today()), "amount_ml": amount_ml}).execute()
    except Exception as e:
        print(f"Su ekleme hatası: {e}")

def get_today_water(user_id):
    try:
        res = supabase.table("water_logs").select("amount_ml").eq("user_id", user_id).eq("date", str(date.today())).execute()
        return res.data[0]["amount_ml"] if res.data else 0
    except Exception as e:
        print(f"Su getirme hatası: {e}")
        return 0

def remove_water(user_id, amount_ml):
    try:
        existing = supabase.table("water_logs").select("id, amount_ml").eq("user_id", user_id).eq("date", str(date.today())).execute()
        if existing.data:
            new_amount = max(0, existing.data[0]["amount_ml"] - amount_ml)
            if new_amount == 0:
                supabase.table("water_logs").delete().eq("id", existing.data[0]["id"]).execute()
            else:
                supabase.table("water_logs").update({"amount_ml": new_amount}).eq("id", existing.data[0]["id"]).execute()
    except Exception as e:
        print(f"Su silme hatası: {e}")

def update_display_name(user_id, new_name):
    try:
        supabase.table("users").update({"display_name": new_name}).eq("id", user_id).execute()
    except Exception as e:
        print(f"İsim güncelleme hatası: {e}")

def clear_today_data(user_id):
    today = str(date.today())
    try:
        supabase.table("meal_entries").delete().eq("user_id", user_id).eq("date", today).execute()
        supabase.table("activity_entries").delete().eq("user_id", user_id).eq("date", today).execute()
        supabase.table("water_logs").delete().eq("user_id", user_id).eq("date", today).execute()
        supabase.table("weight_logs").delete().eq("user_id", user_id).eq("date", today).execute()
    except Exception as e:
        print(f"Veri temizleme hatası: {e}")

def clear_all_data(user_id):
    try:
        supabase.table("meal_entries").delete().eq("user_id", user_id).execute()
        supabase.table("activity_entries").delete().eq("user_id", user_id).execute()
        supabase.table("water_logs").delete().eq("user_id", user_id).execute()
        supabase.table("weight_logs").delete().eq("user_id", user_id).execute()
        supabase.table("custom_foods").delete().eq("user_id", user_id).execute()
        supabase.table("body_measurements").delete().eq("user_id", user_id).execute()
    except Exception as e:
        print(f"Tüm veri temizleme hatası: {e}")

def delete_user_account(user_id):
    try:
        supabase.table("meal_entries").delete().eq("user_id", user_id).execute()
        supabase.table("activity_entries").delete().eq("user_id", user_id).execute()
        supabase.table("water_logs").delete().eq("user_id", user_id).execute()
        supabase.table("weight_logs").delete().eq("user_id", user_id).execute()
        supabase.table("custom_foods").delete().eq("user_id", user_id).execute()
        supabase.table("body_measurements").delete().eq("user_id", user_id).execute()
        supabase.table("users").delete().eq("id", user_id).execute()
    except Exception as e:
        print(f"Hesap silme hatası: {e}")

def get_macro_summary_last_7_days(user_id):
    try:
        today = date.today()
        start_date = today - timedelta(days=6)
        res = supabase.table("meal_entries").select("protein, carbs, fat").eq("user_id", user_id).gte("date", str(start_date)).lte("date", str(today)).execute()
        rows = res.data or []
        total_pro = sum(r["protein"] for r in rows)
        total_carb = sum(r["carbs"] for r in rows)
        total_fat = sum(r["fat"] for r in rows)
        return {"protein": total_pro / 7 if rows else 0, "carbs": total_carb / 7 if rows else 0, "fat": total_fat / 7 if rows else 0}
    except Exception as e:
        print(f"Makro özet hatası: {e}")
        return {"protein": 0, "carbs": 0, "fat": 0}

def get_macro_summary_monthly(user_id, year, month):
    try:
        import calendar
        _, days_in_month = calendar.monthrange(year, month)
        start_date = f"{year}-{month:02d}-01"
        end_date = f"{year}-{month:02d}-{days_in_month}"
        res = supabase.table("meal_entries").select("protein, carbs, fat").eq("user_id", user_id).gte("date", start_date).lte("date", end_date).execute()
        rows = res.data or []
        total_pro = sum(r["protein"] for r in rows)
        total_carb = sum(r["carbs"] for r in rows)
        total_fat = sum(r["fat"] for r in rows)
        return {"protein": total_pro / days_in_month if rows else 0, "carbs": total_carb / days_in_month if rows else 0, "fat": total_fat / days_in_month if rows else 0}
    except Exception as e:
        print(f"Aylık makro hatası: {e}")
        return {"protein": 0, "carbs": 0, "fat": 0}

def add_measurement(user_id, date_str, neck, chest, waist, hips, biceps, thigh):
    try:
        existing = supabase.table("body_measurements").select("id").eq("user_id", user_id).eq("date", date_str).execute()
        if existing.data:
            supabase.table("body_measurements").update({"neck": neck, "chest": chest, "waist": waist, "hips": hips, "biceps": biceps, "thigh": thigh}).eq("id", existing.data[0]["id"]).execute()
        else:
            supabase.table("body_measurements").insert({"user_id": user_id, "date": date_str, "neck": neck, "chest": chest, "waist": waist, "hips": hips, "biceps": biceps, "thigh": thigh}).execute()
    except Exception as e:
        print(f"Ölçü ekleme hatası: {e}")

def get_measurements(user_id):
    try:
        res = supabase.table("body_measurements").select("date, neck, chest, waist, hips, biceps, thigh").eq("user_id", user_id).order("date", desc=False).execute()
        return res.data or []
    except Exception as e:
        print(f"Ölçü getirme hatası: {e}")
        return []

def get_monthly_summary(user_id, year, month):
    try:
        import calendar
        _, days_in_month = calendar.monthrange(year, month)
        result = []
        for day in range(1, days_in_month + 1):
            d_str = f"{year}-{month:02d}-{day:02d}"
            eaten_res = supabase.table("meal_entries").select("calories").eq("user_id", user_id).eq("date", d_str).execute()
            burned_res = supabase.table("activity_entries").select("calories_burned").eq("user_id", user_id).eq("date", d_str).execute()
            eaten = sum(m["calories"] for m in eaten_res.data) if eaten_res.data else 0
            burned = sum(a["calories_burned"] for a in burned_res.data) if burned_res.data else 0
            if eaten > 0 or burned > 0:
                result.append({"date": d_str, "eaten": eaten, "burned": burned})
        return result
    except Exception as e:
        print(f"Aylık özet hatası: {e}")
        return []

def get_measurements_for_chart(user_id, year=None, month=None):
    try:
        if year and month:
            import calendar
            _, days_in_month = calendar.monthrange(year, month)
            start_date = f"{year}-{month:02d}-01"
            end_date = f"{year}-{month:02d}-{days_in_month}"
            res = supabase.table("body_measurements").select("date, waist, chest, hips, biceps").eq("user_id", user_id).gte("date", start_date).lte("date", end_date).order("date", desc=False).execute()
        else:
            res = supabase.table("body_measurements").select("date, waist, chest, hips, biceps").eq("user_id", user_id).order("date", desc=False).execute()
        return res.data or []
    except Exception as e:
        print(f"Grafik ölçü hatası: {e}")
        return []
def delete_custom_food(food_id):
    """Kullanıcının kendi listesine eklediği bir yemeği siler."""
    try:
        supabase.table("custom_foods").delete().eq("id", food_id).execute()
    except Exception as e:
        print(f"Özel yemek silme hatası: {e}")
def get_this_week_summary(user_id):
    """Pazartesi'den bugüne kadar olan kalori özetini döndürür."""
    from datetime import date, timedelta
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    
    try:
        res = supabase.table("meal_entries").select("calories").eq("user_id", user_id).gte("date", str(start_of_week)).lte("date", str(today)).execute()
        eaten = sum(m["calories"] for m in res.data) if res.data else 0
        
        res_act = supabase.table("activity_entries").select("calories_burned").eq("user_id", user_id).gte("date", str(start_of_week)).lte("date", str(today)).execute()
        burned = sum(a["calories_burned"] for a in res_act.data) if res_act.data else 0
        
        return {"eaten": eaten, "burned": burned, "days_passed": today.weekday() + 1}
    except Exception as e:
        print(f"Haftalık özet hatası: {e}")
        return {"eaten": 0, "burned": 0, "days_passed": 1}
