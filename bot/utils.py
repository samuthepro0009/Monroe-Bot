import discord
from discord.ext import commands
from discord import app_commands
from bot.config import Config
from bot.embeds import create_info_embed, create_error_embed

class UtilsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.start_time = discord.utils.utcnow()

    @app_commands.command(name="status", description="Show bot status and uptime information")
    async def status_command(self, interaction: discord.Interaction):
        """Show bot status and uptime information"""
        uptime = discord.utils.utcnow() - self.bot.start_time
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        embed = discord.Embed(
            title="🤖 Monroe Social Club Bot Status",
            description="Your 80s beach paradise is always protected!",
            color=Config.COLORS["cyan"]
        )

        embed.add_field(
            name="⏰ Current Uptime",
            value=f"{days} days, {hours} hours, {minutes} minutes",
            inline=True
        )

        embed.add_field(
            name="🌐 Hosting Service",
            value="Render - 24/7 Cloud Hosting",
            inline=True
        )

        embed.add_field(
            name="📊 Performance",
            value=f"Latency: {round(self.bot.latency * 1000)}ms\nMembers: {len(interaction.guild.members)}",
            inline=True
        )

        embed.add_field(
            name="🛡️ Security Features",
            value="• AutoMod Protection\n• Suspicious Activity Detection\n• 24/7 Monitoring",
            inline=False
        )

        embed.add_field(
            name="🏖️ Always Available",
            value="The Monroe Social Club bot runs 24/7 on Render's reliable cloud infrastructure, ensuring your beach paradise is always moderated and protected!",
            inline=False
        )

        embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.set_footer(text="Powered by Render • 24/7 Uptime", icon_url="https://avatars.githubusercontent.com/u/36424661")
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="help", description="Get help with Monroe Social Club bot commands")
    async def help_command(self, interaction: discord.Interaction):
        """Comprehensive help command for the bot"""
        embed = discord.Embed(
            title="🌴 Monroe Social Club Bot - Help Center",
            description="Welcome to the ultimate 80s beach experience! Here are all available commands:",
            color=Config.COLORS["info"]
        )

        # General Commands
        embed.add_field(
            name="🏖️ General Commands",
            value="`/help` - Show this help message\n`/management` - View management team\n`/verify` - Link your Roblox account",
            inline=False
        )

        # Roblox Integration
        embed.add_field(
            name="🎮 Roblox Commands",
            value="`/get_profile [user]` - View Roblox profile info\n`/group_info` - View group information",
            inline=False
        )

        # Staff Commands
        embed.add_field(
            name="👮 Staff Commands (Staff Only)",
            value="`/warn <user> <reason>` - Warn a member\n`/kick <user> <reason>` - Kick a member\n`/ban <user> <reason>` - Ban a member\n`/announce <message>` - Send announcement\n`/devlog <version>` - Post development log",
            inline=False
        )

        # Applications
        embed.add_field(
            name="📝 Applications",
            value="`/create_applications` - Create application system (Staff)\n`/application_stats` - View application stats (Staff)",
            inline=False
        )

        # Bot Features
        embed.add_field(
            name="🤖 Automatic Features",
            value="• **AutoMod**: Automatically detects and removes inappropriate content\n• **Welcome Messages**: Greets new members\n• **Logging**: Comprehensive action logging\n• **Roblox Integration**: Live data from Rover API",
            inline=False
        )

        # Links and Info
        embed.add_field(
            name="🔗 Important Links",
            value=f"• **Roblox Group ID**: {Config.ROBLOX_GROUP_ID}\n• **Game Map ID**: {Config.ROBLOX_MAP_ID}\n• **Verification**: [RoVer Link](https://rover.link/)",
            inline=False
        )

        embed.add_field(
            name="🔧 Utility Commands",
            value="`/help` - Show this help message\n`/ping` - Check bot latency\n`/status` - Show bot uptime and 24/7 status\n`/management` - View management team\n`/verify` - Link your Roblox account",
            inline=False
        )

        embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.set_footer(text="Monroe Social Club - 80s Beach Paradise 🌴")
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction: discord.Interaction):
        """Check bot ping and latency"""
        latency = round(self.bot.latency * 1000)

        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Bot latency: **{latency}ms**",
            color=Config.COLORS["success"] if latency < 100 else Config.COLORS["warning"] if latency < 200 else Config.COLORS["error"]
        )

        # Add status emoji based on latency
        if latency < 100:
            embed.add_field(name="Status", value="🟢 Excellent", inline=True)
        elif latency < 200:
            embed.add_field(name="Status", value="🟡 Good", inline=True)
        else:
            embed.add_field(name="Status", value="🔴 Poor", inline=True)

        embed.set_footer(text="Monroe Social Club - System Status")
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="server_info", description="Get information about the Monroe Social Club server")
    async def server_info(self, interaction: discord.Interaction):
        """Display server information"""
        guild = interaction.guild

        embed = discord.Embed(
            title=f"🏖️ {guild.name} - Server Information",
            description="Welcome to the ultimate 80s beach experience!",
            color=Config.COLORS["info"]
        )

        # Basic server info
        embed.add_field(
            name="📊 Server Stats",
            value=f"**Members**: {guild.member_count:,}\n**Created**: <t:{int(guild.created_at.timestamp())}:D>\n**Owner**: {guild.owner.mention if guild.owner else 'Unknown'}",
            inline=True
        )

        # Channel and role counts
        text_channels = len([c for c in guild.channels if isinstance(c, discord.TextChannel)])
        voice_channels = len([c for c in guild.channels if isinstance(c, discord.VoiceChannel)])
        categories = len(guild.categories)

        embed.add_field(
            name="📁 Channels",
            value=f"**Text**: {text_channels}\n**Voice**: {voice_channels}\n**Categories**: {categories}",
            inline=True
        )

        embed.add_field(
            name="🎭 Roles",
            value=f"**Total**: {len(guild.roles)}\n**Highest**: {guild.roles[-1].name}",
            inline=True
        )

        # Management team
        embed.add_field(
            name="👑 Management Team",
            value="• **Samu** - Chairman 👑\n• **Luca** - Vice Chairman 💎\n• **Fra** - President 🏆\n• **Rev** - Vice President ⭐",
            inline=False
        )

        # Server features
        features = []
        if guild.features:
            feature_names = {
                'COMMUNITY': '🌍 Community Server',
                'PARTNERED': '🤝 Discord Partner',
                'VERIFIED': '✅ Verified',
                'DISCOVERABLE': '🔍 Discoverable',
                'INVITE_SPLASH': '🎨 Invite Splash',
                'BANNER': '🖼️ Server Banner',
                'VANITY_URL': '🔗 Vanity URL'
            }
            for feature in guild.features:
                if feature in feature_names:
                    features.append(feature_names[feature])

        if features:
            embed.add_field(
                name="✨ Server Features",
                value="\n".join(features[:5]),  # Limit to 5 features
                inline=False
            )

        # Set server icon
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        embed.set_footer(text="Monroe Social Club - 80s Beach Vibes 🌴")
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="user_info", description="Get information about a user")
    @app_commands.describe(user="The user to get information about (leave empty for yourself)")
    async def user_info(self, interaction: discord.Interaction, user: discord.Member = None):
        """Display user information"""
        target_user = user or interaction.user

        embed = discord.Embed(
            title=f"👤 User Information - {target_user.display_name}",
            color=target_user.top_role.color if target_user.top_role.color != discord.Color.default() else Config.COLORS["info"]
        )

        # Basic user info
        embed.add_field(
            name="📝 Basic Info",
            value=f"**Username**: {target_user.name}#{target_user.discriminator}\n**Display Name**: {target_user.display_name}\n**User ID**: {target_user.id}",
            inline=True
        )

        # Account dates
        embed.add_field(
            name="📅 Dates",
            value=f"**Created**: <t:{int(target_user.created_at.timestamp())}:D>\n**Joined**: <t:{int(target_user.joined_at.timestamp())}:D>",
            inline=True
        )

        # Role information
        roles = [role.mention for role in target_user.roles[1:]]  # Exclude @everyone
        if roles:
            roles_text = ', '.join(roles[:10])  # Limit to 10 roles
            if len(target_user.roles) > 11:
                roles_text += f" (+{len(target_user.roles) - 11} more)"
        else:
            roles_text = "No roles"

        embed.add_field(
            name=f"🎭 Roles ({len(target_user.roles) - 1})",
            value=roles_text,
            inline=False
        )

        # Permissions
        key_perms = []
        if target_user.guild_permissions.administrator:
            key_perms.append("👑 Administrator")
        if target_user.guild_permissions.manage_guild:
            key_perms.append("⚙️ Manage Server")
        if target_user.guild_permissions.manage_roles:
            key_perms.append("🎭 Manage Roles")
        if target_user.guild_permissions.manage_channels:
            key_perms.append("📁 Manage Channels")
        if target_user.guild_permissions.kick_members:
            key_perms.append("👢 Kick Members")
        if target_user.guild_permissions.ban_members:
            key_perms.append("🔨 Ban Members")

        if key_perms:
            embed.add_field(
                name="🔑 Key Permissions",
                value="\n".join(key_perms[:5]),
                inline=True
            )

        # Status and activity
        status_emojis = {
            discord.Status.online: "🟢 Online",
            discord.Status.idle: "🟡 Idle", 
            discord.Status.dnd: "🔴 Do Not Disturb",
            discord.Status.offline: "⚫ Offline"
        }

        # Get user status
        user_status = "❓ Unknown"
        if hasattr(target_user, 'status'):
            user_status = status_emojis.get(target_user.status, "❓ Unknown")

        embed.add_field(
            name="📶 Status",
            value=user_status,
            inline=True
        )

        # Set user avatar
        embed.set_thumbnail(url=target_user.avatar.url if target_user.avatar else target_user.default_avatar.url)

        embed.set_footer(text="Monroe Social Club - User Information")
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="bot_info", description="Get information about the Monroe Social Club bot")
    async def botinfo(self, interaction: discord.Interaction):
        """Display bot information"""
        embed = discord.Embed(
            title="🤖 Monroe Social Club Bot Information",
            description="Your friendly 80s beach club assistant!",
            color=Config.COLORS["pink"]
        )

        # Bot stats
        embed.add_field(
            name="📊 Bot Statistics",
            value=f"**Servers**: {len(self.bot.guilds)}\n**Users**: {len(self.bot.users)}\n**Commands**: {len(self.bot.tree.get_commands())}",
            inline=True
        )

        # Bot info
        embed.add_field(
            name="🔧 Technical Info",
            value=f"**Library**: discord.py\n**Python**: 3.8+\n**Latency**: {round(self.bot.latency * 1000)}ms",
            inline=True
        )

        # Features
        embed.add_field(
            name="✨ Features",
            value="• AutoMod System\n• Roblox Integration\n• Staff Management\n• Application System\n• Comprehensive Logging",
            inline=False
        )

        # Links
        embed.add_field(
            name="🔗 Monroe Social Club",
            value=f"• **Roblox Group**: {Config.ROBLOX_GROUP_ID}\n• **Game Map**: {Config.ROBLOX_MAP_ID}\n• **Theme**: 1980s Beach Club",
            inline=False
        )

        embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.set_footer(text="Monroe Social Club - Bot developed for the ultimate 80s experience 🌴")
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(UtilsCog(bot))