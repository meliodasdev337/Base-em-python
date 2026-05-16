import discord
from discord import app_commands
import time
import aiohttp
from datetime import datetime

start_time = time.time()


def format_uptime() -> str:
    uptime = time.time() - start_time
    days = int(uptime // 86400)
    hours = int((uptime % 86400) // 3600)
    minutes = int((uptime % 3600) // 60)
    seconds = int(uptime % 60)
    if days:
        return f"{days}d {hours}h {minutes}m {seconds}s"
    return f"{hours}h {minutes}m {seconds}s"


def get_latency_bar(latency: int) -> str:
    if latency < 50:
        return "🟢🟢🟢🟢🟢"
    if latency < 100:
        return "🟡🟡🟡🟡⚪"
    if latency < 200:
        return "🟠🟠🟠⚪⚪"
    return "🔴🔴⚪⚪⚪"


def get_speed_rating(latency: int) -> str:
    if latency < 50:
        return "⚡ Velocidade Extrema"
    if latency < 100:
        return "🚀 Muito Rápido"
    if latency < 150:
        return "🏎️ Rápido"
    if latency < 200:
        return "🚗 Moderado"
    return "🚶 Lento"


async def discord_status_text():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://discordstatus.com/api/v2/status.json', timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    indicator = data.get('status', {}).get('indicator', 'none')
                    description = data.get('status', {}).get('description', 'Operational')
                    if indicator == 'none':
                        return 0x57F287, f"🟢 **Status:** {description}\n**API:** Operacional\n**Gateway:** Estável\n**CDN:** Normal"
                    if indicator == 'minor':
                        return 0xFEE75C, f"🟡 **Status:** {description}\n**API:** Degradada\n**Gateway:** Estável\n**CDN:** Normal"
                    return 0xED4245, f"🔴 **Status:** {description}\n**API:** Parcial\n**Gateway:** Instável\n**CDN:** Degradada"
    except Exception:
        pass
    return 0x5865F2, "Não foi possível consultar a API de status do Discord agora."


class PingSelect(discord.ui.Select):
    def __init__(self, user_id: int):
        options = [
            discord.SelectOption(label="Status básico", description="Latência e uptime", value="basic", emoji="📊"),
            discord.SelectOption(label="Status Discord", description="Consulta discordstatus.com", value="discord", emoji="🌐"),
            discord.SelectOption(label="Velocidade", description="Classificação da conexão", value="speed", emoji="⚡"),
            discord.SelectOption(label="Atualizar", description="Recarrega dados", value="refresh", emoji="🔄")
        ]
        self.user_id = user_id
        super().__init__(placeholder="Escolha uma opção", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message(view=SimplePingView("Acesso negado", "Esse painel não é seu.", 0xED4245), ephemeral=True)
        latency = round(interaction.client.latency * 1000)
        value = self.values[0]
        if value == 'discord':
            color, description = await discord_status_text()
            return await interaction.response.edit_message(view=PingView(interaction.user.id, "Status do Discord", description, color))
        if value == 'speed':
            description = f"**WebSocket:** `{latency}ms`\n**Barra:** {get_latency_bar(latency)}\n**Classificação:** {get_speed_rating(latency)}"
            return await interaction.response.edit_message(view=PingView(interaction.user.id, "Teste de velocidade", description, 0x5865F2))
        if value == 'refresh':
            now = datetime.now().strftime('%H:%M:%S')
            description = f"**WebSocket:** `{latency}ms`\n**Uptime:** `{format_uptime()}`\n**Atualizado às:** `{now}`"
            return await interaction.response.edit_message(view=PingView(interaction.user.id, "Dados atualizados", description, 0x57F287))
        description = f"**WebSocket:** `{latency}ms`\n**Barra:** {get_latency_bar(latency)}\n**Uptime:** `{format_uptime()}`"
        await interaction.response.edit_message(view=PingView(interaction.user.id, "Status básico", description, 0x57F287 if latency < 100 else 0xFEE75C))


class PingRow(discord.ui.ActionRow):
    def __init__(self, user_id: int):
        super().__init__()
        self.add_item(PingSelect(user_id))


class PingView(discord.ui.LayoutView):
    def __init__(self, user_id: int, title: str, description: str, color: int):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.add_item(discord.ui.Container(
            discord.ui.TextDisplay(f"## {title}\n{description}\n\n-# Use o menu abaixo para trocar a visualização."),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            PingRow(user_id),
            accent_color=color
        ))


class SimplePingView(discord.ui.LayoutView):
    def __init__(self, title: str, description: str, color: int):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Container(discord.ui.TextDisplay(f"## {title}\n{description}"), accent_color=color))


@app_commands.command(name="ping", description="Mostra o status da API e estatísticas em tempo real")
async def ping(interaction: discord.Interaction):
    start = time.perf_counter()
    await interaction.response.defer(thinking=False)
    api_ping = round((time.perf_counter() - start) * 1000)
    ws_ping = round(interaction.client.latency * 1000)
    description = f"**API:** `{api_ping}ms`\n**WebSocket:** `{ws_ping}ms`\n**Uptime:** `{format_uptime()}`"
    await interaction.followup.send(view=PingView(interaction.user.id, "Painel de status", description, 0x5865F2))


def setup(tree: app_commands.CommandTree):
    tree.add_command(ping)
