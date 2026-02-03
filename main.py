import discord
from discord import app_commands
import json
import os
import importlib.util
import sys

from events.bot.ready import ready_event
from events.mensagem.mention import execute

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

def verify_bot_integrity():
    required_files = [
        "commands/user/creditos.py",
        "commands/user/ping.py",
        "commands/user/userinfo.py",
        "commands/admin/ban.py",
        "commands/admin/unban.py",
        "commands/admin/lock.py",
        "events/bot/ready.py",
        "utils/ai.py",
        "functions/emojis.py"
    ]
    
    protected_strings = [
        "Meliodas",
        "1389706621697134674",
        "meliodasdev337",
        "awsupjWb9x",
        "Base.py"
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"❌ Arquivo necessário ausente: {file_path}")
            return False
    
    try:
        with open("commands/user/creditos.py", "r", encoding="utf-8") as f:
            creditos_content = f.read()
            
        for string in protected_strings:
            if string not in creditos_content:
                print(f"❌ Informação protegida removida: {string}")
                return False
    except:
        print("❌ Erro ao verificar créditos")
        return False
    
    return True

class Bot(discord.Client):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        if not verify_bot_integrity():
            print("❌ Integridade do bot comprometida. Desligando...")
            await self.close()
            sys.exit(1)
        
        await load_commands(self.tree)
        await self.tree.sync()

bot = Bot()

async def load_commands(tree: app_commands.CommandTree):
    base_path = "commands"

    for root, _, files in os.walk(base_path):
        for file in files:
            if not file.endswith(".py"):
                continue

            path = os.path.join(root, file)

            spec = importlib.util.spec_from_file_location(file[:-3], path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if hasattr(module, "setup"):
                module.setup(tree)

@bot.event
async def on_ready():
    await ready_event(bot)

@bot.event
async def on_message(message):
    await execute(message, bot)

bot.run(config["token"])