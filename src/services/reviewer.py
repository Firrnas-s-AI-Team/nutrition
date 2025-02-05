# from langchain_groq import ChatGroq
# from langchain.prompts import ChatPromptTemplate
# from dotenv import load_dotenv
# load_dotenv()
# import os
# os.environ['GROQ_API_KEY'] = os.getenv('GROQ_API')
# def evaluate_and_modify_meal_plan(user_data, meal_output):
#     # Initialize the LLM model
#     llm = ChatGroq(
#         model="deepseek-r1-distill-llama-70b",
#         temperature=0,
#         max_tokens=6000,
#     )

#     # Define the prompt messages
#     messages = [
#         (
#             "system",
#             "You are a nutrition evaluator. Review the provided meal plan against the user's dietary profile and address all errors and violations. Edit the meal plan to ensure it meets all criteria, and return the corrected plan in JSON format. Provide explanations for each change and include a summary of issues in a markdown table.",
#         ),
#         ("human", f"User Profile: {user_data}"),
#         ("human", f"Here is the meal plan: {meal_output}"),
#     ]

#     # Create the prompt
#     prompt = ChatPromptTemplate.from_messages(messages)

#     # Chain the prompt with the LLM
#     chain = prompt | llm
#     # Invoke the model
#     answer = chain.invoke({
#         'user_profile': user_data,
#         'meal_output': meal_output
#     })
    
#     # Extract and print the answer content
#     print(answer.content)
    
#     # Extract the JSON part from the response and save it
#     idx = answer.content.find('```json')
#     idx_final = answer.content.rfind('```')
#     js = answer.content[idx + 7: idx_final].strip()
#     with open('out.json', 'w') as f:
#         f.write(js)
#     return js

import json
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
load_dotenv()
import os
os.environ['GROQ_API_KEY'] = os.getenv('GROQ_API')

def evaluate_and_modify_meal_plan(user_data, meal_output):
 
    llm = ChatGroq(
        model="deepseek-r1-distill-llama-70b",
        temperature=0,
        max_tokens=6000,
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

After reviewing, provide the corrected meal plan in JSON format. Include:

A clear explanation for each change.

A summary of issues in a markdown table.

Be thorough and ensure the meal plan is safe, compliant, and meets the user's needs.
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
        'target_calories_per_day': user_data_dict.get('target_calories_per_day', 'Not specified')  # استخدام القاموس هنا
    }

 
    answer = chain.invoke(input_data)
    
    print(answer.content)
 
    idx = answer.content.find('```json')
    idx_final = answer.content.rfind('```')
    js = answer.content[idx + 7: idx_final].strip()
    with open('out.json', 'w') as f:
        f.write(js)
    return js