from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()
groq_api_key=os.getenv('GROQ_API_KEY')
openai_api_key = os.getenv('OPENAI_API_KEY')

model=ChatGroq(groq_api_key=groq_api_key, model_name="llama-3.1-70b-versatile")
# model=ChatOpenAI(openai_api_key=openai_api_key, model_name="gpt-4o-mini")

def generate_chat_title(chat_history):
    chat_history_text = "\n".join([f"User: {msg.content}" if msg.type == "human" else f"Chatbot Response: {msg.content}" for msg in chat_history])

    prompt = ChatPromptTemplate.from_messages([
        ("human", "{chat_history}"),
        ("human", """
        Generate a concise title for the conversation given above. Your response should be 3-6 words long and 
        capture the main theme or topic of the conversation. Do not include quotes or punctuation in the response.
        """)
    ])
    chain = LLMChain(llm=model, prompt=prompt)

    title = chain.invoke({"chat_history": chat_history_text})["text"]

    return title