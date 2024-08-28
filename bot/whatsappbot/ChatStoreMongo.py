import json
import os
import pymongo
from langchain_core.messages import HumanMessage, AIMessage

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")

# Function to establish MongoDB connection
def get_mongo_client():
    client = pymongo.MongoClient(MONGO_URI)
    return client[MONGO_DB]

def serialize_chat_history(chat_history):
    serialized_history = []
    for message in chat_history:
        if isinstance(message, HumanMessage) or isinstance(message, AIMessage):
            serialized_message = {
                "type": message.__class__.__name__,
                "content": message.content
            }
            serialized_history.append(serialized_message)
        # Add additional handling for other message types if necessary
    return serialized_history

# Function to save chat history to MongoDB
def save_chat_history(session_id, chat_history):
    # Connect to MongoDB
    client = get_mongo_client()
    collection = client[MONGO_COLLECTION]

    # Check if session_id already exists in collection
    existing_session = collection.find_one({"session_id": session_id})

    serialized_history = serialize_chat_history(chat_history)

    if existing_session:
        # If session_id exists, update the chat_history
        collection.update_one(
            {"session_id": session_id},
            {"$set": {"chat_history": serialized_history}},
            upsert=True  # Insert if not found
        )
    else:
        # If session_id doesn't exist, create a new document
        collection.insert_one({
            "session_id": session_id,
            "chat_history": serialized_history
        })
        

# Function to load chat history from MongoDB
def load_chat_history(session_id):
    client = get_mongo_client()
    collection = client[MONGO_COLLECTION]
    
    chat_data = collection.find_one({"session_id": session_id})
    if chat_data:
        chat_history = []
        for serialized_message in chat_data["chat_history"]:
            if serialized_message["type"] == "HumanMessage":
                message = HumanMessage(content=serialized_message["content"])
            elif serialized_message["type"] == "AIMessage":
                message = AIMessage(content=serialized_message["content"])
            else:
                raise ValueError(f"Unknown message type: {serialized_message['type']}")
            
            chat_history.append(message)
        
        return chat_history
    else:
        return []