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

return only the number of calories  in json like this:
{{
    "calories":"new value"
}}
Output:
Return the new number of calories only in json
'''
    ai_msg = llm.invoke(prompt)
    return ai_msg.content