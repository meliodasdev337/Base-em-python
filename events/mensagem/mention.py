import discord
from utils.ai import generate_ai_response
from models.settings import settings


def clean_message(content: str, mentions) -> str:
    text = content
    for mention in mentions:
        text = text.replace(f'<@{mention.id}>', '')
        text = text.replace(f'<@!{mention.id}>', '')
    return text.strip()


async def execute(message: discord.Message, client: discord.Client):
    if message.author.bot:
        return

    data = await settings.get()
    mode = data.get('mode', 'mention')
    if mode == 'off':
        return

    channel_id = str(data.get('channel_id') or '')
    mention_target_id = str(data.get('mention_target_id') or client.user.id)
    in_channel = channel_id and str(message.channel.id) == channel_id
    target_mentioned = any(str(user.id) == mention_target_id for user in message.mentions)

    allowed = False
    if mode == 'mention':
        allowed = target_mentioned
    elif mode == 'channel':
        allowed = in_channel
    elif mode == 'both':
        allowed = target_mentioned or in_channel

    if not allowed:
        return

    try:
        content = clean_message(message.content, message.mentions)
        if not content:
            await message.reply('👋 Olá!')
            return
        async with message.channel.typing():
            resposta = await generate_ai_response(content)
            await message.reply(resposta)
    except Exception as error:
        print(f'[CHAT_ERROR] {error}')
        await message.reply('❌ Erro.')
