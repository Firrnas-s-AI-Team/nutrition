import json
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import groq
load_dotenv()
import os
os.environ['GROQ_API_KEY'] = os.getenv('GROQ_API')

def evaluate_and_modify_meal_plan(user_data, meal_output):
 
    llm = ChatGroq(
        model="deepseek-r1-distill-llama-70b",
        temperature=0,
        max_tokens=5000,
    )

 
    try:
        user_data_dict = json.loads(user_data)  
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse user_data as JSON: {e}")
 
    messages = [
        (
            "system",
            '''
            You are a nutrition expert. Review the provided meal plan based on the user's dietary profile. Ensure the following:

Allergies: Remove or substitute any ingredients that could cause allergic reactions. Suggest safe alternatives if needed.

Dietary Preferences: Strictly follow the user's dietary preferences (e.g., vegan, gluten-free, etc.). For example, if the user is vegan, exclude all animal products like meat, dairy, and eggs.

Nutritional Needs: Ensure each meal aligns with the user's nutritional goals and preferences.

After reviewing, provide the corrected meal plan in JSON format.
        '''


        ),
        ("human", "User Profile: {user_profile}"),  
        ("human", "Here is the meal plan: {meal_output}"),
    ]

 
    prompt = ChatPromptTemplate.from_messages(messages)

 
    chain = prompt | llm

 
    input_data = {
        'user_profile': json.dumps(user_data_dict),   
        'meal_output': meal_output,
        'target_calories_per_day': user_data_dict.get('target_calories_per_day', 'Not specified') 
    }
    try:
        answer = chain.invoke(input_data,max_new_tokens = 5500)
    except groq.APIStatusError:
      return meal_output  
    
    # print(answer.content)
 
    idx = answer.content.find('```json')
    idx_final = answer.content.rfind('```')
    js = answer.content[idx + 7: idx_final].strip()
    with open('out.json', 'w') as f:
        f.write(js)
    return js