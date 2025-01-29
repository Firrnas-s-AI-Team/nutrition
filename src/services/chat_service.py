from langchain.chains import LLMChain
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.messages import SystemMessage
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from config import settings

session_memories = {}

def get_memory(session_id: str):
    if session_id not in session_memories:
        session_memories[session_id] = ConversationBufferWindowMemory(
            k=5, 
            memory_key="chat_history", 
            return_messages=True
        )
    return session_memories[session_id]

def initialize_chat_chain(llm, session_id: str, current_meal_plan: str):
    system_prompt = f'You are a friendly nutrition assistant that helps users with their nutrition and plans. Here is the current meal_plan:\n{current_meal_plan}'
    
    memory = get_memory(session_id)
    
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template("{human_input}"),
    ])

    return LLMChain(
        llm=llm,
        prompt=prompt,
        verbose=False,
        memory=memory,
    )