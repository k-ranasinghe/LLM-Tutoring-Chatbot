import os
import json
import mysql.connector
from langchain_core.messages import HumanMessage, AIMessage

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB")

# Function to establish MySQL connection
def get_mysql_connection():
    connection = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB
    )
    return connection

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
    return json.dumps(serialized_history)

def deserialize_chat_history(serialized_history):
    chat_history = []
    for serialized_message in json.loads(serialized_history):
        if serialized_message["type"] == "HumanMessage":
            message = HumanMessage(content=serialized_message["content"])
        elif serialized_message["type"] == "AIMessage":
            message = AIMessage(content=serialized_message["content"])
        else:
            raise ValueError(f"Unknown message type: {serialized_message['type']}")
        
        chat_history.append(message)
    return chat_history

# Function to save chat history to MySQL
def save_chat_history(session_id, user_id, chat_history, chat_summary):
    connection = get_mysql_connection()
    cursor = connection.cursor()
    
    serialized_history = serialize_chat_history(chat_history)
    
    cursor.execute("""
        INSERT INTO chat_sessions (session_id, user_id, chat_history, chat_summary)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE chat_history = %s, chat_summary = %s
    """, (session_id, user_id, serialized_history, chat_summary, serialized_history, chat_summary))
    
    connection.commit()
    cursor.close()
    connection.close()

# Function to load chat history from MySQL
def load_chat_history(session_id):
    connection = get_mysql_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT chat_history, chat_summary FROM chat_sessions WHERE session_id = %s", (session_id,))
    result = cursor.fetchone()
    
    if result:
        chat_history = deserialize_chat_history(result[0])
        chat_summary = result[1]
    else:
        chat_history = []
        chat_summary = ""
    
    cursor.close()
    connection.close()
    
    return chat_history, chat_summary

# Function to save chat summary to MySQL
def save_chat_summary(session_id, chat_summary):
    connection = get_mysql_connection()
    cursor = connection.cursor()
    
    cursor.execute("""
        UPDATE chat_sessions
        SET chat_summary = %s
        WHERE session_id = %s
    """, (chat_summary, session_id))
    
    connection.commit()
    cursor.close()
    connection.close()