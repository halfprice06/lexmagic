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
    while True:
        data = await websocket.receive_json()
        try:
            final_reply, top_10_results = bot.chat_completion(data['text'])
            if bot.needs_more_info == True:  # If the bot needs more information
                await websocket.send_json({"response": "NEED_MORE_INFO"})
            else:
                await websocket.send_json({"response": final_reply, "documents": top_10_results})
        except Exception as e:
            print(f"Error: {e}")  # Log the original error message
            await websocket.send_json({"error": str(e)})
