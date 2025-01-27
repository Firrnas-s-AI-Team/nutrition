
1. **Create/Update User Profile**
- Method: POST
- URL: `http://127.0.0.1:5000/api/user/profile`
- Headers: 
  - Content-Type: application/json
- Body (raw JSON):
```json
{
    "name": "John Doe",
    "age": 30,
    "gender": "male",
    "weight": 80,
    "height": 175,
    "activity_level": "moderate",
    "goal": "weight_loss",
    "target_weight": 75,
    "daily_calorie_target": 2000,
    "meals_per_day": 5,
    "food_preferences": {
        "allergies": ["nuts"],
        "liked_foods": ["chicken", "rice"],
        "disliked_foods": ["fish"]
    }
}
```

2. **Generate Nutrition Plan**
- Method: GET
- URL: `http://127.0.0.1:5000/api/nutrition/plan`
- No body needed

3. **Chat with Model**
- Method: POST
- URL: `http://127.0.0.1:5000/api/nutrition/chat`
- Headers: 
  - Content-Type: application/json
- Body (raw JSON):
```json
{
    "message": "How can I reduce my calorie intake?"
}
```

Important notes:
- Make sure your Flask server is running
- The base URL `http://127.0.0.1:5000` is correct
- Don't forget to include `/api/` in the paths
- Always set the Content-Type header for POST requests
- The server must be running before making requests

Would you like me to modify any of the endpoints or add additional features to the API?