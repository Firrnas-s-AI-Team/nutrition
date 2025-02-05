from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import JSONResponse
import json
import json_repair
from models.schemas import ReplaceMealRequest, ChatRequest, ChatResponse, DataUser
from services.llm_service import initialize_llm, prepare_llm_messages
from services.meal_service import generate_meal_plan, meal_replacer
from services.chat_service import initialize_chat_chain, get_memory, get_chat_history
from utils.file_utils import read_file_as_text
from config import settings
from services.reviewer import evaluate_and_modify_meal_plan


app = FastAPI()

@app.post("/generate_meal_plan")
async def generate_meal_plan_api(data_user: DataUser = Body(...)):
    llm = initialize_llm()
    # Convert the Pydantic model to JSON string
    datauser_text = data_user.json()
    example_response_text = read_file_as_text(settings.EXAMPLE_RESPONSE_FILE)
    
    messages = prepare_llm_messages(datauser_text, example_response_text)
    nutrition_plan = generate_meal_plan(llm, messages)
    # nutrition_plan = str(nutrition_plan)
    plan_json = evaluate_and_modify_meal_plan(datauser_text,nutrition_plan)
    try:
        plan_json = json_repair.loads(plan_json)
        return JSONResponse(content=plan_json)
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate valid JSON meal plan. Error: {e}"
        )

@app.post("/replace_meal")
async def replace_meal_api(request: ReplaceMealRequest):
    llm = initialize_llm()
    new_meal_info = meal_replacer(llm, request.new_meal_text)
    return {"new_meal": json.loads(new_meal_info)}

@app.post("/chat")
async def chat_api(request: ChatRequest):
    with open(settings.OUTPUT_FILE, 'r') as file:
        current_meal_plan = file.read()
    
    llm = initialize_llm()
    conversation = initialize_chat_chain(
        llm, 
        request.session_id, 
        current_meal_plan,
        request.chat_history
    )
    
    response = conversation.predict(human_input=request.user_input)
    memory = get_memory(request.session_id)
    chat_history = get_chat_history(memory)
    
    return ChatResponse(
        response=response,
        chat_history=chat_history
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)