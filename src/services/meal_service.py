import json
from config import settings
from services.llm_service import initialize_llm

def generate_meal_plan(llm, messages):
    ai_msg = llm.invoke(messages)
    idx = ai_msg.content.find("{")  
    idx_final = ai_msg.content.rfind("}") + 1  
    ai_msg = ai_msg.content[idx:idx_final]
    
    with open(settings.OUTPUT_FILE, 'w') as file:
        file.write(ai_msg)
    
    return str(ai_msg)

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