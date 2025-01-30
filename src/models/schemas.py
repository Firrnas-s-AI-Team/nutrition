from pydantic import BaseModel
from typing import List, Dict, Optional

class Meal(BaseModel):
    meal_name: str
    items: List[Dict[str, str]]

class ReplaceMealRequest(BaseModel):
    new_meal_text: str

class ChatRequest(BaseModel):
    user_input: str
    session_id: str
    chat_history: Optional[List[Dict[str, str]]] = None

class ChatResponse(BaseModel):
    response: str
    chat_history: List[Dict[str, str]]