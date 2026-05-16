import discord
import random
import aiohttp
import json

from functions.emojis import upload_emojis
from utils.ai import generate_ai_response

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

API_URL = "https://discord.com/api/v10/applications/@me"

BIOS = [
    "Base feita por Meliodas\nhttps://github.com/meliodasdev337",
    "Base feita por Meliodas\nhttps://github.com/meliodasdev337",
    "Base feita por Meliodas\nhttps://github.com/meliodasdev337"
]

async def set_bio(bot, text):
    headers = {
        "Authorization": f"Bot {bot.http.token}",
        "Content-Type": "application/json"
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        await session.patch(API_URL, json={"description": text})

async def ready_event(bot):
    print(f"[BOT] Online como {bot.user}")

    result = upload_emojis(bot)

    if result:
        print(f"[EMOJIS] Total: {result.get('total')}")
        print(f"[EMOJIS] Criados: {result.get('success')}")
        print(f"[EMOJIS] Falharam: {result.get('failed')}")
        print(f"[EMOJIS] Final: {result.get('finalCount')}")

    await set_bio(bot, random.choice(BIOS))
    print("[BIO] Atualizada")

    if "status" in config:
        status_type = config["status"]["type"]
        status_text = config["status"]["text"]
        
        activity_type = discord.ActivityType.playing
        if status_type == "watching":
            activity_type = discord.ActivityType.watching
        elif status_type == "listening":
            activity_type = discord.ActivityType.listening
        elif status_type == "streaming":
            activity_type = discord.ActivityType.streaming
        
        await bot.change_presence(
            activity=discord.Activity(
                type=activity_type,
                name=status_text
            )
        )
    else:
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="Base Meliodas"
            )
        )

    if config.get("mistral_api_key"):
        print("[AI] API Key configurada")
        test_prompt = "Olá"
        try:
            response = await generate_ai_response(test_prompt)
            if "❌" not in response:
                print(f"[AI] Conectada: ✓")
            else:
                print(f"[AI] Erro: {response}")
        except Exception as e:
            print(f"[AI] Erro de conexão: {e}")
    else:
        print("[AI] API Key não configurada")