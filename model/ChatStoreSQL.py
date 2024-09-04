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
                "content": message.content,
                "context": message.response_metadata
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
            message = AIMessage(content=serialized_message["content"], response_metadata=serialized_message["context"])
        else:
            raise ValueError(f"Unknown message type: {serialized_message['type']}")
        
        chat_history.append(message)
    return chat_history

# Function to save chat history to MySQL
def save_chat_history(ChatID, UserID, chat_history, chat_summary):
    connection = get_mysql_connection()
    cursor = connection.cursor()
    
    serialized_history = serialize_chat_history(chat_history)
    
    cursor.execute("""
        INSERT INTO chat_sessions (ChatID, UserID, chat_history, chat_summary)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE chat_history = %s, chat_summary = %s
    """, (ChatID, UserID, serialized_history, chat_summary, serialized_history, chat_summary))
    
    connection.commit()
    cursor.close()
    connection.close()

# Function to load chat history from MySQL
def load_chat_history(ChatID):
    connection = get_mysql_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT chat_history, chat_summary FROM chat_sessions WHERE ChatID = %s", (ChatID,))
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


def get_instruction(parameter):
    connection = get_mysql_connection()
    cursor = connection.cursor(dictionary=True)

    # Execute the query with the given parameters
    cursor.execute("""
    SELECT instruction 
    FROM PersonalizationInstructions 
    WHERE parameter = %s
    """, (parameter,))

    # Fetch the result
    result = cursor.fetchone()

    # Close the cursor and connection
    cursor.close()
    connection.close()

    return result['instruction']


def get_personalization_params(chat_id):
    # Connect to the MySQL database
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)

    # SQL query to fetch the personalization parameters
    query = """
    SELECT Chat_title, Student_type, Learning_style, Communication_format, Tone_style, Reasoning_framework 
    FROM Chat_info 
    WHERE ChatID = %s
    """
    cursor.execute(query, (chat_id,))
    result = cursor.fetchone()

    # Close the cursor and connection
    cursor.close()
    conn.close()

    # Return the result as a dictionary
    if result:
        return {
            "chat_title": result['Chat_title'],
            "student_type": result['Student_type'],
            "learning_style": result['Learning_style'],
            "communication_format": result['Communication_format'],
            "tone_style": result['Tone_style'],
            "reasoning_framework": result['Reasoning_framework']
        }
    else:
        return {}
    

def update_personalization_params(chat_id, chat_title, student_type, learning_style, communication_format, tone_style, reasoning_framework):
    conn = get_mysql_connection()
    cursor = conn.cursor()
    
    # Check if the chat_id exists
    check_query = "SELECT COUNT(*) FROM Chat_info WHERE ChatID = %s"
    cursor.execute(check_query, (chat_id,))
    exists = cursor.fetchone()[0]

    if exists:
        # If it exists, update the existing row
        query = """
            UPDATE Chat_info
            SET 
                Chat_title = %s,
                Student_type = %s,
                Learning_style = %s,
                Communication_format = %s,
                Tone_style = %s,
                Reasoning_framework = %s
            WHERE 
                ChatID = %s
        """
        cursor.execute(query, (chat_title, student_type, learning_style, communication_format, tone_style, reasoning_framework, chat_id))
    else:
        # If it does not exist, insert a new row
        query = """
            INSERT INTO Chat_info (ChatID, Chat_title, Student_type, Learning_style, Communication_format, Tone_style, Reasoning_framework)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (chat_id, chat_title, student_type, learning_style, communication_format, tone_style, reasoning_framework))

    conn.commit()
    
    cursor.close()
    conn.close()


def get_mentor_notes_by_course(studentid):
    # Establish a database connection
    connection = get_mysql_connection()
    cursor = connection.cursor(dictionary=True)
    
    # SQL query to fetch notes for the given studentid
    query = """
    SELECT course, notes
    FROM mentor_notes
    WHERE studentid = %s
    """
    cursor.execute(query, (studentid,))
    
    # Fetch all results
    results = cursor.fetchall()
    
    # Close the cursor and connection
    cursor.close()
    connection.close()
    
    # Initialize a dictionary to hold concatenated notes by course
    notes_by_course = {}
    
    for result in results:
        course = result['course']
        notes = result['notes']
        
        if course not in notes_by_course:
            notes_by_course[course] = ""
        
        # Concatenate notes with a space
        notes_by_course[course] += " " + notes.strip()
    
    return notes_by_course

def get_past_chats():
    # Establish a database connection
    connection = get_mysql_connection()
    cursor = connection.cursor(dictionary=True)
    
    # SQL query to fetch all past chats
    query = """
    SELECT ChatID, Chat_title 
    FROM Chat_info
    """
    cursor.execute(query)
    
    # Fetch all results
    past_chats = cursor.fetchall()
    
    # Close the cursor and connection
    cursor.close()
    connection.close()
    
    return past_chats

