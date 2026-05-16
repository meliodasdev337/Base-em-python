import discord
from discord import app_commands
import json
import os
from datetime import datetime
from typing import Optional

EMOJI_DB = "database/emojis_ids.json"


def emoji(name: str) -> str:
    if not os.path.exists(EMOJI_DB):
        return ""
    try:
        with open(EMOJI_DB, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get(name, {}).get("full", "")
    except Exception:
        return ""


def format_date(dt: datetime | None) -> str:
    if not dt:
        return "Indisponível"
    return f"<t:{int(dt.timestamp())}:F>"


def presence_status(member: discord.Member) -> str:
    raw = getattr(member, 'raw_status', None)
    if raw and raw != 'offline':
        return raw
    for attr in ('desktop_status', 'mobile_status', 'web_status'):
        value = str(getattr(member, attr, 'offline'))
        if value and value != 'offline':
            return value
    return str(getattr(member, 'status', 'offline'))


def get_status_text(member: discord.Member) -> str:
    names = {
        'online': 'Online',
        'idle': 'Ausente',
        'dnd': 'Não perturbe',
        'offline': 'Offline'
    }
    return names.get(presence_status(member), presence_status(member).title())


def get_status_icon(member: discord.Member) -> str:
    status = presence_status(member)
    if status == 'online':
        return '🟢'
    if status == 'idle':
        return '🟡'
    if status == 'dnd':
        return '🔴'
    return '⚫'


def get_activity_text(member: discord.Member) -> str:
    activities = getattr(member, 'activities', None) or []
    if not activities:
        return "Nenhuma"
    parts = []
    for activity in activities[:3]:
        if isinstance(activity, discord.Game):
            parts.append(f"Jogando {activity.name}")
        elif isinstance(activity, discord.Streaming):
            parts.append(f"Stream: {activity.name}")
        elif isinstance(activity, discord.Spotify):
            parts.append(f"Ouvindo {activity.title}")
        elif isinstance(activity, discord.CustomActivity):
            parts.append(activity.name or "Status customizado")
        elif getattr(activity, 'type', None) == discord.ActivityType.watching:
            parts.append(f"Assistindo {activity.name}")
        elif getattr(activity, 'type', None) == discord.ActivityType.listening:
            parts.append(f"Ouvindo {activity.name}")
        elif getattr(activity, 'name', None):
            parts.append(activity.name)
    return " | ".join(parts) if parts else "Nenhuma"


def format_badges(flags: discord.PublicUserFlags) -> str:
    badges = []
    if flags.staff:
        badges.append("Equipe Discord")
    if flags.partner:
        badges.append("Parceiro")
    if flags.hypesquad:
        badges.append("HypeSquad")
    if flags.hypesquad_balance:
        badges.append("HypeSquad Balance")
    if flags.hypesquad_bravery:
        badges.append("HypeSquad Bravery")
    if flags.hypesquad_brilliance:
        badges.append("HypeSquad Brilliance")
    if flags.bug_hunter:
        badges.append("Caçador de bugs")
    if flags.bug_hunter_level_2:
        badges.append("Caçador de bugs 2")
    if flags.early_supporter:
        badges.append("Apoiador inicial")
    if flags.verified_bot_developer:
        badges.append("Criador verificado")
    if flags.active_developer:
        badges.append("Badge ativa")
    if flags.discord_certified_moderator:
        badges.append("Moderador certificado")
    return ", ".join(badges) if badges else "Nenhuma"


def get_member_badges(member: discord.Member) -> str:
    badges = []
    if member.premium_since:
        badges.append("Booster")
    if member.guild_permissions.administrator:
        badges.append("Administrador")
    elif member.guild_permissions.manage_guild:
        badges.append("Gerencia servidor")
    if member.guild_permissions.manage_messages:
        badges.append("Gerencia mensagens")
    return ", ".join(badges) if badges else "Nenhuma"


def status_note(client: discord.Client, member: discord.Member) -> str:
    if not getattr(client.intents, 'presences', False):
        return "\n-# Para status em tempo real, ligue Presence Intent no painel do bot e reinicie."
    if presence_status(member) == 'offline':
        return "\n-# Offline também aparece para quem está invisível ou sem presença entregue pelo Discord."
    return ""


class UserInfoView(discord.ui.LayoutView):
    def __init__(self, target: discord.Member, requester: discord.abc.User, note: str):
        super().__init__(timeout=None)
        roles = [role.mention for role in target.roles[1:]]
        roles_text = " ".join(roles[-12:]) if roles else "Sem cargos"
        if len(roles) > 12:
            roles_text += f"\n... e mais {len(roles) - 12} cargos"
        avatar = target.display_avatar.url
        devices = []
        for label, attr in [('PC', 'desktop_status'), ('Celular', 'mobile_status'), ('Web', 'web_status')]:
            value = str(getattr(target, attr, 'offline'))
            if value and value != 'offline':
                devices.append(f'{label}: {value}')
        devices_text = ', '.join(devices) if devices else 'Nenhum ativo'
        self.add_item(discord.ui.Container(
            discord.ui.Section(
                f"## {target.display_name}\n"
                f"**Nome:** {target.name}\n"
                f"**ID:** `{target.id}`\n"
                f"**Menção:** {target.mention}\n"
                f"**Bot:** {'Sim' if target.bot else 'Não'}",
                accessory=discord.ui.Thumbnail(avatar)
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                f"### Datas\n"
                f"**Conta criada:** {format_date(target.created_at)}\n"
                f"**Entrou no servidor:** {format_date(target.joined_at)}"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                f"### Presença\n"
                f"**Status:** {get_status_icon(target)} {get_status_text(target)}\n"
                f"**Dispositivo:** {devices_text}\n"
                f"**Atividade:** {get_activity_text(target)}\n"
                f"**Booster:** {'Sim' if target.premium_since else 'Não'}{note}"
            ),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(f"### Cargos ({len(roles)})\n{roles_text}"),
            discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.small),
            discord.ui.TextDisplay(
                f"### Badges\n"
                f"**Discord:** {format_badges(target.public_flags)}\n"
                f"**Servidor:** {get_member_badges(target)}\n"
                f"**Cor:** `{target.color}`\n"
                f"**Cargo mais alto:** {target.top_role.mention}\n"
                f"-# Pedido por {requester}"
            ),
            accent_color=target.color.value if target.color.value else 0x5865F2
        ))


@app_commands.command(name="userinfo", description="Mostra informações de um usuário")
@app_commands.describe(usuario="Usuário")
async def userinfo(interaction: discord.Interaction, usuario: Optional[discord.Member] = None):
    target = usuario or interaction.user
    if interaction.guild:
        cached = interaction.guild.get_member(target.id)
        if cached:
            target = cached
    await interaction.response.send_message(view=UserInfoView(target, interaction.user, status_note(interaction.client, target)))


def setup(tree: app_commands.CommandTree):
    tree.add_command(userinfo)
