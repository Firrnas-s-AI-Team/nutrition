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
from services.nutriton_service import get_nutritional_needs

app = FastAPI()

@app.post("/generate_meal_plan")
async def generate_meal_plan_api(data_user: DataUser = Body(...)):
    llm = initialize_llm()
    datauser_dict = data_user.model_dump()
    nutrition_needs = get_nutritional_needs(datauser_dict)
    nutrition_plan = generate_meal_plan(llm, datauser_dict, nutrition_needs)
    
    try:
        # Ensure the response is properly serialized
        response_json = json.dumps(nutrition_plan, ensure_ascii=False)
        return JSONResponse(content=json.loads(response_json))
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