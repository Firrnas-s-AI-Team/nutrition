import json
from config import settings
from services.llm_service import initialize_llm
from langchain.prompts import ChatPromptTemplate
import time
import json_repair
def generate_meal_plan(llm, data, nutritional_needs):
    # Extract user_profile from the nested structure
    user_profile = data["user_profile"]
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekly_plan = []
    
    for day in days:
        template = """
        You are a professional nutritionist creating a personalized meal plan for {day}. Use the following user details:
        - Age: {age}
        - Gender: {gender}
        - Weight: {weight}kg, Height: {height}cm
        - Activity Level: {activity_level}
        - Goal: {goal} (Target: {target_weight}kg)
        - Dietary Preferences: {dietary_preferences}
        - Allergies: {allergies}
        - Medical Conditions: {medical_conditions}
        Daily Nutritional Targets (must be met within a 5% margin):
        {nutritional_needs}
        STRICT RULES:
        1. Create EXACTLY {meals_per_day} meals.
        2. ONLY use ingredients that match dietary preferences: {dietary_preferences}.
        3. ABSOLUTELY avoid all allergens: {allergies}.
        4. Meet nutritional targets within a 5% margin.
        5. Use correct units:
            - Calories: "XXX kcal"
            - Protein: "XXX g"
            - Carbs: "XXX g"
            - Fats: "XXX g"
        For each meal, evenly distribute daily calories, ensure adequate protein, and use nutrient-dense whole foods. Verify every ingredient against restrictions and adjust portions accordingly.
        OUTPUT ONLY in the EXACT JSON format below with no extra text:
        {{
            "day": "{day}",
            "meals": [
                {{
                    "meal_name": "Meal Name",
                    "items": [
                        {{
                            "name": "Food Item",
                            "calories": "XXX kcal",
                            "protein": "XXX g",
                            "carbs": "XXX g",
                            "fats": "XXX g"
                        }}
                    ],
                    "total_calories": "XXX kcal",
                    "description": "Brief description",
                    "ingredients": [
                        "ingredient1 with amount",
                        "ingredient2 with amount"
                    ]
                }}
            ],
            "daily_totals": {{
                "total_calories": "XXX kcal",
                "total_protein": "XXX g",
                "total_carbs": "XXX g",
                "total_fats": "XXX g"
            }}
        }}
        """
        
        # Convert lists to strings for template formatting
        medical_conditions_str = ", ".join(user_profile["medical_conditions"]) if user_profile["medical_conditions"] else "None"
        allergies_str = ", ".join(user_profile["allergies"]) if user_profile["allergies"] else "None"
        dietary_preferences_str = ", ".join(user_profile["dietary_preferences"]) if user_profile["dietary_preferences"] else "None"
        
        prompt = ChatPromptTemplate.from_template(template)
        messages = prompt.format_messages(
            day=day,
            age=user_profile["age"],
            gender=user_profile["gender"],
            weight=user_profile["weight"],
            height=user_profile["height"],
            activity_level=user_profile["activity_level"],
            goal=user_profile["goal"],
            target_weight=user_profile["target_weight"],
            dietary_preferences=dietary_preferences_str,
            allergies=allergies_str,
            medical_conditions=medical_conditions_str,
            nutritional_needs=json.dumps(nutritional_needs),
            meals_per_day=user_profile["meals_per_day"]
        )
        
        response = llm.invoke(messages)
        time.sleep(4)
        try:
            day_plan = json.loads(response.content)
            weekly_plan.append(day_plan)
            print(f"Generated meal plan for {day}")
        except json.JSONDecodeError as e:
            print(f"Error parsing meal plan for {day}: {e}")
            idx = response.content.find('```json')
            final_idx = response.content.rfind('```')
            plan = response.content[idx+8:final_idx].strip()
            day_plan = json_repair.loads(plan)
            weekly_plan.append(day_plan)
            continue
    
    return weekly_plan

def meal_replacer(llm, meal_text):
    prompt = f'''
Calculate the total calories for the following meal provided by the user:
{meal_text}

Return only the total number of calories in JSON format, like this:
{{
    "calories": "total_calories"
}}
# Rules:
1- Do not include any additional text, explanations, or formatting outside the JSON.
2- Ensure the output is valid JSON and contains only the calories key with the calculated value.

# Output:
{{
    "calories": "total_calories"
}}
'''
    ai_msg = llm.invoke(prompt)
    return ai_msg.content