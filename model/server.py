from fastapi import FastAPI, HTTPException
from typing import List
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware


from app import run_model
from ChatStoreSQL import update_personalization_params, get_personalization_params, get_past_chats, get_chat_ids, load_chat_history

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
async def process_input(req:Request):
    ChatID = req.ChatID
    UserID = req.UserID
    input_text = req.input_text
    response = run_model(ChatID,UserID,input_text)
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

# Run the app using Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
