import os
import json
from datetime import datetime, date
import mysql.connector
#import pymysql
from langchain_core.messages import HumanMessage, AIMessage

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB")

# Function to establish MySQL connection
def get_mysql_connection():
    # timeout = 10
    # connection = pymysql.connect(
    #     charset="utf8mb4",
    #     connect_timeout=timeout,
    #     cursorclass=pymysql.cursors.DictCursor,
    #     db="defaultdb",
    #     host="mysql-2f2f286c-chatbot-llm.l.aivencloud.com",
    #     password="************************",
    #     read_timeout=timeout,
    #     port=15276,
    #     user="avnadmin",
    #     write_timeout=timeout,
    # )

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
        if isinstance(message, HumanMessage):
            serialized_message = {
                "type": "HumanMessage",
                "content": message.content,
                # Serialize the specific response_metadata fields for HumanMessage
                "mediaType": message.response_metadata.get("mediaType"),
                "fileName": message.response_metadata.get("fileName")
            }
        elif isinstance(message, AIMessage):
            serialized_message = {
                "type": "AIMessage",
                "content": message.content,
                # Serialize the specific response_metadata fields for AIMessage
                "context": message.response_metadata.get("context"),
                "files": message.response_metadata.get("files")
            }
        else:
            raise ValueError(f"Unknown message type: {message.__class__.__name__}")
        
        serialized_history.append(serialized_message)
    
    return json.dumps(serialized_history)

def deserialize_chat_history(serialized_history):
    chat_history = []
    for serialized_message in json.loads(serialized_history):
        if serialized_message["type"] == "HumanMessage":
            # Deserialize HumanMessage with mediaType and fileName metadata
            message = HumanMessage(
                content=serialized_message["content"],
                response_metadata={
                    "mediaType": serialized_message.get("mediaType"),
                    "fileName": serialized_message.get("fileName")
                }
            )
        elif serialized_message["type"] == "AIMessage":
            # Deserialize AIMessage with context metadata
            message = AIMessage(
                content=serialized_message["content"],
                response_metadata={
                    "context": serialized_message.get("context"),
                    "files": serialized_message.get("files")
                }
            )
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
        INSERT INTO chat_data (ChatID, chat_history, chat_summary)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE chat_history = %s, chat_summary = %s
    """, (ChatID, serialized_history, chat_summary, serialized_history, chat_summary))

    # Insert or update `User_chats` table
    cursor.execute("""
        INSERT INTO user_chats (ChatID, UserID, Timestamp)
        VALUES (%s, %s, NOW())
        ON DUPLICATE KEY UPDATE Timestamp = NOW()
    """, (ChatID, UserID))
    
    connection.commit()
    cursor.close()
    connection.close()

# Function to load chat history from MySQL
def load_chat_history(ChatID):
    connection = get_mysql_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT chat_history, chat_summary FROM chat_data WHERE ChatID = %s", (ChatID,))
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


def get_instruction(parameter):
    connection = get_mysql_connection()
    cursor = connection.cursor(dictionary=True)

    # Execute the query with the given parameters
    cursor.execute("""
    SELECT instruction 
    FROM Personalization_instructions 
    WHERE parameter = %s
    """, (parameter,))

    # Fetch the result
    result = cursor.fetchone()

    # Close the cursor and connection
    cursor.close()
    connection.close()

    return result['instruction']


def get_personalization_params(ChatID):
    # Connect to the MySQL database
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)

    # SQL query to fetch the personalization parameters
    query = """
    SELECT Chat_title, Student_type, Learning_style, Communication_format, Tone_style, Reasoning_framework 
    FROM Chat_info 
    WHERE ChatID = %s
    """
    cursor.execute(query, (ChatID,))
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


def calculate_student_type(dob):
    # Calculate the user's age based on DOB
    today = date.today()
    birthdate = dob
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    
    # Determine student type based on age
    # if 10 <= age <= 15:
    #     return "type1"
    # elif 16 <= age <= 18:
    #     return "type2"
    # else:
    #     return None
    if age <= 15:
        return "type1"
    else:
        return "type2"


# This function handles existing and new chat personalization parameters
def update_personalization_params(chat_id, UserID, chat_title, learning_style, communication_format, tone_style, reasoning_framework):
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)

    # Get the user's DOB from the user_data table
    cursor.execute("SELECT Date_of_birth FROM user_data WHERE UserID = %s", (UserID,))
    user_data = cursor.fetchone()

    if not user_data or not user_data['Date_of_birth']:
        raise ValueError(f"No date of birth found for UserID: {UserID}")

    # Calculate the student type based on DOB
    dob = user_data['Date_of_birth']
    student_type = calculate_student_type(dob)
    
    if not student_type:
        raise ValueError(f"UserID: {UserID} is outside the valid student age range (10-18).")
    
    cursor.close()
    cursor = conn.cursor()
    
    # Check if the chat_id exists
    check_query = "SELECT COUNT(*) FROM Chat_info WHERE ChatID = %s"
    cursor.execute(check_query, (chat_id,))
    exists = cursor.fetchone()

    if exists[0] > 0:
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

    # Insert or update User_chats table
    cursor.execute("""
        INSERT INTO user_chats (ChatID, UserID, Timestamp)
        VALUES (%s, %s, NOW())
        ON DUPLICATE KEY UPDATE Timestamp = NOW()
    """, (chat_id, UserID))

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
    
    # Flag to check if any notes were found
    notes_found = False
    
    for result in results:
        course = result['course']
        notes = result['notes']
        
        if course not in notes_by_course:
            notes_by_course[course] = ""
        
        # Concatenate notes with a space
        notes_by_course[course] += " " + notes.strip()
        
        # Update the flag if notes are found
        notes_found = True
    
    # If no notes were found, add a default message for each course
    if not notes_found:
        # Query to get a list of all courses for the given studentid
        query_courses = """
        SELECT DISTINCT course
        FROM mentor_notes
        """
        connection = get_mysql_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query_courses)
        courses = cursor.fetchall()
        cursor.close()
        
        for course in [row['course'] for row in courses]:
            notes_by_course[course] = "there are no available notes."
    
    return notes_by_course

# This function returns a list of user chats ordered by timestamp
def get_past_chats(user_id):
    # Establish a database connection
    connection = get_mysql_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Fetching past chats with timestamps from `User_chats` and `Chat_info` for a specific UserID
    query = """
    SELECT uc.ChatID, ci.Chat_title, uc.Timestamp
    FROM User_chats uc
    JOIN Chat_info ci ON uc.ChatID = ci.ChatID
    WHERE uc.UserID = %s
    ORDER BY uc.Timestamp DESC
    """
    cursor.execute(query, (user_id,))
    
    # Fetch all results
    past_chats = cursor.fetchall()
    
    # Close the cursor and connection
    cursor.close()
    connection.close()
    
    return past_chats

# This function returns all the chat IDs. It is used to generate new chat IDs.
def get_chat_ids():
    # Establish a database connection
    connection = get_mysql_connection()
    cursor = connection.cursor(dictionary=True)
    
    # SQL query to get distinct ChatID values from User_chats
    query = """
    SELECT DISTINCT ChatID
    FROM User_chats
    """
    
    cursor.execute(query)
    
    # Fetch all results
    chat_ids = cursor.fetchall()
    
    # Close the cursor and connection
    cursor.close()
    connection.close()
    
    # Return a list of ChatID values
    return [row['ChatID'] for row in chat_ids]


def get_all_user_data():
    connection = None
    try:
        connection = get_mysql_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT UserID, name, Date_of_birth, phone_number, isAdmin FROM User_data"
        cursor.execute(query)
        
        results = cursor.fetchall()
        return results

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def update_user_role(userId, isAdmin):
    connection = get_mysql_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("UPDATE User_data SET isAdmin = %s WHERE UserID = %s", (isAdmin, userId))
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()


# This function is to be used in chain.py to gt values for the course and subject attributes
def get_courses_and_subjects():
    # Establish a database connection
    connection = get_mysql_connection()
    cursor = connection.cursor(dictionary=True)
    
    # SQL query to get distinct courses and subjects
    query = """
    SELECT DISTINCT Course, Subject 
    FROM Curriculum
    """
    
    cursor.execute(query)
    
    # Fetch all results
    distinct_courses_and_subjects = cursor.fetchall()
    
    # Close the cursor and connection
    cursor.close()
    connection.close()
    
    return distinct_courses_and_subjects

def store_feedback(userId, feedback):
    connection = get_mysql_connection()
    cursor = connection.cursor()
    
    # Insert or update the feedback for the given userid
    query = """
    INSERT INTO feedback (userid, feedback)
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE feedback = %s
    """
    cursor.execute(query, (userId, feedback, feedback))
    
    connection.commit()
    cursor.close()
    connection.close()

def log_feedback(userid, user_query, response, feedback_type, feedback_text, instruction):
    connection = get_mysql_connection()
    cursor = connection.cursor()

    query = """
        INSERT INTO feedback_log (userid, user_query, response, feedback_type, feedback_text, instruction)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    data = (userid, user_query, response, feedback_type, feedback_text, instruction)

    try:
        cursor.execute(query, data)
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()


def get_existing_feedback(userId):
    connection = get_mysql_connection()
    cursor = connection.cursor()
    
    # Query to get the feedback for the given userid
    query = "SELECT feedback FROM feedback WHERE userid = %s"
    cursor.execute(query, (userId,))
    result = cursor.fetchone()
    
    cursor.close()
    connection.close()
    
    if result:
        return result[0]  # Return the existing feedback
    return "No existing feedback"  # No feedback found for this userid


def fetch_feedback_logs():
    connection = get_mysql_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM feedback_log")
        rows = cursor.fetchall()
        # feedback_logs = [FeedbackLog(**row) for row in rows]
        return rows
    finally:
        cursor.close()
        connection.close()


def delete_feedback(log_id: int):
    connection = get_mysql_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("DELETE FROM feedback_log WHERE id = %s", (log_id,))
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        cursor.close()
        connection.close()


def update_feedback(log_id: int, instruction: str, selected: bool):
    connection = get_mysql_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute(
            "UPDATE feedback_log SET instruction = %s, selected = %s WHERE id = %s",
            (instruction, selected, log_id)
        )
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        cursor.close()
        connection.close()


# Function to delete a chat from the MySQL database
def delete_chat(chat_id):
    connection = get_mysql_connection()
    cursor = connection.cursor()

    try:
        # Begin a transaction
        connection.start_transaction()

        # Delete from `user_chats` table
        cursor.execute("DELETE FROM user_chats WHERE ChatID = %s", (chat_id,))
        
        # Delete from `chat_data` table
        cursor.execute("DELETE FROM chat_data WHERE ChatID = %s", (chat_id,))
        
        # Delete from `chat_info` table
        cursor.execute("DELETE FROM chat_info WHERE ChatID = %s", (chat_id,))

        # Commit the transaction
        connection.commit()

    except mysql.connector.Error as err:
        # Roll back the transaction in case of an error
        connection.rollback()
        print(f"Error: {err}")
        raise

    finally:
        # Close the cursor and connection
        cursor.close()
        connection.close()

    print(f"Chat with ChatID {chat_id} has been successfully deleted.")


# Function to insert data into the mentor_notes table
def insert_mentor_notes(data):
    try:
        connection = get_mysql_connection()
        cursor = connection.cursor()

        insert_query = """
            INSERT INTO mentor_notes (
                week_no, 
                has_attended, 
                activity_summary, 
                communication_rating, 
                leadership_rating, 
                behaviour_rating, 
                responsiveness_rating, 
                difficult_concepts, 
                understood_concepts, 
                student_id, 
                staff_id, 
                course_id, 
                date_created
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """

        cursor.execute(insert_query, (
            data['week_no'],
            data['has_attended'],
            data['activity_summary'],
            data['communication_rating'],
            data['leadership_rating'],
            data['behaviour_rating'],
            data['responsiveness_rating'],
            data['difficult_concepts'],
            data['understood_concepts'],
            data['student_id'],
            data['staff_id'],
            data['course_id'],
            data['date_created']
        ))

        connection.commit()
        cursor.close()
        connection.close()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        raise 


# Function to get mentor notes for a specific student_id
def get_mentor_notes(student_id):
    try:
        connection = get_mysql_connection()
        cursor = connection.cursor(dictionary=True)  # Enable dictionary cursor for easy access to column names

        query = """
            SELECT 
                week_no, 
                has_attended, 
                activity_summary, 
                communication_rating, 
                leadership_rating, 
                behaviour_rating, 
                responsiveness_rating, 
                difficult_concepts, 
                understood_concepts, 
                student_id, 
                staff_id, 
                course_id, 
                date_created,
                id
            FROM mentor_notes 
            WHERE student_id = %s;
        """

        cursor.execute(query, (student_id,))
        results = cursor.fetchall()

        cursor.close()
        connection.close()

        return results

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        raise


def store_mentor_query(student_id, query, chatbot_response):
    connection = get_mysql_connection()
    cursor = connection.cursor()

    try:
        insert_query = """
            INSERT INTO mentor_queries (studentid, query, chatbot_response)
            VALUES (%s, %s, %s);
        """
        cursor.execute(insert_query, (student_id, query, chatbot_response))
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()


def get_mentor_queries():
    connection = get_mysql_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM mentor_queries WHERE answered = FALSE")  # Adjust your query as needed
        queries = cursor.fetchall()
        cursor.close()
        connection.close()
        return queries
    except Exception as e:
        print("Error updating query response:", e)
        raise e



def respond_to_query(query_id: int, mentor_response: str, mentor_id: str):
    connection = get_mysql_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("""
            UPDATE mentor_queries
            SET mentor_response = %s, mentorid = %s, answered = TRUE
            WHERE id = %s
        """, (mentor_response, mentor_id, query_id))
        connection.commit()
    except Exception as e:
        print("Error updating query response:", e)
        raise e
    finally:
        cursor.close()
        connection.close()


def delete_mentor_query_by_id(query_id: str):
    connection = get_mysql_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("DELETE FROM mentor_queries WHERE id = %s", (query_id,))
        connection.commit()
    except Exception as e:
        print("Error deleting query:", e)
        raise e
    finally:
        cursor.close()
        connection.close()


def get_answered_queries(studentid):
    connection = get_mysql_connection()
    cursor = connection.cursor(dictionary=True)  # Use dictionary for better readability

    try:
        # SQL query to fetch the required fields where answered is true
        query = """
        SELECT id, query, chatbot_response, mentorid, mentor_response, viewed
        FROM mentor_queries
        WHERE studentid = %s AND answered = TRUE
        """
        cursor.execute(query, (studentid,))
        
        # Fetch all matching rows
        results = cursor.fetchall()
        return results

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

    finally:
        cursor.close()
        connection.close()


def update_query(id):
    # Establish a connection to the MySQL database
    connection = get_mysql_connection()
    cursor = connection.cursor()

    try:
        # Create the SQL query to update the 'viewed' field where the 'id' matches
        query = """
        UPDATE mentor_queries
        SET viewed = TRUE
        WHERE id = %s;
        """
        # Execute the query with the given id
        cursor.execute(query, (id,))

        # Commit the changes to the database
        connection.commit()

        print(f"Notification with ID {id} marked as viewed.")
    
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        connection.rollback()  # Roll back in case of any error
        raise
    
    finally:
        # Close the cursor and connection
        cursor.close()
        connection.close()


# Function to check if user exists
def get_user(userid: str):
    try:
        connection = get_mysql_connection()
        cursor = connection.cursor()

        select_query = "SELECT Password, isAdmin FROM User_data WHERE UserID = %s"
        cursor.execute(select_query, (userid,))
        user_data = cursor.fetchone()
        return user_data
    except Exception as e:
        raise e
    finally:
        cursor.close()
        connection.close()


# Function to register a new user
def create_user(email: str, hashed_password: str, dob: date, name: str, phone_number: str):
    try:
        connection = get_mysql_connection()
        cursor = connection.cursor()

        insert_query = """
            INSERT INTO User_data (UserID, Password, Date_of_birth, name, phone_number)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (email, hashed_password, dob, name, phone_number))
        connection.commit()
    except Exception as e:
        raise e
    finally:
        cursor.close()
        connection.close()