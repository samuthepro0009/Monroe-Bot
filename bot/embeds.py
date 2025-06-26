import discord
from bot.config import Config

def create_moderation_embed(action, target, staff_member, reason, color=None):
    """Create a standardized moderation embed"""
    if color is None:
        color = Config.COLORS["info"]
    
    embed = discord.Embed(
        title=f"🔨 {action} - Monroe Social Club",
        description=f"Moderation action taken against {target.mention}",
        color=color
    )
    
    # Target user information
    embed.add_field(
        name="👤 Target User",
        value=f"**User:** {target.mention}\n**Username:** {target.name}#{target.discriminator}\n**User ID:** {target.id}",
        inline=True
    )
    
    # Staff member information
    embed.add_field(
        name="👮 Staff Member",
        value=f"**Staff:** {staff_member.mention}\n**Username:** {staff_member.name}#{staff_member.discriminator}\n**User ID:** {staff_member.id}",
        inline=True
    )
    
    # Action details
    embed.add_field(
        name="📝 Action Details",
        value=f"**Action:** {action}\n**Reason:** {reason}",
        inline=False
    )
    
    # Set target user avatar as thumbnail
    embed.set_thumbnail(url=target.avatar.url if target.avatar else target.default_avatar.url)
    
    # Footer and timestamp
    embed.set_footer(text="Monroe Social Club - Moderation System", icon_url=staff_member.avatar.url if staff_member.avatar else staff_member.default_avatar.url)
    embed.timestamp = discord.utils.utcnow()
    
    return embed

def create_welcome_embed(member, bot):
    """Create a welcome embed for new members"""
    embed = discord.Embed(
        title="🌴 Welcome to Monroe Social Club! 🌴",
        description=f"Hey {member.mention}! Welcome to our retro beach hangout!",
        color=Config.COLORS["pink"]
    )
    
    embed.add_field(
        name="🌊 We are now members strong!",
        value="Get ready for some awesome 80s vibes!",
        inline=False
    )
    
    embed.add_field(
        name="🎮 Join Our Roblox Experience",
        value="**Monroe Social Club**\nExperience the ultimate 80s beach party!",
        inline=True
    )
    
    embed.add_field(
        name="👥 Join Our Roblox Group",
        value="**Monroe Social Club Group**\nGet exclusive perks and stay updated!",
        inline=True
    )
    
    embed.add_field(
        name="👑 Management Team",
        value="• **Samu** - Chairman 👑\n• **Luca** - Vice Chairman 💎\n• **Fra** - President 🏆\n• **Rev** - Vice President 🔨",
        inline=False
    )
    
    embed.add_field(
        name="🔧 Important Commands",
        value="• **/verify** - Link your Roblox account\n• **/profile** - View your Roblox profile\n• **/help** - Get help with commands",
        inline=False
    )
    
    embed.add_field(
        name="🚀 Getting Started",
        value="1. Read the rules\n2. Verify your Roblox account\n3. Get your ping roles\n4. Join our Roblox game\n5. Have fun in the community!",
        inline=False
    )
    
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.set_footer(text="Monroe Social Club - 80s Beach Vibes 🌴", icon_url=bot.user.avatar.url)
    embed.timestamp = discord.utils.utcnow()
    
    return embed

def create_error_embed(title, description, error_details=None):
    """Create a standardized error embed"""
    embed = discord.Embed(
        title=f"❌ {title}",
        description=description,
        color=Config.COLORS["error"]
    )
    
    if error_details:
        embed.add_field(
            name="🔍 Error Details",
            value=error_details,
            inline=False
        )
    
    embed.set_footer(text="Monroe Social Club - Error System")
    embed.timestamp = discord.utils.utcnow()
    
    return embed

def create_success_embed(title, description, additional_info=None):
    """Create a standardized success embed"""
    embed = discord.Embed(
        title=f"✅ {title}",
        description=description,
        color=Config.COLORS["success"]
    )
    
    if additional_info:
        embed.add_field(
            name="ℹ️ Additional Information",
            value=additional_info,
            inline=False
        )
    
    embed.set_footer(text="Monroe Social Club - Success")
    embed.timestamp = discord.utils.utcnow()
    
    return embed

def create_info_embed(title, description, fields=None):
    """Create a standardized info embed"""
    embed = discord.Embed(
        title=f"ℹ️ {title}",
        description=description,
        color=Config.COLORS["info"]
    )
    
    if fields:
        for field in fields:
            embed.add_field(
                name=field.get("name", "Field"),
                value=field.get("value", "No value"),
                inline=field.get("inline", False)
            )
    
    embed.set_footer(text="Monroe Social Club - Information")
    embed.timestamp = discord.utils.utcnow()
    
    return embed
