import discord
from discord import app_commands
import json
import os
import importlib.util

from events.bot.ready import ready_event
from events.mensagem.mention import execute

with open('config.json','r',encoding='utf-8') as f:
    config=json.load(f)

class Bot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.guilds = True
        intents.members = True
        intents.presences = True
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree=app_commands.CommandTree(self)

    async def setup_hook(self):
        await load_commands(self.tree)
        await self.tree.sync()

bot=Bot()

async def load_commands(tree):
    for root,_,files in os.walk('commands'):
        for file in files:
            if file.endswith('.py'):
                path=os.path.join(root,file)
                spec=importlib.util.spec_from_file_location(file[:-3],path)
                module=importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                if hasattr(module,'setup'):
                    module.setup(tree)

@bot.event
async def on_ready():
    await ready_event(bot)

@bot.event
async def on_message(message):
    await execute(message,bot)

bot.run(config['token'])
