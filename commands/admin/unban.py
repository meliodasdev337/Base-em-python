import discord
from discord import app_commands


class MessageView(discord.ui.LayoutView):
    def __init__(self, title: str, description: str, color: int):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Container(discord.ui.TextDisplay(f"## {title}\n{description}"), accent_color=color))


class UnbanConfirmRow(discord.ui.ActionRow):
    def __init__(self, user_id: int, motivo: str, author_id: int):
        super().__init__()
        self.user_id = user_id
        self.motivo = motivo
        self.author_id = author_id

    @discord.ui.button(label="Confirmar", style=discord.ButtonStyle.success, emoji="✅")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id:
            return await interaction.response.send_message(view=MessageView("Acesso negado", "Essa confirmação não é sua.", 0xED4245), ephemeral=True)
        try:
            banned_user = None
            async for entry in interaction.guild.bans():
                if entry.user.id == self.user_id:
                    banned_user = entry.user
                    break
            if not banned_user:
                return await interaction.response.edit_message(view=MessageView("Usuário não banido", f"O ID `{self.user_id}` não está banido neste servidor.", 0xED4245))
            await interaction.guild.unban(banned_user, reason=f"{interaction.user.name}: {self.motivo}")
            await interaction.response.edit_message(view=MessageView("Usuário desbanido", f"**{banned_user}** foi desbanido.\n**Motivo:** {self.motivo}", 0x57F287))
        except discord.Forbidden:
            await interaction.response.edit_message(view=MessageView("Permissão negada", "Não tenho permissão para desbanir este usuário.", 0xED4245))
        except discord.HTTPException as e:
            await interaction.response.edit_message(view=MessageView("Erro", f"Ocorreu um erro ao desbanir: `{e}`", 0xED4245))

    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.secondary, emoji="❌")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id:
            return await interaction.response.send_message(view=MessageView("Acesso negado", "Essa confirmação não é sua.", 0xED4245), ephemeral=True)
        await interaction.response.edit_message(view=MessageView("Ação cancelada", "O desbanimento foi cancelado.", 0x5865F2))


class UnbanConfirmView(discord.ui.LayoutView):
    def __init__(self, user_id: int, motivo: str, author_id: int):
        super().__init__(timeout=30)
        self.add_item(discord.ui.Container(
            discord.ui.TextDisplay(f"## Confirmação de desbanimento\nVocê está prestes a desbanir o ID `{user_id}`.\n**Motivo:** {motivo}"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            UnbanConfirmRow(user_id, motivo, author_id),
            accent_color=0x57F287
        ))


@app_commands.command(name="unban", description="Remove o banimento de um usuário")
@app_commands.describe(usuario_id="ID do usuário para desbanir", motivo="Motivo do desbanimento")
@app_commands.default_permissions(ban_members=True)
@app_commands.checks.has_permissions(ban_members=True)
async def unban(interaction: discord.Interaction, usuario_id: str, motivo: str = "Sem motivo especificado"):
    if not interaction.user.guild_permissions.ban_members:
        return await interaction.response.send_message(view=MessageView("Permissão negada", "Você precisa da permissão **Banir Membros**.", 0xED4245), ephemeral=True)
    if not interaction.guild.me.guild_permissions.ban_members:
        return await interaction.response.send_message(view=MessageView("Erro do bot", "Eu não tenho permissão para gerenciar banimentos.", 0xED4245), ephemeral=True)
    try:
        user_id = int(usuario_id)
    except ValueError:
        return await interaction.response.send_message(view=MessageView("ID inválido", "O ID do usuário deve conter apenas números.", 0xED4245), ephemeral=True)
    await interaction.response.send_message(view=UnbanConfirmView(user_id, motivo, interaction.user.id), ephemeral=True)


@unban.error
async def unban_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(view=MessageView("Permissão negada", "Você precisa da permissão **Banir Membros**.", 0xED4245), ephemeral=True)


def setup(tree: app_commands.CommandTree):
    tree.add_command(unban)
