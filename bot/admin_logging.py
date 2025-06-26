import discord
from discord.ext import commands
from bot.config import Config
import datetime

class AdminLogging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def send_admin_log(self, member, action, description, message_link=None, color=None, additional_info=None):
        """Send a formatted log message to the admin logging channel"""
        channel = self.bot.get_channel(Config.ADMIN_LOG_CHANNEL)
        if not channel:
            return
        
        embed = discord.Embed(
            title=f"📋 {action}",
            description=description,
            color=color or Config.COLORS["info"],
            timestamp=discord.utils.utcnow()
        )
        
        # Add member info
        embed.add_field(
            name="👤 Member",
            value=f"{member.mention}\n`{member.name}` (ID: {member.id})",
            inline=True
        )
        
        # Add message link if provided
        if message_link:
            embed.add_field(
                name="🔗 Message Link",
                value=f"[Jump to message]({message_link})",
                inline=True
            )
        
        # Add additional info if provided
        if additional_info:
            embed.add_field(
                name="ℹ️ Details",
                value=additional_info,
                inline=False
            )
        
        # Set member's avatar as thumbnail
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        else:
            embed.set_thumbnail(url=member.default_avatar.url)
        
        embed.set_footer(text="Monroe Social Club - Admin Logging", icon_url=self.bot.user.avatar.url)
        
        try:
            await channel.send(embed=embed)
        except Exception as e:
            print(f"Failed to send admin log: {e}")
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Log when a member joins the server"""
        await self.send_admin_log(
            member=member,
            action="Member Joined",
            description=f"{member.mention} joined the server",
            color=Config.LOG_COLORS["member_join"],
            additional_info=f"Account created: {member.created_at.strftime('%m/%d/%Y %H:%M')}"
        )
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Log when a member leaves the server"""
        await self.send_admin_log(
            member=member,
            action="Member Left",
            description=f"{member.name} left the server",
            color=Config.LOG_COLORS["member_leave"],
            additional_info=f"Time in server: {(discord.utils.utcnow() - member.joined_at).days if member.joined_at else 'Unknown'} days"
        )
    
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        """Log when a member is banned"""
        await self.send_admin_log(
            member=user,
            action="Member Banned",
            description=f"{user.name} was banned from the server",
            color=Config.LOG_COLORS["member_ban"]
        )
    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """Log when a message is deleted"""
        if message.author.bot:
            return  # Ignore bot messages
        
        message_link = f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}"
        content_preview = message.content[:100] + "..." if len(message.content) > 100 else message.content
        
        await self.send_admin_log(
            member=message.author,
            action="Message Deleted",
            description=f"Message deleted in {message.channel.mention}",
            message_link=message_link,
            color=Config.LOG_COLORS["message_delete"],
            additional_info=f"Content: `{content_preview}`" if content_preview else "Empty content or attachments"
        )
    
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """Log when a message is edited"""
        if before.author.bot or before.content == after.content:
            return
        
        message_link = f"https://discord.com/channels/{after.guild.id}/{after.channel.id}/{after.id}"
        before_preview = before.content[:50] + "..." if len(before.content) > 50 else before.content
        after_preview = after.content[:50] + "..." if len(after.content) > 50 else after.content
        
        await self.send_admin_log(
            member=after.author,
            action="Message Edited",
            description=f"Message edited in {after.channel.mention}",
            message_link=message_link,
            color=Config.LOG_COLORS["message_edit"],
            additional_info=f"Before: `{before_preview}`\nAfter: `{after_preview}`"
        )
    
    @commands.Cog.listener()
    async def on_thread_create(self, thread):
        """Log when a thread is created"""
        if thread.owner:
            await self.send_admin_log(
                member=thread.owner,
                action="Thread Created",
                description=f"Thread created: {thread.mention}",
                color=Config.LOG_COLORS["thread_create"],
                additional_info=f"Channel: {thread.parent.mention}\nName: {thread.name}"
            )
    
    @commands.Cog.listener()
    async def on_thread_delete(self, thread):
        """Log when a thread is deleted"""
        if thread.owner:
            await self.send_admin_log(
                member=thread.owner,
                action="Thread Deleted",
                description=f"Thread deleted: {thread.name}",
                color=Config.LOG_COLORS["thread_delete"],
                additional_info=f"Parent channel: {thread.parent.mention if thread.parent else 'Unknown'}"
            )
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Log voice channel activity"""
        # Member joined a voice channel
        if before.channel is None and after.channel is not None:
            await self.send_admin_log(
                member=member,
                action="Joined Voice",
                description=f"{member.mention} joined {after.channel.mention}",
                color=Config.LOG_COLORS["voice_join"]
            )
        
        # Member left a voice channel
        elif before.channel is not None and after.channel is None:
            await self.send_admin_log(
                member=member,
                action="Left Voice",
                description=f"{member.mention} left {before.channel.mention}",
                color=Config.LOG_COLORS["voice_leave"]
            )
        
        # Member switched voice channels
        elif before.channel != after.channel and before.channel is not None and after.channel is not None:
            await self.send_admin_log(
                member=member,
                action="Switched Voice Channel",
                description=f"{member.mention} moved from {before.channel.mention} to {after.channel.mention}",
                color=Config.LOG_COLORS["voice_join"]
            )
    
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """Log member profile updates"""
        changes = []
        
        # Nickname change
        if before.nick != after.nick:
            old_nick = before.nick or before.name
            new_nick = after.nick or after.name
            changes.append(f"Nickname: `{old_nick}` → `{new_nick}`")
        
        # Role changes
        if before.roles != after.roles:
            added_roles = set(after.roles) - set(before.roles)
            removed_roles = set(before.roles) - set(after.roles)
            
            if added_roles:
                changes.append(f"Roles added: {', '.join([role.mention for role in added_roles])}")
            if removed_roles:
                changes.append(f"Roles removed: {', '.join([role.mention for role in removed_roles])}")
        
        if changes:
            action = "Role Update" if any("Roles" in change for change in changes) else "Nickname Change"
            color = Config.LOG_COLORS["role_update"] if "Role" in action else Config.LOG_COLORS["nickname_change"]
            
            await self.send_admin_log(
                member=after,
                action=action,
                description=f"{after.mention}'s profile updated",
                color=color,
                additional_info="\n".join(changes)
            )
    
    @commands.Cog.listener()
    async def on_app_command_completion(self, interaction, command):
        """Log when slash commands are used"""
        if interaction.user.bot:
            return
        
        # Get command parameters
        params = []
        if hasattr(interaction, 'namespace') and interaction.namespace:
            for name, value in interaction.namespace.__dict__.items():
                if value is not None:
                    params.append(f"{name}: {value}")
        
        param_text = f" with parameters: {', '.join(params)}" if params else ""
        
        await self.send_admin_log(
            member=interaction.user,
            action="Command Used",
            description=f"Command `/{command.name}` used in {interaction.channel.mention}",
            color=Config.LOG_COLORS["command_used"],
            additional_info=f"Full command: `/{command.name}`{param_text}"
        )

async def setup(bot):
    await bot.add_cog(AdminLogging(bot))