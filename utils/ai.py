import aiohttp
from models.settings import settings

async def generate_ai_response(prompt: str) -> str:
    data = await settings.get()
    key = data.get('mistral_api_key', '')
    system_prompt = data.get('prompt', '')

    if not key:
        return '❌ Configure a key usando /config'

    messages = []
    if system_prompt:
        messages.append({'role': 'system', 'content': system_prompt})
    messages.append({'role': 'user', 'content': prompt})

    headers = {
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json'
    }

    payload = {
        'model': data.get('model', 'mistral-medium'),
        'messages': messages
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post('https://api.mistral.ai/v1/chat/completions', headers=headers, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['choices'][0]['message']['content']
                return '❌ Erro na API'
    except Exception:
        return '❌ Erro ao conectar'
