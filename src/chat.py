from dotenv import load_dotenv
import os


from langchain_groq import ChatGroq
from langchain_cohere import CohereEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.document_loaders import JSONLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain import hub
from langchain_core.documents import Document
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict
from langchain_core.prompts import PromptTemplate
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()


load_dotenv()

os.environ["COHERE_API_KEY"] = os.getenv("COHERE_API_KEY")
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API")

llm = ChatGroq(model="llama3-8b-8192")
embeddings = CohereEmbeddings(model="embed-english-v3.0")
vector_store = InMemoryVectorStore(embeddings)

loader = JSONLoader(
    file_path="assets/nutrition_plan.json",
    jq_schema=".days",
    text_content=False
)

docs = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=20)
all_splits = text_splitter.split_documents(docs)

_ = vector_store.add_documents(documents=all_splits)


template = """Use the provided nutritional context to answer diet-related questions. If unsure, admit lack of knowledge. Limit responses to three sentences, stay concise, and always conclude with 'thanks for asking!'.
Context: {context}
Question: {question}
Helpful Answer:"""
prompt = PromptTemplate.from_template(template)


# Define state type
class State(TypedDict):
    question: str
    context: List[Document]
    answer: str


# Define application steps
def retrieve(state: State):
    retrieved_docs = vector_store.similarity_search(state["question"])
    return {"context": retrieved_docs}


def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    response = llm.invoke(messages)
    return {"answer": response.content}


# Compile application and test
graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile(checkpointer=memory)
config = {"configurable": {"thread_id": "abc123"}}

response = graph.invoke({"question": "what is my name?"},config=config)
print(response["answer"])