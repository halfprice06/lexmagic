from fastapi import FastAPI, HTTPException
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

@app.post("/chat")
async def chat(prompt: Prompt):
    bot = PersonalityBot()
    try:
        response, top_10_results = bot.chat_completion(prompt.text)
    except Exception as e:
        print(f"Error: {e}")  # Log the original error message
        raise HTTPException(status_code=500, detail=str(e))
    return {"response": response, "documents": top_10_results}