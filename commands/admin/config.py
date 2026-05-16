import discord
from discord import app_commands
import json
from models.settings import settings

with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)


def owner_ids() -> set[str]:
    ids = set(str(x) for x in config.get('owners', []))
    if config.get('owner_id'):
        ids.add(str(config.get('owner_id')))
    return ids


def is_owner(user_id: int) -> bool:
    return str(user_id) in owner_ids()


async def deny(interaction: discord.Interaction):
    await interaction.response.send_message(view=message_view('Sem permissão', 'Só quem está em `owners` no config.json pode usar isso.', 0xED4245), ephemeral=True)


class ConfigModal(discord.ui.Modal):
    def __init__(self, field: str, label: str, current: str = ''):
        super().__init__(title=label)
        self.field = field
        self.input = discord.ui.TextInput(
            label=label,
            default=current[:4000] if current else None,
            required=False,
            style=discord.TextStyle.paragraph if field == 'prompt' else discord.TextStyle.short,
            max_length=4000 if field == 'prompt' else 300
        )
        self.add_item(self.input)

    async def on_submit(self, interaction: discord.Interaction):
        if not is_owner(interaction.user.id):
            return await deny(interaction)
        await settings.update({self.field: str(self.input.value or '').strip()})
        data = await settings.get()
        await interaction.response.edit_message(view=ConfigPanel(data))


class ModeSelect(discord.ui.Select):
    def __init__(self, current: str):
        options = [
            discord.SelectOption(label='Responder ao mencionar', value='mention', default=current == 'mention'),
            discord.SelectOption(label='Responder em canal fixo', value='channel', default=current == 'channel'),
            discord.SelectOption(label='Responder nos dois', value='both', default=current == 'both'),
            discord.SelectOption(label='Desligado', value='off', default=current == 'off')
        ]
        super().__init__(placeholder='Modo de resposta', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if not is_owner(interaction.user.id):
            return await deny(interaction)
        await settings.update({'mode': self.values[0]})
        data = await settings.get()
        await interaction.response.edit_message(view=ConfigPanel(data))


class ModelSelect(discord.ui.Select):
    def __init__(self, current: str):
        models = ['mistral-large-latest', 'mistral-medium-latest', 'mistral-small-latest', 'open-mistral-nemo', 'open-mixtral-8x7b']
        options = [discord.SelectOption(label=model, value=model, default=current == model) for model in models]
        super().__init__(placeholder='Modelo da Mistral', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if not is_owner(interaction.user.id):
            return await deny(interaction)
        await settings.update({'model': self.values[0]})
        data = await settings.get()
        await interaction.response.edit_message(view=ConfigPanel(data))


class ChannelSelect(discord.ui.ChannelSelect):
    def __init__(self):
        super().__init__(placeholder='Canal de resposta', min_values=1, max_values=1, channel_types=[discord.ChannelType.text, discord.ChannelType.news, discord.ChannelType.public_thread, discord.ChannelType.private_thread])

    async def callback(self, interaction: discord.Interaction):
        if not is_owner(interaction.user.id):
            return await deny(interaction)
        channel = self.values[0]
        await settings.update({'channel_id': str(channel.id)})
        data = await settings.get()
        await interaction.response.edit_message(view=ConfigPanel(data))


class MentionTargetSelect(discord.ui.UserSelect):
    def __init__(self):
        super().__init__(placeholder='Pessoa ou bot para acionar por menção', min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        if not is_owner(interaction.user.id):
            return await deny(interaction)
        user = self.values[0]
        await settings.update({'mention_target_id': str(user.id)})
        data = await settings.get()
        await interaction.response.edit_message(view=ConfigPanel(data))


class SelectRow(discord.ui.ActionRow):
    def __init__(self, item):
        super().__init__()
        self.add_item(item)


class ConfigActions(discord.ui.ActionRow):
    def __init__(self, data: dict):
        super().__init__()
        self.data = data

    @discord.ui.button(label='Key', style=discord.ButtonStyle.primary)
    async def key(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_owner(interaction.user.id):
            return await deny(interaction)
        await interaction.response.send_modal(ConfigModal('mistral_api_key', 'Key da Mistral', self.data.get('mistral_api_key', '')))

    @discord.ui.button(label='Prompt', style=discord.ButtonStyle.primary)
    async def prompt(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_owner(interaction.user.id):
            return await deny(interaction)
        await interaction.response.send_modal(ConfigModal('prompt', 'Prompt', self.data.get('prompt', '')))

    @discord.ui.button(label='Limpar canal', style=discord.ButtonStyle.secondary)
    async def clear_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_owner(interaction.user.id):
            return await deny(interaction)
        await settings.update({'channel_id': ''})
        data = await settings.get()
        await interaction.response.edit_message(view=ConfigPanel(data))

    @discord.ui.button(label='Limpar menção', style=discord.ButtonStyle.secondary)
    async def clear_mention(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_owner(interaction.user.id):
            return await deny(interaction)
        await settings.update({'mention_target_id': ''})
        data = await settings.get()
        await interaction.response.edit_message(view=ConfigPanel(data))

    @discord.ui.button(label='Resetar', style=discord.ButtonStyle.danger)
    async def reset(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_owner(interaction.user.id):
            return await deny(interaction)
        await settings.reset()
        data = await settings.get()
        await interaction.response.edit_message(view=ConfigPanel(data))


class ConfigPanel(discord.ui.LayoutView):
    def __init__(self, data: dict):
        super().__init__(timeout=300)
        key_state = 'salva' if data.get('mistral_api_key') else 'vazia'
        channel = f'<#{data.get("channel_id")}>' if data.get('channel_id') else 'nenhum'
        mention = f'<@{data.get("mention_target_id")}>' if data.get('mention_target_id') else 'bot'
        prompt = data.get('prompt') or 'vazio'
        if len(prompt) > 350:
            prompt = prompt[:347] + '...'
        self.add_item(discord.ui.Container(
            discord.ui.TextDisplay('## Configurações\nAjuste tudo por aqui.'),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                f'**Key:** `{key_state}`\n'
                f'**Modelo:** `{data.get("model", "mistral-medium-latest")}`\n'
                f'**Modo:** `{data.get("mode", "mention")}`\n'
                f'**Canal:** {channel}\n'
                f'**Menção:** {mention}\n'
                f'**Prompt:**\n```{prompt}```'
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            SelectRow(ModelSelect(data.get('model', 'mistral-medium-latest'))),
            SelectRow(ModeSelect(data.get('mode', 'mention'))),
            SelectRow(ChannelSelect()),
            SelectRow(MentionTargetSelect()),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            ConfigActions(data),
            accent_color=0x5865F2
        ))


class SimpleMessage(discord.ui.LayoutView):
    def __init__(self, title: str, description: str, color: int):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Container(discord.ui.TextDisplay(f'## {title}\n{description}'[:4000]), accent_color=color))


def message_view(title: str, description: str, color: int):
    return SimpleMessage(title, description, color)


@app_commands.command(name='config', description='Abre as configurações')
async def config_cmd(interaction: discord.Interaction):
    if not is_owner(interaction.user.id):
        return await deny(interaction)
    data = await settings.get()
    await interaction.response.send_message(view=ConfigPanel(data), ephemeral=True)


def setup(tree):
    tree.add_command(config_cmd)
