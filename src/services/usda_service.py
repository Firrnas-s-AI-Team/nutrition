import json
import requests
from config import settings
from services.llm_service import prepare_llm_messages

def search_usda_food(query):
    """
    Searches the USDA FoodData Central for a food item using the provided query.
    
    Args:
        query (str): The name or query for the food.
        
    Returns:
        dict or None: The first food item found (as a dictionary) or None if not found.
    """
    url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    params = {
        "api_key": settings.USDA_API_KEY,
        "query": query,
        "pageSize": 1
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        if data.get('foods'):
            return data['foods'][0]
    except Exception as e:
        # Optionally log the error
        print(f"Error searching USDA food for query '{query}': {e}")
    return None

def extract_nutrition(usda_data):
    """
    Extracts nutritional information from the USDA API data.
    
    USDA food items include a 'foodNutrients' list that contains nutrient data.
    The relevant nutrient IDs are:
      - 208: Calories (Energy)
      - 203: Protein
      - 205: Carbohydrates
      - 204: Total Fat
    
    Args:
        usda_data (dict): The USDA API response for a food item.
        
    Returns:
        dict: A dictionary containing 'calories', 'protein', 'carbs', and 'fats'.
    """
    nutrient_mapping = {
        208: 'calories',
        203: 'protein',
        205: 'carbs',
        204: 'fats'
    }
    nutrition = {"calories": 0, "protein": 0, "carbs": 0, "fats": 0}
    nutrients = usda_data.get("foodNutrients", [])
    for nutrient in nutrients:
        nutrient_id = nutrient.get("nutrientId")
        if nutrient_id in nutrient_mapping:
            nutrition[nutrient_mapping[nutrient_id]] = nutrient.get("value", 0)
    return nutrition

def generate_meal_plan(llm, datauser_dict, nutrition_needs):
    """
    Generates a meal plan using a language model (LLM) and enriches each meal with USDA nutritional data.
    
    Args:
        llm: An instance of the language model to generate the meal plan.
        datauser_dict (dict): The user's data (preferences, restrictions, etc.).
        nutrition_needs (dict): Additional nutritional needs or constraints.
        
    Returns:
        dict: A meal plan where each meal has been enriched with nutritional information.
        
    The function expects the LLM to return a JSON string structured like:
      {
          "Monday": [
              {"food": "Oatmeal with bananas", ...},
              {"food": "Grilled chicken salad", ...},
              ...
          ],
          "Tuesday": [...],
          ...
      }
    """
    # Prepare messages for the LLM using the user data and nutrition needs.
    messages = prepare_llm_messages(json.dumps(datauser_dict), json.dumps(nutrition_needs))
    response = llm.generate(messages)
    
    try:
        meal_plan = json.loads(response)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding LLM response: {e}")
    
    # Iterate over each day and each meal to enrich with nutritional data.
    for day, meals in meal_plan.items():
        if isinstance(meals, list):
            for meal in meals:
                food_item = meal.get('food')
                if food_item:
                    usda_data = search_usda_food(food_item)
                    if usda_data:
                        nutrition = extract_nutrition(usda_data)
                        meal['nutrition'] = nutrition
                    else:
                        meal['nutrition'] = {"calories": 0, "protein": 0, "carbs": 0, "fats": 0}
        else:
            print(f"Warning: Expected a list of meals for {day} but got {type(meals)}.")
    
    return meal_plan

def meal_replacer(llm, new_meal_text):
    """
    Generates a replacement meal using the language model and enriches it with nutritional data.
    
    Args:
        llm: An instance of the language model.
        new_meal_text (str): The text input for the new meal.
        
    Returns:
        str: A JSON string of the new meal enriched with nutritional information.
        
    The function expects the LLM to return a JSON string structured like:
      {"food": "Some meal description", ...}
    """
    messages = prepare_llm_messages(new_meal_text, "")
    response = llm.generate(messages)
    
    try:
        new_meal = json.loads(response)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error decoding LLM response: {e}")
    
    food_item = new_meal.get('food')
    if food_item:
        usda_data = search_usda_food(food_item)
        if usda_data:
            nutrition = extract_nutrition(usda_data)
            new_meal['nutrition'] = nutrition
        else:
            new_meal['nutrition'] = {"calories": 0, "protein": 0, "carbs": 0, "fats": 0}
    
    return json.dumps(new_meal)
