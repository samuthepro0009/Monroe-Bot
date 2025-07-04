import discord
from discord.ext import commands
import os
import json
from datetime import datetime
from aiohttp import web
import asyncio

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

API_SECRET = os.getenv('API_SECRET', 'default-secret')

# Channel IDs
ANNOUNCEMENT_CHANNEL_ID = 1353388424295350283
BROADCAST_CHANNELS = [1353393437650718910, 1353395315197218847]

@bot.event
async def on_ready():
    print(f'🌴 {bot.user} has connected to Discord!')
    print(f'🏖️ Connected to {len(bot.guilds)} servers')
    bot.start_time = datetime.utcnow()

# Load all cogs
async def load_cogs():
    cogs = [
        'bot.automod',
        'bot.admin_logging', 
        'bot.moderation',
        'bot.utils',
        'bot.suspicious_activity'  # Add our new suspicious activity system
    ]
    
    for cog in cogs:
        try:
            await bot.load_extension(cog)
            print(f'✅ Loaded {cog}')
        except Exception as e:
            print(f'❌ Failed to load {cog}: {e}')

@bot.event
async def on_ready():
    print(f'🌴 {bot.user} has connected to Discord!')
    print(f'🏖️ Connected to {len(bot.guilds)} servers')
    bot.start_time = datetime.utcnow()
    
    # Load cogs after bot is ready
    await load_cogs()
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f'🔄 Synced {len(synced)} command(s)')
    except Exception as e:
        print(f'❌ Failed to sync commands: {e}')

async def start_health_server():
    """Complete API server with all endpoints for Monroe Dashboard"""
    print("🌐 Starting API server...")

    async def check_auth(request):
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer ') or auth[7:] != API_SECRET:
            return web.json_response({'error': 'Unauthorized'}, status=401)
        return None

    async def handle_health(request):
        return web.Response(text="Bot is running!")

    async def handle_status(request):
        auth_error = await check_auth(request)
        if auth_error: return auth_error

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
                "lastSeen": datetime.utcnow().isoformat()
            })

    async def handle_broadcast(request):
        auth_error = await check_auth(request)
        if auth_error: return auth_error

        try:
            data = await request.json()
            message = data.get('message', '')
            dashboard_user = data.get('dashboard_user', 'Dashboard Admin')
            if not message:
                return web.json_response({'error': 'Message required'}, status=400)

            sent_count = 0
            for guild in bot.guilds:
                try:
                    for channel_id in BROADCAST_CHANNELS:
                        channel = bot.get_channel(channel_id)
                        if channel and channel.guild == guild and channel.permissions_for(guild.me).send_messages:
                            embed = discord.Embed(
                                title="📢 Monroe Bot Broadcast", 
                                description=message, 
                                color=0x7c3aed, 
                                timestamp=datetime.utcnow()
                            )
                            embed.set_author(name=f"Sent by {dashboard_user}")
                            embed.set_footer(text="Sent from Monroe Dashboard")
                            await channel.send(content="@everyone", embed=embed)
                            sent_count += 1
                            print(f"✅ Broadcast sent to {channel.name}")
                except Exception as e:
                    print(f"❌ Broadcast error in guild {guild.name}: {e}")

            return web.json_response({
                'success': True, 
                'sent_to': sent_count, 
                'message': f'Broadcast sent to {sent_count} channels'
            })
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)

    async def handle_qotd(request):
        auth_error = await check_auth(request)
        if auth_error: return auth_error

        try:
            data = await request.json()
            question = data.get('question', '')
            dashboard_user = data.get('dashboard_user', 'Dashboard Admin')
            if not question:
                return web.json_response({'error': 'Question required'}, status=400)

            sent_count = 0
            embed = discord.Embed(
                title="🤔 Question of the Day", 
                description=question, 
                color=0xf59e0b, 
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text="Answer below! 🏖️")
            embed.set_author(name=f"Sent by {dashboard_user}")

            for guild in bot.guilds:
                try:
                    channel = None
                    # Look for QOTD channels
                    for ch_name in ['qotd', 'question-of-the-day', 'daily-question', 'general', 'chat']:
                        channel = discord.utils.get(guild.text_channels, name=ch_name)
                        if channel and channel.permissions_for(guild.me).send_messages:
                            break

                    # Fallback to any channel we can send to
                    if not channel:
                        for ch in guild.text_channels:
                            if ch.permissions_for(guild.me).send_messages:
                                channel = ch
                                break

                    if channel:
                        await channel.send(content="@everyone", embed=embed)
                        sent_count += 1
                        print(f"✅ QOTD sent to {channel.name}")
                except Exception as e:
                    print(f"❌ QOTD error in guild {guild.name}: {e}")

            return web.json_response({
                'success': True, 
                'sent_to': sent_count, 
                'message': f'QOTD sent to {sent_count} servers'
            })
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)

    async def handle_announcement(request):
        auth_error = await check_auth(request)
        if auth_error: return auth_error

        try:
            data = await request.json()
            title = data.get('title', '')
            content = data.get('content', '')
            dashboard_user = data.get('dashboard_user', 'Dashboard Admin')
            if not title or not content:
                return web.json_response({'error': 'Title and content required'}, status=400)

            sent_count = 0
            embed = discord.Embed(
                title=f"📢 {title}", 
                description=content, 
                color=0x7c3aed, 
                timestamp=datetime.utcnow()
            )
            embed.set_author(name=f"Sent by {dashboard_user}")
            embed.set_footer(text="Official Monroe Announcement")

            for guild in bot.guilds:
                try:
                    channel = bot.get_channel(ANNOUNCEMENT_CHANNEL_ID)
                    if channel and channel.guild == guild and channel.permissions_for(guild.me).send_messages:
                        await channel.send(content="@everyone", embed=embed)
                        sent_count += 1
                        print(f"✅ Announcement sent to {channel.name}")
                except Exception as e:
                    print(f"❌ Announcement error in guild {guild.name}: {e}")

            return web.json_response({
                'success': True, 
                'sent_to': sent_count, 
                'message': f'Announcement sent to {sent_count} servers'
            })
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)

    async def handle_moderation(request):
        auth_error = await check_auth(request)
        if auth_error: return auth_error

        try:
            data = await request.json()
            action = data.get('action', '').lower()
            user_id = data.get('user_id', '')
            reason = data.get('reason', 'No reason provided')
            dashboard_user = data.get('dashboard_user', 'Dashboard Admin')

            if not action or not user_id:
                return web.json_response({'error': 'Action and user_id required'}, status=400)

            if action not in ['warn', 'kick', 'ban']:
                return web.json_response({'error': 'Invalid action'}, status=400)

            # Use first available guild
            guild = bot.guilds[0] if bot.guilds else None
            if not guild:
                return web.json_response({'error': 'No guild available'}, status=404)

            # Get member
            try:
                member = await guild.fetch_member(int(user_id))
            except:
                return web.json_response({'error': 'User not found'}, status=404)

            result = ""

            if action == 'warn':
                try:
                    embed = discord.Embed(
                        title="⚠️ Warning",
                        description=f"You have been warned in {guild.name}",
                        color=0xfbbf24,
                        timestamp=datetime.utcnow()
                    )
                    embed.add_field(name="Reason", value=reason, inline=False)
                    embed.add_field(name="Moderator", value=dashboard_user, inline=True)

                    await member.send(embed=embed)
                    result = f"Warning sent to {member.display_name}"
                except:
                    result = f"Warning issued to {member.display_name} (DM failed)"

            elif action == 'kick':
                await member.kick(reason=f"Dashboard moderation by {dashboard_user}: {reason}")
                result = f"Successfully kicked {member.display_name}"

            elif action == 'ban':
                await member.ban(reason=f"Dashboard moderation by {dashboard_user}: {reason}")
                result = f"Successfully banned {member.display_name}"

            print(f"✅ Moderation: {action} on {member.display_name} by {dashboard_user}")

            return web.json_response({
                'success': True,
                'message': result,
                'action': action,
                'user': member.display_name
            })

        except Exception as e:
            print(f"❌ Moderation error: {str(e)}")
            return web.json_response({'error': str(e)}, status=500)

    # Create web app with all endpoints
    app = web.Application()
    app.router.add_get('/health', handle_health)
    app.router.add_get('/', lambda req: web.Response(text="Monroe Bot API Server"))
    app.router.add_get('/api/status', handle_status)
    app.router.add_post('/api/broadcast', handle_broadcast)
    app.router.add_post('/api/qotd', handle_qotd)
    app.router.add_post('/api/announcement', handle_announcement)
    app.router.add_post('/api/moderation', handle_moderation)

    # Start server on correct address and port
    port = int(os.getenv('PORT', 8000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)  # Important: bind to 0.0.0.0
    await site.start()

    print(f"🌐 Monroe Bot API server listening on 0.0.0.0:{port}")
    print(f"✅ Health check: http://0.0.0.0:{port}/health")
    print(f"✅ API endpoints ready for dashboard connections")

# Bot commands
@bot.command(name='ping')
async def ping(ctx):
    await ctx.send('🏓 Pong!')

async def main():
    """Main function to start both bot and server"""
    print("🌴 Monroe Social Club Bot - Starting...")

    # Start the health server
    await start_health_server()

    # Start the bot
    print("🔌 Connecting to Discord...")
    await bot.start(os.getenv('DISCORD_TOKEN'))

# Run the bot
if __name__ == "__main__":
    asyncio.run(main())
