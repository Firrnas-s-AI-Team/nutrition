import os
from langchain_mistralai import MistralAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import JSONLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import settings

def initialize_rag():
    os.environ["MISTRALAI_API_KEY"] = settings.MISTRAL_API_KEY
    embeddings = MistralAIEmbeddings(model="mistral-embed")
    vector_store = Chroma(embedding_function=embeddings)
    
    loader = JSONLoader(
        file_path=settings.OUTPUT_FILE,
        jq_schema=".days",
        text_content=False,
    )
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=20, chunk_overlap=5)
    all_splits = text_splitter.split_documents(docs)
    
    vectorstore = vector_store.add_documents(documents=all_splits)
    return vectorstore.as_retriever()