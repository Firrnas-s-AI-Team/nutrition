from pydantic import BaseModel
from typing import List, Dict

class Meal(BaseModel):
    meal_name: str
    items: List[Dict[str, str]]

class ReplaceMealRequest(BaseModel):
    original_meal: str
    new_meal_text: str

class ChatRequest(BaseModel):
    user_input: str
    session_id: str