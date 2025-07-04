
import discord
from discord.ext import commands
from discord import app_commands
from bot.config import Config
import random

class ASCIIArtCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # 80s Beach Club themed ASCII art
        self.ascii_art = {
            'palm_tree': """
```
      🌴
     🌴🌴
    🌴🌴🌴
   🌴🌴🌴🌴
      ||
      ||
      ||
~~~~~~~~~~~~~~~~
```""",
            'sunset': """
```
    🌅
   ☀️☀️☀️
  ☀️☀️☀️☀️
 ☀️☀️☀️☀️☀️
🌊🌊🌊🌊🌊🌊
🌊🌊🌊🌊🌊🌊
```""",
            'beach': """
```
    🏖️ MONROE BEACH CLUB 🏖️
  🌴                       🌴
     🏄‍♂️  🌊  🏄‍♀️  🌊  🏐
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        Welcome to Paradise!
```""",
            'sunglasses': """
```
    😎 COOL VIBES ONLY 😎
  ╔══════════════════════╗
  ║  🕶️  NEON NIGHTS  🕶️  ║
  ╚══════════════════════╝
```""",
            'waves': """
```
🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊
  🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊
🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊
  🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊
```""",
            'cocktail': """
```
    🍹 TROPICAL PARADISE 🍹
    ╔══════════════════╗
    ║  🥥 🍓 🥭 🍌 🥝  ║
    ║   Beach Bar Open  ║
    ╚══════════════════╝
```""",
            'neon_welcome': """
```
██╗    ██╗███████╗██╗      ██████╗ ██████╗ ███╗   ███╗███████╗
██║    ██║██╔════╝██║     ██╔════╝██╔═══██╗████╗ ████║██╔════╝
██║ █╗ ██║█████╗  ██║     ██║     ██║   ██║██╔████╔██║█████╗  
██║███╗██║██╔══╝  ██║     ██║     ██║   ██║██║╚██╔╝██║██╔══╝  
╚███╔███╔╝███████╗███████╗╚██████╗╚██████╔╝██║ ╚═╝ ██║███████╗
 ╚══╝╚══╝ ╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝
          🌴 MONROE SOCIAL CLUB 🌴
```""",
            'dance_floor': """
```
    💃 DANCE FLOOR OPEN 🕺
  ╔══════════════════════╗
  ║  🎵 ♪ ♫ ♪ ♫ ♪ ♫ 🎵  ║
  ║    80s BEATS ONLY    ║
  ║  🎤 🎹 🎸 🥁 🎺 🎷  ║
  ╚══════════════════════╝
```""",
            'retro_car': """
```
    🚗💨 RETRO RIDE 🚗💨
      ╔══════════════╗
      ║  🎵 Synthwave ║
      ║  🌈 Neon Glow ║
      ╚══════════════╝
    🛞              🛞
```""",
            'vip_lounge': """
```
    ✨ VIP LOUNGE ✨
  ╔════════════════════╗
  ║  🥂 Exclusive Area  ║
  ║  👑 Premium Members ║
  ║  🌟 Special Events  ║
  ╚════════════════════╝
```"""
        }
        
        # Random beach quotes
        self.beach_quotes = [
            "Life's a beach, enjoy the waves! 🌊",
            "Sandy toes and salty kisses 💋",
            "Good vibes and tide vibes 🌴",
            "Beach hair, don't care! 🏖️",
            "Tropical state of mind 🥥",
            "Paradise found at Monroe! 🌺",
            "Sun, sand, and 80s jams 🎵",
            "Neon nights and beach lights ✨"
        ]
    
    def has_management_permissions(self, member):
        """Check if member has management permissions"""
        management_role_names = list(Config.MANAGEMENT_ROLES.keys())
        member_roles = [role.name for role in member.roles]
        return any(role in management_role_names for role in member_roles) or member.guild_permissions.manage_guild
    
    @app_commands.command(name="ascii", description="Display ASCII art")
    @app_commands.describe(art_type="Type of ASCII art to display")
    @app_commands.choices(art_type=[
        app_commands.Choice(name="🌴 Palm Tree", value="palm_tree"),
        app_commands.Choice(name="🌅 Sunset", value="sunset"),
        app_commands.Choice(name="🏖️ Beach", value="beach"),
        app_commands.Choice(name="😎 Sunglasses", value="sunglasses"),
        app_commands.Choice(name="🌊 Waves", value="waves"),
        app_commands.Choice(name="🍹 Cocktail", value="cocktail"),
        app_commands.Choice(name="💃 Dance Floor", value="dance_floor"),
        app_commands.Choice(name="🚗 Retro Car", value="retro_car"),
        app_commands.Choice(name="✨ VIP Lounge", value="vip_lounge")
    ])
    async def ascii_art(self, interaction: discord.Interaction, art_type: str):
        """Display ASCII art"""
        if art_type in self.ascii_art:
            art = self.ascii_art[art_type]
            quote = random.choice(self.beach_quotes)
            
            embed = discord.Embed(
                title="🎨 Monroe Social Club ASCII Art",
                description=f"{art}\n\n*{quote}*",
                color=Config.COLORS["pink"]
            )
            embed.set_footer(text="Monroe Social Club - 80s Beach Vibes")
            
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ ASCII art not found!", ephemeral=True)
    
    @app_commands.command(name="welcome_art", description="Display welcome ASCII art (Management only)")
    async def welcome_art(self, interaction: discord.Interaction):
        """Display welcome ASCII art"""
        if not self.has_management_permissions(interaction.user):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return
        
        art = self.ascii_art['neon_welcome']
        
        embed = discord.Embed(
            title="🌴 Welcome to Monroe Social Club! 🌴",
            description=art,
            color=Config.COLORS["pink"]
        )
        embed.add_field(
            name="🎉 What We Offer",
            value="• 80s Beach Club Experience\n• Roblox Gaming Community\n• Exclusive Events\n• VIP Perks\n• Neon Nights",
            inline=False
        )
        embed.set_footer(text="Monroe Social Club - Where the 80s Never Ended!")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="random_ascii", description="Display random ASCII art")
    async def random_ascii(self, interaction: discord.Interaction):
        """Display random ASCII art"""
        # Exclude welcome art from random selection
        available_art = {k: v for k, v in self.ascii_art.items() if k != 'neon_welcome'}
        art_type = random.choice(list(available_art.keys()))
        art = available_art[art_type]
        quote = random.choice(self.beach_quotes)
        
        embed = discord.Embed(
            title=f"🎨 Random ASCII Art - {art_type.replace('_', ' ').title()}",
            description=f"{art}\n\n*{quote}*",
            color=Config.COLORS["pink"]
        )
        embed.set_footer(text="Monroe Social Club - 80s Beach Vibes")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(ASCIIArtCog(bot))
