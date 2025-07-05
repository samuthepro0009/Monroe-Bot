import discord
from discord.ext import commands
import os
import json
from datetime import datetime
from aiohttp import web
from aiohttp_jinja2 import setup as jinja2_setup, template
import aiohttp_jinja2
import jinja2
import asyncio
from bot.credentials import credentials_manager

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

API_SECRET = os.getenv('API_SECRET', 'default-secret')

# Channel IDs
ANNOUNCEMENT_CHANNEL_ID = 1353388424295350283
BROADCAST_CHANNELS = [1353393437650718910, 1353395315197218847]

# Load all cogs
async def load_cogs():
    cogs = [
        'bot.automod',
        'bot.admin_logging',
        'bot.moderation',
        'bot.utils',
        'bot.suspicious_activity',
        'bot.announcement_templates',
        'bot.ascii_art',
        'bot.activity_leaderboard',
        'bot.applications',
        'bot.welcome',
        'bot.keep_alive'
    ]

    for cog in cogs:
        try:
            await bot.load_extension(cog)
            print(f'✅ Loaded {cog}')

            # Check if moderation cog loaded correctly
            if cog == 'bot.moderation':
                moderation_cog = bot.get_cog('ModerationCog')
                if moderation_cog:
                    app_commands = getattr(moderation_cog, '__cog_app_commands__', [])
                    print(f'✅ Moderation cog loaded with {len(app_commands)} app commands: {[cmd.name for cmd in app_commands]}')

                    # Verify specific commands exist
                    command_names = [cmd.name for cmd in app_commands]
                    if 'warn' in command_names:
                        print(f'✅ Warn command found and ready')
                    else:
                        print(f'❌ Warn command NOT found in app commands')
                else:
                    print(f'❌ Moderation cog not found after loading')
        except Exception as e:
            print(f'❌ Failed to load {cog}: {e}')
            import traceback
            traceback.print_exc()

# Load cogs immediately when bot starts
async def setup_bot():
    """Setup function to load cogs before starting bot"""
    await load_cogs()

@bot.event
async def on_ready():
    print(f'🌴 {bot.user} has connected to Discord!')
    print(f'🏖️ Connected to {len(bot.guilds)} servers')
    bot.start_time = datetime.utcnow()

    # Wait a moment for cogs to fully initialize (they're already loaded by setup_bot)
    await asyncio.sleep(2)

    # Sync slash commands with better error handling
    try:
        # Clear existing commands first
        bot.tree.clear_commands(guild=None)

        # Copy commands from cogs to the tree
        for cog_name, cog in bot.cogs.items():
            for command in getattr(cog, '__cog_app_commands__', []):
                bot.tree.add_command(command)
                print(f'➕ Added command: {command.name} from {cog_name}')

        # List all registered commands for debugging BEFORE sync
        all_commands = bot.tree.get_commands()
        print(f'📋 Commands ready to sync: {[cmd.name for cmd in all_commands]}')

        # Sync commands globally
        synced = await bot.tree.sync()
        print(f'🔄 Synced {len(synced)} command(s) globally')

        # Verify sync worked
        if len(synced) > 0:
            print(f'✅ Successfully synced commands: {[cmd.name for cmd in synced]}')
        else:
            print('❌ No commands were synced - checking for issues...')

            # Debug: Check individual cogs
            for cog_name, cog in bot.cogs.items():
                cog_commands = getattr(cog, '__cog_app_commands__', [])
                if cog_commands:
                    print(f'🔍 {cog_name} has {len(cog_commands)} commands: {[cmd.name for cmd in cog_commands]}')

    except Exception as e:
        print(f'❌ Failed to sync commands: {e}')
        import traceback
        traceback.print_exc()

    # Generate invite link with proper permissions (now that bot.user is available)
    try:
        permissions = discord.Permissions(
            administrator=True,
            send_messages=True,
            manage_messages=True,
            kick_members=True,
            ban_members=True,
            use_application_commands=True,
            manage_roles=True,
            view_channel=True,
            read_message_history=True
        )

        invite_link = discord.utils.oauth_url(
            client_id=bot.user.id,
            permissions=permissions,
            scopes=('bot', 'applications.commands')
        )

        print(f"🔗 Invite link with proper permissions: {invite_link}")
    except Exception as e:
        print(f"❌ Failed to generate invite link: {e}")

async def start_health_server():
    """Complete API server with all endpoints for Monroe Dashboard"""
    print("🌐 Starting API server...")

    async def check_auth(request):
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer ') or auth[7:] != API_SECRET:
            return web.json_response({'error': 'Unauthorized'}, status=401)
        return None

    async def handle_login(request):
            """Handle dashboard login with username/password"""
            try:
                data = await request.json()
                username = data.get('username', '')
                password = data.get('password', '')

                if not username or not password:
                    return web.json_response({'error': 'Username and password required'}, status=400)

                if credentials_manager.verify_credentials(username, password):
                    print(f"✅ Dashboard login successful for user: {username}")
                    return web.json_response({
                        'success': True,
                        'message': 'Login successful',
                        'token': API_SECRET,  # In production, generate unique tokens
                        'username': username
                    })
                else:
                    print(f"❌ Dashboard login failed for user: {username}")
                    return web.json_response({'error': 'Invalid username or password'}, status=401)

            except Exception as e:
                print(f"❌ Dashboard login error: {str(e)}")
                return web.json_response({'error': 'Login system error'}, status=500)

    async def handle_health(request):
        return web.Response(text="Bot is running!")

    @template('index.html')
    async def handle_index(request):
        """Serve the main web interface"""
        bot_avatar_url = str(bot.user.avatar.url) if bot.user and bot.user.avatar else "https://cdn.discordapp.com/embed/avatars/0.png"
        return {
            'bot_avatar': bot_avatar_url
        }

    async def handle_status(request):
        # Allow public access to status for the web interface
        # Only require auth if Authorization header is present but invalid
        auth_header = request.headers.get('Authorization', '')
        if auth_header and not (auth_header.startswith('Bearer ') and auth_header[7:] == API_SECRET):
            return web.json_response({'error': 'Unauthorized'}, status=401)

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
                    # Send DM to user
                    dm_embed = discord.Embed(
                        title="⚠️ Warning - Monroe Social Club",
                        description=f"You have been warned in {guild.name}",
                        color=0xfbbf24,
                        timestamp=datetime.utcnow()
                    )
                    dm_embed.add_field(name="Reason", value=reason, inline=False)
                    dm_embed.add_field(name="Staff Member", value=dashboard_user, inline=True)
                    dm_embed.set_footer(text="Please follow server rules to avoid further action.")

                    await member.send(embed=dm_embed)
                    dm_result = "DM sent"
                except:
                    dm_result = "DM failed"

                # Log to moderation channel
                try:
                    from bot.config import Config
                    from bot.embeds import create_moderation_embed

                    # Create a mock staff member object for the embed
                    class MockUser:
                        def __init__(self, name):
                            self.mention = f"@{name}"
                            self.name = name
                            self.discriminator = "0000"
                            self.id = "dashboard"
                            self.avatar = None
                            self.default_avatar = type('obj', (object,), {'url': 'https://cdn.discordapp.com/embed/avatars/0.png'})()

                    mock_staff = MockUser(dashboard_user)

                    # Create moderation embed
                    log_embed = create_moderation_embed(
                        action="Warning",
                        target=member,
                        staff_member=mock_staff,
                        reason=reason,
                        color=Config.COLORS["warning"]
                    )

                    # Send to both moderation log channels
                    log_channels = [
                        bot.get_channel(1353388676981456917),
                        bot.get_channel(1387524238117830776)
                    ]

                    logged_count = 0
                    for log_channel in log_channels:
                        if log_channel:
                            try:
                                await log_channel.send(embed=log_embed)
                                logged_count += 1
                            except Exception as e:
                                print(f"Failed to send dashboard log to channel {log_channel.id}: {e}")

                    log_result = f"logged to {logged_count} channels" if logged_count > 0 else "log failed"

                    result = f"Warning issued to {member.display_name} ({dm_result}, {log_result})"
                except Exception as e:
                    result = f"Warning issued to {member.display_name} ({dm_result}, log failed: {str(e)})"

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

    # Setup Jinja2 templates
    jinja2_setup(app, loader=jinja2.FileSystemLoader('templates'))

    app.router.add_get('/', handle_index)
    app.router.add_get('/health', handle_health)
    app.router.add_get('/api/status', handle_status)
    app.router.add_post('/api/login', handle_login)
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

@bot.command(name='checkperms')
async def check_permissions(ctx):
    """Check bot permissions (admin only)"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Solo gli amministratori possono usare questo comando.")
        return

    bot_member = ctx.guild.get_member(bot.user.id)
    if not bot_member:
        await ctx.send("❌ Impossibile trovare il bot nel server.")
        return

    perms = bot_member.guild_permissions

    embed = discord.Embed(
        title="🔑 Permessi Bot",
        description="Controllo dei permessi del bot",
        color=0x00ff00 if perms.administrator else 0xff0000
    )

    critical_perms = {
        "Administrator": perms.administrator,
        "Use App Commands": perms.use_application_commands,
        "Send Messages": perms.send_messages,
        "Manage Messages": perms.manage_messages,
        "Kick Members": perms.kick_members,
        "Ban Members": perms.ban_members,
        "Manage Roles": perms.manage_roles,
        "View Channels": perms.view_channel,
        "Read Message History": perms.read_message_history
    }

    for perm_name, has_perm in critical_perms.items():
        embed.add_field(
            name=perm_name,
            value="✅ Sì" if has_perm else "❌ No",
            inline=True
        )

    # Check if bot was invited with proper scopes
    embed.add_field(
        name="💡 Suggerimento",
        value="Se i comandi slash non funzionano, il bot potrebbe essere stato invitato senza lo scope `applications.commands`",
        inline=False
    )

    await ctx.send(embed=embed)

@bot.command(name='sync')
async def sync(ctx):
    """Force sync slash commands (admin only)"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Solo gli amministratori possono usare questo comando.")
        return

    try:
        # Clear and sync commands
        bot.tree.clear_commands(guild=None)
        synced = await bot.tree.sync()

        # Get all registered commands
        all_commands = bot.tree.get_commands()
        command_names = [cmd.name for cmd in all_commands]

        embed = discord.Embed(
            title="🔄 Comandi Sincronizzati",
            description=f"Sincronizzati {len(synced)} comandi slash",
            color=0x00ff00
        )

        if command_names:
            embed.add_field(
                name="📋 Comandi Registrati",
                value=", ".join(command_names),
                inline=False
            )

        # Check bot permissions
        bot_member = ctx.guild.get_member(bot.user.id)
        if bot_member:
            perms = bot_member.guild_permissions
            embed.add_field(
                name="🔑 Permessi Bot",
                value=f"Admin: {perms.administrator}\nUse App Commands: {perms.use_application_commands}\nManage Messages: {perms.manage_messages}",
                inline=False
            )

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"❌ Errore nella sincronizzazione: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Main function to start both bot and server"""
    print("🌴 Monroe Social Club Bot - Starting...")

    # Start the health server
    await start_health_server()

    # Setup bot with cogs loaded
    await setup_bot()

    # Start the bot
    print("🔌 Connecting to Discord...")
    await bot.start(os.getenv('DISCORD_TOKEN'))

# Run the bot
if __name__ == "__main__":
    asyncio.run(main())