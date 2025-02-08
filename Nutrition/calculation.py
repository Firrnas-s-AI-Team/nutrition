import pandas as pd
import random

def calculate_bmr(age, gender, weight, height):
    """
    Calculate Basal Metabolic Rate (BMR) using the Mifflin-St Jeor Equation.
    
    Parameters:
        age (int): Age in years.
        gender (str): 'male' or 'female'.
        weight (float): Weight in kilograms.
        height (float): Height in centimeters.
    
    Returns:
        float: Calculated BMR.
    """
    if gender.lower() == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    elif gender.lower() == "female":
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    else:
        raise ValueError("Invalid gender. Choose 'male' or 'female'.")
    return bmr

def calculate_tdee(bmr, activity_level):
    """
    Calculate Total Daily Energy Expenditure (TDEE) by applying an activity multiplier to the BMR.
    
    Parameters:
        bmr (float): Basal Metabolic Rate.
        activity_level (str): One of "sedentary", "lightly active", "moderately active", "very active", "super active", or "extremely_active".
    
    Returns:
        float: Calculated TDEE.
    """
    activity_multipliers = {
        "sedentary": 1.2,
        "lightly active": 1.375,
        "moderately active": 1.55,
        "very active": 1.725,
        "super active": 1.9,
        "extremely_active": 2.0
    }
    if activity_level not in activity_multipliers:
        raise ValueError("Invalid activity level")
    return bmr * activity_multipliers[activity_level]

def compose_balanced_meal(meal_calories, target_protein, target_carb, target_fat, food_df, food_exclusions, user_preferences=None):
    """
    Compose a balanced meal by selecting one lean protein, one carbohydrate, and one healthy fat.
    
    For each food item, an initial portion is calculated so that its primary nutrient meets
    the per-meal target. All portions are then scaled so that the total meal calories equal meal_calories.
    
    Parameters:
        meal_calories (float): Desired total calories for the meal.
        target_protein (float): Target grams of protein for the meal.
        target_carb (float): Target grams of carbohydrates for the meal.
        target_fat (float): Target grams of fat for the meal.
        food_df (DataFrame): DataFrame containing food items with nutritional information.
        food_exclusions (set): Set of food items already used (to promote variety).
        user_preferences (dict, optional): Contains keys like 'dislikes', 'allergies', and 'dietary_restrictions'.
    
    Returns:
        tuple: (list of food items for the meal, updated food_exclusions set)
    
    Raises:
        ValueError: If no candidate is found for any of the required food categories.
    """
    if user_preferences is None:
        user_preferences = {}
        
    # Convert preferences to sets for easy exclusion.
    disliked = set(user_preferences.get("dislikes", []))
    allergies = set(user_preferences.get("allergies", []))
    restrictions = set(user_preferences.get("dietary_restrictions", []))
    
    # --- Choose a lean protein ---
    protein_candidates = food_df[
        (food_df["type_category"] == "protein") &
        (food_df["fats_per_100_gm"] <= 5) &
        (~food_df["food_item"].isin(food_exclusions.union(disliked)))
    ]
    if protein_candidates.empty:
        protein_candidates = food_df[
            (food_df["type_category"] == "protein") &
            (~food_df["food_item"].isin(food_exclusions.union(disliked)))
        ]
    if protein_candidates.empty:
        raise ValueError("No available protein candidates. Check your food database, exclusions, and user preferences.")
    protein_item = protein_candidates.sample().iloc[0]

    # --- Choose a carbohydrate source ---
    carb_candidates = food_df[
        (food_df["type_category"] == "carb") &
        (~food_df["food_item"].isin(food_exclusions.union(disliked)))
    ]
    if carb_candidates.empty:
        carb_candidates = food_df[food_df["type_category"] == "carb"]
    if carb_candidates.empty:
        raise ValueError("No available carbohydrate candidates. Check your food database and exclusions.")
    carb_item = carb_candidates.sample().iloc[0]

    # --- Choose a healthy fat ---
    fat_candidates = food_df[
        (food_df["type_category"] == "fats") &
        (food_df["fats_per_100_gm"] >= 5) &
        (food_df["fats_per_100_gm"] <= 20) &
        (~food_df["food_item"].isin(food_exclusions.union(disliked)))
    ]
    if fat_candidates.empty:
        fat_candidates = food_df[
            (food_df["type_category"] == "fats") &
            (~food_df["food_item"].isin(food_exclusions.union(disliked)))
        ]
    if fat_candidates.empty:
        raise ValueError("No available fat candidates. Check your food database and exclusions.")
    fat_item = fat_candidates.sample().iloc[0]

    # --- Compute initial portion sizes based on target macronutrient content ---
    grams_protein = (target_protein * 100) / protein_item["protein_per_100_gm"] if protein_item["protein_per_100_gm"] > 0 else 0
    grams_carb = (target_carb * 100) / carb_item["carb_per_100_gm"] if carb_item["carb_per_100_gm"] > 0 else 0
    grams_fat = (target_fat * 100) / fat_item["fats_per_100_gm"] if fat_item["fats_per_100_gm"] > 0 else 0

    # --- Calculate calories contributed by each food based on initial portions ---
    cal_protein = (protein_item["calories_per_100_gm"] * grams_protein) / 100
    cal_carb = (carb_item["calories_per_100_gm"] * grams_carb) / 100
    cal_fat = (fat_item["calories_per_100_gm"] * grams_fat) / 100

    initial_total_cal = cal_protein + cal_carb + cal_fat

    # --- Scale portions so that total calories equal meal_calories ---
    scale = meal_calories / initial_total_cal if initial_total_cal > 0 else 1
    grams_protein *= scale
    grams_carb *= scale
    grams_fat *= scale

    # --- Recalculate macronutrients after scaling ---
    final_protein = (protein_item["protein_per_100_gm"] * grams_protein) / 100
    final_carb = (carb_item["carb_per_100_gm"] * grams_carb) / 100
    final_fat = (fat_item["fats_per_100_gm"] * grams_fat) / 100

    final_cal_protein = (protein_item["calories_per_100_gm"] * grams_protein) / 100
    final_cal_carb = (carb_item["calories_per_100_gm"] * grams_carb) / 100
    final_cal_fat = (fat_item["calories_per_100_gm"] * grams_fat) / 100

    meal_items = [
        {
            "item": protein_item["food_item"],
            "grams": grams_protein,
            "calories": final_cal_protein,
            "protein": final_protein,
            "carb": (protein_item["carb_per_100_gm"] * grams_protein) / 100,
            "fats": (protein_item["fats_per_100_gm"] * grams_protein) / 100,
        },
        {
            "item": carb_item["food_item"],
            "grams": grams_carb,
            "calories": final_cal_carb,
            "protein": (carb_item["protein_per_100_gm"] * grams_carb) / 100,
            "carb": final_carb,
            "fats": (carb_item["fats_per_100_gm"] * grams_carb) / 100,
        },
        {
            "item": fat_item["food_item"],
            "grams": grams_fat,
            "calories": final_cal_fat,
            "protein": (fat_item["protein_per_100_gm"] * grams_fat) / 100,
            "carb": (fat_item["carb_per_100_gm"] * grams_fat) / 100,
            "fats": final_fat,
        }
    ]

    # Update the exclusion set to avoid reusing the same food items in subsequent meals.
    food_exclusions.update([
        protein_item["food_item"],
        carb_item["food_item"],
        fat_item["food_item"]
    ])
    return meal_items, food_exclusions


def generate_daily_meal_plan(tdee, goal, food_df, meals_per_day, gender, food_exclusions=None, user_preferences=None):
    """
    For a weight loss goal, a modest calorie deficit is applied to the TDEE.
    Daily macronutrient targets are computed as percentages of the adjusted target calories,
    then divided evenly across meals.
    
    Parameters:
        tdee (float): Total Daily Energy Expenditure.
        goal (str): One of "weight_loss", "gain_weight", or "gain_muscles".
        food_df (DataFrame): DataFrame with food nutritional information.
        meals_per_day (int): Number of meals to generate.
        gender (str): User gender.
        food_exclusions (set, optional): Set of already-used food items.
        user_preferences (dict, optional): Contains user preferences/dietary restrictions.
    
    Returns:
        dict: Daily meal plan with each meal's items and nutritional breakdown.
    """
    if food_exclusions is None:
        food_exclusions = set()
    if user_preferences is None:
        user_preferences = {}
        
    # Define target calories and daily macronutrient targets based on the goal.
    if goal == "weight_loss":
        deficit = 250
        target_calories = tdee - deficit
        # Percentages: 30% protein, 40% carbohydrates, 30% fat.
        daily_protein_grams = (0.30 * target_calories) / 4
        daily_carb_grams = (0.40 * target_calories) / 4
        daily_fat_grams = (0.30 * target_calories) / 9
    elif goal == "gain_weight":
        surplus = 250
        target_calories = tdee + surplus
        daily_protein_grams = (0.25 * target_calories) / 4
        daily_carb_grams = (0.50 * target_calories) / 4
        daily_fat_grams = (0.25 * target_calories) / 9
    elif goal == "gain_muscles":
        surplus = 250
        target_calories = tdee + surplus
        daily_protein_grams = (0.35 * target_calories) / 4
        daily_carb_grams = (0.45 * target_calories) / 4
        daily_fat_grams = (0.20 * target_calories) / 9
    else:
        raise ValueError("Invalid goal. Choose 'weight_loss', 'gain_weight', or 'gain_muscles'.")

    meal_calories = target_calories / meals_per_day
    protein_per_meal = daily_protein_grams / meals_per_day
    carb_per_meal = daily_carb_grams / meals_per_day
    fat_per_meal = daily_fat_grams / meals_per_day

    daily_meal_plan = {}
    for i in range(meals_per_day):
        meal_name = f"Meal_{i+1}"
        meal_items, food_exclusions = compose_balanced_meal(
            meal_calories,
            protein_per_meal,
            carb_per_meal,
            fat_per_meal,
            food_df,
            food_exclusions,
            user_preferences=user_preferences
        )
        total_calories = sum(item["calories"] for item in meal_items)
        total_protein = sum(item["protein"] for item in meal_items)
        total_carb = sum(item["carb"] for item in meal_items)
        total_fat = sum(item["fats"] for item in meal_items)
        daily_meal_plan[meal_name] = {
            "items": meal_items,
            "total_calories": total_calories,
            "total_protein": total_protein,
            "total_carb": total_carb,
            "total_fats": total_fat
        }
    return daily_meal_plan

def generate_meal_plans_for_days(num_days, tdee, goal, food_df, meals_per_day, gender, user_preferences=None, vary_across_days=False):
    """
    Parameters:
        num_days (int): Number of days for which to generate meal plans.
        tdee (float): Total Daily Energy Expenditure.
        goal (str): User's nutritional goal (e.g., "weight_loss", "gain_weight", "gain_muscles").
        food_df (DataFrame): DataFrame containing food nutritional data.
        meals_per_day (int): Number of meals per day.
        gender (str): User's gender.
        user_preferences (dict, optional): Additional user preferences or dietary restrictions.
        vary_across_days (bool, optional): If True, maintain a cumulative food exclusion set across days; 
                                           if False, each day starts with a fresh exclusion set.
    
    Returns:
        dict: A dictionary with keys "Day_1", "Day_2", ... and values as the daily meal plans.
    """
    multi_day_plan = {}
    if vary_across_days:
        food_exclusions = set()
        for day in range(1, num_days + 1):
            daily_plan = generate_daily_meal_plan(tdee, goal, food_df, meals_per_day, gender, food_exclusions=food_exclusions, user_preferences=user_preferences)
            multi_day_plan[f"Day_{day}"] = daily_plan
    else:
        for day in range(1, num_days + 1):
            daily_plan = generate_daily_meal_plan(tdee, goal, food_df, meals_per_day, gender, food_exclusions=set(), user_preferences=user_preferences)
            multi_day_plan[f"Day_{day}"] = daily_plan
    return multi_day_plan
