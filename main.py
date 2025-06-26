
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

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    bot.start_time = datetime.utcnow()

    # Start the API server
    await start_health_server()

async def start_health_server():
    """Complete API server with all endpoints for Monroe Dashboard"""

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
            if not message:
                return web.json_response({'error': 'Message required'}, status=400)

            sent_count = 0
            for guild in bot.guilds:
                try:
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
                except:
                    pass

            return web.json_response({
                'success': True, 
                'sent_to': sent_count, 
                'message': f'Broadcast sent to {sent_count} servers'
            })
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)

    async def handle_qotd(request):
        auth_error = await check_auth(request)
        if auth_error: return auth_error

        try:
            data = await request.json()
            question = data.get('question', '')
            if not question:
                return web.json_response({'error': 'Question required'}, status=400)

            sent_count = 0
            embed = discord.Embed(
                title=f"🤔 Question of the Day - {bot_config['qotd_message_style']}", 
                description=question, 
                color=bot_config['qotd_embed_color'], 
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text="Answer below! 🏖️")
            embed.set_author(name="Monroe Social Club")

            for guild in bot.guilds:
                try:
                    channel = None
                    # Look for configured QOTD channels first
                    for ch_name in bot_config['qotd_channels']:
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
                        await channel.send(embed=embed)
                        sent_count += 1
                except:
                    pass

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
            if not title or not content:
                return web.json_response({'error': 'Title and content required'}, status=400)

            sent_count = 0
            embed = discord.Embed(
                title=f"📢 {title}", 
                description=content, 
                color=bot_config['announcement_embed_color'], 
                timestamp=datetime.utcnow()
            )
            embed.set_author(name=f"Monroe Social Club - {bot_config['announcement_style']}")
            embed.set_footer(text="Official Monroe Announcement")

            for guild in bot.guilds:
                try:
                    channel = None
                    # Look for configured announcement channels first
                    for ch_name in bot_config['announcement_channels']:
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
                        await channel.send(embed=embed)
                        sent_count += 1
                except:
                    pass

            return web.json_response({
                'success': True, 
                'sent_to': sent_count, 
                'message': f'Announcement sent to {sent_count} servers'
            })
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)

    # Configuration storage
    bot_config = {
        "qotd_channels": ["qotd", "question-of-the-day", "daily-question", "general", "chat"],
        "announcement_channels": ["announcements", "news", "updates", "general"],
        "qotd_message_style": "80s Beach Vibes",
        "announcement_style": "Official Monroe",
        "qotd_embed_color": 0xf59e0b,
        "announcement_embed_color": 0x7c3aed
    }

    async def handle_config_get(request):
        auth_error = await check_auth(request)
        if auth_error: return auth_error
        return web.json_response(bot_config)

    async def handle_config_post(request):
        auth_error = await check_auth(request)
        if auth_error: return auth_error
        
        try:
            data = await request.json()
            if 'qotd_channels' in data:
                bot_config['qotd_channels'] = data['qotd_channels']
            if 'announcement_channels' in data:
                bot_config['announcement_channels'] = data['announcement_channels']
            if 'qotd_message_style' in data:
                bot_config['qotd_message_style'] = data['qotd_message_style']
            if 'announcement_style' in data:
                bot_config['announcement_style'] = data['announcement_style']
            
            return web.json_response({'success': True, 'config': bot_config})
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)

    # Create web app with all endpoints
    app = web.Application()
    app.router.add_get('/health', handle_health)
    app.router.add_get('/', lambda req: web.Response(text="Monroe Bot API Server"))
    app.router.add_get('/api/status', handle_status)
    app.router.add_post('/api/broadcast', handle_broadcast)
    app.router.add_post('/api/qotd', handle_qotd)
    app.router.add_post('/api/announcement', handle_announcement)
    app.router.add_get('/api/config', handle_config_get)
    app.router.add_post('/api/config', handle_config_post)

    # Start server
    port = int(os.getenv('PORT', 8000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Monroe Bot API server started on port {port}")
    print("API endpoints ready - dashboard commands should work now!")

# Add your existing bot commands here
@bot.command(name='ping')
async def ping(ctx):
    await ctx.send('Pong!')

# Run the bot
if __name__ == "__main__":
    bot.run(os.getenv('DISCORD_TOKEN'))
