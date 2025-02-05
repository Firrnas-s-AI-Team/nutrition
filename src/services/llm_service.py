from langchain_groq import ChatGroq
from config import settings

def initialize_llm():
    llm = ChatGroq(
        temperature=0.2,
        model_name="llama-3.3-70b-versatile",
        api_key=settings.GROQ_API_KEY
    )
    return llm

def prepare_llm_messages(datauser_text, example_response_text):
    messages = [
    {"role": "system", "content": "You are an expert nutrition assistant with a focus on precision and dietary needs."},
    {
        "role": "user",
        "content": (
            f'''Task:
Generate a personalized weekly meal plan in JSON format to help the user lose weight while maintaining balanced nutrition.

Input Data:
{datauser_text}

Instructions:
1. **Follow User Data**: Use the number of meals and all variables provided in `datauser`.
2. **Complete Week**: Include meal plans for all seven days (Monday to Sunday).
3. **Realistic Choices**: Use common, real-world food items with accurate nutritional values. Avoid highly processed foods.
4. **Provide Alternatives**: Offer alternatives for any specified allergies or dislikes. Ensure there are safe options for any allergic reactions listed.
5. **Adhere to Dietary Preferences**: Strictly follow all dietary preferences specified by the user, such as vegetarian, vegan, gluten-free, paleo, keto, etc.
   - If "Paleo" is preferred, exclude grains, legumes, and processed foods.
   - If "Gluten-Free" is requested, exclude all gluten-containing items and suggest gluten-free alternatives.
   - If "Vegan" is requested, avoid all animal products, including dairy and eggs.
6. **Accommodate Allergies**: Ensure all meal plans avoid ingredients that users are allergic to and provide safe alternatives where necessary. 
7. **Target Calories**: The meal plan should adhere to the daily calorie target specified by the user. Adjust portions accordingly to meet the user's goals (e.g., weight loss, weight gain).
8. **Balanced Macronutrients**: Ensure that each meal provides a balanced amount of protein, carbs, and fats according to dietary guidelines and the user’s preferences.
9. **Nutritional Consistency**: Ensure that the daily calorie total is close to the target (e.g., for weight loss or gain), and include nutrient-dense, filling meals to support the user’s health goals.
10. **JSON Only**: Return solely the JSON structure without any additional text or explanations.

Example JSON Template:
{example_response_text}

Output:
Return the complete meal plans for all seven days (Monday to Sunday) as JSON following the structure and data provided in `datauser`.
'''
        )
    }
]

    return messages
