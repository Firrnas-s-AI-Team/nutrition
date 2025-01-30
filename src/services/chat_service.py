from langchain.chains import LLMChain
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.messages import SystemMessage
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from config import settings
from typing import List, Dict

session_memories = {}

def get_memory(session_id: str, chat_history: List[Dict[str, str]] = None):
    if session_id not in session_memories:
        memory = ConversationBufferWindowMemory(
            k=5,
            memory_key="chat_history",
            return_messages=True
        )
        # Initialize memory with provided chat history
        if chat_history:
            for message in chat_history:
                if message["role"] == "user":
                    memory.chat_memory.add_user_message(message["content"])
                elif message["role"] == "assistant":
                    memory.chat_memory.add_ai_message(message["content"])
        session_memories[session_id] = memory
    return session_memories[session_id]


def get_chat_history(memory) -> List[Dict[str, str]]:
    history = []
    for i, msg in enumerate(memory.chat_memory.messages):
        history.append({
            "role": "assistant" if i % 2 else "user",
            "content": msg.content
        })
    return history

def initialize_chat_chain(llm, session_id: str, current_meal_plan: str, chat_history: List[Dict[str, str]] = None):
    system_prompt = f'You are a friendly nutrition assistant. Here is the current meal_plan:\n{current_meal_plan}'
    memory = get_memory(session_id, chat_history)
    
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template("{human_input}"),
    ])

    return LLMChain(llm=llm, prompt=prompt, verbose=False, memory=memory)