from flask import Flask, request, jsonify
import json
import subprocess
from functools import wraps
import os

app = Flask(__name__)

# Constants
DATA_FILE = 'assets/datausers.json'
MODEL_NAME = "deepseek-r1:1.5b"


def load_user_data():
    """Load user data from JSON file"""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None


def save_user_data(data):
    """Save user data to JSON file"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)


def calculate_bmi(weight, height):
    """Calculate BMI given weight in kg and height in cm"""
    height_m = height / 100
    bmi = weight / (height_m ** 2)
    return round(bmi, 2)


def calculate_water_intake(weight):
    """Calculate daily water intake in liters"""
    return round(weight * 0.035, 2)


def require_json(f):
    """Decorator to require JSON content type"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
        return f(*args, **kwargs)

    return decorated_function


@app.route('/api/user/profile', methods=['POST'])
@require_json
def create_user_profile():
    """Create or update user profile"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['name', 'age', 'gender', 'weight', 'height',
                           'activity_level', 'goal', 'target_weight',
                           'daily_calorie_target', 'meals_per_day']

        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400

        # Calculate BMI
        data['bmi'] = calculate_bmi(data['weight'], data['height'])

        # Save user data
        user_data = {
            "user_profile": data
        }
        save_user_data(user_data)

        return jsonify({
            "message": "User profile created successfully",
            "profile": data
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/nutrition/plan', methods=['GET'])
def generate_nutrition_plan():
    """Generate nutrition plan based on user profile"""
    try:
        user_data = load_user_data()
        if not user_data:
            return jsonify({"error": "User profile not found"}), 404

        profile = user_data['user_profile']
        bmi = calculate_bmi(profile['weight'], profile['height'])
        water_intake = calculate_water_intake(profile['weight'])

        # Construct prompt
        prompt = f"""Create a detailed weekly nutrition plan for {profile['name']} based on the following profile:
- Age: {profile['age']}
- Gender: {profile['gender']}
- Weight: {profile['weight']} kg
- Height: {profile['height']} cm
- BMI: {bmi}
- Activity Level: {profile['activity_level']}
- Goal: {profile['goal']}
- Target Weight: {profile['target_weight']} kg
- Daily Calorie Target: {profile['daily_calorie_target']} calories
- Meals per Day: {profile['meals_per_day']}
- Allergies: {', '.join(profile.get('food_preferences', {}).get('allergies', []))}
- Liked Foods: {', '.join(profile.get('food_preferences', {}).get('liked_foods', []))}
- Disliked Foods: {', '.join(profile.get('food_preferences', {}).get('disliked_foods', []))}

**Requirements:**
1. Provide a 7-day meal plan (Saturday to Friday)
2. For each day, include:
   - All meals (breakfast, mid-morning snack, lunch, afternoon snack, dinner)
   - Detailed menu items for each meal
   - Calories per item and total calories per meal
   - Macronutrient breakdown (protein, carbs, fats) for each meal
   - Total daily calories and macronutrients
3. Include water intake recommendation: {water_intake} liters/day
4. Ensure meals are personalized to preferences and avoid allergies
5. Maintain nutritional balance and weight loss goals"""

        # Generate nutrition plan using Ollama
        result = subprocess.run(
            ["ollama", "run", MODEL_NAME],
            input=prompt,
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=True
        )

        # Process the result
        if result.stdout:
            try:
                nutrition_plan = json.loads(result.stdout.strip())
            except json.JSONDecodeError:
                nutrition_plan = {"raw_plan": result.stdout.strip()}

            return jsonify({
                "user_info": {
                    "name": profile['name'],
                    "bmi": bmi,
                    "water_intake": water_intake,
                    "daily_calorie_target": profile['daily_calorie_target']
                },
                "nutrition_plan": nutrition_plan
            })
        else:
            return jsonify({"error": "No plan generated"}), 500

    except subprocess.CalledProcessError as e:
        return jsonify({
            "error": "Model error",
            "details": {
                "stdout": e.stdout,
                "stderr": e.stderr
            }
        }), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/nutrition/chat', methods=['POST'])
@require_json
def chat_with_model():
    """Chat endpoint for nutrition advice"""
    try:
        data = request.get_json()
        if 'message' not in data:
            return jsonify({"error": "Message is required"}), 400

        result = subprocess.run(
            ["ollama", "run", MODEL_NAME],
            input=data['message'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=True
        )

        if result.stdout:
            return jsonify({"response": result.stdout.strip()})
        else:
            return jsonify({"error": "No response generated"}), 500

    except subprocess.CalledProcessError as e:
        return jsonify({
            "error": "Model error",
            "details": {
                "stdout": e.stdout,
                "stderr": e.stderr
            }
        }), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)