from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from typing import List, Dict
from BMR import (
    calc_bmr,
    calc_total_calories_in_day,
    allocate_grams,
    recommend_meals,
    adjust_macronutrient_ratios
)
import json
from langchain_groq import ChatGroq

# Initialize FastAPI app
app = FastAPI()

# Constants
INPUT_FILE = 'assets/datauser.json'
OUTPUT_FILE = 'assets/nutrition_plan.json'
EXAMPLE_RESPONSE_FILE = 'assets/example_response.json'
# MODEL_NAME = "deepseek-r1:32b"

# Pydantic models for request bodies
class Meal(BaseModel):
    meal_name: str
    items: List[Dict[str, str]]

class ReplaceMealRequest(BaseModel):
    original_meal: str
    new_meal_text: str

class ChatRequest(BaseModel):
    user_input: str

# Initialize the Language Model (LLM)
def initialize_llm():
    """
    Initialize the Language Model.
    
    Returns:
        An instance of the LLM.
    """
    llm = ChatGroq(
        temperature=0.2,
        model_name="llama-3.1-8b-instant",
        api_key='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'
    )
    return llm

# Utility function to read file content
def read_file_as_text(file_path):
    """
    Read and return the content of a file as plain text.
    
    Args:
        file_path (str): Path to the file.
    
    Returns:
        str: Content of the file as a string.
    """
    try:
        with open(file_path, 'r') as file:
            data = file.read()
        return data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File {file_path} not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading {file_path}: {e}")

# Prepare messages for LLM to generate meal plan
def prepare_llm_messages(datauser_text, example_response_text):
    """
    Prepare the messages to be sent to the LLM for generating a meal plan.
    
    Args:
        datauser_text (str): User profile data as a string.
        example_response_text (str): Example response template as a string.
    
    Returns:
        list: List of message dictionaries.
    """
    messages = [
        {"role": "system", "content": "You are an expert nutrition assistant."},
        {
            "role": "user",
            "content": (
                f'''Task:
Generate a personalized weekly meal plan in JSON format to help the user lose weight while maintaining balanced nutrition.

Input Data:
#json:
{datauser_text}

Instructions:
1. **Follow User Data**: Use the number of meals and all variables provided in `datauser`. Each meal must reflect the user's preferences, dietary restrictions, and nutritional goals.
2. **Complete Week**: Include meal plans for all seven days (Monday to Sunday).
3. **Realistic Choices**: Use common, real-world food items with accurate nutritional values.
4. **Provide Alternatives**: Offer alternatives for any specified allergies or dislikes.
5. **JSON Only**: Return solely the JSON structure without any additional text or explanations.

Example JSON Template:
#json:
{example_response_text}

Output:
Return the complete meal plans for all seven days (Monday to Sunday) as JSON following the structure and data provided in `datauser`. Do not include any extra information.
                '''
            )
        }
    ]
    return messages

# Generate meal plan using LLM
def generate_meal_plan(llm, messages):
    """
    Invoke the LLM to generate a meal plan based on the provided messages.
    
    Args:
        llm: The initialized Language Model.
        messages (list): List of message dictionaries.
    
    Returns:
        str: The generated meal plan in JSON format.
    """
    ai_msg = llm.invoke(messages)
    idx = ai_msg.content.find("{")  
    idx_final = ai_msg.content.rfind("}") + 1  
    ai_msg = ai_msg.content[idx:idx_final]
    with open(OUTPUT_FILE, 'w') as file:
        file.write(ai_msg)
    
    return str(ai_msg)

# Replace a meal in the plan using LLM
def meal_replacer(llm, meal, meal_text):
    """
    Replace a specified meal with new meal details using the LLM.
    
    Args:
        llm: The initialized Language Model.
        meal (str): The original meal description.
        meal_text (str): The new meal description to replace with.
    
    Returns:
        str: The new meal information in JSON format.
    """
    prompt = f'''For the given meal:
{meal}

I want to replace it with the following meal from the user:
{meal_text}

Please provide me the new meal information details.

**JSON Only**: Return solely the JSON structure without any additional text or explanations.

Example JSON Template:
#json
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
Return the new meal information as JSON following the structure. Do not include any extra information.
'''
    ai_msg = llm.invoke(prompt)
    return ai_msg.content

# API endpoint to generate meal plan
@app.get("/generate_meal_plan")
async def generate_meal_plan_api():
    """
    API to generate and return the full meal plan.
    """
    llm = initialize_llm()
    datauser_text = read_file_as_text(INPUT_FILE)
    example_response_text = read_file_as_text(EXAMPLE_RESPONSE_FILE)
    
    messages = prepare_llm_messages(datauser_text, example_response_text)
    nutrition_plan = generate_meal_plan(llm, messages)
    
    # Debug: Print the generated plan
    print("Generated Plan:", nutrition_plan)
    
    try:
        # Attempt to parse the plan as JSON
        plan_json = json.loads(nutrition_plan)
        
        # Return the JSON directly
        return JSONResponse(content=plan_json)
    except json.JSONDecodeError as e:
        # If not valid JSON, return an error message
        raise HTTPException(status_code=500, detail=f"Failed to generate valid JSON meal plan. Error: {e}")
    

# API endpoint to replace a meal
@app.post("/replace_meal")
async def replace_meal_api(request: ReplaceMealRequest):
    """
    API to replace a meal in the plan.
    """
    llm = initialize_llm()
    new_meal_info = meal_replacer(llm, request.original_meal, request.new_meal_text)
    
    return {"new_meal": json.loads(new_meal_info)}

# API endpoint for interactive chat
@app.post("/chat")
async def chat_api(request: ChatRequest):
    """
    API for interactive chat with the user.
    """
    llm = initialize_llm()
    prompt = f'''User: {request.user_input}

You are an expert nutrition assistant. Provide a helpful response to the user's query or request. If the user wants to modify a meal, provide the updated meal details in JSON format.

**JSON Only**: If the response includes meal details, return solely the JSON structure without any additional text or explanations.

Output:
Respond to the user's query or provide the updated meal details in JSON format if applicable.
'''
    ai_msg = llm.invoke(prompt)
    return {"response": ai_msg.content}

# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)