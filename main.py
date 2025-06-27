"""
Monroe Bot API Integration - COMPLETE WORKING VERSION
Replace your current health server with this code in your Monroe Bot's main.py

CRITICAL: Your Monroe Bot currently only has /health endpoint working.
The dashboard shows 500 errors because /api/status, /api/broadcast, etc. don't exist yet.

EXACT STEPS TO FIX:
1. In your main.py, find your current health server code (probably around line 100-150)
2. Replace it ENTIRELY with the start_health_server() function below
3. Add bot.start_time = datetime.utcnow() to your on_ready event
4. Restart your bot - all dashboard features will work immediately

Current Status: /health works ✓, /api/* endpoints missing ✗
After Fix: All endpoints work ✓, dashboard commands execute ✓
"""

# ADD THESE IMPORTS TO TOP OF YOUR main.py
import json
import os
from datetime import datetime
from aiohttp import web
import asyncio
import discord
from discord.ext import commands

# COPY ALL FUNCTIONS BELOW INTO YOUR main.py

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
    """REPLACE YOUR CURRENT HEALTH SERVER WITH THIS FUNCTION"""
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
    port = int(os.getenv('PORT', 8000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Monroe Bot API server started on port {port}")

# MODIFY YOUR on_ready EVENT TO INCLUDE THIS LINE:
# Add this line to your existing on_ready function:
# bot.start_time = datetime.utcnow()

# REPLACE YOUR CURRENT SERVER STARTUP WITH:
# asyncio.create_task(start_api_server())

"""
COMPLETE SETUP CHECKLIST:
□ Added imports to top of main.py
□ Copied all functions above into main.py
□ Added bot.start_time = datetime.utcnow() to on_ready event
□ Replaced health server startup with: asyncio.create_task(start_api_server())
□ Restarted Monroe Bot
□ Dashboard now shows real server counts and commands work
"""
