from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import os
import httpx
from dotenv import load_dotenv
from uuid import uuid4
from chat.schemas import ChatRequest
from chat.dify_service import call_dify_agent_stream

import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

DIFY_API_URL = os.getenv("DIFY_API_URL")
DIFY_API_KEY = os.getenv("DIFY_API_KEY")



@app.post("/chat") 
async def chat_stream(request: ChatRequest):
    
    user_id = str(uuid4())

    return StreamingResponse(
        call_dify_agent_stream(request.message, user_id=user_id),
        media_type="text/event-stream"
    )


@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)




