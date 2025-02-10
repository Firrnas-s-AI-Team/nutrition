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
        model="llama-3.1-8b-instant",
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
            # 🥗 Personalized Meal Plan Review & Optimization  

## **Role:**  
You are a highly skilled **nutrition expert** specializing in personalized meal planning. Your task is to **review and optimize** the provided meal plan based on the user's dietary profile.  

## **Review & Optimization Guidelines**  

### **1. Allergy & Food Sensitivity Considerations**  
- Identify and **remove or substitute** any ingredients that could cause allergic reactions.  
- Suggest **safe and nutritionally equivalent alternatives** to maintain balance.  

### **2. Dietary Preferences & Restrictions**  
- **Strictly follow** the user's dietary preferences (e.g., vegan, keto, gluten-free, halal, kosher, etc.).  
- Ensure **compliance with cultural or ethical food choices** (e.g., no pork for halal diets, no dairy for vegans).  
- Avoid **cross-contaminants** that may affect the user’s dietary needs (e.g., hidden gluten sources in condiments).  

### **3. Nutritional Goals & Macros**  
- Optimize **macronutrient (protein, carbs, fats) and micronutrient (vitamins, minerals) intake** based on the user’s health objectives (e.g., weight loss, muscle gain, blood sugar control).  
- Maintain **proper caloric intake and portion sizes** to align with the user’s fitness or medical goals.  
- Ensure **balanced meal composition**, including fiber, healthy fats, and essential nutrients.  

### **4. Meal Variety & Practicality**  
- Provide **a diverse selection of meals** to prevent monotony while keeping the user engaged.  
- Ensure the meals are **practical, accessible, and easy to prepare** based on the user’s lifestyle.  

## **Structured Output Format**  
Deliver the revised meal plan in **JSON format** with the following structure:  

```json



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
    answer = chain.invoke(input_data,max_new_tokens = 5500)
    with open('out2.json','w') as f:
        f.write(answer.content)
    
    # print(answer.content)
 
    idx = answer.content.find('```json')
    idx_final = answer.content.rfind('```')
    js = answer.content[idx + 7: idx_final].strip()
    with open('out.json', 'w') as f:
        f.write(js)
    return js