import discord
from discord import app_commands


class MessageView(discord.ui.LayoutView):
    def __init__(self, title: str, description: str, color: int):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Container(discord.ui.TextDisplay(f"## {title}\n{description}"), accent_color=color))


class BanConfirmRow(discord.ui.ActionRow):
    def __init__(self, usuario: discord.Member, motivo: str, dias: int, author_id: int):
        super().__init__()
        self.usuario = usuario
        self.motivo = motivo
        self.dias = dias
        self.author_id = author_id

    @discord.ui.button(label="Confirmar", style=discord.ButtonStyle.danger, emoji="✅")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id:
            return await interaction.response.send_message(view=MessageView("Acesso negado", "Essa confirmação não é sua.", 0xED4245), ephemeral=True)
        try:
            await self.usuario.ban(reason=f"{interaction.user.name}: {self.motivo}", delete_message_days=self.dias)
            await interaction.response.edit_message(view=MessageView("Usuário banido", f"**{self.usuario}** foi banido.\n**Motivo:** {self.motivo}\n**Mensagens deletadas:** {self.dias} dias", 0xED4245))
        except discord.Forbidden:
            await interaction.response.edit_message(view=MessageView("Erro", "Não tenho permissão para banir este usuário.", 0xED4245))
        except discord.HTTPException as e:
            await interaction.response.edit_message(view=MessageView("Erro", f"Ocorreu um erro ao banir: `{e}`", 0xED4245))

    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.secondary, emoji="❌")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id:
            return await interaction.response.send_message(view=MessageView("Acesso negado", "Essa confirmação não é sua.", 0xED4245), ephemeral=True)
        await interaction.response.edit_message(view=MessageView("Ação cancelada", "O banimento foi cancelado.", 0x57F287))


class BanConfirmView(discord.ui.LayoutView):
    def __init__(self, usuario: discord.Member, motivo: str, dias: int, author_id: int):
        super().__init__(timeout=30)
        self.add_item(discord.ui.Container(
            discord.ui.TextDisplay(f"## Confirmação de banimento\nVocê está prestes a banir **{usuario}**.\n**ID:** `{usuario.id}`\n**Motivo:** {motivo}\n**Deletar mensagens:** {dias} dias"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            BanConfirmRow(usuario, motivo, dias, author_id),
            accent_color=0xED4245
        ))


@app_commands.command(name="ban", description="Bane um usuário do servidor")
@app_commands.describe(usuario="Usuário para banir", motivo="Motivo do banimento", deletar_mensagens="Número de dias de mensagens para deletar")
@app_commands.choices(deletar_mensagens=[
    app_commands.Choice(name="0 dias", value=0),
    app_commands.Choice(name="1 dia", value=1),
    app_commands.Choice(name="3 dias", value=3),
    app_commands.Choice(name="7 dias", value=7)
])
@app_commands.default_permissions(ban_members=True)
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, usuario: discord.Member, motivo: str = "Sem motivo especificado", deletar_mensagens: int = 0):
    if not interaction.user.guild_permissions.ban_members:
        return await interaction.response.send_message(view=MessageView("Permissão negada", "Você precisa da permissão **Banir Membros**.", 0xED4245), ephemeral=True)
    if usuario == interaction.user:
        return await interaction.response.send_message(view=MessageView("Erro", "Você não pode banir a si mesmo.", 0xED4245), ephemeral=True)
    if usuario.top_role >= interaction.user.top_role and interaction.guild.owner_id != interaction.user.id:
        return await interaction.response.send_message(view=MessageView("Erro", "Você não pode banir alguém com cargo igual ou superior ao seu.", 0xED4245), ephemeral=True)
    if not interaction.guild.me.guild_permissions.ban_members:
        return await interaction.response.send_message(view=MessageView("Erro do bot", "Eu não tenho permissão para banir membros.", 0xED4245), ephemeral=True)
    if usuario.top_role >= interaction.guild.me.top_role:
        return await interaction.response.send_message(view=MessageView("Erro do bot", "Não posso banir usuário com cargo igual ou superior ao meu.", 0xED4245), ephemeral=True)
    await interaction.response.send_message(view=BanConfirmView(usuario, motivo, deletar_mensagens, interaction.user.id), ephemeral=True)


@ban.error
async def ban_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(view=MessageView("Permissão negada", "Você precisa da permissão **Banir Membros**.", 0xED4245), ephemeral=True)


def setup(tree: app_commands.CommandTree):
    tree.add_command(ban)
