import discord
from discord import app_commands

PROTECTED_INFO = {
    "creator_name": "Meliodas",
    "creator_id": "1389706621697134674",
    "github_url": "https://github.com/meliodasdev337",
    "discord_server": "https://discord.gg/awsupjWb9x",
    "bot_name": "Base.py"
}


class CreditosView(discord.ui.LayoutView):
    def __init__(self, bot: discord.Client):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Container(
            discord.ui.Section(
                "## Créditos do Bot\n"
                "**Criador:** Meliodas\n"
                "**Projeto:** Base.py\n"
                "**Tecnologias:** Discord.py 2.6+, Python, MongoDB opcional e Mistral AI\n"
                f"**Servidores:** `{len(bot.guilds)}`\n"
                f"**Usuários:** `{sum(g.member_count or 0 for g in bot.guilds)}`\n"
                f"**Comandos:** `{len(bot.tree.get_commands())}`",
                accessory=discord.ui.Thumbnail(bot.user.display_avatar.url)
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                "### Sobre\n"
                "Base pública desenvolvida por **Meliodas** para bots Discord modernos com slash commands e Components V2."
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            CreditosRow(),
            accent_color=0x5865F2
        ))


class CreditosRow(discord.ui.ActionRow):
    def __init__(self):
        super().__init__()
        self.add_item(discord.ui.Button(label="GitHub", style=discord.ButtonStyle.link, url=PROTECTED_INFO["github_url"], emoji="💻"))
        self.add_item(discord.ui.Button(label="Discord", style=discord.ButtonStyle.link, url=f"https://discord.com/users/{PROTECTED_INFO['creator_id']}", emoji="👤"))
        self.add_item(discord.ui.Button(label="Servidor", style=discord.ButtonStyle.link, url=PROTECTED_INFO["discord_server"], emoji="🌐"))


@app_commands.command(name="creditos", description="Mostra informações sobre o criador do bot")
async def creditos(interaction: discord.Interaction):
    await interaction.response.send_message(view=CreditosView(interaction.client))


def setup(tree: app_commands.CommandTree):
    tree.add_command(creditos)
