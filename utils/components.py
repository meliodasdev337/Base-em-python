import discord


def text_block(title: str, description: str = "", color: discord.Color | int = 0x5865F2):
    if isinstance(color, discord.Color):
        color = color.value
    body = f"## {title}"
    if description:
        body += f"\n{description}"
    return discord.ui.Container(
        discord.ui.TextDisplay(body[:4000]),
        accent_color=color
    )


class BasePanel(discord.ui.LayoutView):
    def __init__(self, title: str, description: str = "", color: discord.Color | int = 0x5865F2, timeout: float | None = 180):
        super().__init__(timeout=timeout)
        self.add_item(text_block(title, description, color))


async def send_panel(interaction: discord.Interaction, title: str, description: str = "", color: discord.Color | int = 0x5865F2, ephemeral: bool = False):
    view = BasePanel(title, description, color)
    if interaction.response.is_done():
        return await interaction.followup.send(view=view, ephemeral=ephemeral)
    return await interaction.response.send_message(view=view, ephemeral=ephemeral)


async def edit_panel(interaction: discord.Interaction, title: str, description: str = "", color: discord.Color | int = 0x5865F2):
    view = BasePanel(title, description, color)
    return await interaction.edit_original_response(view=view)
