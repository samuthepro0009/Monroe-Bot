
import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timedelta
from collections import defaultdict, deque
import re
from bot.config import Config

class SuspiciousActivityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # Tracking dictionaries
        self.message_frequency = defaultdict(deque)  # User ID -> timestamps
        self.channel_hopping = defaultdict(deque)    # User ID -> channel IDs
        self.failed_commands = defaultdict(int)      # User ID -> failed attempts
        self.reaction_spam = defaultdict(deque)      # User ID -> reaction timestamps
        self.suspicious_patterns = defaultdict(int) # User ID -> pattern count
        self.voice_hopping = defaultdict(deque)      # User ID -> voice channel switches
        
        # Suspicious activity thresholds
        self.SPAM_THRESHOLD = 8  # messages per minute
        self.CHANNEL_HOP_THRESHOLD = 5  # channels in 2 minutes
        self.FAILED_COMMAND_THRESHOLD = 10  # failed commands per hour
        self.REACTION_SPAM_THRESHOLD = 15  # reactions per minute
        self.VOICE_HOP_THRESHOLD = 4  # voice channels in 5 minutes
        
        # Suspicious patterns
        self.suspicious_keywords = [
            'raid', 'nuke', 'destroy server', 'delete everything', 'crash bot',
            'mass ban', 'exploit', 'hack', 'ddos', 'doxx', 'token grab',
            'server crash', 'mass kick', 'admin panel', 'backdoor'
        ]
        
        # Cleanup task
        self.cleanup_task = asyncio.create_task(self.cleanup_old_data())

    def cog_unload(self):
        self.cleanup_task.cancel()

    async def cleanup_old_data(self):
        """Clean up old tracking data every 10 minutes"""
        while True:
            try:
                await asyncio.sleep(600)  # 10 minutes
                current_time = datetime.utcnow()
                
                # Clean message frequency data (older than 5 minutes)
                for user_id in list(self.message_frequency.keys()):
                    self.message_frequency[user_id] = deque([
                        timestamp for timestamp in self.message_frequency[user_id]
                        if current_time - timestamp < timedelta(minutes=5)
                    ])
                    if not self.message_frequency[user_id]:
                        del self.message_frequency[user_id]
                
                # Clean channel hopping data (older than 10 minutes)
                for user_id in list(self.channel_hopping.keys()):
                    self.channel_hopping[user_id] = deque([
                        (timestamp, channel_id) for timestamp, channel_id in self.channel_hopping[user_id]
                        if current_time - timestamp < timedelta(minutes=10)
                    ])
                    if not self.channel_hopping[user_id]:
                        del self.channel_hopping[user_id]
                
                # Reset failed commands counter every hour
                if current_time.minute == 0:
                    self.failed_commands.clear()
                
                print("🧹 Cleaned up suspicious activity tracking data")
                
            except Exception as e:
                print(f"❌ Error in cleanup task: {e}")

    async def log_suspicious_activity(self, user, activity_type, description, severity="medium", additional_info=None):
        """Log suspicious activity to the admin logs channel"""
        log_channel = self.bot.get_channel(Config.ADMIN_LOG_CHANNEL)
        if not log_channel:
            return

        # Severity colors
        severity_colors = {
            "low": 0xFFFF00,      # Yellow
            "medium": 0xFF8C00,   # Orange  
            "high": 0xFF0000,     # Red
            "critical": 0x8B0000  # Dark Red
        }
        
        severity_emojis = {
            "low": "🟡",
            "medium": "🟠", 
            "high": "🔴",
            "critical": "⚠️"
        }

        embed = discord.Embed(
            title=f"{severity_emojis.get(severity, '🔍')} Suspicious Activity Detected",
            description=f"**Activity Type:** {activity_type}\n**Description:** {description}",
            color=severity_colors.get(severity, 0xFF8C00),
            timestamp=discord.utils.utcnow()
        )

        # User information
        embed.add_field(
            name="👤 User Information", 
            value=f"**User:** {user.mention}\n**Username:** {user.name}#{user.discriminator}\n**User ID:** {user.id}\n**Account Age:** {(discord.utils.utcnow() - user.created_at).days} days",
            inline=False
        )

        # Server information
        if hasattr(user, 'joined_at') and user.joined_at:
            embed.add_field(
                name="🏰 Server Information",
                value=f"**Joined Server:** <t:{int(user.joined_at.timestamp())}:R>\n**Top Role:** {user.top_role.mention}\n**Role Count:** {len(user.roles) - 1}",
                inline=True
            )

        # Additional information
        if additional_info:
            embed.add_field(
                name="ℹ️ Additional Details",
                value=additional_info,
                inline=False
            )

        # Severity level
        embed.add_field(
            name="⚠️ Severity Level",
            value=f"**{severity.upper()}**",
            inline=True
        )

        # Set user avatar
        embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
        embed.set_footer(text="Monroe Social Club - Suspicious Activity Monitor", icon_url=self.bot.user.avatar.url)

        try:
            await log_channel.send(embed=embed)
        except Exception as e:
            print(f"Failed to send suspicious activity log: {e}")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Monitor messages for suspicious activity"""
        if message.author.bot or not message.guild:
            return

        user_id = message.author.id
        current_time = datetime.utcnow()

        # Track message frequency (spam detection)
        self.message_frequency[user_id].append(current_time)
        
        # Remove messages older than 1 minute
        while (self.message_frequency[user_id] and 
               current_time - self.message_frequency[user_id][0] > timedelta(minutes=1)):
            self.message_frequency[user_id].popleft()

        # Check for spam
        if len(self.message_frequency[user_id]) >= self.SPAM_THRESHOLD:
            await self.log_suspicious_activity(
                message.author,
                "Message Spam",
                f"Sent {len(self.message_frequency[user_id])} messages in 1 minute",
                severity="high",
                additional_info=f"**Channel:** {message.channel.mention}\n**Threshold:** {self.SPAM_THRESHOLD} messages/minute"
            )

        # Track channel hopping
        self.channel_hopping[user_id].append((current_time, message.channel.id))
        
        # Remove entries older than 2 minutes
        while (self.channel_hopping[user_id] and 
               current_time - self.channel_hopping[user_id][0][0] > timedelta(minutes=2)):
            self.channel_hopping[user_id].popleft()

        # Check for channel hopping
        unique_channels = len(set(channel_id for _, channel_id in self.channel_hopping[user_id]))
        if unique_channels >= self.CHANNEL_HOP_THRESHOLD:
            channels_list = [f"<#{channel_id}>" for _, channel_id in list(self.channel_hopping[user_id])[-5:]]
            await self.log_suspicious_activity(
                message.author,
                "Channel Hopping",
                f"Posted in {unique_channels} different channels within 2 minutes",
                severity="medium",
                additional_info=f"**Recent Channels:** {', '.join(channels_list)}\n**Threshold:** {self.CHANNEL_HOP_THRESHOLD} channels"
            )

        # Check for suspicious keywords
        message_lower = message.content.lower()
        found_keywords = [keyword for keyword in self.suspicious_keywords if keyword in message_lower]
        if found_keywords:
            self.suspicious_patterns[user_id] += len(found_keywords)
            await self.log_suspicious_activity(
                message.author,
                "Suspicious Keywords",
                f"Used potentially harmful keywords in message",
                severity="high",
                additional_info=f"**Keywords Found:** {', '.join(found_keywords)}\n**Message:** `{message.content[:200]}{'...' if len(message.content) > 200 else ''}`\n**Channel:** {message.channel.mention}"
            )

        # Check for excessive mentions
        if len(message.mentions) >= 5:
            await self.log_suspicious_activity(
                message.author,
                "Mass Mentions",
                f"Mentioned {len(message.mentions)} users in a single message",
                severity="medium",
                additional_info=f"**Mentions:** {', '.join([user.mention for user in message.mentions[:10]])}\n**Channel:** {message.channel.mention}"
            )

        # Check for invite links (unless in designated channels)
        invite_pattern = r'(discord\.gg/|discordapp\.com/invite/|discord\.com/invite/)'
        if re.search(invite_pattern, message.content, re.IGNORECASE):
            await self.log_suspicious_activity(
                message.author,
                "Invite Link Posted",
                "Posted Discord invite link",
                severity="medium",
                additional_info=f"**Channel:** {message.channel.mention}\n**Message:** `{message.content[:200]}{'...' if len(message.content) > 200 else ''}`"
            )

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """Monitor reaction spam"""
        if user.bot:
            return

        user_id = user.id
        current_time = datetime.utcnow()

        # Track reaction frequency
        self.reaction_spam[user_id].append(current_time)
        
        # Remove reactions older than 1 minute
        while (self.reaction_spam[user_id] and 
               current_time - self.reaction_spam[user_id][0] > timedelta(minutes=1)):
            self.reaction_spam[user_id].popleft()

        # Check for reaction spam
        if len(self.reaction_spam[user_id]) >= self.REACTION_SPAM_THRESHOLD:
            await self.log_suspicious_activity(
                user,
                "Reaction Spam",
                f"Added {len(self.reaction_spam[user_id])} reactions in 1 minute",
                severity="medium",
                additional_info=f"**Threshold:** {self.REACTION_SPAM_THRESHOLD} reactions/minute\n**Channel:** {reaction.message.channel.mention}"
            )

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Monitor voice channel hopping"""
        if member.bot:
            return

        user_id = member.id
        current_time = datetime.utcnow()

        # Only track if user switched channels (not just joined/left)
        if before.channel and after.channel and before.channel != after.channel:
            self.voice_hopping[user_id].append((current_time, after.channel.id))
            
            # Remove entries older than 5 minutes
            while (self.voice_hopping[user_id] and 
                   current_time - self.voice_hopping[user_id][0][0] > timedelta(minutes=5)):
                self.voice_hopping[user_id].popleft()

            # Check for voice hopping
            if len(self.voice_hopping[user_id]) >= self.VOICE_HOP_THRESHOLD:
                channels_list = [f"<#{channel_id}>" for _, channel_id in list(self.voice_hopping[user_id])[-3:]]
                await self.log_suspicious_activity(
                    member,
                    "Voice Channel Hopping",
                    f"Switched between {len(self.voice_hopping[user_id])} voice channels in 5 minutes",
                    severity="low",
                    additional_info=f"**Recent Channels:** {', '.join(channels_list)}\n**Threshold:** {self.VOICE_HOP_THRESHOLD} switches"
                )

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Monitor for suspicious new accounts"""
        account_age = (discord.utils.utcnow() - member.created_at).days
        
        # Flag very new accounts
        if account_age < 1:
            await self.log_suspicious_activity(
                member,
                "New Account Joined",
                f"Account created {account_age} day(s) ago",
                severity="low",
                additional_info=f"**Account Created:** <t:{int(member.created_at.timestamp())}:R>\n**Default Avatar:** {'Yes' if not member.avatar else 'No'}"
            )
        
        # Flag accounts with suspicious usernames
        suspicious_name_patterns = [
            r'[0-9]{4,}',  # Many numbers
            r'^[a-z]+[0-9]{4,}$',  # Word followed by many numbers
            r'discord|admin|mod|staff|owner|bot',  # Staff impersonation
        ]
        
        for pattern in suspicious_name_patterns:
            if re.search(pattern, member.name.lower()):
                await self.log_suspicious_activity(
                    member,
                    "Suspicious Username",
                    f"Username matches suspicious pattern: {pattern}",
                    severity="low",
                    additional_info=f"**Username:** {member.name}\n**Account Age:** {account_age} days"
                )
                break

    @commands.Cog.listener()
    async def on_app_command_error(self, interaction, error):
        """Track failed command attempts"""
        user_id = interaction.user.id
        self.failed_commands[user_id] += 1
        
        if self.failed_commands[user_id] >= self.FAILED_COMMAND_THRESHOLD:
            await self.log_suspicious_activity(
                interaction.user,
                "Excessive Failed Commands",
                f"Failed {self.failed_commands[user_id]} commands in the past hour",
                severity="medium",
                additional_info=f"**Latest Error:** {type(error).__name__}\n**Command:** /{interaction.command.name if interaction.command else 'Unknown'}\n**Threshold:** {self.FAILED_COMMAND_THRESHOLD} failures/hour"
            )

async def setup(bot):
    await bot.add_cog(SuspiciousActivityCog(bot))
