import pandas as pd
import json
import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from calculation import calculate_bmr, calculate_tdee, generate_meal_plans_for_days

# Load environment variables and set the API key.
load_dotenv()
os.environ['groq_api_key'] = os.getenv('api_key')

INPUT_FILE = 'user_profile.json'
DATA_FILE = 'GPT_data.csv'
OUTPUT_FILE = 'meal_plan_output.json'  # Now saving as a JSON file.

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
    
    # Extract user details.
    name = user_profile['user_profile'].get("name", "User")
    age = user_profile['user_profile']["age"]
    gender = user_profile['user_profile']["gender"]
    weight = user_profile['user_profile']["weight"]
    height = user_profile['user_profile']["height"]
    activity_level = user_profile['user_profile']["activity_level"]
    goal = user_profile['user_profile']["goal"].lower()
    meals_per_day = user_profile['user_profile']["meals_per_day"]
    dietary_preferences = user_profile['user_profile']["dietary_preferences"]
    allergies = user_profile['user_profile']["allergies"]
    num_days = user_profile['user_profile'].get("num_days", 3)
    
    user_preferences = {
        "dislikes": user_profile['user_profile'].get("dislikes", []),
        "allergies": user_profile['user_profile'].get("allergies", []),
        "dietary_restrictions": user_profile['user_profile'].get("dietary_restrictions", [])
    }
    
    # Calculate BMR and TDEE.
    bmr = calculate_bmr(age, gender, weight, height)
    tdee = calculate_tdee(bmr, activity_level)
    
    # Generate multi-day meal plan.
    try:
        # Using vary_across_days=True to maintain a cumulative exclusion set for variety.
        multi_day_plan = generate_meal_plans_for_days(
            num_days, tdee, goal, food_df, meals_per_day, gender,
            user_preferences=user_preferences, vary_across_days=True
        )
    except Exception as e:
        print("Error generating multi-day meal plan:")
        print(e)
        return

    # Build JSON structure following the provided template.
    meal_plan_json = {
        "Name": name,
        "BMR": bmr,
        "TDEE": tdee,
        "Goal": goal,
        "Meals per Day": meals_per_day,
        "Plan Duration": f"{num_days} days",
        "days": []
    }

    for day_key, daily_plan in multi_day_plan.items():
        day_data = {
            "day": day_key,
            "meals": []
        }
        for meal_key, details in daily_plan.items():
            # Create the meal object
            meal_data = {
                "meal_name": meal_key,
                "items": [],
                "total_calories": details["total_calories"],
                "description": "",  # Empty description; can be filled later.
                "ingredients": []   # Empty ingredients list; can be updated later.
            }
            # For each food item in this meal:
            for item in details["items"]:
                item_data = {
                    "name": item["item"],
                    "calories": item["calories"],
                    "protein_grams": item["protein"],
                    "carbs_grams": item["carb"],
                    "fats_grams": item["fats"]
                }
                meal_data["items"].append(item_data)
            day_data["meals"].append(meal_data)
        meal_plan_json["days"].append(day_data)

    # Save the JSON output to the file.
    with open(OUTPUT_FILE, "w") as f:
        json.dump(meal_plan_json, f, indent=2)
    print(f"Output saved to {OUTPUT_FILE}")

    # Read the saved file and send it to the LLM for further adjustments.
    with open(OUTPUT_FILE, "r") as f:
        meal_plan_content = f.read()

    
    
    messages = [
        {"role": "system", "content": "You are an expert nutrition assistant."},
        {
            "role": "user",
            "content": (
                f"Based on the following user data:\n"
                f"- Name: {name}\n"
                f"- Age: {age}\n"
                f"- Gender: {gender}\n"
                f"- Weight: {weight} kg\n"
                f"- Height: {height} cm\n"
                f"- BMR: {bmr:.2f} calories\n"
                f"- TDEE: {tdee:.2f} calories\n"
                f"- Activity Level: {activity_level}\n"
                f"- Goal: {goal}\n"
                f"- Meals per Day: {meals_per_day}\n"
                f"- Plan Duration: {num_days} days\n"
                f"- dietary_preferences: {dietary_preferences}\n"
                f"- allergies: {allergies}\n\n"
                f"Here is the current multi-day meal plan in JSON format:\n\n{meal_plan_content}\n\n"
                "Please adjust the meal plan to better align with the user's data, ensuring it supports their goal of {goal}, dietary preferences: {dietary_preferences}, and allergies: {allergies} while maintaining a balanced nutrient profile. "
                "Provide a complete adjusted plan with all meals and their nutritional details. Do not replace items that already fit well in the plan.\n\n"
                "respnde in json format."
            ),
        },
    ]
    
    ai_msg = llm.invoke(messages)
    print(ai_msg.content)

if __name__ == "__main__":
    main()
