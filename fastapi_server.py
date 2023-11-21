from fastapi import FastAPI, WebSocket, HTTPException, status, Depends, Request, Form
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import Optional
from lexmagic import LawBot
from vector_search_cc import vector_search_civil_code



app = FastAPI()

templates = Jinja2Templates(directory="templates")  # Assuming your templates are in a directory named "templates"

app.mount("/static", StaticFiles(directory="static"), name="static")

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

class Query(BaseModel):
    question: str

@app.websocket("/ws")
async def chat(websocket: WebSocket):
    bot = LawBot()
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

import re

@app.post("/vector_search", response_class=HTMLResponse)
async def vector_search(request: Request, query: Optional[str] = Form(None)):
    if not query:
        return HTMLResponse(content="<div> Your Answer Will Appear here </div>")
    print(query)
    _, top_articles = vector_search_civil_code(query, collections=['cc_articles', 'ccp_articles', 'ccrp_articles'], top_n_number=5)
    
    formatted_responses = []
    for (article, meta) in top_articles:
        # Check if the article can be split into title and content
        if "\n" in article:
            title, content = article.split("\n", 1)
        else:
            title = article
            content = ""
        
        # Replace single newline characters followed by a capital letter with two newline characters
        content = re.sub(r'\n([A-Z])', r'\n\n\1', content)

        # Replace '(1)' pattern with two newline characters and a tab, regardless of what precedes it
        content = re.sub(r'\((\d)\)', r'\n\n&emsp;&emsp;(\1)', content)
        
        # Further split the content into paragraphs
        paragraphs = content.split("\n\n")  # Split on two consecutive newline characters
        
        # Remove any empty strings from the list of paragraphs
        paragraphs = [paragraph for paragraph in paragraphs if paragraph]
        
        # Format the response
        formatted_response = {
            "title": title,
            "paragraphs": paragraphs,
            "metadata": meta  # Include the metadata
        }
        formatted_responses.append(formatted_response)
    
    return templates.TemplateResponse("response.html", {"request": request, "responses": formatted_responses})

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("search.html", {"request": request})

@app.get("/magicsearch", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("magicsearch.html", {"request": request})