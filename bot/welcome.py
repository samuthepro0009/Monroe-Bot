
import discord
from discord.ext import commands
from bot.config import Config
import asyncio

class WelcomeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Send welcome message when a new member joins"""
        
        # Get welcome channel
        welcome_channel = self.bot.get_channel(getattr(Config, 'WELCOME_CHANNEL', None))
        if not welcome_channel:
            return

        # Calculate member count
        member_count = member.guild.member_count

        # Create welcome embed
        embed = discord.Embed(
            title="🏖️ Welcome to Monroe Social Club! 🏖️",
            description=f"Hey {member.mention}! Welcome to our retro beach hangout!",
            color=Config.COLORS["pink"]
        )

        # Add member count with strong formatting
        embed.add_field(
            name="👥 We are now **members** strong!",
            value=f"Get ready for some awesome 80s vibes!",
            inline=False
        )

        # Add Roblox Experience section
        embed.add_field(
            name="🎮 Join Our Roblox Experience",
            value="Monroe Social Club\nExperience the ultimate 80s beach party!",
            inline=True
        )

        embed.add_field(
            name="🔗 Join Our Roblox Group", 
            value="Monroe Social Club Group\nGet exclusive perks and stay updated!",
            inline=True
        )

        # Add Management Team
        embed.add_field(
            name="👑 Management Team",
            value="• Samu - Chairman 👑\n• Luca - Vice Chairman 💎\n• Fra - President 🏆\n• Rev - Vice President 🔨",
            inline=False
        )

        # Add Important Commands
        embed.add_field(
            name="🔧 Important Commands",
            value="• **/verify** - Link your Roblox account\n• **/profile** - View your Roblox profile\n• **/help** - Get help with commands",
            inline=False
        )

        # Add Getting Started
        embed.add_field(
            name="📋 Getting Started",
            value="1. Read the rules\n2. Verify your Roblox account\n3. Get your ping roles\n4. Join our Roblox game\n5. Have fun in the community!",
            inline=False
        )

        # Set thumbnail to member's avatar
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        
        # Set footer
        embed.set_footer(
            text="Monroe Social Club - 80s Beach Vibes 🌴",
            icon_url=member.guild.icon.url if member.guild.icon else None
        )
        embed.timestamp = discord.utils.utcnow()

        # Replace member count placeholder
        embed.description = embed.description.replace("**members**", f"**{member_count} members**")
        for field in embed.fields:
            if "**members**" in field.value:
                field.value = field.value.replace("**members**", f"**{member_count} members**")

        try:
            await welcome_channel.send(embed=embed)
        except Exception as e:
            print(f"❌ Error sending welcome message: {e}")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Log when a member leaves"""
        print(f"👋 {member.display_name} left Monroe Social Club")

async def setup(bot):
    await bot.add_cog(WelcomeCog(bot))
