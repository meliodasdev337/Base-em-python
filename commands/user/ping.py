import discord
from discord import app_commands, ui
import json
import os
import time
import aiohttp
from datetime import datetime

EMOJI_DB = "database/emojis_ids.json"
start_time = time.time()

def emoji(name: str) -> str:
    if not os.path.exists(EMOJI_DB):
        return ""
    try:
        with open(EMOJI_DB, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get(name, {}).get("full", "")
    except:
        return ""

def format_uptime() -> str:
    uptime = time.time() - start_time
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    seconds = int(uptime % 60)
    return f"{hours}h {minutes}m {seconds}s"

def get_latency_bar(latency: int) -> str:
    if latency < 50:
        return "🟢🟢🟢🟢🟢"
    elif latency < 100:
        return "🟡🟡🟡🟡⚪"
    elif latency < 200:
        return "🟠🟠🟠⚪⚪"
    else:
        return "🔴🔴⚪⚪⚪"

def get_speed_rating(latency: int) -> str:
    if latency < 50:
        return "⚡ Velocidade Extrema"
    elif latency < 100:
        return "🚀 Muito Rápido"
    elif latency < 150:
        return "🏎️ Rápido"
    elif latency < 200:
        return "🚗 Moderado"
    else:
        return "🚶 Lento"

class PingSelect(ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Status Básico",
                description="Latência e uptime do bot",
                value="basic_status",
                emoji=emoji("status") or "📊"
            ),
            discord.SelectOption(
                label="Status da API Discord",
                description="Status em tempo real do Discord",
                value="discord_status",
                emoji=emoji("net") or "🌐"
            ),
            discord.SelectOption(
                label="Velocidade de Conexão",
                description="Teste de velocidade e ping",
                value="speed_test",
                emoji=emoji("latencia") or "⚡"
            ),
            discord.SelectOption(
                label="Atualizar Dados",
                description="Atualiza todos os dados em tempo real",
                value="refresh_data",
                emoji=emoji("atualizar") or "🔄"
            )
        ]
        
        super().__init__(
            placeholder="Selecione uma opção...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="ping_menu",
            row=0
        )
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        if self.values[0] == "basic_status":
            latency = round(interaction.client.latency * 1000)
            latency_color = discord.Color.green() if latency < 100 else discord.Color.orange() if latency < 200 else discord.Color.red()
            
            embed = discord.Embed(
                title=f"{emoji('status')} Status Básico",
                color=latency_color,
                timestamp=datetime.now()
            )
            
            embed.set_thumbnail(url="https://photo.hakari.fun/uploads/WEBSITE/2724dbdc-1d8ae2f7-01022026-1000126540.png")
            embed.add_field(
                name=f"{emoji('net')} Latência API:",
                value=f"```yaml\n{get_latency_bar(latency)} {latency}ms\n```",
                inline=False
            )
            embed.add_field(
                name=f"{emoji('tempo')} Tempo de Atividade:",
                value=f"```fix\n{format_uptime()}\n```",
                inline=False
            )
            embed.set_footer(text="Painel de Status • Atualizado")
            
        elif self.values[0] == "discord_status":
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get('https://discordstatus.com/api/v2/status.json', timeout=5) as response:
                        if response.status == 200:
                            data = await response.json()
                            indicator = data['status']['indicator']
                            
                            if indicator == "none":
                                color = discord.Color.green()
                                status_text = f"{emoji('certo')} Operacional"
                                components = f"{emoji('certo')} **API:** Operacional\n{emoji('certo')} **Gateway:** Estável\n{emoji('certo')} **CDN:** Normal"
                            elif indicator == "minor":
                                color = discord.Color.orange()
                                status_text = f"{emoji('certo')} Degradado"
                                components = f"{emoji('certo')} **API:** Degradado\n{emoji('certo')} **Gateway:** Estável\n{emoji('certo')} **CDN:** Normal"
                            else:
                                color = discord.Color.red()
                                status_text = f"{emoji('erro')} Parcial"
                                components = f"{emoji('erro')} **API:** Parcial\n{emoji('erro')} **Gateway:** Instável\n{emoji('certo')} **CDN:** Degradado"
                        else:
                            color = discord.Color.green()
                            status_text = f"{emoji('certo')} Operacional"
                            components = f"{emoji('certo')} **API:** Operacional\n{emoji('certo')} **Gateway:** Estável\n{emoji('certo')} **CDN:** Normal"
            except:
                color = discord.Color.green()
                status_text = f"{emoji('certo')} Operacional"
                components = f"{emoji('certo')} **API:** Operacional\n{emoji('certo')} **Gateway:** Estável\n{emoji('certo')} **CDN:** Normal"
            
            embed = discord.Embed(
                title=f"{emoji('net')} Status do Discord",
                description="API oficial em tempo real",
                color=color,
                timestamp=datetime.now()
            )
            
            embed.set_thumbnail(url="https://photo.hakari.fun/uploads/WEBSITE/2724dbdc-1d8ae2f7-01022026-1000126540.png")
            embed.add_field(name="Status Atual:", value=status_text, inline=False)
            embed.add_field(name=f"{emoji('grafico')} Componentes:", value=components, inline=False)
            embed.set_footer(text="Discord Status API • Atualizado")
            
        elif self.values[0] == "speed_test":
            latency = round(interaction.client.latency * 1000)
            
            embed = discord.Embed(
                title=f"{emoji('latencia')} Teste de Velocidade",
                description="Medição em tempo real",
                color=discord.Color.blurple(),
                timestamp=datetime.now()
            )
            
            embed.set_thumbnail(url="https://photo.hakari.fun/uploads/WEBSITE/2724dbdc-1d8ae2f7-01022026-1000126540.png")
            embed.add_field(
                name=f"{emoji('latencia')} Resultados:",
                value=f"```yaml\nAPI: {latency}ms\nClassificação: {get_speed_rating(latency)}\n```",
                inline=False
            )
            embed.set_footer(text="Teste de Velocidade • Atualizado")
            
        elif self.values[0] == "refresh_data":
            latency = round(interaction.client.latency * 1000)
            current_time = datetime.now().strftime("%H:%M:%S")
            
            embed = discord.Embed(
                title=f"{emoji('atualizar')} Dados Atualizados",
                description="Todos os dados foram atualizados com sucesso!",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            
            embed.set_thumbnail(url="https://photo.hakari.fun/uploads/WEBSITE/2724dbdc-1d8ae2f7-01022026-1000126540.png")
            embed.add_field(
                name="Dados Atualizados:",
                value=f"```yaml\nLatência: {latency}ms\nUptime: {format_uptime()}\nHora: {current_time}\n```",
                inline=False
            )
            embed.set_footer(text="Dados Atualizados • Atualizado")
        
        view = ui.View(timeout=60)
        view.add_item(PingSelect())
        await interaction.edit_original_response(embed=embed, view=view)

class PingView(ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.add_item(PingSelect())
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id
    
    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        if hasattr(self, 'message'):
            try:
                embed = discord.Embed(
                    title="⏰ Painel de Status Expirado",
                    description="Use `/ping` novamente para reabrir o painel.",
                    color=discord.Color.light_gray()
                )
                await self.message.edit(embed=embed, view=self)
            except:
                pass

@app_commands.command(
    name="ping",
    description="Mostra o status da API e estatísticas em tempo real"
)
async def ping(interaction: discord.Interaction):
    start = time.perf_counter()
    await interaction.response.defer()
    end = time.perf_counter()
    api_ping = round((end - start) * 1000)
    ws_ping = round(interaction.client.latency * 1000)
    
    embed = discord.Embed(
        title=f"{emoji('status')} Painel de Status",
        description=f"**{interaction.client.user.name}** • Monitoramento em tempo real\nSelecione uma opção abaixo para ver informações detalhadas.",
        color=discord.Color.blurple(),
        timestamp=datetime.now()
    )
    
    embed.set_thumbnail(url="https://photo.hakari.fun/uploads/WEBSITE/2724dbdc-1d8ae2f7-01022026-1000126540.png")
    embed.add_field(
        name=f"{emoji('tempo')} Status Atual:",
        value=f"{emoji('ws')} **API:** `{api_ping}ms`\n{emoji('ws')} **WebSocket:** `{ws_ping}ms`\n{emoji('tempo')} **Uptime:** `{format_uptime()}`",
        inline=False
    )
    embed.add_field(name="\u200b", value="▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬", inline=False)
    embed.add_field(
        name=f"{emoji('info')} Opções Disponíveis:",
        value=f"{emoji('status')} **Status Básico**\n{emoji('net')} **Status Discord**\n{emoji('latencia')} **Velocidade**\n{emoji('atualizar')} **Atualizar**",
        inline=False
    )
    embed.set_footer(text="Painel de Status Interativo")
    
    view = PingView(interaction.user.id)
    message = await interaction.followup.send(embed=embed, view=view, wait=True)
    view.message = message

def setup(tree: app_commands.CommandTree):
    tree.add_command(ping)
