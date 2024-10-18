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
    
    combined_text = f"Summary of past converstaion: {existing_summary}\n\n Most recent chat history: {chat_history_text}\n\n"

    prompt = ChatPromptTemplate.from_messages([
        ("human", """
        {text}
        Generate a concise summary of the conversation, capturing essential context and key points. Focus on:
        1. Main topics discussed
        2. Important questions asked by the user
        3. Key concepts explained or explored
        4. Any unresolved issues or ongoing threads of discussion
        5. User preferences or specific requests made during the conversation

        Keep the summary brief while retaining critical information.
        Prioritize the most recent interactions and overarching themes.
        Ensure the output is well-structured and easy to read.
        Avoid using technical jargon unless it's essential to understanding the conversation.
        Integrate new information from recent messages with the existing summary.
        If there are contradictions between the existing summary and recent messages, prioritize the most recent information.

        Structure the summary with clear headers and bullet points for easy scanning. Use the following format:

        **Conversation Summary**
        // Overview of the past conversation. Generate a consice summary for this section.//

        // For the below sections do not exceed 10 bullet points for each section.//
        ## Main Topics:
        - Topic 1
        - Topic 2
        - ...

        ## Key Questions:
        - Question 1
        - Question 2
        - ...

        ## Important Concepts:
        - Concept 1: Brief explanation
        - Concept 2: Brief explanation
        - ...

        ## Unresolved Issues:
        - Issue 1
        - Issue 2
        - ...

        ## User Preferences:
        - Preference 1
        - Preference 2
        - ...

        Ensure that the summary provides a comprehensive yet concise overview of the entire conversation, highlighting the most important elements without losing essential details.
        """)
    ])
    chain = LLMChain(llm=model, prompt=prompt)

    summary = chain.invoke({"text": combined_text})["text"]
    
    # Append the last chat pair to the summary
    summary += f"\n\n**Last Chat Pair**:\n{last_chat_pair}"

    return summary