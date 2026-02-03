import discord
from discord import app_commands
import json
import os
from datetime import datetime

EMOJI_DB = "database/emojis_ids.json"

def emoji(name: str) -> str:
    if not os.path.exists(EMOJI_DB):
        return ""
    try:
        with open(EMOJI_DB, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get(name, {}).get("full", "")
    except:
        return ""

PROTECTED_INFO = {
    "creator_name": "Meliodas",
    "creator_id": "1389706621697134674",
    "github_url": "https://github.com/meliodasdev337",
    "discord_server": "https://discord.gg/awsupjWb9x",
    "bot_name": "Base.py"
}

def verify_credits_integrity():
    with open(__file__, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_info = ["Meliodas", "1389706621697134674", "github.com/meliodasdev337", "awsupjWb9x"]
    
    for info in required_info:
        if info not in content:
            return False
    
    return True

class CreditosView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
        github_button = discord.ui.Button(
            label="GitHub",
            style=discord.ButtonStyle.link,
            url=PROTECTED_INFO["github_url"],
            emoji="💻"
        )
        
        discord_button = discord.ui.Button(
            label="Discord",
            style=discord.ButtonStyle.link,
            url=f"https://discord.com/users/{PROTECTED_INFO['creator_id']}",
            emoji="👤"
        )
        
        server_button = discord.ui.Button(
            label="Servidor",
            style=discord.ButtonStyle.link,
            url=PROTECTED_INFO["discord_server"],
            emoji="🌐"
        )
        
        self.add_item(github_button)
        self.add_item(discord_button)
        self.add_item(server_button)

@app_commands.command(
    name="creditos",
    description="Mostra informações sobre o criador do bot"
)
async def creditos(interaction: discord.Interaction):
    if not verify_credits_integrity():
        embed = discord.Embed(
            title=f"{emoji('erro')} Erro de Integridade",
            description="Os créditos do bot foram modificados.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    embed = discord.Embed(
        title=f"{emoji('info')} Créditos do Bot",
        description="Informações sobre o desenvolvimento e criação deste bot.",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )
    
    embed.set_thumbnail(url=interaction.client.user.display_avatar.url)
    
    embed.add_field(
        name=f"{emoji('certo')} Criador",
        value="**Meliodas**\n"
              "Desenvolvedor & Bot Developer\n"
              "Especializado em Discord bots",
        inline=False
    )
    
    embed.add_field(
        name=f"{emoji('net')} Tecnologias Utilizadas",
        value="```yaml\n"
              "• Discord.py v2.4.0\n"
              "• Python 3.11+\n"
              "• MongoDB (Motor)\n"
              "• Mistral AI API\n"
              "```",
        inline=True
    )
    
    embed.add_field(
        name=f"{emoji('tempo')} Estatísticas",
        value=f"```yaml\n"
              f"Servidores: {len(interaction.client.guilds)}\n"
              f"Usuários: {sum(g.member_count for g in interaction.client.guilds)}\n"
              f"Comandos: {len(interaction.client.tree.get_commands())}\n"
              f"```",
        inline=True
    )
    
    embed.add_field(
        name=f"{emoji('atualizar')} Contato",
        value=f"**ID do Discord:** `1389706621697134674`\n"
              "**GitHub:** [meliodasdev337](https://github.com/meliodasdev337)\n"
              "**Servidor:** [Discord](https://discord.gg/awsupjWb9x)",
        inline=False
    )
    
    embed.add_field(
        name=f"{emoji('grafico')} Sobre o Bot",
        value="Este bot é uma base pública desenvolvida por **Meliodas**.\n"
              "Código aberto e gratuito para uso e modificação.\n"
              "Se você gostou do projeto, considere dar uma ⭐ no GitHub!",
        inline=False
    )
    
    embed.set_footer(
        text=f"Base.py • Criado com ❤️ por Meliodas",
        icon_url="https://avatars.githubusercontent.com/u/1464688517064953980"
    )
    
    view = CreditosView()
    
    await interaction.response.send_message(embed=embed, view=view)

def setup(tree: app_commands.CommandTree):
    tree.add_command(creditos)