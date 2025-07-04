import discord
from datetime import datetime
from bot.config import Config

def create_moderation_embed(action: str, target: discord.User, staff_member: discord.User, reason: str, color: int):
    """Create a moderation log embed"""
    embed = discord.Embed(
        title=f"🛡️ {action} - Monroe Social Club",
        description=f"Moderation action taken against {target.mention}",
        color=color,
        timestamp=datetime.utcnow()
    )

    embed.add_field(
        name="👤 Target User",
        value=f"**User:** {target.mention}\n**Username:** {target.name}#{target.discriminator}\n**User ID:** {target.id}",
        inline=True
    )

    embed.add_field(
        name="👮 Staff Member",
        value=f"**Staff:** {staff_member.mention}\n**Username:** {staff_member.name}#{staff_member.discriminator}\n**User ID:** {staff_member.id}",
        inline=True
    )

    embed.add_field(
        name="📝 Action Details",
        value=f"**Action:** {action}\n**Reason:** {reason}",
        inline=False
    )

    embed.set_footer(
        text="Monroe Social Club - Moderation System",
        icon_url=staff_member.avatar.url if staff_member.avatar else staff_member.default_avatar.url
    )

    return embed

def create_error_embed(title: str, description: str):
    """Create an error embed"""
    embed = discord.Embed(
        title=f"❌ {title}",
        description=description,
        color=Config.COLORS["error"]
    )
    return embed

def create_success_embed(title: str, description: str):
    """Create a success embed"""
    embed = discord.Embed(
        title=f"✅ {title}",
        description=description,
        color=Config.COLORS["success"]
    )
    return embed

def create_warning_embed(title: str, description: str):
    """Create a warning embed"""
    embed = discord.Embed(
        title=f"⚠️ {title}",
        description=description,
        color=Config.COLORS["warning"]
    )
    return embed

def create_info_embed(title: str, description: str):
    """Create an info embed"""
    embed = discord.Embed(
        title=f"ℹ️ {title}",
        description=description,
        color=Config.COLORS["info"]
    )
    return embed