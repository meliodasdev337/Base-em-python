import discord
from discord import app_commands
import json
import os
from datetime import timedelta

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
    name="ban",
    description="Bane um usuário do servidor"
)
@app_commands.describe(
    usuario="Usuário para banir",
    motivo="Motivo do banimento",
    deletar_mensagens="Número de dias de mensagens para deletar"
)
@app_commands.choices(deletar_mensagens=[
    app_commands.Choice(name="0 dias", value=0),
    app_commands.Choice(name="1 dia", value=1),
    app_commands.Choice(name="3 dias", value=3),
    app_commands.Choice(name="7 dias", value=7)
])
@app_commands.default_permissions(ban_members=True)
@app_commands.checks.has_permissions(ban_members=True)
async def ban(
    interaction: discord.Interaction,
    usuario: discord.Member,
    motivo: str = "Sem motivo especificado",
    deletar_mensagens: int = 0
):
    if not interaction.user.guild_permissions.ban_members:
        embed = discord.Embed(
            title=f"{emoji('erro')} Permissão Negada",
            description="Você precisa da permissão **Banir Membros** para usar este comando.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if usuario == interaction.user:
        embed = discord.Embed(
            title=f"{emoji('erro')} Erro",
            description="Você não pode banir a si mesmo.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if usuario.top_role >= interaction.user.top_role:
        embed = discord.Embed(
            title=f"{emoji('erro')} Erro",
            description="Você não pode banir um usuário com cargo igual ou superior ao seu.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if not interaction.guild.me.guild_permissions.ban_members:
        embed = discord.Embed(
            title=f"{emoji('erro')} Erro do Bot",
            description="Eu não tenho permissão para banir membros.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if usuario.top_role >= interaction.guild.me.top_role:
        embed = discord.Embed(
            title=f"{emoji('erro')} Erro do Bot",
            description="Não posso banir um usuário com cargo igual ou superior ao meu.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    embed = discord.Embed(
        title=f"{emoji('certo')} Confirmação de Banimento",
        description=f"Você está prestes a banir **{usuario.name}**.",
        color=discord.Color.orange(),
        timestamp=discord.utils.utcnow()
    )
    
    embed.add_field(name="Usuário:", value=f"{usuario.mention} ({usuario.id})", inline=True)
    embed.add_field(name="Motivo:", value=motivo, inline=False)
    embed.add_field(name="Deletar Mensagens:", value=f"{deletar_mensagens} dias", inline=True)
    embed.set_footer(text="Esta ação não pode ser desfeita")
    
    class ConfirmView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=30)
            self.value = None
        
        @discord.ui.button(label="Confirmar", style=discord.ButtonStyle.danger, emoji=emoji("certo") or "✅")
        async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.value = True
            await interaction.response.defer()
            self.stop()
        
        @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.secondary, emoji=emoji("erro") or "❌")
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
            description="A confirmação de banimento expirou.",
            color=discord.Color.light_gray()
        )
        await interaction.edit_original_response(embed=embed, view=None)
        return
    
    if view.value:
        try:
            await usuario.ban(
                reason=f"{interaction.user.name}: {motivo}",
                delete_message_days=deletar_mensagens
            )
            
            embed = discord.Embed(
                title=f"{emoji('certo')} Usuário Banido",
                description=f"**{usuario.name}** foi banido do servidor.",
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )
            
            embed.add_field(name="Usuário:", value=f"{usuario.mention} ({usuario.id})", inline=True)
            embed.add_field(name="Motivo:", value=motivo, inline=False)
            embed.add_field(name="Banido por:", value=interaction.user.mention, inline=True)
            embed.add_field(name="Mensagens Deletadas:", value=f"{deletar_mensagens} dias", inline=True)
            
            await interaction.edit_original_response(embed=embed, view=None)
            
        except discord.Forbidden:
            embed = discord.Embed(
                title=f"{emoji('erro')} Erro",
                description="Não tenho permissão para banir este usuário.",
                color=discord.Color.red()
            )
            await interaction.edit_original_response(embed=embed, view=None)
            
        except discord.HTTPException as e:
            embed = discord.Embed(
                title=f"{emoji('erro')} Erro",
                description=f"Ocorreu um erro ao banir: {e}",
                color=discord.Color.red()
            )
            await interaction.edit_original_response(embed=embed, view=None)
    else:
        embed = discord.Embed(
            title=f"{emoji('certo')} Ação Cancelada",
            description="O banimento foi cancelado.",
            color=discord.Color.green()
        )
        await interaction.edit_original_response(embed=embed, view=None)

@ban.error
async def ban_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        embed = discord.Embed(
            title=f"{emoji('erro')} Permissão Negada",
            description="Você precisa da permissão **Banir Membros** para usar este comando.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

def setup(tree: app_commands.CommandTree):
    tree.add_command(ban)
