import discord
from discord.ext import commands
import asyncio
import os
from bot.config import Config
from bot.embeds import create_welcome_embed
from aiohttp import web

# Bot intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

# Create bot instance
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'🌴 Monroe Social Club Bot is ready! Logged in as {bot.user}')
    print(f'🏖️ Connected to {len(bot.guilds)} servers')
    
    # Wait for all cogs to load before syncing
    await asyncio.sleep(3)
    
    # Sync slash commands to fix "unknown integration" errors
    try:
        # Get the guild ID
        guild_id = list(bot.guilds)[0].id if bot.guilds else None
        
        if guild_id:
            # Clear guild-specific commands first
            bot.tree.clear_commands(guild=discord.Object(id=guild_id))
            
            # Sync to guild first for immediate availability
            guild_synced = await bot.tree.sync(guild=discord.Object(id=guild_id))
            print(f'✨ Guild sync completed: {len(guild_synced)} commands')
            
            # Then sync globally for all servers
            global_synced = await bot.tree.sync()
            print(f'✨ Global sync completed: {len(global_synced)} commands')
        else:
            # Fallback to global sync only
            synced = await bot.tree.sync()
            print(f'✨ Global sync completed: {len(synced)} commands')
            
    except Exception as e:
        print(f'Command sync error: {e}')
        # Try simple sync as final fallback
        try:
            synced = await bot.tree.sync()
            print(f'✨ Simple sync completed: {len(synced)} commands')
        except Exception as fallback_error:
            print(f'All sync attempts failed: {fallback_error}')

@bot.event
async def on_member_join(member):
    """Welcome new members with 80s beach club style"""
    welcome_channel = bot.get_channel(Config.WELCOME_CHANNEL_ID)
    if welcome_channel:
        embed = discord.Embed(
            title="🌴 Welcome to Monroe Social Club! 🌴",
            description=f"Hey {member.mention}! Welcome to our retro beach hangout!",
            color=0xFF69B4  # Hot pink for 80s vibe
        )
        embed.add_field(
            name="🌊 We are now members strong!",
            value=f"Get ready for some awesome 80s vibes!",
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
        
        await welcome_channel.send(embed=embed)

@bot.tree.command(name="management", description="Display the Monroe Social Club management team")
async def management_command(interaction: discord.Interaction):
    """Display management team information"""
    embed = discord.Embed(
        title="👑 Monroe Social Club Management Team",
        description="Meet the leadership team operating from our beachfront yacht!",
        color=0x00CED1  # Dark turquoise for ocean theme
    )
    
    embed.add_field(
        name="👑 Chairman",
        value="**Samu** - Server Owner\nLeading the club from the yacht's bridge",
        inline=True
    )
    embed.add_field(
        name="💎 Vice Chairman",
        value="**Luca** - Second in Command\nEnsuring smooth operations",
        inline=True
    )
    embed.add_field(
        name="🏆 President",
        value="**Fra** - Club President\nManaging daily activities",
        inline=True
    )
    embed.add_field(
        name="🔨 Vice President",
        value="**Rev** - Assistant President\nSupporting club initiatives",
        inline=True
    )
    
    embed.set_footer(text="Monroe Social Club - 1980s Beach Paradise 🌴")
    embed.timestamp = discord.utils.utcnow()
    
    await interaction.response.send_message(embed=embed)

# Health check endpoint for Render/UptimeRobot
async def health_check(request):
    return web.Response(text="Bot is running!", status=200)

async def start_health_server():
    """Start health check server for Render deployment"""
    app = web.Application()
    app.router.add_get('/health', health_check)
    app.router.add_get('/', health_check)  # Root endpoint too
    
    port = int(os.environ.get('PORT', 8080))  # Render sets PORT env var
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"✅ Health check server started on port {port}")

async def main():
    # Load cogs first
    cogs = [
        "bot.moderation",
        "bot.automod", 
        "bot.roblox_integration",
        "bot.applications",
        "bot.utils",
        "bot.qotd_system",
        "bot.keep_alive",
        "bot.rich_presence",
        "bot.admin_logging",
        "bot.custom_embeds"
    ]
    
    for cog in cogs:
        try:
            await bot.load_extension(cog)
            print(f"✅ Loaded {cog}")
        except Exception as e:
            print(f"❌ Failed to load {cog}: {e}")
    
    # Setup hook with health server and command sync
    async def setup_hook():
        # Start health check server for Render
        await start_health_server()
        
        print("🔄 Setting up commands...")
        try:
            # Sync commands immediately after setup
            synced = await bot.tree.sync()
            print(f"✨ Synced {len(synced)} commands during setup")
        except Exception as e:
            print(f"Setup sync failed: {e}")
    
    bot.setup_hook = setup_hook
    
    # Start the bot
    await bot.start(Config.BOT_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
