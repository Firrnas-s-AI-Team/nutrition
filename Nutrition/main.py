import pandas as pd
import json
import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from calculation import calculate_bmr, calculate_tdee, generate_daily_meal_plan

# Load environment variables and set API key.
load_dotenv()
os.environ['groq_api_key'] = os.getenv('api_key')

INPUT_FILE = 'user_profile.json'
OUTPUT_FILE = 'nutrition_plan.json'
DATA_FILE = 'GPT_data.csv'

llm = ChatGroq(
    temperature=0.1,
    model_name="llama3-70b-8192",
    api_key=os.environ['groq_api_key']
)

def main():
    # Load food data and remove duplicate entries.
    food_df = pd.read_csv(DATA_FILE)
    food_df.drop_duplicates(subset='food_item', keep="last", inplace=True)

    # Load user profile.
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        user_profile = json.load(f)
    age = user_profile['age']
    gender = user_profile['gender']
    weight = user_profile['weight']
    height = user_profile['height']
    activity_level = user_profile['activity_level']
    goal = user_profile['goal']
    meals_per_day = user_profile['meals_per_day']

    # Calculate BMR and TDEE.
    bmr = calculate_bmr(age, gender, weight, height)
    tdee = calculate_tdee(bmr, activity_level)

    # Generate the balanced daily meal plan.
    daily_meal_plan = generate_daily_meal_plan(tdee, goal, food_df, meals_per_day, gender)

    # Prepare output.
    output = []
    output.append(f"BMR = {bmr:.2f} calories")
    output.append(f"Total Daily Calories (TDEE) = {tdee:.2f} calories")
    output.append(f"Goal: {goal}")
    output.append(f"Meals per Day: {meals_per_day}\n")
    output.append("Recommended Meal Plan (please space out your meals evenly throughout the day):")

    total_calories = 0
    total_protein = 0
    total_carb = 0
    total_fats = 0

    for meal, details in daily_meal_plan.items():
        output.append(f"\n{meal}:")
        for item in details["items"]:
            output.append(
                f"  - {item['item']}: {item['grams']:.2f} g "
                f"({item['calories']:.2f} cal, {item['protein']:.2f} g protein, "
                f"{item['carb']:.2f} g carbs, {item['fats']:.2f} g fats)"
            )
        output.append(
            f"  Meal Totals: {details['total_calories']:.2f} cal, "
            f"{details['total_protein']:.2f} g protein, "
            f"{details['total_carb']:.2f} g carbs, "
            f"{details['total_fats']:.2f} g fats"
        )
        total_calories += details['total_calories']
        total_protein += details['total_protein']
        total_carb += details['total_carb']
        total_fats += details['total_fats']

    output.append("\nDaily Totals:")
    output.append(f"  Calories: {total_calories:.2f}")
    output.append(f"  Protein: {total_protein:.2f} g")
    output.append(f"  Carbs: {total_carb:.2f} g")
    output.append(f"  Fats: {total_fats:.2f} g")
    output.append("\nNote: For optimal energy levels, space your meals evenly throughout the day.")

    # Save output to file.
    with open("meal_plan_output.txt", "w") as file:
        file.write("\n".join(output))
    print("Output saved to meal_plan_output.txt")

    # Read the saved file and send it to the LLM for further adjustments.
    with open("meal_plan_output.txt", "r") as file:
        meal_plan_content = file.read()

    messages = [
        {"role": "system", "content": "You are an expert nutrition assistant."},
        {
            "role": "user",
            "content": (
                f"Based on the following user data:\n"
                f"- Age: {age}\n"
                f"- Gender: {gender}\n"
                f"- Weight: {weight} kg\n"
                f"- Height: {height} cm\n"
                f"- BMR: {bmr:.2f} calories\n"
                f"- TDEE: {tdee:.2f} calories\n"
                f"- Activity Level: {activity_level}\n"
                f"- Goal: {goal}\n"
                f"- Meals per Day: {meals_per_day}\n\n"
                f"Here is the current meal plan:\n\n{meal_plan_content}\n\n"
                "Please adjust the meal plan to better align with the user's data, ensuring it supports their goal of losing weight while maintaining a balanced nutrient profile. "
                "Provide a complete adjusted plan with all meals and their nutritional details. Do not replace items that already fit well in the plan."
            ),
        },
    ]

    ai_msg = llm.invoke(messages)
    print(ai_msg.content)


if __name__ == "__main__":
    main()
