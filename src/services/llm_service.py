from langchain_groq import ChatGroq
from config import settings

def initialize_llm():
    llm = ChatGroq(
        temperature=0.2,
        model_name="llama-3.1-8b-instant",
        api_key=settings.GROQ_API_KEY
    )
    return llm

def prepare_llm_messages(datauser_text, example_response_text):
    messages = [
        {"role": "system", "content": "You are an expert nutrition assistant."},
        {
            "role": "user",
            "content": (
                f'''Task:
Generate a personalized weekly meal plan in JSON format to help the user lose weight while maintaining balanced nutrition.

Input Data:
{datauser_text}

Instructions:
1. **Follow User Data**: Use the number of meals and all variables provided in `datauser`.
2. **Complete Week**: Include meal plans for all seven days (Monday to Sunday).
3. **Realistic Choices**: Use common, real-world food items with accurate nutritional values.
4. **Provide Alternatives**: Offer alternatives for any specified allergies or dislikes.
5. **JSON Only**: Return solely the JSON structure without any additional text or explanations.

Example JSON Template:
{example_response_text}

Output:
Return the complete meal plans for all seven days (Monday to Sunday) as JSON following the structure and data provided in `datauser`.
                '''
            )
        }
    ]
    return messages
