import json
import httpx
import logging
from app.config import get_params_dify

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)



async def call_dify_agent_stream(user_message: str, user_id: str = "fastapi_user"):
    """
    An asynchronous function that reads an SSE stream from Dify and returns a string generator.
    """
    dify_params = get_params_dify


    headers = {
        "Authorization": f"Bearer {dify_params["dify_api_key"]}",
        "Content-Type": "application/json",
    }

    payload = {
        "inputs": {},
        "query": user_message,
        "response_mode": "streaming", 
        "user": user_id,
    }

    logger.debug(f"Sending request to Dify: {dify_params["dify_api_url"]} with payload {payload}")
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:

            async with client.stream(
                method="POST",
                url=dify_params["dify_api_url"],
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