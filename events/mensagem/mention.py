import discord
from utils.ai import generate_ai_response

async def execute(message: discord.Message, client: discord.Client):
    if message.author.bot:
        return
    
    bot_mentioned = client.user in message.mentions
    
    if bot_mentioned:
        try:
            print(f"[AI] Mensagem de {message.author}: {message.content}")
            
            content_without_mention = message.content
            
            for mention in message.mentions:
                content_without_mention = content_without_mention.replace(f'<@{mention.id}>', '')
                content_without_mention = content_without_mention.replace(f'<@!{mention.id}>', '')
            
            content_without_mention = content_without_mention.strip()
            
            if not content_without_mention:
                await message.reply('👋 Olá!')
                return
            
            async with message.channel.typing():
                resposta = await generate_ai_response(content_without_mention)
                print(f"[AI] Resposta: {resposta}")
                await message.reply(resposta)
                
        except Exception as error:
            print(f'[MENTION_AI_ERROR] {error}')
            await message.reply('❌ Erro.')