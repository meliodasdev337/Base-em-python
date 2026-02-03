import discord
from discord import app_commands, ui
from discord.ext import commands
import json
import os

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

class LockView(ui.View):
    def __init__(self, channel_id: int, author_id: int):
        super().__init__(timeout=None)
        self.channel_id = channel_id
        self.author_id = author_id
    
    @ui.button(label="Destravar Canal", style=discord.ButtonStyle.green, custom_id="unlock_button", emoji=emoji("atualizar") or "🔓")
    async def unlock_button(self, interaction: discord.Interaction, button: ui.Button):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message(
                f"{emoji('erro')} Você precisa da permissão **Gerenciar Canais** para destravar.",
                ephemeral=True
            )
            return
        
        channel = interaction.guild.get_channel(self.channel_id)
        if not channel:
            await interaction.response.send_message(
                f"{emoji('erro')} Canal não encontrado.",
                ephemeral=True
            )
            return
        
        await channel.set_permissions(interaction.guild.default_role, send_messages=True)
        
        embed = discord.Embed(
            title=f"{emoji('certo')} Canal Destravado",
            description=f"O canal {channel.mention} foi destravado por {interaction.user.mention}.",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )
        
        await interaction.response.send_message(embed=embed)
        
        for item in self.children:
            item.disabled = True
        
        await interaction.message.edit(view=self)
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.guild_permissions.manage_channels

@app_commands.command(
    name="lock",
    description="Tranca o canal atual para todos os membros"
)
@app_commands.default_permissions(manage_channels=True)
@app_commands.checks.has_permissions(manage_channels=True)
async def lock(interaction: discord.Interaction, motivo: str = "Sem motivo especificado"):
    if not interaction.user.guild_permissions.manage_channels:
        embed = discord.Embed(
            title=f"{emoji('erro')} Permissão Negada",
            description="Você precisa da permissão **Gerenciar Canais** para usar este comando.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    channel = interaction.channel
    
    if isinstance(channel, discord.TextChannel):
        await channel.set_permissions(interaction.guild.default_role, send_messages=False)
        
        embed = discord.Embed(
            title=f"{emoji('certo')} Canal Trancado",
            description=f"O canal {channel.mention} foi trancado por {interaction.user.mention}.",
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )
        
        embed.add_field(name="Motivo:", value=motivo, inline=False)
        embed.add_field(name="Ação:", value="Use o botão abaixo para destravar o canal.", inline=False)
        embed.set_footer(text=f"Trancado por {interaction.user}", icon_url=interaction.user.avatar.url)
        
        view = LockView(channel.id, interaction.user.id)
        
        await interaction.response.send_message(embed=embed, view=view)
        
    elif isinstance(channel, discord.Thread):
        await channel.edit(locked=True)
        
        embed = discord.Embed(
            title=f"{emoji('certo')} Thread Trancada",
            description=f"A thread foi trancada por {interaction.user.mention}.",
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )
        
        embed.add_field(name="Motivo:", value=motivo, inline=False)
        embed.set_footer(text=f"Trancado por {interaction.user}", icon_url=interaction.user.avatar.url)
        
        await interaction.response.send_message(embed=embed)

@lock.error
async def lock_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        embed = discord.Embed(
            title=f"{emoji('erro')} Permissão Negada",
            description="Você precisa da permissão **Gerenciar Canais** para usar este comando.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

def setup(tree: app_commands.CommandTree):
    tree.add_command(lock)
