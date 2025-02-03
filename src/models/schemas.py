from pydantic import BaseModel
from typing import List, Dict, Optional

class Meal(BaseModel):
    meal_name: str
    items: List[Dict[str, str]]

class FoodPreferences(BaseModel):
    liked_foods: List[str]
    disliked_foods: List[str]
    allergies: List[str]

class DietaryRestrictions(BaseModel):
    avoid: List[str]
    must_include: List[str]

class FlavorPreferences(BaseModel):
    spicy: bool
    sweet: bool
    savory: bool

class UserProfile(BaseModel):
    name: str
    age: int
    gender: str
    weight: float
    height: float
    activity_level: str
    goal: str
    target_weight: float
    meals_per_day: int
    medical_conditions: List[str]
    allergies: List[str]
    dietary_preferences: List[str]
    inbody_test_file: Optional[str] = None  # رابط ملف اختبار InBody

class MealDetails(BaseModel):
    items: List[str] = []
    total_calories: float = 0
    macronutrients: dict = {}
    personalization_notes: str = ""

class NutritionPlan(BaseModel):
    daily_details: str
    meal_breakdown: dict
    daily_total: dict

class PersonalizationGuidelines(BaseModel):
    preference_accommodation: str
    alternative_meal_strategy: str
    feedback_mechanism: str

class DataUser(BaseModel):
    user_profile: UserProfile



class ReplaceMealRequest(BaseModel):
    new_meal_text: str

class ChatRequest(BaseModel):
    user_input: str
    session_id: str
    chat_history: Optional[List[Dict[str, str]]] = None

class ChatResponse(BaseModel):
    response: str
    chat_history: List[Dict[str, str]]