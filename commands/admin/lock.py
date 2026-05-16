import discord
from discord import app_commands


class MessageView(discord.ui.LayoutView):
    def __init__(self, title: str, description: str, color: int):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Container(discord.ui.TextDisplay(f"## {title}\n{description}"), accent_color=color))


class UnlockRow(discord.ui.ActionRow):
    def __init__(self, channel_id: int):
        super().__init__()
        self.channel_id = channel_id

    @discord.ui.button(label="Destravar canal", style=discord.ButtonStyle.success, emoji="🔓")
    async def unlock(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.manage_channels:
            return await interaction.response.send_message(view=MessageView("Permissão negada", "Você precisa da permissão **Gerenciar Canais**.", 0xED4245), ephemeral=True)
        channel = interaction.guild.get_channel(self.channel_id)
        if not channel:
            return await interaction.response.send_message(view=MessageView("Erro", "Canal não encontrado.", 0xED4245), ephemeral=True)
        await channel.set_permissions(interaction.guild.default_role, send_messages=True)
        await interaction.response.edit_message(view=MessageView("Canal destravado", f"{channel.mention} foi destravado por {interaction.user.mention}.", 0x57F287))


class LockView(discord.ui.LayoutView):
    def __init__(self, channel: discord.abc.GuildChannel, user: discord.abc.User, motivo: str):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Container(
            discord.ui.TextDisplay(f"## Canal trancado\n{channel.mention} foi trancado por {user.mention}.\n**Motivo:** {motivo}"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            UnlockRow(channel.id),
            accent_color=0xED4245
        ))


@app_commands.command(name="lock", description="Tranca o canal atual para todos os membros")
@app_commands.default_permissions(manage_channels=True)
@app_commands.checks.has_permissions(manage_channels=True)
async def lock(interaction: discord.Interaction, motivo: str = "Sem motivo especificado"):
    if not interaction.user.guild_permissions.manage_channels:
        return await interaction.response.send_message(view=MessageView("Permissão negada", "Você precisa da permissão **Gerenciar Canais**.", 0xED4245), ephemeral=True)
    channel = interaction.channel
    if isinstance(channel, discord.TextChannel):
        await channel.set_permissions(interaction.guild.default_role, send_messages=False)
        await interaction.response.send_message(view=LockView(channel, interaction.user, motivo))
    elif isinstance(channel, discord.Thread):
        await channel.edit(locked=True)
        await interaction.response.send_message(view=MessageView("Thread trancada", f"A thread foi trancada por {interaction.user.mention}.\n**Motivo:** {motivo}", 0xED4245))
    else:
        await interaction.response.send_message(view=MessageView("Erro", "Esse tipo de canal não pode ser trancado por este comando.", 0xED4245), ephemeral=True)


@lock.error
async def lock_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(view=MessageView("Permissão negada", "Você precisa da permissão **Gerenciar Canais**.", 0xED4245), ephemeral=True)


def setup(tree: app_commands.CommandTree):
    tree.add_command(lock)
