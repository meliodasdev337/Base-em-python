import discord
from discord import app_commands
import json
import os
from typing import Optional

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

@app_commands.command(
    name="unban",
    description="Remove o banimento de um usuário"
)
@app_commands.describe(
    usuario_id="ID do usuário para desbanir",
    motivo="Motivo do desbanimento"
)
@app_commands.default_permissions(ban_members=True)
@app_commands.checks.has_permissions(ban_members=True)
async def unban(
    interaction: discord.Interaction,
    usuario_id: str,
    motivo: str = "Sem motivo especificado"
):
    if not interaction.user.guild_permissions.ban_members:
        embed = discord.Embed(
            title=f"{emoji('erro')} Permissão Negada",
            description="Você precisa da permissão **Banir Membros** para usar este comando.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if not interaction.guild.me.guild_permissions.ban_members:
        embed = discord.Embed(
            title=f"{emoji('erro')} Erro do Bot",
            description="Eu não tenho permissão para gerenciar banimentos.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    try:
        user_id = int(usuario_id)
    except ValueError:
        embed = discord.Embed(
            title=f"{emoji('erro')} ID Inválido",
            description="O ID do usuário deve conter apenas números.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if user_id == interaction.user.id:
        embed = discord.Embed(
            title=f"{emoji('erro')} Erro",
            description="Você não pode se desbanir.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if user_id == interaction.client.user.id:
        embed = discord.Embed(
            title=f"{emoji('erro')} Erro",
            description="Eu não posso me desbanir.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    embed = discord.Embed(
        title=f"{emoji('certo')} Confirmação de Desbanimento",
        description=f"Você está prestes a desbanir o usuário com ID **{user_id}**.",
        color=discord.Color.orange()
    )
    
    embed.add_field(name="ID do Usuário:", value=f"`{user_id}`", inline=True)
    embed.add_field(name="Motivo:", value=motivo, inline=False)
    embed.set_footer(text="Esta ação irá remover o banimento do usuário")
    
    class ConfirmView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=30)
            self.value = None
        
        @discord.ui.button(label="Confirmar", style=discord.ButtonStyle.green, emoji=emoji('certo') or "✅")
        async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.value = True
            await interaction.response.defer()
            self.stop()
        
        @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.secondary, emoji=emoji('erro') or "❌")
        async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.value = False
            await interaction.response.defer()
            self.stop()
    
    view = ConfirmView()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    await view.wait()
    
    if view.value is None:
        embed = discord.Embed(
            title="⏰ Tempo Esgotado",
            description="A confirmação de desbanimento expirou.",
            color=discord.Color.light_gray()
        )
        await interaction.edit_original_response(embed=embed, view=None)
        return
    
    if view.value:
        try:
            user = await interaction.client.fetch_user(user_id)
            
            bans = await interaction.guild.bans()
            banned_user = None
            
            for ban_entry in bans:
                if ban_entry.user.id == user_id:
                    banned_user = ban_entry.user
                    break
            
            if not banned_user:
                embed = discord.Embed(
                    title=f"{emoji('erro')} Usuário Não Banido",
                    description=f"O usuário com ID `{user_id}` não está banido deste servidor.",
                    color=discord.Color.red()
                )
                await interaction.edit_original_response(embed=embed, view=None)
                return
            
            await interaction.guild.unban(banned_user, reason=f"{interaction.user.name}: {motivo}")
            
            embed = discord.Embed(
                title=f"{emoji('certo')} Usuário Desbanido",
                description=f"**{user.name if user else 'Usuário'}** foi desbanido do servidor.",
                color=discord.Color.green()
            )
            
            if user:
                embed.add_field(name="Usuário:", value=f"{user.mention} ({user.id})", inline=True)
            else:
                embed.add_field(name="ID:", value=f"`{user_id}`", inline=True)
            
            embed.add_field(name="Motivo:", value=motivo, inline=False)
            embed.add_field(name="Desbanido por:", value=interaction.user.mention, inline=True)
            
            await interaction.edit_original_response(embed=embed, view=None)
            
        except discord.NotFound:
            embed = discord.Embed(
                title=f"{emoji('erro')} Usuário Não Encontrado",
                description=f"Não foi possível encontrar um usuário com o ID `{user_id}`.",
                color=discord.Color.red()
            )
            await interaction.edit_original_response(embed=embed, view=None)
            
        except discord.Forbidden:
            embed = discord.Embed(
                title=f"{emoji('erro')} Permissão Negada",
                description="Não tenho permissão para desbanir este usuário.",
                color=discord.Color.red()
            )
            await interaction.edit_original_response(embed=embed, view=None)
            
        except discord.HTTPException as e:
            embed = discord.Embed(
                title=f"{emoji('erro')} Erro",
                description=f"Ocorreu um erro ao desbanir: {e}",
                color=discord.Color.red()
            )
            await interaction.edit_original_response(embed=embed, view=None)
    else:
        embed = discord.Embed(
            title=f"{emoji('certo')} Ação Cancelada",
            description="O desbanimento foi cancelado.",
            color=discord.Color.green()
        )
        await interaction.edit_original_response(embed=embed, view=None)

@unban.error
async def unban_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        embed = discord.Embed(
            title=f"{emoji('erro')} Permissão Negada",
            description="Você precisa da permissão **Banir Membros** para usar este comando.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

def setup(tree: app_commands.CommandTree):
    tree.add_command(unban)