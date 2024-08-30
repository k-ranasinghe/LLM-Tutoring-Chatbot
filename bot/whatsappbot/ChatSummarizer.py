from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()
groq_api_key=os.getenv('GROQ_API_KEY')
openai_api_key = os.getenv('OPENAI_API_KEY')

model=ChatGroq(groq_api_key=groq_api_key, model_name="llama3-70b-8192")
# model=ChatOpenAI(openai_api_key=openai_api_key, model_name="gpt-4o-mini")

def summarize_chat_history(existing_summary, chat_history):
    chat_history_text = "\n".join([f"User: {msg.content}" if msg.type == "human" else f"Chatbot Response: {msg.content}" for msg in chat_history])
    last_chat_pair = "\n".join([f"User: {msg.content}" if msg.type == "human" else f"Chatbot Response: {msg.content}" for msg in chat_history[-2:]])

    combined_text = f"Summary of past converstaion: {existing_summary}\n Most recent chat history: {chat_history_text}"

    prompt = ChatPromptTemplate.from_messages([
        ("human", "{text}"),
        ("human", """
        Generate a concise summary of the conversation, capturing essential context and key points. Focus on:
        1. Main topics discussed
        2. Important questions asked by the user
        3. Key concepts explained or explored
        4. Any unresolved issues or ongoing threads of discussion

        Keep the summary brief while retaining critical information. 
        Prioritize the most recent interactions and overarching themes.

        After generating the summary, append the following most recent query-response pair:
        {last_chat_pair}
        """)
    ])
    chain = LLMChain(llm=model, prompt=prompt)

    summary = chain.invoke({"text": combined_text, "last_chat_pair": last_chat_pair})["text"]

    return summary