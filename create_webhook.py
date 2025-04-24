import os
from dotenv import load_dotenv
import logging
import json
import sys
import aiohttp
import asyncio
from typing import Optional, Dict, Any
from config import CLICKUP_API_BASE_URL, CLICKUP_API_TOKEN, LOG_FORMAT, MAX_CONNECTIONS

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    stream=sys.stdout
)
logger = logging.getLogger(__name__)
logger.propagate = False

class ClickUpClient:
    def __init__(self, api_token=None, task_id=None):
        load_dotenv()
        self.api_token = api_token or CLICKUP_API_TOKEN
        self.base_url = CLICKUP_API_BASE_URL
        self.task_id = task_id
        self._session = None
        
        if not self.api_token:
            raise ValueError("Missing API token. Please provide it as a parameter or set CLICKUP_API_TOKEN in environment variables")
    
    async def __aenter__(self):
        self._session = aiohttp.ClientSession(
            headers={"Authorization": self.api_token},
            connector=aiohttp.TCPConnector(limit=MAX_CONNECTIONS)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()

    def format_and_print_json(self, data, title):
        json_str = json.dumps(
            data,
            ensure_ascii=False,
            separators=(',', ':'),
            default=str
        )
        print(f"\n{title}:")
        print(json_str)
        print("-" * 80)

    async def test_authentication(self, team_id: Optional[str] = None) -> bool:
        try:
            url = f"{self.base_url}/team"
            if team_id:
                url = f"{url}?team_id={team_id}"
            
            async with self._session.get(url) as response:
                data = await response.json()
                self.format_and_print_json(data, "Resposta da autenticação")
                return response.status == 200
        except aiohttp.ClientError as e:
            print(f"Erro de autenticação: {e}")
            return False

    async def get_task_details(self) -> Dict[str, Any]:
        try:
            url = f"{self.base_url}/task/{self.task_id}"
            print(f"\nURL da requisição: {url}")
            
            async with self._session.get(url) as response:
                print(f"Código de status da resposta: {response.status}")
                response.raise_for_status()
                task_data = await response.json()
                
                self.format_and_print_json(task_data, "Detalhes completos da tarefa")
                return task_data

        except aiohttp.ClientError as e:
            print(f"Erro ao buscar detalhes da tarefa: {e}")
            raise

if __name__ == "__main__":
    async def main():
        try:
            api_token = input("Enter your ClickUp API token: ")
            team_id = input("Enter your team ID (optional): ")
            task_id = input("Enter the task ID: ")
            
            async with ClickUpClient(api_token=api_token, task_id=task_id) as client:
                if not await client.test_authentication(team_id if team_id else None):
                    print("Falha na autenticação. Verifique seu token API.")
                    return
                
                print("Autenticação bem sucedida. Buscando detalhes da tarefa...")
                task_details = await client.get_task_details()
                client.format_and_print_json(task_details, "Detalhes da tarefa obtidos com sucesso")
        except Exception as e:
            print(f"Falha ao obter detalhes da tarefa: {e}")
    
    asyncio.run(main())