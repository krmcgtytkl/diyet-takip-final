ACTIVITY_FACTORS = {
    "hareketsiz": 1.2,
    "az":         1.375,
    "orta":       1.55,
    "çok":        1.725,
    "aşırı":      1.9,
}


def bmr(weight_kg, height_cm, age, gender):
    if gender == "erkek":
        return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161


def tdee(weight_kg, height_cm, age, gender, activity_level):
    return bmr(weight_kg, height_cm, age, gender) * ACTIVITY_FACTORS.get(activity_level, 1.2)


def calorie_target(weight_kg, height_cm, age, gender, activity_level, goal):
    t = tdee(weight_kg, height_cm, age, gender, activity_level)
    if goal == "kilo ver":
        return round(max(1200, t - 500))
    if goal == "kilo al":
        return round(t + 300)
    return round(t)