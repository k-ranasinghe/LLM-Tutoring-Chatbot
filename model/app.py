from langchain_openai import OpenAIEmbeddings
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv
import os
import time

from chain import create_chain
from ChatStoreSQL import save_chat_history, load_chat_history, get_instruction, get_personalization_params, get_mentor_notes_by_course
from ChatSummarizer import summarize_chat_history

load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"]="true"
os.environ["LANGCHAIN_API_KEY"]=os.getenv("LANGCHAIN_API_KEY")


def process_chat(chain, question, chat_history, chat_summary, personalization, notes):
    response = chain.invoke({
        "input": question,
        "chat_history": chat_history,
        "chat_summary": chat_summary,
        "student_type" : get_instruction(personalization['student_type']),
        "learning_style" : get_instruction(personalization['learning_style']),
        "communication_format" : get_instruction(personalization['communication_format']),
        "tone_style" : get_instruction(personalization['tone_style']),
        "reasoning_framework" : get_instruction(personalization['reasoning_framework']),
        "programming_notes" : notes["Programming"],
        "3Ddesign_notes" :  notes["3D Design"]
    })

    if response["context"] == []:
        return "Your query is outside of my knowledge. Apologies for the inconvenience. You should direct this question to a mentor.", []
    else:
        return response["answer"], response["context"]
    

def process_context(context):
    result_lines = []
    for c in context:
        metadata = getattr(c, "metadata", {})
        source = metadata["source"]
        format_type = metadata["format"]
        page = metadata["page"]

        if format_type == "text":
            line = f"{source}, Page: {page}"
        else:
            line = f"{source}"
        
        result_lines.append(line)

    return result_lines


def run_model(ChatID, UserID, input_text):
    vectorStore = PineconeVectorStore(
        index_name=os.getenv("PINECONE_INDEX"),
        embedding=HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    )

    chain = create_chain(vectorStore)
    personalization = get_personalization_params(ChatID)
    notes = get_mentor_notes_by_course(UserID)
    
    chat_history, chat_summary = load_chat_history(ChatID)
    if chat_history is None:
        chat_history = []
    if chat_summary is None:
        chat_summary = ""

    if input_text:
        start=time.process_time()
        chat_history = chat_history[-10:]
        chat_summary = chat_summary
        response, context = process_chat(chain, input_text, chat_history, chat_summary, personalization, notes)

        formatted_string = process_context(context)
        print(formatted_string)

        response_time = str(time.process_time()-start)
        response_str = {"response":response, "response_time":response_time, "context":formatted_string}

        chat_history.append(HumanMessage(content=input_text))
        chat_history.append(AIMessage(content=response))

        chat_history = chat_history[-10:]
        new_chat_summary = summarize_chat_history(chat_summary, chat_history)
        save_chat_history(ChatID, UserID, chat_history, new_chat_summary)

        return (response_str)