# Automated Nutritional Meal Plan Generator

This project is an automated meal plan generator that creates a balanced daily meal plan based on a user's personal data and nutritional goals. The system calculates the user's Basal Metabolic Rate (BMR) and Total Daily Energy Expenditure (TDEE), applies a calorie deficit (or surplus) depending on the goal (e.g., weight loss, weight gain, or muscle gain), and then distributes the target calories into several balanced meals. Each meal is composed of a lean protein, a carbohydrate source, and a healthy fat, with portion sizes computed to meet specific per-meal macronutrient targets.

Additionally, the system integrates with a language model (via the ChatGroq API) to allow expert-level adjustments and recommendations for the generated meal plan.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Workflow](#workflow)
- [Function Descriptions](#function-descriptions)
  - [Calculations Module (`calculation.py`)](#calculations-module-calculationpy)
    - [`calculate_bmr(age, gender, weight, height)`](#calculate_bmr)
    - [`calculate_tdee(bmr, activity_level)`](#calculate_tdee)
    - [`compose_balanced_meal(meal_calories, target_protein, target_carb, target_fat, food_df, food_exclusions)`](#compose_balanced_meal)
    - [`generate_daily_meal_plan(tdee, goal, food_df, meals_per_day, gender, food_exclusions)`](#generate_daily_meal_plan)
  - [Main Module (`main.py`)](#main-module-mainpy)
- [Installation and Setup](#installation-and-setup)
- [Usage](#usage)
- [Conclusion](#conclusion)

---

## Project Overview

The project creates a complete meal plan based on user-provided data:
- **User Profile:** Loaded from a JSON file (`user_profile.json`) containing age, gender, weight, height, activity level, nutritional goal, and the number of meals per day.
- **Food Data:** Loaded from a CSV file (`GPT_data.csv`), which includes food items along with their nutritional information (calories, protein, carbohydrates, fats per 100g, type, and meal category).

The system calculates the BMR and TDEE, then uses these values to generate a meal plan that meets a modest calorie deficit (for weight loss) or a surplus (for weight/muscle gain) while ensuring balanced macronutrient distribution.

---

## Workflow

1. **Data Loading:**
   - Load food data from `GPT_data.csv` (duplicates removed).
   - Load user profile from `user_profile.json`.

2. **BMR and TDEE Calculation:**
   - **`calculate_bmr`** computes the Basal Metabolic Rate using the Mifflin-St Jeor equation.
   - **`calculate_tdee`** applies an activity multiplier to the BMR to compute the Total Daily Energy Expenditure.

3. **Meal Plan Generation:**
   - **`generate_daily_meal_plan`** is used to generate the complete meal plan. For weight loss, it subtracts a modest calorie deficit from the TDEE.
   - Daily macronutrient targets (protein, carbohydrates, fat) are calculated as percentages of the adjusted target calories.
   - These daily targets are divided evenly among the meals.
   - **`compose_balanced_meal`** is called for each meal to select one lean protein, one carbohydrate, and one healthy fat. It calculates initial portion sizes to meet per-meal macronutrient targets and then scales the portions so the meal's total calories match the desired value.
   - An exclusion list is maintained to improve food variety.

4. **Output Preparation and LLM Integration:**
   - The meal plan is formatted into a human-readable text file (`meal_plan_output.txt`).
   - The output is sent to a language model (via ChatGroq) along with the user data for expert-level adjustments.
   - The language model's suggestions are printed for further review.

---

## Function Descriptions

### Calculations Module (`calculation.py`)

#### `calculate_bmr(age, gender, weight, height)`
- **Purpose:**  
  Computes the Basal Metabolic Rate using the Mifflin-St Jeor equation.
- **Inputs:**  
  - `age`: User’s age (years).
  - `gender`: `"male"` or `"female"`.
  - `weight`: Weight in kilograms.
  - `height`: Height in centimeters.
- **Output:**  
  - Returns the BMR (calories/day).

#### `calculate_tdee(bmr, activity_level)`
- **Purpose:**  
  Adjusts the BMR with an activity multiplier to calculate the Total Daily Energy Expenditure.
- **Inputs:**  
  - `bmr`: The calculated Basal Metabolic Rate.
  - `activity_level`: A string indicating the user's activity level (e.g., `"sedentary"`, `"lightly active"`, etc.).
- **Output:**  
  - Returns the TDEE (calories/day).

#### `compose_balanced_meal(meal_calories, target_protein, target_carb, target_fat, food_df, food_exclusions)`
- **Purpose:**  
  Constructs a balanced meal by selecting:
  - A lean protein (filtered to have low fat content).
  - A carbohydrate source.
  - A healthy fat (preferably with moderate fat content).
- **Process:**  
  - **Selection:** Filters candidate food items based on type and nutritional criteria.
  - **Portion Calculation:** Computes initial portions required to meet the per-meal macronutrient targets.
  - **Scaling:** Adjusts portion sizes so that the total calorie content equals the target for that meal.
- **Inputs:**  
  - `meal_calories`: Target calories for the meal.
  - `target_protein`, `target_carb`, `target_fat`: Per-meal macronutrient targets (in grams).
  - `food_df`: DataFrame of food items with nutritional details.
  - `food_exclusions`: List of food items already used.
- **Output:**  
  - Returns a list of meal items (with details on grams, calories, and macronutrients) and an updated exclusion list.

#### `generate_daily_meal_plan(tdee, goal, food_df, meals_per_day, gender, food_exclusions)`
- **Purpose:**  
  Generates a full-day meal plan.
- **Process:**  
  - Adjusts the TDEE by applying a modest calorie deficit (or surplus) based on the user's goal.
  - Computes daily macronutrient targets as percentages of the adjusted calories.
  - Divides daily targets evenly across the meals.
  - Calls `compose_balanced_meal` for each meal to compile the full-day plan.
- **Inputs:**  
  - `tdee`: Total Daily Energy Expenditure.
  - `goal`: The nutritional goal (e.g., `"lose weight"`).
  - `food_df`: Food data DataFrame.
  - `meals_per_day`: Number of meals to create.
  - `gender`: User's gender.
  - `food_exclusions`: (Optional) List to track already used food items.
- **Output:**  
  - Returns a dictionary where each key is a meal (e.g., `"Meal_1"`) with details on meal items and nutritional breakdown.

---

### Main Module (`main.py`)

The main module is responsible for:
1. **Data Loading:**  
   - Reads food data from `GPT_data.csv` and removes duplicates.
   - Loads the user profile from `user_profile.json`.
2. **Nutritional Calculations:**  
   - Computes the BMR using `calculate_bmr`.
   - Calculates TDEE using `calculate_tdee`.
3. **Meal Plan Generation:**  
   - Generates a daily meal plan using `generate_daily_meal_plan`.
4. **Output Formatting:**  
   - Formats the meal plan with detailed nutritional information.
   - Saves the output to `meal_plan_output.txt`.
5. **LLM Integration:**  
   - Sends the meal plan along with user data to a language model (ChatGroq) for expert-level adjustments.
   - Prints the response from the language model.

---

## Installation and Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/meal-plan-generator.git
   cd meal-plan-generator
