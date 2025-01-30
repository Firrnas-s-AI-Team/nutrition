from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    INPUT_FILE = 'assets/datauser.json'
    OUTPUT_FILE = 'assets/nutrition_plan.json'
    EXAMPLE_RESPONSE_FILE = 'assets/example_response.json'
    GROQ_API_KEY = os.getenv("GROQ_API")
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

settings = Settings()