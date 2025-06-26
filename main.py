
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monroe Bot - Complete Discord Bot with Dashboard API Integration
"""

import discord
from discord.ext import commands
import asyncio
import logging
import os
import json
from datetime import datetime
from aiohttp import web

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = os.getenv('BOT_PREFIX', '!')
API_SECRET = os.getenv('API_SECRET', 'default-secret')

if not TOKEN:
    logger.error("DISCORD_TOKEN environment variable is required!")
    exit(1)

# Set up bot intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

# Create bot instance
bot = commands.Bot(
    command_prefix=PREFIX,
    intents=intents,
    description="Monroe Bot - Discord Administration Bot with Web Dashboard"
)

# Bot startup time for uptime tracking
bot.start_time = None

@bot.event
async def on_ready():
    """Event triggered when bot is ready"""
    bot.start_time = datetime.utcnow()
    logger.info(f'{bot.user} has connected to Discord!')
    logger.info(f'Bot ID: {bot.user.id}')
    logger.info(f'Connected to {len(bot.guilds)} guilds')
    
    # Set bot status
    activity = discord.Activity(type=discord.ActivityType.watching, name="Monroe Social Club")
    await bot.change_presence(activity=activity, status=discord.Status.online)
    
    # Start API server
    asyncio.create_task(start_api_server())

@bot.event
async def on_guild_join(guild):
    """Event when bot joins a new guild"""
    logger.info(f'Joined new guild: {guild.name} (ID: {guild.id})')

@bot.event
async def on_guild_remove(guild):
    """Event when bot leaves a guild"""
    logger.info(f'Left guild: {guild.name} (ID: {guild.id})')

@bot.event
async def on_command_error(ctx, error):
    """Global error handler"""
    if isinstance(error, commands.CommandNotFound):
        return  # Ignore command not found errors
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command!")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("❌ I don't have the required permissions to execute this command!")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("❌ Member not found!")
    else:
        logger.error(f'Command error in {ctx.command}: {error}')
        await ctx.send("❌ An error occurred while processing the command.")

# Basic Commands
@bot.command(name='ping')
async def ping(ctx):
    """Check bot latency"""
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Bot latency: {latency}ms",
        color=0x7c3aed
    )
    await ctx.send(embed=embed)

@bot.command(name='info')
async def info(ctx):
    """Bot information"""
    uptime_seconds = (datetime.utcnow() - bot.start_time).total_seconds() if bot.start_time else 0
    uptime_display = f"{int(uptime_seconds // 3600)}h {int((uptime_seconds % 3600) // 60)}m"
    
    embed = discord.Embed(
        title="🤖 Monroe Bot Info",
        description="Discord Administration Bot with Web Dashboard",
        color=0x7c3aed,
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="📊 Servers", value=len(bot.guilds), inline=True)
    embed.add_field(name="👥 Users", value=sum(g.member_count or 0 for g in bot.guilds), inline=True)
    embed.add_field(name="⏱️ Uptime", value=uptime_display, inline=True)
    embed.add_field(name="🏓 Latency", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.set_footer(text="Monroe Social Club", icon_url=bot.user.avatar.url if bot.user.avatar else None)
    await ctx.send(embed=embed)

@bot.command(name='servers')
@commands.has_permissions(administrator=True)
async def servers(ctx):
    """List all servers (Admin only)"""
    if len(bot.guilds) == 0:
        await ctx.send("❌ Not connected to any servers.")
        return
    
    embed = discord.Embed(
        title="📋 Server List",
        description=f"Connected to {len(bot.guilds)} servers:",
        color=0x7c3aed
    )
    
    for guild in bot.guilds[:10]:  # Limit to first 10 servers
        embed.add_field(
            name=f"🏠 {guild.name}",
            value=f"Members: {guild.member_count}\nID: {guild.id}",
            inline=True
        )
    
    if len(bot.guilds) > 10:
        embed.set_footer(text=f"And {len(bot.guilds) - 10} more servers...")
    
    await ctx.send(embed=embed)

# Moderation Commands
@bot.command(name='warn')
@commands.has_permissions(kick_members=True)
async def warn(ctx, member: discord.Member, *, reason="No reason provided"):
    """Warn a member"""
    try:
        embed = discord.Embed(
            title="⚠️ Warning",
            description=f"You were warned in {ctx.guild.name}",
            color=0xfbbf24,
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
        
        await member.send(embed=embed)
        
        # Log in current channel
        log_embed = discord.Embed(
            title="✅ Warning Issued",
            description=f"{member.mention} has been warned",
            color=0x10b981
        )
        log_embed.add_field(name="Reason", value=reason, inline=False)
        log_embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
        await ctx.send(embed=log_embed)
        
    except discord.Forbidden:
        await ctx.send(f"✅ {member.mention} has been warned (couldn't send DM)")

@bot.command(name='kick')
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    """Kick a member"""
    try:
        # Send DM before kicking
        embed = discord.Embed(
            title="👢 Kicked",
            description=f"You were kicked from {ctx.guild.name}",
            color=0xf97316,
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
        
        try:
            await member.send(embed=embed)
        except:
            pass  # Ignore if DM fails
        
        await member.kick(reason=f"Kicked by {ctx.author}: {reason}")
        
        # Log in current channel
        log_embed = discord.Embed(
            title="✅ Member Kicked",
            description=f"{member} has been kicked",
            color=0x10b981
        )
        log_embed.add_field(name="Reason", value=reason, inline=False)
        log_embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
        await ctx.send(embed=log_embed)
        
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to kick this member.")

@bot.command(name='ban')
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
    """Ban a member"""
    try:
        # Send DM before banning
        embed = discord.Embed(
            title="🔨 Banned",
            description=f"You were banned from {ctx.guild.name}",
            color=0xef4444,
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
        
        try:
            await member.send(embed=embed)
        except:
            pass  # Ignore if DM fails
        
        await member.ban(reason=f"Banned by {ctx.author}: {reason}")
        
        # Log in current channel
        log_embed = discord.Embed(
            title="✅ Member Banned",
            description=f"{member} has been banned",
            color=0x10b981
        )
        log_embed.add_field(name="Reason", value=reason, inline=False)
        log_embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
        await ctx.send(embed=log_embed)
        
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to ban this member.")

# API Server for Dashboard Integration
async def start_api_server():
    """Start the API server for dashboard integration"""
    
    async def check_auth(request):
        """Simple authentication check"""
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
            guild_count = len(bot.guilds)
            member_count = sum(g.member_count or 0 for g in bot.guilds)
            uptime_seconds = (datetime.utcnow() - bot.start_time).total_seconds() if bot.start_time else 0
            uptime_display = f"{int(uptime_seconds // 3600)}h {int((uptime_seconds % 3600) // 60)}m"
            
            guilds_info = []
            for guild in bot.guilds[:5]:  # Limit to first 5 guilds
                guilds_info.append({
                    "id": str(guild.id),
                    "name": guild.name,
                    "memberCount": guild.member_count or 0
                })
            
            return web.json_response({
                "online": True,
                "serverCount": guild_count,
                "userCount": member_count,
                "uptime": uptime_display,
                "lastSeen": datetime.utcnow().isoformat(),
                "guilds": guilds_info
            })
        except Exception as e:
            logger.error(f"Status endpoint error: {e}")
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
            message = data.get('message', '').strip()
            
            if not message:
                return web.json_response({'error': 'Message required'}, status=400)
            
            sent_count = 0
            failed_count = 0
            
            embed = discord.Embed(
                title="📢 Monroe Bot Broadcast",
                description=message,
                color=0x7c3aed,
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text="Sent from Monroe Dashboard")
            embed.set_author(name="Monroe Social Club")
            
            for guild in bot.guilds:
                try:
                    # Find best channel to send to
                    channel = None
                    
                    # Try to find general/announcements channel
                    for ch_name in ['general', 'announcements', 'chat', 'main']:
                        channel = discord.utils.get(guild.text_channels, name=ch_name)
                        if channel and channel.permissions_for(guild.me).send_messages:
                            break
                    
                    # Fallback to first available channel
                    if not channel:
                        for ch in guild.text_channels:
                            if ch.permissions_for(guild.me).send_messages:
                                channel = ch
                                break
                    
                    if channel:
                        await channel.send(embed=embed)
                        sent_count += 1
                        logger.info(f"Broadcast sent to {guild.name} (#{channel.name})")
                    else:
                        failed_count += 1
                        logger.warning(f"No suitable channel found in {guild.name}")
                        
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Failed to send broadcast to {guild.name}: {e}")
            
            return web.json_response({
                'success': True,
                'sent_to': sent_count,
                'failed': failed_count,
                'message': f'Broadcast sent to {sent_count} servers, {failed_count} failed'
            })
            
        except Exception as e:
            logger.error(f"Broadcast endpoint error: {e}")
            return web.json_response({'error': str(e)}, status=500)

    async def handle_qotd(request):
        """Question of the Day endpoint"""
        auth_error = await check_auth(request)
        if auth_error:
            return auth_error
        
        try:
            data = await request.json()
            question = data.get('question', '').strip()
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
            embed.set_footer(text="Answer in the comments below!")
            embed.set_author(name="Monroe Social Club")
            
            for guild in bot.guilds:
                try:
                    # Look for QOTD specific channels first
                    channel = None
                    for ch_name in ['qotd', 'question-of-the-day', 'daily-question', 'general', 'chat']:
                        channel = discord.utils.get(guild.text_channels, name=ch_name)
                        if channel and channel.permissions_for(guild.me).send_messages:
                            break
                    
                    # Fallback to first available channel
                    if not channel:
                        for ch in guild.text_channels:
                            if ch.permissions_for(guild.me).send_messages:
                                channel = ch
                                break
                    
                    if channel:
                        message = await channel.send(embed=embed)
                        # Add reaction for engagement
                        try:
                            await message.add_reaction('🤔')
                        except:
                            pass
                        sent_count += 1
                        logger.info(f"QOTD sent to {guild.name} (#{channel.name})")
                    else:
                        failed_count += 1
                        
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Failed to send QOTD to {guild.name}: {e}")
            
            return web.json_response({
                'success': True,
                'sent_to': sent_count,
                'failed': failed_count,
                'message': f'QOTD sent to {sent_count} servers, {failed_count} failed'
            })
            
        except Exception as e:
            logger.error(f"QOTD endpoint error: {e}")
            return web.json_response({'error': str(e)}, status=500)

    async def handle_announcement(request):
        """Announcement endpoint"""
        auth_error = await check_auth(request)
        if auth_error:
            return auth_error
        
        try:
            data = await request.json()
            title = data.get('title', '').strip()
            content = data.get('content', '').strip()
            
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
                    # Look for announcement channels first
                    channel = None
                    for ch_name in ['announcements', 'news', 'updates', 'general', 'main']:
                        channel = discord.utils.get(guild.text_channels, name=ch_name)
                        if channel and channel.permissions_for(guild.me).send_messages:
                            break
                    
                    # Fallback to first available channel
                    if not channel:
                        for ch in guild.text_channels:
                            if ch.permissions_for(guild.me).send_messages:
                                channel = ch
                                break
                    
                    if channel:
                        await channel.send(embed=embed)
                        sent_count += 1
                        logger.info(f"Announcement sent to {guild.name} (#{channel.name})")
                    else:
                        failed_count += 1
                        
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Failed to send announcement to {guild.name}: {e}")
            
            return web.json_response({
                'success': True,
                'sent_to': sent_count,
                'failed': failed_count,
                'message': f'Announcement sent to {sent_count} servers, {failed_count} failed'
            })
            
        except Exception as e:
            logger.error(f"Announcement endpoint error: {e}")
            return web.json_response({'error': str(e)}, status=500)

    async def handle_moderation(request):
        """Moderation endpoint"""
        auth_error = await check_auth(request)
        if auth_error:
            return auth_error
        
        try:
            data = await request.json()
            action = data.get('action', '').lower()
            user_id = data.get('user_id', '')
            reason = data.get('reason', 'No reason provided')
            guild_id = data.get('guild_id')  # Optional guild ID
            
            if not action or not user_id:
                return web.json_response({'error': 'Action and user_id required'}, status=400)
            
            if action not in ['warn', 'kick', 'ban']:
                return web.json_response({'error': 'Invalid action. Must be warn, kick, or ban'}, status=400)
            
            # Select guild
            if guild_id:
                guild = bot.get_guild(int(guild_id))
                if not guild:
                    return web.json_response({'error': 'Guild not found'}, status=404)
            else:
                guild = bot.guilds[0] if bot.guilds else None
                if not guild:
                    return web.json_response({'error': 'No guild available'}, status=404)
            
            # Get member
            try:
                member = await guild.fetch_member(int(user_id))
            except:
                return web.json_response({'error': 'User not found in guild'}, status=404)
            
            # Execute moderation action
            result = ""
            
            if action == 'warn':
                try:
                    embed = discord.Embed(
                        title="⚠️ Warning",
                        description=f"You were warned in {guild.name}",
                        color=0xfbbf24,
                        timestamp=datetime.utcnow()
                    )
                    embed.add_field(name="Reason", value=reason, inline=False)
                    embed.add_field(name="Server", value=guild.name, inline=True)
                    
                    await member.send(embed=embed)
                    result = f"Warning sent to {member.display_name}"
                except:
                    result = f"Warning issued to {member.display_name} (DM failed)"
                    
            elif action == 'kick':
                try:
                    # Send DM before kicking
                    embed = discord.Embed(
                        title="👢 Kicked",
                        description=f"You were kicked from {guild.name}",
                        color=0xf97316,
                        timestamp=datetime.utcnow()
                    )
                    embed.add_field(name="Reason", value=reason, inline=False)
                    
                    try:
                        await member.send(embed=embed)
                    except:
                        pass
                    
                    await member.kick(reason=f"Dashboard moderation: {reason}")
                    result = f"Kicked {member.display_name} from {guild.name}"
                except discord.Forbidden:
                    return web.json_response({'error': 'Insufficient permissions to kick user'}, status=403)
                    
            elif action == 'ban':
                try:
                    # Send DM before banning
                    embed = discord.Embed(
                        title="🔨 Banned",
                        description=f"You were banned from {guild.name}",
                        color=0xef4444,
                        timestamp=datetime.utcnow()
                    )
                    embed.add_field(name="Reason", value=reason, inline=False)
                    
                    try:
                        await member.send(embed=embed)
                    except:
                        pass
                    
                    await member.ban(reason=f"Dashboard moderation: {reason}")
                    result = f"Banned {member.display_name} from {guild.name}"
                except discord.Forbidden:
                    return web.json_response({'error': 'Insufficient permissions to ban user'}, status=403)
            
            logger.info(f"Moderation action executed: {action} on {member.display_name} in {guild.name}")
            
            return web.json_response({
                'success': True,
                'message': result,
                'action': action,
                'user': member.display_name,
                'guild': guild.name
            })
            
        except Exception as e:
            logger.error(f"Moderation endpoint error: {e}")
            return web.json_response({'error': str(e)}, status=500)

    # Create web application
    app = web.Application()
    
    # Health endpoint (no auth required)
    app.router.add_get('/health', lambda req: web.Response(text="Bot is running!"))
    app.router.add_get('/', lambda req: web.Response(text="Monroe Bot API Server - All endpoints active"))
    
    # API endpoints (auth required)
    app.router.add_get('/api/status', handle_status)
    app.router.add_post('/api/broadcast', handle_broadcast)
    app.router.add_post('/api/qotd', handle_qotd)
    app.router.add_post('/api/announcement', handle_announcement)
    app.router.add_post('/api/moderation', handle_moderation)
    
    # Start server on 0.0.0.0 to make it accessible
    port = int(os.getenv('PORT', 3000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    logger.info(f"Monroe Bot API server started on 0.0.0.0:{port}")
    logger.info("Available endpoints:")
    logger.info("  GET  /health")
    logger.info("  GET  /api/status")
    logger.info("  POST /api/broadcast")
    logger.info("  POST /api/qotd")
    logger.info("  POST /api/announcement")
    logger.info("  POST /api/moderation")

# Main execution
if __name__ == "__main__":
    try:
        logger.info("Starting Monroe Bot...")
        bot.run(TOKEN)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
