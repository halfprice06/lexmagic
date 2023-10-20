from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from chat_with_civil_code import PersonalityBot

app = FastAPI()

class Prompt(BaseModel):
    text: str

@app.post("/chat")
async def chat(prompt: Prompt):
    bot = PersonalityBot()
    try:
        response = bot.chat_completion(prompt.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"response": response}