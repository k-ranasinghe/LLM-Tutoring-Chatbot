from langchain_openai import OpenAIEmbeddings
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv
import os
import time

from .chain import create_chain
from .ChatStoreSQL import save_chat_history, load_chat_history
from .ChatSummarizer import summarize_chat_history

load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"]="true"
os.environ["LANGCHAIN_API_KEY"]=os.getenv("LANGCHAIN_API_KEY")


def process_chat(chain, question, chat_history, chat_summary):
    response = chain.invoke({
        "input": question,
        "chat_history": chat_history,
        "chat_summary": chat_summary
    })
    return response["answer"]


# Streamlit UI code
def run_model(session_id, user_id, input_text):
    
    vectorStore = PineconeVectorStore(
        index_name=os.getenv("PINECONE_INDEX"),
        embedding=HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    )

    chain = create_chain(vectorStore)
    
    chat_history, chat_summary = load_chat_history(session_id)
    if chat_history is None:
        chat_history = []
    if chat_summary is None:
        chat_summary = ""

    if input_text:
        chat_history = chat_history[-10:]
        chat_summary = chat_summary
        response = process_chat(chain, input_text, chat_history, chat_summary)

        chat_history.append(HumanMessage(content=input_text))
        chat_history.append(AIMessage(content=response))

        chat_history = chat_history[-10:]
        new_chat_summary = summarize_chat_history(chat_summary, chat_history)
        save_chat_history(session_id, user_id, chat_history, new_chat_summary)

        return (response)