from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from typing import List
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
from groq import Groq
from fastapi.responses import StreamingResponse, JSONResponse
from gtts import gTTS
import io

from app import run_model
from ChatStoreSQL import update_personalization_params, get_personalization_params, get_past_chats, get_chat_ids, load_chat_history
from FileProcess import process_file

client = Groq(api_key=os.getenv('GROQ_API_KEY'))

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

@app.post("/run-model")
async def process_input(ChatID: str = Form(...), UserID: str = Form(...), input_text: str = Form(...), mediaType: str = Form(...), fileName: str = Form(...), file: UploadFile = File(None)):
    # If a file is uploaded, handle the file
    if file:
        file_content = await file.read()

        # Save it to a directory or send it to another service
        file_location = f"uploads/{file.filename}"
        with open(file_location, "wb") as f:
            f.write(file_content)
        
        # Process the file content
        extract = process_file(file_location)

        # Process the text input
        response = run_model(ChatID, UserID, input_text, extract, mediaType, fileName)

        # After processing, remove the file
        try:
            os.remove(file_location)
        except OSError as e:
            return JSONResponse(content={"error": f"Error removing file: {e}"}, status_code=500)
        
    else:
        extract = "No file attachments provided"
        response = run_model(ChatID, UserID, input_text, extract, mediaType, fileName)
    
    return(response)


@app.post("/update-personalization")
async def update_personalization(data: PersonalizationData):
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
async def get_past_chats_endpoint(userId: str):
    try:
        past_chats = get_past_chats(userId)
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
async def get_chat(chat_id: str):
    try:
        chat_history, chat_summary = load_chat_history(chat_id)
        
        # Convert chat history to a dictionary format for the frontend
        response_data = {
            "messages": chat_history,
            "summary": chat_summary
        }
        
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
