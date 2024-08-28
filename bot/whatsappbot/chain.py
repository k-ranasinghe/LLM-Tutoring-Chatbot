from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import MessagesPlaceholder
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from dotenv import load_dotenv
import os
from .PromptEng import get_template

load_dotenv()
groq_api_key=os.getenv('GROQ_API_KEY')

def create_chain(vectorStore):
    model=ChatGroq(groq_api_key=groq_api_key, model_name="llama-3.1-70b-versatile")
    chain = create_stuff_documents_chain(
        llm=model,
        prompt=get_template(),
    )
    retriever = vectorStore.as_retriever()

    retriever_prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        ("human", "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation. Only provide the query, not other details. Capture as much context as possible. Keep the word count of search query to 40-60 words."),
    ])

    history_aware_retriever = create_history_aware_retriever(
        llm=model,
        retriever=retriever,
        prompt=retriever_prompt
    )

    retrieval_chain = create_retrieval_chain(
        history_aware_retriever,
        chain
    )

    return retrieval_chain