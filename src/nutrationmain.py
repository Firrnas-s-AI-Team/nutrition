# from BMR import (
#     calc_bmr,
#     calc_total_calories_in_day,
#     allocate_grams,
#     recommend_meals,
#     adjust_macronutrient_ratios
# )
# import pandas as pd
# import subprocess
# import json
# from langchain_groq import ChatGroq
# from langchain_ollama.llms import OllamaLLM
# import os


# # Constants
# INPUT_FILE = 'datauser.json'
# OUTPUT_FILE = 'nutrition_plan.json'
# MODEL_NAME = "deepseek-r1:32b"

# def initialize_llm():
#     """
#     Initialize the Language Model.
    
#     Returns:
#         An instance of the LLM.
#     """
#     llm = ChatGroq(
#         temperature=0.2,
#         model_name="llama-3.1-8b-instant",
#         api_key='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'
#     )
#     # Alternatively, you can use OllamaLLM
#     # llm = OllamaLLM(model=MODEL_NAME)
#     return llm

# def read_file_as_text(file_path):
#     """
#     Read and return the content of a file as plain text.
    
#     Args:
#         file_path (str): Path to the file.
    
#     Returns:
#         str: Content of the file as a string.
#     """
#     try:
#         with open(file_path, 'r') as file:
#             data = file.read()
#         print(f"Loaded data from {file_path}")
#         return data
#     except FileNotFoundError:
#         print(f"Error: {file_path} not found.")
#         return ""
#     except Exception as e:
#         print(f"Error reading {file_path}: {e}")
#         return ""

# def prepare_llm_messages(datauser_text, example_response_text):
#     """
#     Prepare the messages to be sent to the LLM for generating a meal plan.
    
#     Args:
#         datauser_text (str): User profile data as a string.
#         example_response_text (str): Example response template as a string.
    
#     Returns:
#         list: List of message dictionaries.
#     """
#     messages = [
#         {"role": "system", "content": "You are an expert nutrition assistant."},
#         {
#             "role": "user",
#             "content": (
#                 f'''Task:
# Generate a personalized weekly meal plan in JSON format to help the user lose weight while maintaining balanced nutrition.

# Input Data:
# #json:
# {datauser_text}

# Instructions:
# 1. **Follow User Data**: Use the number of meals and all variables provided in `datauser`. Each meal must reflect the user's preferences, dietary restrictions, and nutritional goals.
# 2. **Complete Week**: Include meal plans for all seven days (Monday to Sunday).
# 3. **Realistic Choices**: Use common, real-world food items with accurate nutritional values.
# 4. **Provide Alternatives**: Offer alternatives for any specified allergies or dislikes.
# 5. **JSON Only**: Return solely the JSON structure without any additional text or explanations.

# Example JSON Template:
# #json:
# {example_response_text}

# Output:
# Return the complete meal plans for all seven days (Monday to Sunday) as JSON following the structure and data provided in `datauser`. Do not include any extra information.
#                 '''
#             )
#         }
#     ]
#     return messages

# def generate_meal_plan(llm, messages):
#     """
#     Invoke the LLM to generate a meal plan based on the provided messages.
    
#     Args:
#         llm: The initialized Language Model.
#         messages (list): List of message dictionaries.
    
#     Returns:
#         str: The generated meal plan in JSON format.
#     """
#     ai_msg = llm.invoke(messages)
#     return ai_msg.content

# def meal_replacer(llm, meal, meal_text):
#     """
#     Replace a specified meal with new meal details using the LLM.
    
#     Args:
#         llm: The initialized Language Model.
#         meal (str): The original meal description.
#         meal_text (str): The new meal description to replace with.
    
#     Returns:
#         str: The new meal information in JSON format.
#     """
#     prompt = f'''For the given meal:
# {meal}

# I want to replace it with the following meal from the user:
# {meal_text}

# Please provide me the new meal information details.

# **JSON Only**: Return solely the JSON structure without any additional text or explanations.

# Example JSON Template:
# #json
# {{
#     "meal_name": "",
#     "items": [
#         {{
#             "name": "",
#             "calories": value in kcal,
#             "protein_grams": value in g,
#             "carbs_grams": value in g,
#             "fats_grams": value in g
#         }}
#     ]
# }}
    
# Output:
# Return the new meal information as JSON following the structure. Do not include any extra information.
# '''
#     ai_msg = llm.invoke(prompt)
#     return ai_msg.content



# def save_nutrition_plan(nutrition_plan, output_file):
#     """
#     Save the generated nutrition plan to a JSON file.
    
#     Args:
#         nutrition_plan (str): The nutrition plan in JSON format.
#         output_file (str): Path to the output JSON file.
#     """
#     try:
#         with open(output_file, 'w') as file:
#             file.write(nutrition_plan)
#         print(f"Nutrition plan saved to {output_file}")
#     except Exception as e:
#         print(f"Error saving nutrition plan: {e}")

# def main():
#     # Initialize the Language Model
#     llm = initialize_llm()
    
#     # Read user data and example response as plain text
#     datauser_text = read_file_as_text("datauser.json")
#     example_response_text = read_file_as_text("example_response.json")
    
#     if not datauser_text or not example_response_text:
#         print("Error: Missing required data. Exiting.")
#         return
    
#     # Prepare messages for LLM
#     messages = prepare_llm_messages(datauser_text, example_response_text)
    
#     # Generate meal plan
#     print("Generating meal plan...")
#     nutrition_plan = generate_meal_plan(llm, messages)
#     print("Generated Nutrition Plan:")
#     print(nutrition_plan)
    
#     # Save the nutrition plan to a file
#     save_nutrition_plan(nutrition_plan, OUTPUT_FILE)
    
#     # Demonstrate meal replacement

#     meal_text = '''- 2 eggs and 150 g Broccoli.'''
    
#     meal = '''- Chicken Breast: 108.41g (178.88 calories, 33.61g protein, 0.00g carb, 3.90g fats)
#                 - Broccoli: 409.20g (139.13 calories, 11.46g protein, 28.64g carb, 1.64g fats)
#                 Total Calories: 318.01
#                 Total Protein: 45.07g
#                 Total Carbs: 28.64g
#                 Total Fats: 5.54g'''

#     print(meal_replacer(llm, meal, meal_text))
    

# if __name__ == "__main__":
#     main()



from BMR import (
    calc_bmr,
    calc_total_calories_in_day,
    allocate_grams,
    recommend_meals,
    adjust_macronutrient_ratios
)
import pandas as pd
import subprocess
import json
from langchain_groq import ChatGroq
from langchain_ollama.llms import OllamaLLM
import os


# Constants
INPUT_FILE = 'datauser.json'
OUTPUT_FILE = 'nutrition_plan.json'
MODEL_NAME = "deepseek-r1:32b"

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
    # Alternatively, you can use OllamaLLM
    # llm = OllamaLLM(model=MODEL_NAME)
    return llm

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
        print(f"Loaded data from {file_path}")
        return data
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return ""
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return ""

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
    return ai_msg.content

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

def save_nutrition_plan(nutrition_plan, output_file):
    """
    Save the generated nutrition plan to a JSON file.
    
    Args:
        nutrition_plan (str): The nutrition plan in JSON format.
        output_file (str): Path to the output JSON file.
    """
    try:
        with open(output_file, 'w') as file:
            file.write(nutrition_plan)
        print(f"Nutrition plan saved to {output_file}")
    except Exception as e:
        print(f"Error saving nutrition plan: {e}")

def chat_with_user(llm):
    """
    Interactive chat function to allow the user to ask questions or modify meals.
    
    Args:
        llm: The initialized Language Model.
    """
    print("Welcome to the Nutrition Chatbot! Type 'exit' to end the chat.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
        
        # Prepare the prompt for the LLM
        prompt = f'''User: {user_input}

You are an expert nutrition assistant. Provide a helpful response to the user's query or request. If the user wants to modify a meal, provide the updated meal details in JSON format.

**JSON Only**: If the response includes meal details, return solely the JSON structure without any additional text or explanations.

Output:
Respond to the user's query or provide the updated meal details in JSON format if applicable.
'''
        
        # Get the response from the LLM
        ai_msg = llm.invoke(prompt)
        print(f"Nutrition Assistant: {ai_msg.content}")

def main():
    # Initialize the Language Model
    llm = initialize_llm()
    
    # Read user data and example response as plain text
    datauser_text = read_file_as_text("datauser.json")
    example_response_text = read_file_as_text("example_response.json")
    
    if not datauser_text or not example_response_text:
        print("Error: Missing required data. Exiting.")
        return
    
    # Prepare messages for LLM
    messages = prepare_llm_messages(datauser_text, example_response_text)
    
    # Generate meal plan
    print("Generating meal plan...")
    nutrition_plan = generate_meal_plan(llm, messages)
    print("Generated Nutrition Plan:")
    print(nutrition_plan)
    
    # Save the nutrition plan to a file
    save_nutrition_plan(nutrition_plan, OUTPUT_FILE)
    
    # Demonstrate meal replacement
    meal_text = '''- 2 eggs and 150 g Broccoli.'''
    meal = '''- Chicken Breast: 108.41g (178.88 calories, 33.61g protein, 0.00g carb, 3.90g fats)
                - Broccoli: 409.20g (139.13 calories, 11.46g protein, 28.64g carb, 1.64g fats)
                Total Calories: 318.01
                Total Protein: 45.07g
                Total Carbs: 28.64g
                Total Fats: 5.54g'''
    print(meal_replacer(llm, meal, meal_text))
    
     
    chat_with_user(llm)

if __name__ == "__main__":
    main()