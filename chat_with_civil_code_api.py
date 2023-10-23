from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
from chat_with_civil_code import PersonalityBot
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class Prompt(BaseModel):
    text: str

@app.websocket("/ws")
async def chat(websocket: WebSocket):
    bot = PersonalityBot()
    await websocket.accept()
    data = await websocket.receive_json()
    try:
        followup_question, need_more_info = bot.chat_completion(data['text'])
        if need_more_info == "NEED_MORE_INFO":
            await websocket.send_json({"response": followup_question, "documents": need_more_info})
            data = await websocket.receive_json()
            followup_question, need_more_info = bot.chat_completion(data['text'])
        await websocket.send_json({"response": followup_question, "documents": need_more_info})
    except Exception as e:
        print(f"Error: {e}")  # Log the original error message
        await websocket.send_json({"error": str(e)})