from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
from typing import List
from datetime import datetime

app = FastAPI()
MODEL_NAME = "deepseek-r1:1.5b"


class FoodPreferences(BaseModel):
    allergies: List[str]
    liked_foods: List[str]
    disliked_foods: List[str]


class UserProfile(BaseModel):
    name: str
    age: int
    gender: str
    weight: float
    height: float
    activity_level: str
    goal: str
    target_weight: float
    daily_calorie_target: int
    meals_per_day: int
    food_preferences: FoodPreferences


class NutritionPlan(BaseModel):
    profile_summary: dict
    meal_plan: List[dict]
    timestamp: str


def calculate_bmi(weight: float, height: float) -> float:
    height_m = height / 100
    return round(weight / (height_m ** 2), 2)


def format_meal_plan(plan_text: str) -> List[dict]:
    days = []
    current_day = None
    for line in plan_text.split('\n'):
        if 'Day' in line:
            if current_day:
                days.append(current_day)
            current_day = {'title': line.strip(), 'meals': []}
        elif line.strip().startswith(('Breakfast:', 'Lunch:', 'Dinner:', 'Snack:')):
            if current_day:
                meal_type, meal_content = line.split(':', 1)
                current_day['meals'].append({
                    'type': meal_type.strip(),
                    'content': meal_content.strip()})

    if current_day:
        days.append(current_day)
    return days


@app.post("/generate-plan/", response_model=NutritionPlan)
async def generate_nutrition_plan(user: UserProfile):
    try:
        bmi = calculate_bmi(user.weight, user.height)
        water_intake = round(user.weight * 0.035, 2)
        prompt = f"""Create a 7-day meal plan for {user.name}:
Profile:
- Age: {user.age}
- Gender: {user.gender}
- Weight: {user.weight} kg
- Height: {user.height} cm
- BMI: {bmi}
- Activity: {user.activity_level}
- Goal: {user.goal}
- Target Weight: {user.target_weight} kg
- Daily Calories: {user.daily_calorie_target}
- Meals/Day: {user.meals_per_day}
- Allergies: {', '.join(user.food_preferences.allergies)}
- Liked Foods: {', '.join(user.food_preferences.liked_foods)}
- Disliked Foods: {', '.join(user.food_preferences.disliked_foods)}

Please provide a structured 7-day meal plan with:
Day 1:
Breakfast: [meal] ([calories] cal)
Lunch: [meal] ([calories] cal)
Dinner: [meal] ([calories] cal)
Snack: [meal] ([calories] cal)

[Continue for all 7 days]"""

        result = subprocess.run(
            ["ollama", "run", MODEL_NAME],
            input=prompt,
            capture_output=True,
            text=True,
            check=True)
        meal_plan = format_meal_plan(result.stdout)
        response = NutritionPlan(

            profile_summary={
                "name": user.name,
                "bmi": bmi,
                "water_intake": water_intake,
                "daily_calories": user.daily_calorie_target,
                "goal": user.goal},

            meal_plan=meal_plan,
            timestamp=str(datetime.now()))
        return response

    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Model error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

