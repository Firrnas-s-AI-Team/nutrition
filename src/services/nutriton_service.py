def get_nutritional_needs(data):
    # Extract the user_profile from the nested structure
    user_profile = data["user_profile"]
    
    weight = user_profile["weight"]
    height = user_profile["height"]
    age = user_profile["age"]
    gender = user_profile["gender"]
    activity_level = user_profile["activity_level"]
   
    if gender == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
       
    activity_multipliers = {
        "sedentary": 1.2,
        "lightly_active": 1.375,
        "moderately_active": 1.55,
        "very_active": 1.725,
        "extra_active": 1.9
    }
    tdee = bmr * activity_multipliers[activity_level]
    if user_profile["goal"] == "weight_loss":
        tdee -= 500
    elif user_profile["goal"] == "weight_gain":
        tdee += 500
    nutritional_needs = {
        "calories": tdee,
        "protein": weight * 1.6,  # Higher protein for vegan diet
        "carbs": (tdee * 0.5) / 4,  # 50% of calories from carbs
        "fats": (tdee * 0.3) / 9  # 30% of calories from fats
    }
    return nutritional_needs