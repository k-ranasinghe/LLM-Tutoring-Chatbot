from fastapi import FastAPI, Request, BackgroundTasks, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from typing import List
from pydantic import BaseModel
from passlib.context import CryptContext # type: ignore
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import random
import string
from groq import Groq
from langchain_chroma import Chroma # type: ignore
from fastapi.responses import StreamingResponse, JSONResponse
from gtts import gTTS # type: ignore
import io
import aiofiles # type: ignore
from datetime import datetime, date

from app import run_model
from FileProcess import process_file
from ProcessFeedback import review_feedback
from whatsapp import whatsapp
from ChatStoreSQL import (update_personalization_params, get_personalization_params, get_past_chats, get_chat_ids, get_all_user_data, update_user_role,
                        load_chat_history, store_feedback, log_feedback, get_existing_feedback, fetch_feedback_logs, delete_feedback, update_feedback, delete_chat, get_mentor_notes, 
                        insert_mentor_notes, get_mentor_queries, respond_to_query, delete_mentor_query_by_id, get_answered_queries, update_query, get_user, create_user)
from MultimodalRAG import (transcribe_audio_files, process_all_pdfs, generate_captions_for_images, 
                            create_documents_from_captions, process_videos_in_directory, 
                            text_preprocess, update_metadata, save_doc)
from AdminDB import conn, lecture_materials

client = Groq(api_key=os.getenv('GROQ_API_KEY'))


# Cache for preloading variables
preloaded_data = {}

# Password hashing setup using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Directory to store files relevant to the knowledge base
UPLOAD_DIRECTORY = "uploads"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

# Directory to store images relevant to the knowledge base
IMG_DIRECTORY = "images"
os.makedirs(IMG_DIRECTORY, exist_ok=True)

class PersonalizationData(BaseModel):
    ChatID: str
    UserID: str
    chat_title: str
    learning_style: str
    communication_format: str
    tone_style: str
    reasoning_framework: str


class TextRequest(BaseModel):
    text: str
    

class UpdateUserRole(BaseModel):
    userId: str
    isAdmin: bool

class Feedback(BaseModel):
    text: str
    feedback: str
    feedbackText: str
    userText: str
    userId: str

class UpdateFeedback(BaseModel):
    id: int
    instruction: str
    selected: bool

class DeleteChatRequest(BaseModel):
    chat_id: str

class ResourceRequest(BaseModel):
    input_text: str
    response: str
    chatId: str

class LectureMaterialSchema(BaseModel):
    # file: bytes 
    file_name: str 
    file_type: str

class QueryResponse(BaseModel):
    queryId: int
    mentorResponse: str
    mentorId: str

class User(BaseModel):
    email: str
    password: str
    dateOfBirth: str
    name: str
    phoneNumber: str

class LoginModel(BaseModel):
    email: str
    password: str

app = FastAPI()

# Allowing Cross Origin Resource Sharing
origins = [
    "http://localhost:3000",  # React dev server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows requests from the specified origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all HTTP headers
)

app.mount("/images", StaticFiles(directory=IMG_DIRECTORY), name="images")

async def handle_file(file):
    # Async file read and write
    file_content = await file.read()
    file_location = f"uploads/{file.filename}"
    async with aiofiles.open(file_location, "wb") as f:
        await f.write(file_content)
    return file_location

async def remove_file(file):
    try:
        os.remove(file)
    except OSError as e:
        return JSONResponse(content={"error": f"Error removing file: {e}"}, status_code=500)

# Helper function to hash passwords
def hash_password(password: str):
    return pwd_context.hash(password)

# Helper function to verify hashed passwords
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def verify_login(email: str, password: str):
    user_data = get_user(email)

    if not user_data:
        return {"success": False, "message": "Invalid email or password", "isAdmin": user_data[1]}

    if not verify_password(password, user_data[0]):
        return {"success": False, "message": "Invalid email or password", "isAdmin": user_data[1]}

    return {"success": True, "message": "Login successful", "isAdmin": user_data[1]}

# Function to generate random ChatID
def generate_random_string(length, past_chats):
    charset = string.ascii_letters + string.digits
    while True:
        random_string = ''.join(random.choices(charset, k=length))
        if not any(chat == random_string for chat in past_chats):
            return random_string

# Helper function to preload chat-specific data
async def preload_chat_data(ChatID):
    global preloaded_data
    if ChatID not in preloaded_data:
        preloaded_data[ChatID] = {}
        
    # Preload chat history and summary
    chat_history, chat_summary = load_chat_history(ChatID)
    preloaded_data[ChatID]["chat_history"] = chat_history if chat_history else []
    preloaded_data[ChatID]["chat_summary"] = chat_summary if chat_summary else ""

    # Preload personalization data
    preloaded_data[ChatID]["personalization"] = get_personalization_params(ChatID)

    print(f"Preloaded data for ChatID {ChatID}")

async def preload_user_data(UserID):
    global preloaded_data
    if UserID not in preloaded_data:
        preloaded_data[UserID] = {}
        
    # Preload mentor notes and feedback using UserID
    preloaded_data[UserID]["notes"] = get_mentor_notes(UserID)
    preloaded_data[UserID]["feedback"] = get_existing_feedback(UserID)

    print(f"Preloaded data for UserID {UserID}")

async def update_preload_data(ChatID):
    global preloaded_data
    if ChatID not in preloaded_data:
        preloaded_data[ChatID] = {}
        
    # Preload chat history and summary
    chat_history, chat_summary = load_chat_history(ChatID)
    preloaded_data[ChatID]["chat_history"] = chat_history if chat_history else []
    preloaded_data[ChatID]["chat_summary"] = chat_summary if chat_summary else ""

    print(f"Updated chat history and chat summary for ChatID {ChatID}")


@app.post("/run-model")
async def process_input(ChatID: str = Form(...), UserID: str = Form(...), input_text: str = Form(...), mediaType: str = Form(...), fileName: str = Form(...), file: UploadFile = File(None), background_tasks: BackgroundTasks = BackgroundTasks()):
    if ChatID not in preloaded_data:
            await preload_chat_data(ChatID)
    if UserID not in preloaded_data:
            await preload_user_data(UserID)
    
    # If a file is uploaded, handle the file
    if file:
        # Handle the uploaded file
        file_location = await handle_file(file)
        
        # Process the file content
        extract = process_file(file_location, input_text, background_tasks)
        
        # Process the text input
        response = run_model(ChatID, UserID, input_text, extract, mediaType, fileName, preloaded_data, background_tasks)
        
        # After processing, remove the file
        remove_response = await remove_file(file_location)
        if remove_response:
            return remove_response
    else:
        extract = "No file attachments provided"
        response = run_model(ChatID, UserID, input_text, extract, mediaType, fileName, preloaded_data, background_tasks)
        
    await update_preload_data(ChatID)

    return response


@app.post("/fetch-resources")
async def fetch_resources(request: ResourceRequest):
    try:
        ChatID = request.chatId
        chat_history = preloaded_data[ChatID]["chat_history"]
        msg = chat_history[-1]
        context = msg.response_metadata["context"]
        resources = []
        resources.append(context)
        return resources
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/update-personalization")
async def update_personalization(data: PersonalizationData):
    try:
        print(data)
        update_personalization_params(
            data.ChatID, 
            data.UserID, 
            data.chat_title,  
            data.learning_style, 
            data.communication_format, 
            data.tone_style, 
            data.reasoning_framework
        )
        
        return {"message": "Personalization data updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get-personalization")
async def get_personalization(chat_id: str):
    try:
        data = get_personalization_params(chat_id)
        
        if not data:
            raise HTTPException(status_code=404, detail="Personalization data not found")
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get-past-chats")
async def get_past_chats_endpoint(userId: str, background_tasks: BackgroundTasks = BackgroundTasks()):
    try:
        past_chats = get_past_chats(userId)
        
        await preload_user_data(userId)
        return past_chats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get-chat-ids", response_model=List[str])
async def fetch_chat_ids():
    try:
        chat_ids = get_chat_ids()
        return chat_ids
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get-chat")
async def get_chat(chat_id: str, background_tasks: BackgroundTasks = BackgroundTasks()):
    try:
        chat_history, chat_summary = load_chat_history(chat_id)
        
        # Convert chat history to a dictionary format for the frontend
        response_data = {
            "messages": chat_history,
            "summary": chat_summary
        }
        
        background_tasks.add_task(preload_chat_data, chat_id)
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get-users")
async def get_users():
    user_data = get_all_user_data()
    if user_data is None:
        raise HTTPException(status_code=500, detail="Could not retrieve user data.")
    return user_data


@app.put("/update-user")
async def update_user_endpoint(request: UpdateUserRole):
    try:
        userId = request.userId
        isAdmin = request.isAdmin
        update_user_role(userId, isAdmin)
        return {"message": "User role updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/transcribe-audio")
async def get_transcription(file: UploadFile = File(...)):
    try:
        # Send the audio file for transcription
        transcription = client.audio.transcriptions.create(
            file=(file.filename, file.file),  # Use the audio file from the request
            model="whisper-large-v3-turbo",  # The required transcription model
            prompt="Specify context or spelling",  # Optional prompt to guide transcription
            response_format="json",  # Get response in JSON format
            language="en",  # Specify language
            temperature=0.0  # Set temperature for deterministic transcription
        )
        
        transcribed_text = transcription.text  # Extract the transcription text
        print(transcribed_text)
        return {"transcription": transcribed_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/text-to-speech")
async def text_to_speech(request: TextRequest):
    text = request.text

    if not text:
        raise HTTPException(status_code=400, detail="No text provided")

    tts = gTTS(text=text, lang='en', slow=False, tld='us')
    audio_file = io.BytesIO()
    tts.write_to_fp(audio_file)
    audio_file.seek(0)

    return StreamingResponse(audio_file, media_type="audio/mp3")


@app.post("/feedback")
async def feedback(request: Feedback, background_tasks: BackgroundTasks = BackgroundTasks()):
    text = request.text
    feedback = request.feedback
    feedbackText = request.feedbackText
    userText = request.userText
    userId = request.userId
    
    # Determine the type of feedback
    feedback_type = "positive" if feedback == "up" else "negative"
    feedbackText = feedbackText if feedbackText else "No feedback provided"
    
    # Get existing feedback from the database
    existing_feedback = get_existing_feedback(userId)
    
    review = review_feedback(userText, text, feedback_type, feedbackText, existing_feedback)
    print(review)
    
    # Store the updated review in the feedback table
    store_feedback(userId, review)
    log_feedback(userId, userText, text, feedback_type, feedbackText, review)
    
    await preload_user_data(userId)

    return review


@app.get("/feedback-logs")
async def get_feedback_logs():
    try:
        feedback_logs = fetch_feedback_logs()
        return feedback_logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/delete-feedback")
async def delete_feedback_endpoint(id: int):
    try:
        delete_feedback(id)
        return {"message": "Feedback log deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/update-feedback")
async def update_feedback_endpoint(request: UpdateFeedback):
    try:
        id = request.id
        instruction = request.instruction
        selected = request.selected
        update_feedback(id, instruction, selected)
        return {"message": "Feedback log updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/delete-chat")
async def delete_chat_endpoint(request: DeleteChatRequest):
    chat_id = request.chat_id
    print(chat_id)
    
    try:
        # Call the delete_chat function from ChatStoreSQL to delete the chat from the database
        response = delete_chat(chat_id)
        return response

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# WhatsApp Bot Endpoint
@app.post("/")
async def bot(request: Request, background_tasks: BackgroundTasks = BackgroundTasks()):
    await whatsapp(request, background_tasks)


# Admin Panel Endpoints

# Retrieve all lecture materials
@app.get("/get-files")
async def read_data():
    result = conn.execute(lecture_materials.select()).fetchall()
    response = [] 
    for row in result:
        response.append({
            "id": row.id,
            "file_name": row.file_name,
            "file_type": row.file_type,
            "uploaded_at": row.uploaded_at.isoformat()  
        })
    return response

# Retrieve a lecture material by ID
# @app.get("/get-files/{id}")
# async def read_data(id: int):
#     # Update the query to use 'like' for file_name
#     result = conn.execute(lecture_materials.select().where(lecture_materials.c.file_name.like(f"{id}%"))).fetchone()
#     if result:
#         return {
#             "id": result.id,
#             "file_name": result.file_name,
#             "file_type": result.file_type,
#             "uploaded_at": result.uploaded_at.isoformat()
#         }
#     else:
#         raise HTTPException(status_code=404, detail="Lecture Material not found")

# Update an existing lecture material by ID
@app.put("/update-file/{id}")
async def update_data(id: int, material: LectureMaterialSchema):
    result = conn.execute(lecture_materials.select().where(lecture_materials.c.id == id)).fetchone()
    if result:
        conn.execute(lecture_materials.update().where(lecture_materials.c.id == id).values(
            file=material.file,  # Update the Binary data
            file_name=material.file_name,
            file_type=material.file_type
        ))
        conn.connection.commit()
        return {"message": "Lecture material updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Lecture Material not found")

# Delete a lecture material by ID
@app.delete("/delete-file/{id}")
async def delete_data(id: int):
    result = conn.execute(lecture_materials.select().where(lecture_materials.c.id == id)).fetchone()
    if result:
        conn.execute(lecture_materials.delete().where(lecture_materials.c.id == id))
        conn.connection.commit()

        # Initialize ChromaDB index
        chroma = Chroma(persist_directory="../knowledge_base") 
        
        ids_to_delete = []
        print("document id: ", id)
        
        documents = chroma.get(where={"id": id})
        ids_to_delete = documents['ids']
        print("no. of vectors: ",len(ids_to_delete))
        if ids_to_delete:
            chroma.delete(ids=ids_to_delete)
        return {"message": "Lecture material deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Lecture Material not found")


@app.post("/upload-files")
async def write_data(subject: str = Form(...), files: List[UploadFile] = File(...)):

    audio_files = []
    converted_audio_files = []
    pdf_files = []
    video_files = []
    text_files = []
    file_info = []
    
    for file in files:
        file_info.append({
            "filename": file.filename,
            "subject": subject
        })

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename, file_extension = os.path.splitext(file.filename)
        new_filename = f"{filename}_{timestamp}{file_extension}"
        file_location = os.path.join(UPLOAD_DIRECTORY, new_filename)
    
        # Open the file location and write the uploaded file content
        with open(file_location, "wb") as f:
            content = file.file.read()  # Read the file content
            f.write(content) 

        insert_stmt = lecture_materials.insert().values(
            file_name=file.filename,
            file_type=file.content_type
        )
        result = conn.execute(insert_stmt)
        conn.connection.commit()

        file_id = result.lastrowid
        file_name = file.filename
        file.name = str(file_id) + "-" + file.filename
        print(file.name)

        if file_name.endswith((".m4a", ".mp3", ".webm", ".wav", ".mpeg", ".ogg", ".opus", ".flac", ".mp4")):
                audio_files.append((content, file.name))
        if file_name.endswith(".pdf"):
                pdf_files.append((content, file))
                # text_files.append(file)
        if file_name.endswith((".mp4", ".avi", ".mov", ".mkv", ".webm", ".mpeg", ".ogg")):
                video_files.append((content, file.name))
        if file_name.endswith((".docx", ".txt", ".html", ".md", ".epub", ".pptx", ".csv", ".xlsx", ".ipynb", ".py", ".xml")):
                text_files.append(file)

    ############## Audio ###############

    if audio_files:
        for content, file_name in audio_files:
            # audio, sr = librosa.load(io.BytesIO(file_content), sr=None)
            converted_audio_files.append((content, file_name))

        transcribed_audio_files = transcribe_audio_files(converted_audio_files, subject)
    
    ############## Images ###############

    pdf_dir = os.path.join(UPLOAD_DIRECTORY, 'pdfs')
    extracted_images_dir = os.path.join(UPLOAD_DIRECTORY, 'extracted_images')

    if os.path.exists(pdf_dir):
        shutil.rmtree(pdf_dir)

    os.makedirs(pdf_dir, exist_ok=True)
    os.makedirs(extracted_images_dir, exist_ok=True) 

    for content, file in pdf_files:
        file_path = os.path.join(pdf_dir, file.name)
        with open(file_path, 'wb') as f:
            f.write(content)

    process_all_pdfs(pdf_dir, extracted_images_dir)

    captions = generate_captions_for_images(extracted_images_dir)
    pdf_image_captions = create_documents_from_captions(captions, subject)


    ############## Video ###############

    video_dir = os.path.join(UPLOAD_DIRECTORY, 'videos')
    os.makedirs(video_dir, exist_ok=True)  # Create the videos directory if it doesn't exist

    for content, file_name in video_files:
        file_path = os.path.join(video_dir, file_name)
        with open(file_path, 'wb') as f:
            f.write(content)

    frame_dir = os.path.join(UPLOAD_DIRECTORY, 'video_frames')
    os.makedirs(frame_dir, exist_ok=True) 

    frame_rate = 1
    proccessed_videos = process_videos_in_directory(video_dir, frame_dir, frame_rate, subject)
    
    converted_audio_files = []


    ############## Text ###############

    text_files_dir = os.path.join(UPLOAD_DIRECTORY, 'textFiles')
    os.makedirs(text_files_dir, exist_ok=True)  # Create the textFiles directory if it doesn't exist

    for file in text_files:
        file_path = os.path.join(text_files_dir, file.name)
        await file.seek(0)
        async with aiofiles.open(file_path, 'wb') as f:
            while True:
                chunk = await file.read(1024)  # Read in chunks of 1024 bytes
                if not chunk:
                    break
                await f.write(chunk)

    preproccessed_text = text_preprocess(text_files_dir)
    # print(preproccessed_text)

    documents = update_metadata(preproccessed_text, subject)

    ############## Update Metadata ###############

    if audio_files:
        for doc in transcribed_audio_files:
            documents.append(doc)

    if pdf_files:
        for doc in pdf_image_captions:
            documents.append(doc)

    if video_files:
        for doc in proccessed_videos:
            documents.append(doc)

    print(len(documents))
    # print(documents)
    
    save_doc(documents)
    print("done")

    ############## Cleanup ###############

    # Remove the directories and their contents
    if os.path.exists(pdf_dir):
        shutil.rmtree(pdf_dir)
    if os.path.exists(extracted_images_dir):
        for filename in os.listdir(extracted_images_dir):
            src_file = os.path.join(extracted_images_dir, filename)
            dest_file = os.path.join(IMG_DIRECTORY, filename)
            shutil.move(src_file, dest_file)
        shutil.rmtree(extracted_images_dir)
    if os.path.exists(video_dir):
        shutil.rmtree(video_dir)
    if os.path.exists(frame_dir):
        for filename in os.listdir(frame_dir):
            src_file = os.path.join(frame_dir, filename)
            dest_file = os.path.join(IMG_DIRECTORY, filename)
            shutil.move(src_file, dest_file)
        shutil.rmtree(frame_dir)
    if os.path.exists(text_files_dir):
        shutil.rmtree(text_files_dir)

    return JSONResponse(content={"message": "Files uploaded successfully!", "files": file_info})


@app.post("/mentor-notes")
async def submit_notes(
    week_no: str = Form(...),
    has_attended: bool = Form(...),
    activity_summary: str = Form(...),
    communication_rating: str = Form(...),
    leadership_rating: str = Form(...),
    behaviour_rating: str = Form(...),
    responsiveness_rating: str = Form(...),
    difficult_concepts: str = Form(...),
    understood_concepts: str = Form(...),
    student_id: str = Form(...),
    staff_id: str = Form(...),
    course_id: str = Form(...),
    date_created: str = Form(...),
):
    try:
        json_data = {
            "week_no": int(week_no),
            "has_attended": has_attended,
            "activity_summary": activity_summary,
            "communication_rating": int(communication_rating),
            "leadership_rating": int(leadership_rating),
            "behaviour_rating": int(behaviour_rating),
            "responsiveness_rating": int(responsiveness_rating),
            "difficult_concepts": difficult_concepts,
            "understood_concepts": understood_concepts,
            "student_id": student_id,
            "staff_id": staff_id,
            "course_id": course_id,
            "date_created": date_created,
            # "id": id
        }
        print(json_data)
        # Insert data into the database
        insert_mentor_notes(json_data)
        
        notes = get_mentor_notes(student_id)
        return notes

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/get-mentor-queries")
async def get_mentor_queries_endpoint():
    try:
        queries = get_mentor_queries()
        return {"queries": queries}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/respond-to-query")
async def respond_to_query_endpoint(response: QueryResponse):
    try:
        query_id = response.queryId
        mentor_response = response.mentorResponse
        mentor_id = response.mentorId
        respond_to_query(query_id, mentor_response, mentor_id)
        return {"message": "Response submitted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/delete-mentor_query")
async def delete_mentor_query(queryId: str):
    try:
        print("queryId:", queryId)
        delete_mentor_query_by_id(queryId)
        return {"message": "Query deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get-notifications")
async def get_notifications_endpoint(user_id: str):
    try:
        notifications = get_answered_queries(user_id)
        return notifications
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/update-notification")
async def update_notification_endpoint(id: str):
    try:
        update_query(id)
        return {"message": "Query updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint for registration
@app.post("/register")
async def register(user: User):
    print(user)
    user_data = get_user(user.email)
    
    if user_data:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_pwd = hash_password(user.password)
    create_user(user.email, hashed_pwd, user.dateOfBirth, user.name, user.phoneNumber)
    all_chatid = get_chat_ids()
    chat_id = generate_random_string(10, all_chatid)
    update_personalization_params(chat_id, user.email, "", "Verbal", "Textbook", "Neutral", "Deductive")

    return {"success": True, "message": "User registered successfully"}


# Endpoint for login
@app.post("/login")
async def login(login: LoginModel):
    result = verify_login(login.email, login.password)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
