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

def meal_replacer(llm, meal, meal_text):
    prompt = f'''For the given meal:
{meal}

I want to replace it with the following meal from the user:
{meal_text}

Please provide me the new meal information details.

**JSON Only**: Return solely the JSON structure without any additional text or explanations.

Example JSON Template:
{{
    "meal_name": "",
    "items": [
        {{
            "name": "",
            "calories": value in kcal,
            "protein_grams": value in g,
            "carbs_grams": value in g,
            "fats_grams": value in g
        }}
    ]
}}
    
Output:
Return the new meal information as JSON following the structure.
'''
    ai_msg = llm.invoke(prompt)
    return ai_msg.content