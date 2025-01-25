# import gradio as gr
# import json
# import subprocess
# from datetime import datetime
# from pathlib import Path
# import traceback
#
# DATA_FILE = 'C:\\Users\\ahmed\\PycharmProjects\\nutrition\\assets\\datausers.json'
# MODEL_NAME = "deepseek-r1:1.5b"
#
#
# def calculate_bmi(weight, height):
#     height_m = height / 100
#     bmi = weight / (height_m ** 2)
#     return round(bmi, 2)
#
#
# def format_meal_plan(plan_text):
#     days = []
#     current_day = None
#
#     for line in plan_text.split('\n'):
#         if 'Day' in line:
#             if current_day:
#                 days.append(current_day)
#             current_day = {'title': line.strip(), 'meals': []}
#         elif line.strip().startswith(('Breakfast:', 'Lunch:', 'Dinner:', 'Snack:')):
#             if current_day:
#                 meal_type, meal_content = line.split(':', 1)
#                 current_day['meals'].append({
#                     'type': meal_type.strip(),
#                     'content': meal_content.strip()
#                 })
#
#     if current_day:
#         days.append(current_day)
#
#     return days
#
#
# def save_user_profile(name, age, gender, weight, height, activity_level, goal,
#                       target_weight, daily_calories, meals_per_day,
#                       allergies, liked_foods, disliked_foods):
#     user_data = {
#         "user_profile": {
#             "name": name,
#             "age": age,
#             "gender": gender,
#             "weight": weight,
#             "height": height,
#             "activity_level": activity_level,
#             "goal": goal,
#             "target_weight": target_weight,
#             "daily_calorie_target": daily_calories,
#             "meals_per_day": meals_per_day,
#             "food_preferences": {
#                 "allergies": [a.strip() for a in allergies.split(',') if a.strip()],
#                 "liked_foods": [f.strip() for f in liked_foods.split(',') if f.strip()],
#                 "disliked_foods": [f.strip() for f in disliked_foods.split(',') if f.strip()]
#             }
#         }
#     }
#
#     with open(DATA_FILE, 'w', encoding='utf-8') as f:
#         json.dump(user_data, f, indent=4)
#
#     return "Profile saved successfully!"
#
#
# def generate_plan():
#     try:
#         with open(DATA_FILE, 'r', encoding='utf-8') as f:
#             user_data = json.load(f)
#
#         bmi = calculate_bmi(user_data['user_profile']['weight'],
#                             user_data['user_profile']['height'])
#         water_intake = round((user_data['user_profile']['weight'] * 0.035), 2)
#
#         prompt = f"""Create a 7-day meal plan for {user_data['user_profile']['name']}:
# Profile:
# - Age: {user_data['user_profile']['age']}
# - Gender: {user_data['user_profile']['gender']}
# - Weight: {user_data['user_profile']['weight']} kg
# - Height: {user_data['user_profile']['height']} cm
# - BMI: {bmi}
# - Activity: {user_data['user_profile']['activity_level']}
# - Goal: {user_data['user_profile']['goal']}
# - Target Weight: {user_data['user_profile']['target_weight']} kg
# - Daily Calories: {user_data['user_profile']['daily_calorie_target']}
# - Meals/Day: {user_data['user_profile']['meals_per_day']}
# - Allergies: {', '.join(user_data['user_profile']['food_preferences']['allergies'])}
# - Liked Foods: {', '.join(user_data['user_profile']['food_preferences']['liked_foods'])}
# - Disliked Foods: {', '.join(user_data['user_profile']['food_preferences']['disliked_foods'])}
#
# Please provide a structured 7-day meal plan with:
# Day 1:
# Breakfast: [meal] ([calories] cal)
# Lunch: [meal] ([calories] cal)
# Dinner: [meal] ([calories] cal)
# Snack: [meal] ([calories] cal)
#
# [Continue for all 7 days]"""
#
#         result = subprocess.run(
#             ["ollama", "run", MODEL_NAME],
#             input=prompt,
#             capture_output=True,
#             text=True,
#             check=True
#         )
#
#         # Save chat history
#         chat_history = {
#             "user_profile": user_data["user_profile"],
#             "generated_plan": result.stdout,
#             "timestamp": str(datetime.now())
#         }
#
#         history_file = 'chat_history.json'
#         if Path(history_file).exists():
#             with open(history_file, 'r', encoding='utf-8') as f:
#                 history = json.load(f)
#         else:
#             history = []
#
#         history.append(chat_history)
#         with open(history_file, 'w', encoding='utf-8') as f:
#             json.dump(history, f, indent=4)
#
#         # Format plan for display
#         days = format_meal_plan(result.stdout)
#         html_output = f"""
#         <div class="p-4">
#             <div class="mb-4 p-3 bg-blue-100 rounded">
#                 <h2 class="text-xl font-bold">Profile Summary</h2>
#                 <p>Name: {user_data['user_profile']['name']}</p>
#                 <p>BMI: {bmi}</p>
#                 <p>Daily Water Intake: {water_intake} L</p>
#             </div>
#
#             <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
#         """
#
#         for day in days:
#             html_output += f"""
#                 <div class="p-4 bg-white rounded shadow">
#                     <h3 class="font-bold mb-2">{day['title']}</h3>
#                     <ul class="space-y-2">
#             """
#
#             for meal in day['meals']:
#                 html_output += f"""
#                         <li>
#                             <span class="font-semibold">{meal['type']}:</span>
#                             <span>{meal['content']}</span>
#                         </li>
#                 """
#
#             html_output += """
#                     </ul>
#                 </div>
#             """
#
#         html_output += """
#             </div>
#         </div>
#         """
#
#         return html_output
#
#     except Exception as e:
#         return f"Error: {str(e)}\n{traceback.format_exc()}"
#
#
# def chat_with_model(message, history):
#     try:
#         result = subprocess.run(
#             ["ollama", "run", MODEL_NAME],
#             input=message,
#             capture_output=True,
#             text=True,
#             check=True
#         )
#         return result.stdout.strip()
#     except Exception as e:
#         return f"Error: {str(e)}"
#
#
# # Create Gradio interface
# with gr.Blocks(title="Nutrition Planning System") as demo:
#     with gr.Tab("User Profile"):
#         with gr.Row():
#             with gr.Column():
#                 name = gr.Textbox(label="Name")
#                 age = gr.Number(label="Age")
#                 gender = gr.Dropdown(choices=["Male", "Female", "Other"], label="Gender")
#                 weight = gr.Number(label="Weight (kg)")
#                 height = gr.Number(label="Height (cm)")
#                 activity = gr.Dropdown(
#                     choices=["Sedentary", "Light", "Moderate", "Very Active"],
#                     label="Activity Level"
#                 )
#
#             with gr.Column():
#                 goal = gr.Dropdown(
#                     choices=["Weight Loss", "Maintenance", "Muscle Gain"],
#                     label="Goal"
#                 )
#                 target = gr.Number(label="Target Weight (kg)")
#                 calories = gr.Number(label="Daily Calories")
#                 meals = gr.Number(label="Meals per Day")
#                 allergies = gr.Textbox(label="Allergies (comma-separated)")
#                 liked = gr.Textbox(label="Liked Foods (comma-separated)")
#                 disliked = gr.Textbox(label="Disliked Foods (comma-separated)")
#
#         save_btn = gr.Button("Save Profile", variant="primary")
#         save_output = gr.Textbox(label="Status")
#
#         save_btn.click(
#             save_user_profile,
#             inputs=[name, age, gender, weight, height, activity, goal,
#                     target, calories, meals, allergies, liked, disliked],
#             outputs=save_output
#         )
#
#     with gr.Tab("Generate Plan"):
#         generate_btn = gr.Button("Generate Nutrition Plan", variant="primary")
#         plan_output = gr.HTML(label="Your Personalized Nutrition Plan")
#
#         generate_btn.click(generate_plan, outputs=plan_output)
#
#     with gr.Tab("Chat"):
#         chatbot = gr.Chatbot()
#         msg = gr.Textbox(label="Ask questions about your plan")
#         clear = gr.Button("Clear Chat")
#
#         msg.submit(chat_with_model, [msg, chatbot], chatbot)
#         clear.click(lambda: None, None, chatbot, queue=False)
#
# if __name__ == "__main__":
#     demo.launch()

import gradio as gr
import json
import subprocess
from pathlib import Path
import traceback
from datetime import datetime

DATA_FILE = 'C:\\Users\\ahmed\\PycharmProjects\\nutrition\\assets\\datausers.json'
MODEL_NAME = "deepseek-r1:1.5b"


def calculate_bmi(weight, height):
    height_m = height / 100
    bmi = weight / (height_m ** 2)
    return round(bmi, 2)


def save_user_profile(name, age, gender, weight, height, activity_level, goal,
                      target_weight, daily_calories, meals_per_day,
                      allergies, liked_foods, disliked_foods):
    user_data = {
        "user_profile": {
            "name": name,
            "age": age,
            "gender": gender,
            "weight": weight,
            "height": height,
            "activity_level": activity_level,
            "goal": goal,
            "target_weight": target_weight,
            "daily_calorie_target": daily_calories,
            "meals_per_day": meals_per_day,
            "food_preferences": {
                "allergies": [a.strip() for a in allergies.split(',') if a.strip()],
                "liked_foods": [f.strip() for f in liked_foods.split(',') if f.strip()],
                "disliked_foods": [f.strip() for f in disliked_foods.split(',') if f.strip()]
            }
        }
    }
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(user_data, f, indent=4)
    return "Profile saved successfully!"


def generate_plan():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            user_data = json.load(f)
        bmi = calculate_bmi(user_data['user_profile']['weight'],
                            user_data['user_profile']['height'])
        water_intake = round((user_data['user_profile']['weight'] * 0.035), 2)

        prompt = f"""Create a detailed weekly nutrition plan for {user_data['user_profile']['name']} based on the following profile:
- Age: {user_data['user_profile']['age']}
- Gender: {user_data['user_profile']['gender']}
- Weight: {user_data['user_profile']['weight']} kg
- Height: {user_data['user_profile']['height']} cm
- BMI: {bmi}
- Activity Level: {user_data['user_profile']['activity_level']}
- Goal: {user_data['user_profile']['goal']}
- Target Weight: {user_data['user_profile']['target_weight']} kg
- Daily Calories: {user_data['user_profile']['daily_calorie_target']}
- Meals per Day: {user_data['user_profile']['meals_per_day']}
- Allergies: {', '.join(user_data['user_profile']['food_preferences']['allergies'])}
- Liked Foods: {', '.join(user_data['user_profile']['food_preferences']['liked_foods'])}
- Disliked Foods: {', '.join(user_data['user_profile']['food_preferences']['disliked_foods'])}

Requirements:
1. Provide a 7-day meal plan
2. Include all meals with calories and macros
3. Water intake: {water_intake} liters/day
4. Respect preferences and allergies
5. Focus on {user_data['user_profile']['goal']}"""

        result = subprocess.run(
            ["ollama", "run", MODEL_NAME],
            input=prompt,
            capture_output=True,
            text=True,
            check=True
        )

        # Save chat history
        chat_history = {
            "user_profile": user_data["user_profile"],
            "generated_plan": result.stdout,
            "timestamp": str(datetime.now())}

        history_file = 'chat_history.json'
        if Path(history_file).exists():
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        else:
            history = []

        history.append(chat_history)
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=4)

        return (f"✅ Plan generated for {user_data['user_profile']['name']}\n"
                f"BMI: {bmi}\n"
                f"Water Intake: {water_intake} L/day\n\n"
                f"Nutrition Plan:\n{result.stdout}")

    except Exception as e:
        return f"Error: {str(e)}\n{traceback.format_exc()}"


def chat_with_model(message, history):
    try:
        result = subprocess.run(
            ["ollama", "run", MODEL_NAME],
            input=message,
            capture_output=True,
            text=True,
            check=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {str(e)}"


# Create Gradio interface
with gr.Blocks(title="Nutrition Planning System") as demo:
    with gr.Tab("User Profile"):
        with gr.Row():
            with gr.Column():
                name = gr.Textbox(label="Name")
                age = gr.Number(label="Age")
                gender = gr.Dropdown(choices=["Male", "Female", "Other"], label="Gender")
                weight = gr.Number(label="Weight (kg)")
                height = gr.Number(label="Height (cm)")
                activity = gr.Dropdown(
                    choices=["Sedentary", "Light", "Moderate", "Very Active"],
                    label="Activity Level")

            with gr.Column():
                goal = gr.Dropdown(
                    choices=["Weight Loss", "Maintenance", "Muscle Gain"],
                    label="Goal")

                target = gr.Number(label="Target Weight (kg)")
                calories = gr.Number(label="Daily Calories")
                meals = gr.Number(label="Meals per Day")
                allergies = gr.Textbox(label="Allergies (comma-separated)")
                liked = gr.Textbox(label="Liked Foods (comma-separated)")
                disliked = gr.Textbox(label="Disliked Foods (comma-separated)")

        save_btn = gr.Button("Save Profile")
        save_output = gr.Textbox(label="Status")

        save_btn.click(
            save_user_profile,
            inputs=[name, age, gender, weight, height, activity, goal,
                    target, calories, meals, allergies, liked, disliked],
            outputs=save_output)

    with gr.Tab("Generate Plan"):
        generate_btn = gr.Button("Generate Nutrition Plan")
        plan_output = gr.Textbox(label="Generated Plan", lines=20)

        generate_btn.click(generate_plan, outputs=plan_output)

    with gr.Tab("Chat"):
        chatbot = gr.Chatbot()
        msg = gr.Textbox(label="Message")
        clear = gr.Button("Clear")

        msg.submit(chat_with_model, [msg, chatbot], chatbot)
        clear.click(lambda: None, None, chatbot, queue=False)

if __name__ == "__main__":
    demo.launch()