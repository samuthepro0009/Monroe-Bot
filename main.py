import discord
from discord.ext import commands
import asyncio
import os
import json
from datetime import datetime
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
    # Set bot start time for API uptime tracking
    bot.start_time = datetime.utcnow()
    
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

# API Secret for dashboard authentication
API_SECRET = os.environ.get('API_SECRET', 'default-secret')

# Bot start time will be set in on_ready event

# Health check endpoint for Render/UptimeRobot
async def health_check(request):
    return web.Response(text="Bot is running!", status=200)

# Authentication middleware
async def check_auth(request):
    """Check API authentication"""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return web.Response(status=401, text='Unauthorized')
    
    token = auth_header[7:]  # Remove 'Bearer ' prefix
    if token != API_SECRET:
        return web.Response(status=401, text='Invalid token')
    
    return None

# Bot status endpoint
async def handle_status(request):
    """Return bot status information"""
    auth_error = await check_auth(request)
    if auth_error:
        return auth_error
    
    if bot.is_ready():
        uptime = str(datetime.utcnow() - bot.start_time) if bot.start_time else "Unknown"
        status = {
            "online": True,
            "serverCount": len(bot.guilds),
            "userCount": sum(guild.member_count for guild in bot.guilds),
            "uptime": uptime,
            "lastSeen": datetime.utcnow().isoformat(),
            "guilds": [
                {
                    "id": str(guild.id),
                    "name": guild.name,
                    "memberCount": guild.member_count
                } for guild in bot.guilds
            ]
        }
    else:
        status = {
            "online": False,
            "serverCount": 0,
            "userCount": 0,
            "uptime": "0",
            "lastSeen": datetime.utcnow().isoformat()
        }
    
    return web.json_response(status)

# Broadcast message endpoint
async def handle_broadcast(request):
    """Send broadcast message to channel"""
    auth_error = await check_auth(request)
    if auth_error:
        return auth_error
    
    try:
        data = await request.json()
        message = data.get('message', '')
        channel_id = data.get('channel_id', '')
        dashboard_user = data.get('dashboard_user', 'Dashboard Admin')
        
        if not message:
            return web.json_response({'error': 'Message is required'}, status=400)
        
        # If no channel specified, use first available text channel
        if channel_id:
            channel = bot.get_channel(int(channel_id))
        else:
            # Find first text channel in first guild
            channel = None
            for guild in bot.guilds:
                for ch in guild.text_channels:
                    if ch.permissions_for(guild.me).send_messages:
                        channel = ch
                        break
                if channel:
                    break
        
        if not channel:
            return web.json_response({'error': 'No valid channel found'}, status=404)
        
        # Create embed for broadcast
        embed = discord.Embed(
            title="📢 Server Announcement",
            description=message,
            color=0xFF6B6B,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"Sent by {dashboard_user} via Dashboard")
        
        await channel.send(embed=embed)
        
        return web.json_response({
            'success': True,
            'message': f'Broadcast sent to {channel.name}',
            'channel': channel.name,
            'channel_id': str(channel.id)
        })
        
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)

# Question of the Day endpoint
async def handle_qotd(request):
    """Send Question of the Day"""
    auth_error = await check_auth(request)
    if auth_error:
        return auth_error
    
    try:
        data = await request.json()
        question = data.get('question', '')
        channel_id = data.get('channel_id', '')
        dashboard_user = data.get('dashboard_user', 'Dashboard Admin')
        
        if not question:
            return web.json_response({'error': 'Question is required'}, status=400)
        
        # If no channel specified, use first available text channel
        if channel_id:
            channel = bot.get_channel(int(channel_id))
        else:
            # Find first text channel in first guild
            channel = None
            for guild in bot.guilds:
                for ch in guild.text_channels:
                    if ch.permissions_for(guild.me).send_messages:
                        channel = ch
                        break
                if channel:
                    break
        
        if not channel:
            return web.json_response({'error': 'No valid channel found'}, status=404)
        
        # Create QOTD embed
        embed = discord.Embed(
            title="🤔 Question of the Day",
            description=question,
            color=0x4ECDC4,
            timestamp=datetime.utcnow()
        )
        embed.add_field(
            name="💭 How to participate",
            value="React with your thoughts in the replies below!",
            inline=False
        )
        embed.set_footer(text=f"Posted by {dashboard_user} via Dashboard")
        
        message = await channel.send(embed=embed)
        await message.add_reaction("🤔")
        await message.add_reaction("💭")
        
        return web.json_response({
            'success': True,
            'message': f'QOTD posted in {channel.name}',
            'channel': channel.name,
            'channel_id': str(channel.id),
            'message_id': str(message.id)
        })
        
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)

# Announcement endpoint
async def handle_announcement(request):
    """Send formal announcement"""
    auth_error = await check_auth(request)
    if auth_error:
        return auth_error
    
    try:
        data = await request.json()
        title = data.get('title', '')
        content = data.get('content', '')
        channel_id = data.get('channel_id', '')
        dashboard_user = data.get('dashboard_user', 'Dashboard Admin')
        
        if not title or not content:
            return web.json_response({'error': 'Title and content are required'}, status=400)
        
        # If no channel specified, use first available text channel
        if channel_id:
            channel = bot.get_channel(int(channel_id))
        else:
            # Find first text channel in first guild
            channel = None
            for guild in bot.guilds:
                for ch in guild.text_channels:
                    if ch.permissions_for(guild.me).send_messages:
                        channel = ch
                        break
                if channel:
                    break
        
        if not channel:
            return web.json_response({'error': 'No valid channel found'}, status=404)
        
        # Create announcement embed
        embed = discord.Embed(
            title=f"📋 {title}",
            description=content,
            color=0xF39C12,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"Official Announcement by {dashboard_user}")
        
        await channel.send("@everyone", embed=embed)
        
        return web.json_response({
            'success': True,
            'message': f'Announcement posted in {channel.name}',
            'channel': channel.name,
            'channel_id': str(channel.id)
        })
        
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)

# Moderation endpoint
async def handle_moderation(request):
    """Execute moderation actions"""
    auth_error = await check_auth(request)
    if auth_error:
        return auth_error
    
    try:
        data = await request.json()
        action = data.get('action', '')
        user_id = data.get('user_id', '')
        reason = data.get('reason', 'No reason provided')
        dashboard_user = data.get('dashboard_user', 'Dashboard Admin')
        
        if not action or not user_id:
            return web.json_response({'error': 'Action and user_id are required'}, status=400)
        
        # Find user in guilds
        user = None
        guild = None
        for g in bot.guilds:
            try:
                user = await g.fetch_member(int(user_id))
                guild = g
                break
            except:
                continue
        
        if not user:
            return web.json_response({'error': 'User not found in any guild'}, status=404)
        
        # Execute moderation action
        result = {}
        
        if action == 'warn':
            # Send warning to user
            try:
                embed = discord.Embed(
                    title="⚠️ Warning",
                    description=f"You have been warned in {guild.name}",
                    color=0xFFD700
                )
                embed.add_field(name="Reason", value=reason, inline=False)
                embed.add_field(name="Moderator", value=dashboard_user, inline=False)
                await user.send(embed=embed)
                result['dm_sent'] = True
            except:
                result['dm_sent'] = False
            
            result['action'] = 'warned'
            
        elif action == 'kick':
            await user.kick(reason=f"Kicked by {dashboard_user}: {reason}")
            result['action'] = 'kicked'
            
        elif action == 'ban':
            delete_days = data.get('delete_days', 0)
            await user.ban(reason=f"Banned by {dashboard_user}: {reason}", delete_message_days=delete_days)
            result['action'] = 'banned'
        
        # Log moderation action in a log channel if exists
        log_channel = None
        for channel in guild.text_channels:
            if 'log' in channel.name.lower() or 'mod' in channel.name.lower():
                log_channel = channel
                break
        
        if log_channel:
            embed = discord.Embed(
                title=f"🔨 Moderation Action: {action.title()}",
                color=0xE74C3C,
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="User", value=f"{user.mention} ({user.id})", inline=True)
            embed.add_field(name="Action", value=action.title(), inline=True)
            embed.add_field(name="Moderator", value=dashboard_user, inline=True)
            embed.add_field(name="Reason", value=reason, inline=False)
            
            await log_channel.send(embed=embed)
        
        return web.json_response({
            'success': True,
            'message': f'User {user.name} has been {action}ed',
            'user': user.name,
            'action': action,
            **result
        })
        
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)

async def start_health_server():
    """Start API server with all dashboard endpoints"""
    app = web.Application()
    
    # Health check routes
    app.router.add_get('/health', health_check)
    app.router.add_get('/', health_check)
    
    # Dashboard API routes
    app.router.add_get('/api/status', handle_status)
    app.router.add_post('/api/broadcast', handle_broadcast)
    app.router.add_post('/api/qotd', handle_qotd)
    app.router.add_post('/api/announcement', handle_announcement)
    app.router.add_post('/api/moderation', handle_moderation)
    
    port = int(os.environ.get('PORT', 8080))  # Render sets PORT env var
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"✅ API server started on port {port} with dashboard endpoints")

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
