from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn
import os
import json
from typing import Optional
import httpx
from dotenv import load_dotenv
from uuid import uuid4

import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

DIFY_API_URL = os.getenv("DIFY_API_URL")
DIFY_API_KEY = os.getenv("DIFY_API_KEY")

if not DIFY_API_URL or not DIFY_API_KEY:
    raise EnvironmentError("Требуются переменные окружения: DIFY_API_URL и DIFY_API_KEY")

class ChatRequest(BaseModel):
    message: str

async def call_dify_agent_stream(user_message: str, user_id: str = "fastapi_user"):
    """
    Асинхронная функция, которая читает SSE-поток от Dify и возвращает генератор строк.
    """
    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "inputs": {},
        "query": user_message,
        "response_mode": "streaming", 
        "user": user_id,
    }

    logger.debug(f"Sending request to Dify: {DIFY_API_URL} with payload {payload}")
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:

            async with client.stream(
                method="POST",
                url=DIFY_API_URL,
                json=payload,
                headers=headers
            ) as response:
                logger.debug(f"Dify response status: {response.status_code}")
                logger.debug(f"Dify response headers: {response.headers}")

       
                if response.status_code != 200:
                 
                    error_msg = f" {{\"error\": \"Dify API error\", \"status\": {response.status_code}}}\n\n"
                    logger.error(f"Yielding error: {error_msg}")
                    yield error_msg
                    return 

                logger.debug("Starting to read Dify stream...")


                async for chunk in response.aiter_lines():

                    if chunk:
                        json_part = chunk[6:]
                        data = json.loads(json_part)

                        if data['event'] == 'agent_thought':
                            logger.debug(f"Yielding JSON: {data['thought']}")
                            yield data['thought']


        except httpx.ReadTimeout:
            error_msg = f" {{\"error\": \"Request to Dify API timed out\"}}\n\n"
            logger.error(f"Yielding timeout error: {error_msg}")
            yield error_msg
        except httpx.RequestError as e:
            error_msg = f" {{\"error\": \"Request error: {str(e)}\"}}\n\n"
            logger.error(f"Yielding request error: {error_msg}")
            yield error_msg
        except Exception as e:
            error_msg = f" {{\"error\": \"An error occurred: {str(e)}\"}}\n\n"
            logger.error(f"Yielding general error: {error_msg}")
            yield error_msg


@app.post("/chat") 
async def chat_stream(request: ChatRequest):
    """
    Эндпоинт, который принимает сообщение и возвращает потоковый ответ от Dify.
    """
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




