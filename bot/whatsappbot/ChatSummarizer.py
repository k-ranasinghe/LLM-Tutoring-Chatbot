from langchain_core.prompts import ChatPromptTemplate
from langchain import LLMChain
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()
groq_api_key=os.getenv('GROQ_API_KEY')
model=ChatGroq(groq_api_key=groq_api_key, model_name="llama-3.1-70b-versatile")

def summarize_chat_history(existing_summary, chat_history):
    chat_history_text = "\n".join([f"User: {msg.content}" if msg.type == "human" else f"Chatbot Response: {msg.content}" for msg in chat_history])
    
    combined_text = f"Summary of past converstaion: {existing_summary}\n Most recent chat history: {chat_history_text}"

    prompt = ChatPromptTemplate.from_messages([
        ("human", "{text}"),
        ("human", "You are given above a summary of the past conversation and with it the most recent chat messages, generate a summary of the conversation capturing the key points and context. Give more weight to the most recent messages. At the end include the latest 'User' message and 'Chatbot Response' message provided in the above context.")
    ])
    chain = LLMChain(llm=model, prompt=prompt)

    summary = chain.invoke({"text": combined_text})["text"]

    return summary