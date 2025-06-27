
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
                except:
                    pass

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
                title=f"🤔 Question of the Day - {bot_config['qotd_message_style']}", 
                description=question, 
                color=bot_config['qotd_embed_color'], 
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text="Answer below! 🏖️")
            embed.set_author(name=f"Sent by {dashboard_user}")

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
                        await channel.send(content="@everyone", embed=embed)
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
            dashboard_user = data.get('dashboard_user', 'Dashboard Admin')
            if not title or not content:
                return web.json_response({'error': 'Title and content required'}, status=400)

            sent_count = 0
            embed = discord.Embed(
                title=f"📢 {title}", 
                description=content, 
                color=bot_config['announcement_embed_color'], 
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

    async def handle_moderation(request):
        """Complete moderation endpoint with full rule system"""
        auth_error = await check_auth(request)
        if auth_error: return auth_error
        
        try:
            data = await request.json()
            action = data.get('action', '').lower()
            user_id = data.get('user_id', '')
            reason = data.get('reason', 'No reason provided')
            rule_violations = data.get('rule_violations', [])
            delete_days = data.get('delete_days', 0)
            dashboard_user = data.get('dashboard_user', 'Dashboard Admin')
            
            if not action or not user_id:
                return web.json_response({'error': 'Action and user_id required'}, status=400)
            
            if action not in ['warn', 'kick', 'ban']:
                return web.json_response({'error': 'Invalid action. Must be warn, kick, or ban'}, status=400)
            
            # Use first available guild
            guild = bot.guilds[0] if bot.guilds else None
            if not guild:
                return web.json_response({'error': 'No guild available'}, status=404)
            
            # Get member
            try:
                member = await guild.fetch_member(int(user_id))
            except:
                return web.json_response({'error': 'User not found in guild'}, status=404)
            
            # Check bot permissions
            bot_member = guild.get_member(bot.user.id)
            if not bot_member:
                return web.json_response({'error': 'Bot not found in guild'}, status=500)
            
            # Execute moderation action
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
                    if rule_violations:
                        embed.add_field(name="Rule Violations", value="\n".join(rule_violations), inline=False)
                    embed.add_field(name="Moderator", value=dashboard_user, inline=True)
                    embed.set_footer(text="Monroe Social Club Moderation")
                    
                    await member.send(embed=embed)
                    result = f"Warning sent to {member.display_name}"
                except discord.Forbidden:
                    result = f"Warning issued to {member.display_name} (DM failed - user has DMs disabled)"
                except Exception as e:
                    result = f"Warning issued to {member.display_name} (DM failed - {str(e)})"
                    
            elif action == 'kick':
                if not bot_member.guild_permissions.kick_members:
                    return web.json_response({'error': 'Bot lacks kick permissions'}, status=403)
                
                try:
                    # Send DM before kicking
                    embed = discord.Embed(
                        title="👢 Kicked from Server",
                        description=f"You have been kicked from {guild.name}",
                        color=0xf97316,
                        timestamp=datetime.utcnow()
                    )
                    embed.add_field(name="Reason", value=reason, inline=False)
                    if rule_violations:
                        embed.add_field(name="Rule Violations", value="\n".join(rule_violations), inline=False)
                    embed.add_field(name="Moderator", value=dashboard_user, inline=True)
                    embed.set_footer(text="Monroe Social Club Moderation")
                    
                    try:
                        await member.send(embed=embed)
                    except:
                        pass  # Ignore if DM fails
                    
                    await member.kick(reason=f"Dashboard moderation by {dashboard_user}: {reason}")
                    result = f"Successfully kicked {member.display_name} from {guild.name}"
                except discord.Forbidden:
                    return web.json_response({'error': 'Insufficient permissions to kick this user'}, status=403)
                except Exception as e:
                    return web.json_response({'error': f'Failed to kick user: {str(e)}'}, status=500)
                    
            elif action == 'ban':
                if not bot_member.guild_permissions.ban_members:
                    return web.json_response({'error': 'Bot lacks ban permissions'}, status=403)
                
                try:
                    # Send DM before banning
                    embed = discord.Embed(
                        title="🔨 Banned from Server",
                        description=f"You have been banned from {guild.name}",
                        color=0xef4444,
                        timestamp=datetime.utcnow()
                    )
                    embed.add_field(name="Reason", value=reason, inline=False)
                    if rule_violations:
                        embed.add_field(name="Rule Violations", value="\n".join(rule_violations), inline=False)
                    embed.add_field(name="Moderator", value=dashboard_user, inline=True)
                    embed.set_footer(text="Monroe Social Club Moderation")
                    
                    try:
                        await member.send(embed=embed)
                    except:
                        pass  # Ignore if DM fails
                    
                    await member.ban(
                        reason=f"Dashboard moderation by {dashboard_user}: {reason}", 
                        delete_message_days=min(delete_days, 7)  # Discord limit
                    )
                    result = f"Successfully banned {member.display_name} from {guild.name}"
                except discord.Forbidden:
                    return web.json_response({'error': 'Insufficient permissions to ban this user'}, status=403)
                except Exception as e:
                    return web.json_response({'error': f'Failed to ban user: {str(e)}'}, status=500)
            
            print(f"Moderation action executed: {action} on {member.display_name} in {guild.name} by {dashboard_user}")
            
            return web.json_response({
                'success': True,
                'message': result,
                'action': action,
                'user': member.display_name,
                'user_id': str(member.id),
                'guild': guild.name,
                'reason': reason,
                'moderator': dashboard_user
            })
            
        except Exception as e:
            print(f"Moderation endpoint error: {str(e)}")
            return web.json_response({'error': f'Internal server error: {str(e)}'}, status=500)

    app.router.add_post('/api/moderation', handle_moderation)

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
