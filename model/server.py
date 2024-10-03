from fastapi import FastAPI, BackgroundTasks, HTTPException, UploadFile, File, Form
from typing import List
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
from groq import Groq
from fastapi.responses import StreamingResponse, JSONResponse
from gtts import gTTS
import io
import aiofiles

from app import run_model
from ChatStoreSQL import update_personalization_params, get_personalization_params, get_past_chats, get_chat_ids, load_chat_history, store_feedback, get_existing_feedback, delete_chat, get_mentor_notes_by_course
from FileProcess import process_file
from ProcessFeedback import review_feedback

client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# Cache for preloading variables
preloaded_data = {}

class Request(BaseModel):
    ChatID:str
    UserID:str
    input_text:str


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
    

class Feedback(BaseModel):
    text: str
    feedback: str
    feedbackText: str
    userText: str
    userId: str

class DeleteChatRequest(BaseModel):
    chat_id: str

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
    preloaded_data[UserID]["notes"] = get_mentor_notes_by_course(UserID)
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
        extract = process_file(file_location)

        # Process the text input
        response = run_model(ChatID, UserID, input_text, extract, mediaType, fileName, preloaded_data, background_tasks)

        # After processing, remove the file
        remove_response = await remove_file(file_location)
        if remove_response:
            return remove_response
    else:
        extract = "No file attachments provided"
        response = run_model(ChatID, UserID, input_text, extract, mediaType, fileName, preloaded_data, background_tasks)
        
    background_tasks.add_task(update_preload_data, ChatID)

    return response


@app.post("/update-personalization")
async def update_personalization(data: PersonalizationData, background_tasks: BackgroundTasks = BackgroundTasks()):
    try:
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
        
        background_tasks.add_task(preload_user_data, userId)
        return past_chats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/get-chat-ids", response_model=List[str])
async def fetch_chat_ids():
    try:
        chat_ids = get_chat_ids()  # Call the synchronous function here
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


@app.post("/transcribe-audio")
async def get_transcription(file: UploadFile = File(...)):
    try:
        # Send the audio file for transcription
        transcription = client.audio.transcriptions.create(
            file=(file.filename, file.file),  # Use the audio file from the request
            model="distil-whisper-large-v3-en",  # The required transcription model
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
    
    background_tasks.add_task(preload_user_data, userId)

    return review


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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
