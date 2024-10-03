from langchain_openai import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv
import os
import time
import warnings
from fastapi import BackgroundTasks

from chain import create_chain
from ChatStoreSQL import save_chat_history, load_chat_history, get_instruction, get_personalization_params, update_personalization_params, get_mentor_notes_by_course, get_courses_and_subjects, get_existing_feedback
from ChatSummarizer import summarize_chat_history
from TitleGenerator import generate_chat_title

load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"]="true"
os.environ["LANGCHAIN_API_KEY"]=os.getenv("LANGCHAIN_API_KEY")
warnings.filterwarnings("ignore", category=FutureWarning, module="transformers")

# Pre-load the vector store and chain
vector_store = PineconeVectorStore(
    index_name=os.getenv("PINECONE_INDEX"),
    embedding=HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
)

# chain = create_chain(vector_store)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
chroma = Chroma(persist_directory="../admin/backend/db", embedding_function=embeddings)
chain = create_chain(chroma)

def process_chat(chain, question, extract, chat_history, chat_summary, personalization, notes, feedback):
    response = chain.invoke({
        "input": question,
        "extract": extract,
        "chat_history": chat_history,
        "chat_summary": chat_summary,
        "student_type" : get_instruction(personalization['student_type']),
        "learning_style" : get_instruction(personalization['learning_style']),
        "communication_format" : get_instruction(personalization['communication_format']),
        "tone_style" : get_instruction(personalization['tone_style']),
        "reasoning_framework" : get_instruction(personalization['reasoning_framework']),
        "programming_notes" : notes["Programming"],
        "3Ddesign_notes" :  notes["3D Design"],
        "feedback" : feedback
    })

    # This condition is to handle out of context queries
    if response["context"] == []:
        return "Your query is outside of my knowledge. Apologies for the inconvenience. You should direct this question to a mentor.", []
    else:
        return response["answer"], response["context"]
    

# This function processes the context and returns a list of strings.
# Used to show Recommended Resources in the chat interface.
def process_context(context):
    result_lines = []
    for c in context:
        metadata = getattr(c, "metadata", {})
        source = metadata["source"]
        format_type = metadata["format"]
        
        if format_type == "text":
            page = metadata["page"]
            line = f"{source}, Page: {page}"
        else:
            line = f"{source}"
        
        result_lines.append(line)

    return result_lines


def update_chat_history_and_summary(ChatID, UserID, input_text, mediaType, fileName, chat_history, response, formatted_string, personalization, chat_summary):
    # Store input and response in chat history
    chat_history.append(HumanMessage(content=input_text, response_metadata={"mediaType": mediaType, "fileName": fileName}))
    chat_history.append(AIMessage(content=response, response_metadata={"context": formatted_string}))

    if personalization["chat_title"] == "":
        personalization["chat_title"] = generate_chat_title(chat_history)
        update_personalization_params(ChatID, UserID, personalization["chat_title"], 
                                        personalization["learning_style"], personalization["communication_format"], 
                                        personalization["tone_style"], personalization["reasoning_framework"])

    # This contains the latest history with the current user query and response added.
    latest_chat_history = chat_history[-10:]  # Use the last 10 interactions
    # Chat summary is generated using the latest chat history and existing chat summary.
    new_chat_summary = summarize_chat_history(chat_summary, latest_chat_history)
    
    # Save the chat history and new summary
    save_chat_history(ChatID, UserID, chat_history, new_chat_summary)
    print("task completed")


def run_model(ChatID, UserID, input_text, extract, mediaType, fileName, preloaded_data, background_tasks: BackgroundTasks):
    data = get_courses_and_subjects()
    courses = [entry["Course"] for entry in data]
    subjects = [entry["Subject"] for entry in data]

    # Remove duplicates by converting to a set, then back to a list
    distinct_courses = list(set(courses))
    distinct_subjects = list(set(subjects))

    # Optionally, sort the lists for better readability
    distinct_courses.sort()
    distinct_subjects.sort()

    # Create comma-separated strings
    courses_string = ", ".join(distinct_courses)
    subjects_string = ", ".join(distinct_subjects)
    # TODO: Add the courses and subjects to process chat

    print("Courses:", courses_string)
    print("Subjects:", subjects_string)

    chat_history = preloaded_data[ChatID]["chat_history"]
    chat_summary = preloaded_data[ChatID]["chat_summary"]
    personalization = preloaded_data[ChatID]["personalization"]
    notes = preloaded_data[UserID]["notes"]
    feedback = preloaded_data[UserID]["feedback"]

    if input_text:
        start=time.time()

        # Only the latest 5 query-response pairs are used in processing phase. This maintains a fixed token size.
        latest_chat_history = chat_history[-10:]
        response, context = process_chat(chain, input_text, extract, latest_chat_history, chat_summary, personalization, notes, feedback)
        formatted_string = process_context(context)
        response_time = str(time.time()-start)
        print(response_time)
        response_str = {"response":response, "response_time":response_time, "context":formatted_string}

        # Offload the chat history and summary updates to a background task
        background_tasks.add_task(update_chat_history_and_summary, ChatID, UserID, input_text, mediaType, fileName, chat_history, response, formatted_string, personalization, chat_summary)


        return (response_str)