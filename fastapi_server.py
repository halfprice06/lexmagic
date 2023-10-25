from fastapi import FastAPI, WebSocket, HTTPException, status, Depends
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from lexmagic import PersonalityBot


app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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
        output, top_10_results = bot.chat_completion(data['text'])
        if top_10_results == "NEED_MORE_INFO":
            await websocket.send_json({"response": output, "documents": top_10_results})
            data = await websocket.receive_json()
        await websocket.send_json({"response": output, "documents": top_10_results})
    except Exception as e:
        print(f"Error: {e}")  # Log the original error message
        await websocket.send_json({"error": str(e)})

@app.post("/token")
async def token(form_data: OAuth2PasswordRequestForm = Depends()):
    # Validate the user. Use form_data.username and form_data.password.
    # If the user is valid, generate and return a new access token.
    # If the user is invalid, raise an HTTPException.
    return {"access_token": "access_token", "token_type": "bearer"}

@app.get("/users/me")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    # Use the token to get user information.
    return {"token": token}