import discord
from discord.ext import commands
import asyncio
import os
import json
from datetime import datetime
from aiohttp import web
from bot.config import Config
from bot.embeds import create_welcome_embed

# Bot intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

# Create bot instance
bot = commands.Bot(command_prefix='!', intents=intents)

# API Configuration
API_SECRET = os.getenv('API_SECRET', 'default-secret')

async def check_auth(request):
    """Simple auth check"""
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer ') or auth[7:] != API_SECRET:
        return web.json_response({'error': 'Unauthorized'}, status=401)
    return None

async def handle_status(request):
    """Bot status endpoint"""
    auth_error = await check_auth(request)
    if auth_error:
        return auth_error
    
    try:
        guild_count = len(bot.guilds) if hasattr(bot, 'guilds') else 0
        member_count = sum(g.member_count or 0 for g in bot.guilds) if hasattr(bot, 'guilds') else 0
        
        uptime_seconds = (datetime.utcnow() - bot.start_time).total_seconds() if hasattr(bot, 'start_time') else 0
        uptime_display = f"{int(uptime_seconds // 3600)}h {int((uptime_seconds % 3600) // 60)}m"
        
        return web.json_response({
            "online": True,
            "serverCount": guild_count,
            "userCount": member_count,
            "uptime": uptime_display,
            "lastSeen": datetime.utcnow().isoformat()
        })
    except Exception as e:
        return web.json_response({
            "online": False,
            "serverCount": 0,
            "userCount": 0,
            "uptime": "Error",
            "lastSeen": datetime.utcnow().isoformat(),
            "error": str(e)
        })

async def handle_broadcast(request):
    """Broadcast message endpoint"""
    auth_error = await check_auth(request)
    if auth_error:
        return auth_error
    
    try:
        data = await request.json()
        message = data.get('message', '')
        
        if not message:
            return web.json_response({'error': 'Message required'}, status=400)
        
        sent_count = 0
        failed_count = 0
        
        for guild in bot.guilds:
            try:
                # Find first available text channel
                channel = None
                for ch in guild.text_channels:
                    if ch.permissions_for(guild.me).send_messages:
                        channel = ch
                        break
                
                if channel:
                    embed = discord.Embed(
                        title="📢 Monroe Bot Broadcast",
                        description=message,
                        color=0x7c3aed,
                        timestamp=datetime.utcnow()
                    )
                    embed.set_footer(text="Sent from Monroe Dashboard")
                    await channel.send(embed=embed)
                    sent_count += 1
                else:
                    failed_count += 1
            except:
                failed_count += 1
        
        return web.json_response({
            'success': True,
            'sent_to': sent_count,
            'failed': failed_count,
            'message': f'Broadcast sent to {sent_count} servers'
        })
    
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)

async def handle_qotd(request):
    """Question of the Day endpoint"""
    auth_error = await check_auth(request)
    if auth_error:
        return auth_error
    
    try:
        data = await request.json()
        question = data.get('question', '')
        category = data.get('category', 'General')
        
        if not question:
            return web.json_response({'error': 'Question required'}, status=400)
        
        sent_count = 0
        failed_count = 0
        
        embed = discord.Embed(
            title=f"🤔 Question of the Day - {category}",
            description=question,
            color=0xf59e0b,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text="Answer below!")
        
        for guild in bot.guilds:
            try:
                # Look for QOTD channel or use general
                channel = None
                for ch_name in ['qotd', 'question-of-the-day', 'general', 'chat']:
                    channel = discord.utils.get(guild.text_channels, name=ch_name)
                    if channel and channel.permissions_for(guild.me).send_messages:
                        break
                
                if not channel:
                    for ch in guild.text_channels:
                        if ch.permissions_for(guild.me).send_messages:
                            channel = ch
                            break
                
                if channel:
                    await channel.send(embed=embed)
                    sent_count += 1
                else:
                    failed_count += 1
            except:
                failed_count += 1
        
        return web.json_response({
            'success': True,
            'sent_to': sent_count,
            'failed': failed_count,
            'message': f'QOTD sent to {sent_count} servers'
        })
    
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)

async def handle_announcement(request):
    """Announcement endpoint"""
    auth_error = await check_auth(request)
    if auth_error:
        return auth_error
    
    try:
        data = await request.json()
        title = data.get('title', '')
        content = data.get('content', '')
        
        if not title or not content:
            return web.json_response({'error': 'Title and content required'}, status=400)
        
        sent_count = 0
        failed_count = 0
        
        embed = discord.Embed(
            title=f"📢 {title}",
            description=content,
            color=0x7c3aed,
            timestamp=datetime.utcnow()
        )
        embed.set_author(name="Monroe Social Club")
        embed.set_footer(text="Official Monroe Announcement")
        
        for guild in bot.guilds:
            try:
                # Look for announcement channel or use general
                channel = None
                for ch_name in ['announcements', 'news', 'updates', 'general']:
                    channel = discord.utils.get(guild.text_channels, name=ch_name)
                    if channel and channel.permissions_for(guild.me).send_messages:
                        break
                
                if not channel:
                    for ch in guild.text_channels:
                        if ch.permissions_for(guild.me).send_messages:
                            channel = ch
                            break
                
                if channel:
                    await channel.send(embed=embed)
                    sent_count += 1
                else:
                    failed_count += 1
            except:
                failed_count += 1
        
        return web.json_response({
            'success': True,
            'sent_to': sent_count,
            'failed': failed_count,
            'message': f'Announcement sent to {sent_count} servers'
        })
    
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)

async def handle_moderation(request):
    """Moderation endpoint"""
    auth_error = await check_auth(request)
    if auth_error:
        return auth_error
    
    try:
        data = await request.json()
        action = data.get('action')
        user_id = data.get('user_id')
        reason = data.get('reason', 'No reason provided')
        
        if not action or not user_id:
            return web.json_response({'error': 'Action and user_id required'}, status=400)
        
        # Use first guild for moderation
        guild = bot.guilds[0] if bot.guilds else None
        if not guild:
            return web.json_response({'error': 'No guild available'}, status=404)
        
        try:
            user = await guild.fetch_member(int(user_id))
        except:
            return web.json_response({'error': 'User not found'}, status=404)
        
        if action == 'warn':
            try:
                embed = discord.Embed(title="⚠️ Warning", description=f"You were warned in {guild.name}", color=0xfbbf24)
                embed.add_field(name="Reason", value=reason)
                await user.send(embed=embed)
                result = f"Warning sent to {user.display_name}"
            except:
                result = f"Warning issued to {user.display_name} (DM failed)"
        elif action == 'kick':
            await user.kick(reason=reason)
            result = f"Kicked {user.display_name}"
        elif action == 'ban':
            await user.ban(reason=reason)
            result = f"Banned {user.display_name}"
        else:
            return web.json_response({'error': 'Invalid action'}, status=400)
        
        return web.json_response({
            'success': True,
            'message': result,
            'action': action,
            'user': user.display_name
        })
    
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)

async def start_api_server():
    """Start the API server with dashboard endpoints"""
    app = web.Application()
    
    # Health endpoint (no auth)
    app.router.add_get('/health', lambda req: web.Response(text="Bot is running!"))
    app.router.add_get('/', lambda req: web.Response(text="Monroe Bot API Server"))
    
    # API endpoints (with auth)
    app.router.add_get('/api/status', handle_status)
    app.router.add_post('/api/broadcast', handle_broadcast)
    app.router.add_post('/api/qotd', handle_qotd)
    app.router.add_post('/api/announcement', handle_announcement)
    app.router.add_post('/api/moderation', handle_moderation)
    
    # Start server
    port = int(os.getenv('PORT', 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"✅ API server started on port {port}")

@bot.event
async def on_ready():
    # Set start time for uptime tracking
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
