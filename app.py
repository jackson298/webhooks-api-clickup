from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
from typing import Dict, Any, List
import os
from dotenv import load_dotenv
import aiohttp
from create_webhook import ClickUpClient
from config import CLICKUP_API_TOKEN, API_TITLE, API_DESCRIPTION, API_VERSION, API_LOG_FORMAT, DEFAULT_HOST, DEFAULT_PORT

logging.basicConfig(
    level=logging.INFO,
    format=API_LOG_FORMAT
)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CLICKUP_API_TOKEN = os.getenv('CLICKUP_API_TOKEN')
if not CLICKUP_API_TOKEN:
    raise ValueError("CLICKUP_API_TOKEN environment variable is required")

class WebhookCreate(BaseModel):
    endpoint: str
    description: str = None

class Webhook(BaseModel):
    id: str
    endpoint: str
    client_id: str
    workspace_id: str
    user_id: str
    events: List[str]

class WebhookList(BaseModel):
    webhooks: List[Webhook]

@app.post("/team/{team_id}/webhook", response_model=Webhook, tags=["webhooks"])
async def create_webhook(team_id: int, webhook: WebhookCreate):
    try:
        async with ClickUpClient(api_token=CLICKUP_API_TOKEN) as client:
            url = f"{client.base_url}/team/{team_id}/webhook"
            async with client._session.post(
                url,
                json={"endpoint": webhook.endpoint, "description": webhook.description}
            ) as response:
                response.raise_for_status()
                return await response.json()
    
    except aiohttp.ClientError as e:
        logger.error(f"Error creating webhook: {str(e)}")
        raise HTTPException(
            status_code=getattr(e, 'status', 500),
            detail=str(e)
        )

@app.get("/team/{team_id}/webhook", response_model=WebhookList, tags=["webhooks"])
async def get_webhooks(team_id: int):
    try:
        async with ClickUpClient(api_token=CLICKUP_API_TOKEN) as client:
            url = f"{client.base_url}/team/{team_id}/webhook"
            async with client._session.get(url) as response:
                response.raise_for_status()
                webhooks_data = await response.json()
                return {"webhooks": webhooks_data.get("webhooks", [])}
    
    except aiohttp.ClientError as e:
        logger.error(f"Error retrieving webhooks: {str(e)}")
        raise HTTPException(
            status_code=getattr(e, 'status', 500),
            detail=str(e)
        )

if __name__ == "__main__":
    import uvicorn
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=DEFAULT_PORT)
    args = parser.parse_args()
    
    uvicorn.run(app, host=DEFAULT_HOST, port=args.port)