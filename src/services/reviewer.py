from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
load_dotenv()
import os
os.environ['GROQ_API_KEY'] = os.getenv('GROQ_API')
def evaluate_and_modify_meal_plan(user_data, meal_output):
    # Initialize the LLM model
    llm = ChatGroq(
        model="deepseek-r1-distill-llama-70b",
        temperature=0,
        max_tokens=6000,
    )

    # Define the prompt messages
    messages = [
        (
            "system",
            "You are a nutrition evaluator. Review the provided meal plan against the user's dietary profile and address all errors and violations. Edit the meal plan to ensure it meets all criteria, and return the corrected plan in JSON format. Provide explanations for each change and include a summary of issues in a markdown table.",
        ),
        ("human", f"User Profile: {user_data}"),
        ("human", f"Here is the meal plan: {meal_output}"),
    ]

    # Create the prompt
    prompt = ChatPromptTemplate.from_messages(messages)

    # Chain the prompt with the LLM
    chain = prompt | llm
    # Invoke the model
    answer = chain.invoke({
        'user_profile': user_data,
        'meal_output': meal_output
    })
    
    # Extract and print the answer content
    print(answer.content)
    
    # Extract the JSON part from the response and save it
    idx = answer.content.find('```json')
    idx_final = answer.content.rfind('```')
    js = answer.content[idx + 7: idx_final].strip()
    with open('out.json', 'w') as f:
        f.write(js)
    return js
