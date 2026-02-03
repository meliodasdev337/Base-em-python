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
    except:
        return ""

def format_date(dt: datetime) -> str:
    return f"<t:{int(dt.timestamp())}:F>"

def get_status_emoji(status):
    if status == discord.Status.online:
        return f"{emoji('certo')}"
    elif status == discord.Status.idle:
        return f"{emoji('tempo')}"
    elif status == discord.Status.dnd:
        return f"{emoji('erro')}"
    else:
        return "⚫"

def get_status_text(status):
    if status == discord.Status.online:
        return "Online"
    elif status == discord.Status.idle:
        return "Ausente"
    elif status == discord.Status.dnd:
        return "Não Perturbe"
    else:
        return "Offline"

def get_activity_text(member):
    if not member.activity:
        return f"{emoji('erro')} Nenhuma"
    
    activity = member.activity
    
    if isinstance(activity, discord.Game):
        return f"{emoji('certo')} Jogando {activity.name}"
    elif isinstance(activity, discord.Streaming):
        return f"{emoji('net')} Stream: {activity.name}"
    elif isinstance(activity, discord.Spotify):
        return f"{emoji('certo')} Ouvindo {activity.title}"
    elif isinstance(activity, discord.CustomActivity):
        return f"{emoji('info')} {activity.name}"
    elif hasattr(activity, 'type'):
        if activity.type == discord.ActivityType.listening:
            return f"{emoji('certo')} Ouvindo {activity.name}"
        elif activity.type == discord.ActivityType.watching:
            return f"{emoji('grafico')} Assistindo {activity.name}"
        elif activity.type == discord.ActivityType.competing:
            return f"{emoji('certo')} Competindo em {activity.name}"
    
    return f"{emoji('info')} {activity.name}"

def format_badges(flags: discord.PublicUserFlags) -> str:
    badges = []
    
    if flags.staff:
        badges.append(f"{emoji('certo')}")
    if flags.partner:
        badges.append(f"{emoji('certo')}")
    if flags.hypesquad:
        badges.append(f"{emoji('certo')}")
    if flags.hypesquad_balance:
        badges.append("⚖️")
    if flags.hypesquad_bravery:
        badges.append("🛡️")
    if flags.hypesquad_brilliance:
        badges.append("🎓")
    if flags.bug_hunter:
        badges.append("🐛")
    if flags.bug_hunter_level_2:
        badges.append("🐛")
    if flags.early_supporter:
        badges.append("🌟")
    if flags.verified_bot_developer:
        badges.append(f"{emoji('certo')}")
    if flags.active_developer:
        badges.append("💻")
    if flags.discord_certified_moderator:
        badges.append("🛡️")
    
    return " ".join(badges) if badges else f"{emoji('erro')} Nenhum"

def get_member_badges(member: discord.Member) -> str:
    badges = []
    
    if member.premium_since:
        badges.append("💎")
    
    if member.guild_permissions.administrator:
        badges.append("👑")
    elif member.guild_permissions.manage_guild:
        badges.append("⚙️")
    
    if member.guild_permissions.manage_messages:
        badges.append("💬")
    
    return " ".join(badges)

@app_commands.command(
    name="userinfo",
    description="Mostra informações sobre um usuário"
)
@app_commands.describe(
    usuario="Usuário para ver informações (deixe vazio para você mesmo)"
)
async def userinfo(
    interaction: discord.Interaction,
    usuario: Optional[discord.Member] = None
):
    target = usuario or interaction.user
    
    embed = discord.Embed(
        title=f"{emoji('info')} Informações de {target.name}",
        color=target.color if target.color.value != 0 else discord.Color.blue(),
        timestamp=datetime.now()
    )
    
    embed.set_thumbnail(url=target.display_avatar.url)
    
    status_emoji = get_status_emoji(target.status)
    status_text = get_status_text(target.status)
    
    embed.add_field(
        name=f"{emoji('info')} Informações Básicas",
        value=f"{emoji('certo')} **Nome:** {target.name}\n"
              f"{emoji('certo')} **ID:** `{target.id}`\n"
              f"{emoji('certo')} **Mencionar:** {target.mention}\n"
              f"{emoji('certo')} **Bot:** {'Sim 🤖' if target.bot else 'Não 👤'}",
        inline=False
    )
    
    embed.add_field(
        name=f"{emoji('tempo')} Datas",
        value=f"{emoji('tempo')} **Conta criada:** {format_date(target.created_at)}\n"
              f"{emoji('tempo')} **Entrou no servidor:** {format_date(target.joined_at)}",
        inline=False
    )
    
    roles = [role.mention for role in target.roles[1:]]
    roles_text = " ".join(roles[-10:]) if roles else f"{emoji('erro')} Sem cargos"
    
    if len(roles) > 10:
        roles_text += f"\n{emoji('info')} ... e mais {len(roles) - 10} cargos"
    
    embed.add_field(
        name=f"{emoji('grafico')} Cargos ({len(roles)})",
        value=roles_text,
        inline=False
    )
    
    activity_text = get_activity_text(target)
    erro_emoji = emoji('erro')
    embed.add_field(
        name=f"{emoji('latencia')} Status & Atividade",
        value=f"{status_emoji} **Status:** {status_text}\n"
              f"{emoji('certo')} **Atividade:** {activity_text}\n"
              f"{emoji('certo')} **Booster:** {'Sim 💎' if target.premium_since else erro_emoji + ' Não'}",
        inline=True
    )
    
    discord_badges = format_badges(target.public_flags)
    member_badges = get_member_badges(target)
    
    all_badges = []
    erro_emoji = emoji('erro')
    if discord_badges != erro_emoji + " Nenhum":
        all_badges.append(discord_badges)
    if member_badges:
        all_badges.append(member_badges)
    
    badges_text = " | ".join(all_badges) if all_badges else erro_emoji + " Nenhum badge especial"
    
    embed.add_field(
        name=f"{emoji('certo')} Badges & Cargos",
        value=badges_text,
        inline=False
    )
    
    if target.nick:
        embed.add_field(
            name=f"{emoji('info')} Apelido",
            value=target.nick,
            inline=True
        )
    
    embed.add_field(
        name=f"{emoji('net')} Outras Informações",
        value=f"{emoji('certo')} **Cor:** `{target.color}`\n"
              f"{emoji('certo')} **Avatar:** [Link]({target.display_avatar.url})\n"
              f"{emoji('certo')} **Cargo mais alto:** {target.top_role.mention}",
        inline=True
    )
    
    embed.set_footer(
        text=f"Solicitado por {interaction.user} • ID: {target.id}",
        icon_url=interaction.user.display_avatar.url
    )
    
    await interaction.response.send_message(embed=embed)

def setup(tree: app_commands.CommandTree):
    tree.add_command(userinfo)