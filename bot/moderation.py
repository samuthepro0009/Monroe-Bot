import discord
from discord.ext import commands
from discord import app_commands
from bot.config import Config
from bot.embeds import create_moderation_embed
import datetime

class RuleViolationSelect(discord.ui.Select):
    def __init__(self, action_type, target, staff_member, image=None):
        self.action_type = action_type
        self.target = target
        self.staff_member = staff_member
        self.image = image
        
        options = []
        for rule_id, rule_desc in Config.SERVER_RULES.items():
            options.append(discord.SelectOption(
                label=f"{rule_id} - {rule_desc.split(' - ')[0]}",
                description=rule_desc.split(' - ')[1][:100] if ' - ' in rule_desc else rule_desc[:100],
                value=rule_id
            ))
        
        # Add "Other" option
        options.append(discord.SelectOption(
            label="Other",
            description="Custom violation reason",
            value="other"
        ))
        
        super().__init__(placeholder="Select rule violations (can select multiple)...", options=options, min_values=1, max_values=len(options))
    
    async def callback(self, interaction: discord.Interaction):
        if "other" in self.values:
            modal = CustomReasonModal(self.action_type, self.target, self.staff_member, self.image, self.values)
            await interaction.response.send_modal(modal)
        else:
            # Multiple rule violations selected
            reasons = []
            for rule_id in self.values:
                reasons.append(f"{rule_id} - {Config.SERVER_RULES[rule_id]}")
            reason = " | ".join(reasons)
            await self.execute_moderation_action(interaction, reason)
    
    async def execute_moderation_action(self, interaction, reason):
        if self.action_type == "Warning":
            color = Config.COLORS["warning"]
        elif self.action_type == "Ban":
            color = Config.COLORS["error"]
            try:
                await self.target.ban(reason=f"Banned by {self.staff_member} - {reason}")
            except discord.Forbidden:
                await interaction.response.send_message("❌ I don't have permission to ban this user.", ephemeral=True)
                return
        
        # Create moderation embed
        embed = create_moderation_embed(
            action=self.action_type,
            target=self.target,
            staff_member=self.staff_member,
            reason=reason,
            color=color
        )
        
        if self.image:
            embed.set_image(url=self.image.url)
        
        # Log to moderation channel
        log_channel = interaction.client.get_channel(Config.MODERATION_LOG_CHANNEL)
        if log_channel:
            await log_channel.send(embed=embed)
        
        # Send DM to user
        try:
            if self.action_type == "Warning":
                dm_embed = discord.Embed(
                    title="⚠️ Warning - Monroe Social Club",
                    description=f"You have been warned in Monroe Social Club.",
                    color=color
                )
            else:
                dm_embed = discord.Embed(
                    title="🔨 Banned - Monroe Social Club",
                    description=f"You have been banned from Monroe Social Club.",
                    color=color
                )
            
            dm_embed.add_field(name="Reason", value=reason, inline=False)
            dm_embed.add_field(name="Staff Member", value=self.staff_member.mention, inline=True)
            dm_embed.set_footer(text="Please follow server rules to avoid further action.")
            
            await self.target.send(embed=dm_embed)
        except discord.Forbidden:
            pass
        
        await interaction.response.send_message(f"✅ {self.target.mention} has been {self.action_type.lower()}ed for: {reason}", ephemeral=True)

class CustomReasonModal(discord.ui.Modal):
    def __init__(self, action_type, target, staff_member, image=None, selected_rules=None):
        super().__init__(title=f"Custom {action_type} Reason")
        self.action_type = action_type
        self.target = target
        self.staff_member = staff_member
        self.image = image
        self.selected_rules = selected_rules or []
        
        self.reason_input = discord.ui.TextInput(
            label="Other Motivation",
            placeholder="Enter the custom reason for this action...",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=1000
        )
        self.add_item(self.reason_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        # Combine selected rules with custom reason
        reasons = []
        for rule_id in self.selected_rules:
            if rule_id != "other":
                reasons.append(f"{rule_id} - {Config.SERVER_RULES[rule_id]}")
        
        if reasons:
            reason = " | ".join(reasons) + f" | Other - {self.reason_input.value}"
        else:
            reason = f"Other - {self.reason_input.value}"
        
        if self.action_type == "Warning":
            color = Config.COLORS["warning"]
        elif self.action_type == "Ban":
            color = Config.COLORS["error"]
            try:
                await self.target.ban(reason=f"Banned by {self.staff_member} - {reason}")
            except discord.Forbidden:
                await interaction.response.send_message("❌ I don't have permission to ban this user.", ephemeral=True)
                return
        
        # Create moderation embed
        embed = create_moderation_embed(
            action=self.action_type,
            target=self.target,
            staff_member=self.staff_member,
            reason=reason,
            color=color
        )
        
        if self.image:
            embed.set_image(url=self.image.url)
        
        # Log to moderation channel
        log_channel = interaction.client.get_channel(Config.MODERATION_LOG_CHANNEL)
        if log_channel:
            await log_channel.send(embed=embed)
        
        # Send DM to user
        try:
            if self.action_type == "Warning":
                dm_embed = discord.Embed(
                    title="⚠️ Warning - Monroe Social Club",
                    description=f"You have been warned in Monroe Social Club.",
                    color=color
                )
            else:
                dm_embed = discord.Embed(
                    title="🔨 Banned - Monroe Social Club",
                    description=f"You have been banned from Monroe Social Club.",
                    color=color
                )
            
            dm_embed.add_field(name="Reason", value=reason, inline=False)
            dm_embed.add_field(name="Staff Member", value=self.staff_member.mention, inline=True)
            dm_embed.set_footer(text="Please follow server rules to avoid further action.")
            
            await self.target.send(embed=dm_embed)
        except discord.Forbidden:
            pass
        
        await interaction.response.send_message(f"✅ {self.target.mention} has been {self.action_type.lower()}ed for: {reason}", ephemeral=True)

class RuleViolationView(discord.ui.View):
    def __init__(self, action_type, target, staff_member, image=None):
        super().__init__(timeout=300)
        self.add_item(RuleViolationSelect(action_type, target, staff_member, image))

class ClearApplicationsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="Confirm Clear", style=discord.ButtonStyle.danger, emoji="🗑️")
    async def confirm_clear(self, interaction: discord.Interaction, button: discord.ui.Button):
        log_channel = interaction.client.get_channel(Config.APPLICATION_LOG_CHANNEL)
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Delete all messages in the application log channel
            deleted = await log_channel.purge(limit=None)
            
            # Send confirmation
            embed = discord.Embed(
                title="✅ Applications Database Cleared",
                description=f"Successfully cleared {len(deleted)} application messages.",
                color=Config.COLORS["success"]
            )
            embed.add_field(
                name="Staff Member",
                value=f"{interaction.user.mention}",
                inline=True
            )
            embed.timestamp = discord.utils.utcnow()
            
            await interaction.followup.send(embed=embed, ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send("❌ I don't have permission to delete messages in the application channel.", ephemeral=True)
    
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary, emoji="❌")
    async def cancel_clear(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="❌ Operation Cancelled",
            description="Application database clearing has been cancelled.",
            color=Config.COLORS["error"]
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

class ModerationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def has_staff_permissions(self, member):
        """Check if member has staff permissions"""
        # Check for administrator permission or specific staff roles
        if member.guild_permissions.administrator:
            return True
        
        # Check staff roles (configure these in config.py)
        staff_role_ids = Config.STAFF_ROLES
        member_roles = [role.id for role in member.roles]
        return any(role_id in member_roles for role_id in staff_role_ids)

    @app_commands.command(name="warn", description="Warn a member")
    @app_commands.describe(
        member="The member to warn",
        image="Optional image attachment"
    )
    async def warn(self, interaction: discord.Interaction, member: discord.Member, image: discord.Attachment = None):
        if not self.has_staff_permissions(interaction.user):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return

        # Show rule selection interface
        embed = discord.Embed(
            title="⚠️ Warning Member",
            description=f"Select the rule violation for {member.mention}:",
            color=Config.COLORS["warning"]
        )
        
        view = RuleViolationView("Warning", member, interaction.user, image)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name="kick", description="Kick a member from the server")
    @app_commands.describe(
        member="The member to kick",
        reason="Reason for the kick",
        image="Optional image attachment"
    )
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str, image: discord.Attachment = None):
        if not self.has_staff_permissions(interaction.user):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return

        if member.top_role >= interaction.user.top_role and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You cannot kick this member due to role hierarchy.", ephemeral=True)
            return

        # Create kick embed
        embed = create_moderation_embed(
            action="Kick",
            target=member,
            staff_member=interaction.user,
            reason=reason,
            color=Config.COLORS["error"]
        )
        
        if image:
            embed.set_image(url=image.url)

        # Send DM before kicking
        try:
            dm_embed = discord.Embed(
                title="👢 Kicked - Monroe Social Club",
                description=f"You have been kicked from Monroe Social Club.",
                color=Config.COLORS["error"]
            )
            dm_embed.add_field(name="Reason", value=reason, inline=False)
            dm_embed.add_field(name="Staff Member", value=interaction.user.mention, inline=True)
            dm_embed.set_footer(text="You can rejoin the server if you follow the rules.")
            
            await member.send(embed=dm_embed)
        except discord.Forbidden:
            pass

        # Kick the member
        try:
            await member.kick(reason=f"Kicked by {interaction.user} - {reason}")
            
            # Log to moderation channel
            log_channel = self.bot.get_channel(Config.MODERATION_LOG_CHANNEL)
            if log_channel:
                await log_channel.send(embed=embed)

            await interaction.response.send_message(f"👢 {member.mention} has been kicked for: {reason}", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to kick this member.", ephemeral=True)

    @app_commands.command(name="ban", description="Ban a member from the server")
    @app_commands.describe(
        member="The member to ban",
        delete_days="Days of messages to delete (0-7)",
        image="Optional image attachment"
    )
    async def ban(self, interaction: discord.Interaction, member: discord.Member, delete_days: int = 0, image: discord.Attachment = None):
        if not self.has_staff_permissions(interaction.user):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return

        if member.top_role >= interaction.user.top_role and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You cannot ban this member due to role hierarchy.", ephemeral=True)
            return

        if delete_days < 0 or delete_days > 7:
            await interaction.response.send_message("❌ Delete days must be between 0 and 7.", ephemeral=True)
            return

        # Show rule selection interface
        embed = discord.Embed(
            title="🔨 Banning Member",
            description=f"Select the rule violation for {member.mention}:",
            color=Config.COLORS["error"]
        )
        
        view = RuleViolationView("Ban", member, interaction.user, image)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name="announce", description="Send an announcement to the announcement channel")
    @app_commands.describe(message="The announcement message to send")
    async def announce(self, interaction: discord.Interaction, message: str):
        if not self.has_staff_permissions(interaction.user):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return

        announcement_channel = self.bot.get_channel(Config.ANNOUNCEMENT_CHANNEL)
        if not announcement_channel:
            await interaction.response.send_message("❌ Announcement channel not found.", ephemeral=True)
            return

        # Create announcement embed
        embed = discord.Embed(
            title="📢 Monroe Social Club Announcement",
            description=message,
            color=Config.COLORS["info"]
        )
        embed.set_footer(text=f"Announced by {interaction.user.display_name}", icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
        embed.timestamp = discord.utils.utcnow()

        await announcement_channel.send("@everyone", embed=embed)
        await interaction.response.send_message("✅ Announcement sent successfully!", ephemeral=True)

    @app_commands.command(name="devlog", description="Post a development log")
    @app_commands.describe(
        version="Version number (e.g., 0.0.1)",
        additions="New features added",
        fixes="Bugs fixed",
        removed="Features removed",
        image="Optional image attachment"
    )
    async def devlog(self, interaction: discord.Interaction, version: str, additions: str = None, fixes: str = None, removed: str = None, image: discord.Attachment = None):
        if not self.has_staff_permissions(interaction.user):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return

        devlog_channel = self.bot.get_channel(Config.DEVLOG_CHANNEL)
        if not devlog_channel:
            await interaction.response.send_message("❌ Devlog channel not found.", ephemeral=True)
            return

        # Create devlog embed
        embed = discord.Embed(
            title=f"🔧 DEVLOG {version}",
            description="Latest updates for Monroe Social Club!",
            color=Config.COLORS["purple"]
        )

        if additions:
            embed.add_field(name="✨ Additions", value=additions, inline=False)
        if fixes:
            embed.add_field(name="🔧 Fixes", value=fixes, inline=False)
        if removed:
            embed.add_field(name="🗑️ Removed Features", value=removed, inline=False)

        if image:
            embed.set_image(url=image.url)

        embed.set_footer(text=f"Development Team • Version {version}", icon_url=self.bot.user.avatar.url)
        embed.timestamp = discord.utils.utcnow()

        # Send with @everyone ping
        await devlog_channel.send("@everyone", embed=embed)
        await interaction.response.send_message(f"✅ Devlog {version} posted successfully!", ephemeral=True)

    @app_commands.command(name="unban", description="Unban a user from the server")
    @app_commands.describe(
        user_id="The ID of the user to unban",
        reason="Reason for the unban"
    )
    async def unban(self, interaction: discord.Interaction, user_id: str, reason: str):
        if not self.has_staff_permissions(interaction.user):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return

        try:
            user_id = int(user_id)
        except ValueError:
            await interaction.response.send_message("❌ Invalid user ID provided.", ephemeral=True)
            return

        try:
            # Get the banned user
            banned_user = await self.bot.fetch_user(user_id)
            
            # Unban the user
            await interaction.guild.unban(banned_user, reason=f"Unbanned by {interaction.user} - {reason}")
            
            # Create unban embed
            embed = create_moderation_embed(
                action="Unban",
                target=banned_user,
                staff_member=interaction.user,
                reason=reason,
                color=Config.COLORS["success"]
            )
            
            # Log to moderation channel
            log_channel = self.bot.get_channel(Config.MODERATION_LOG_CHANNEL)
            if log_channel:
                await log_channel.send(embed=embed)

            await interaction.response.send_message(f"✅ {banned_user.mention} has been unbanned for: {reason}", ephemeral=True)
        except discord.NotFound:
            await interaction.response.send_message("❌ User not found or not banned.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to unban this user.", ephemeral=True)

    @app_commands.command(name="unwarn", description="Remove a warning from a user")
    @app_commands.describe(
        member="The member to remove warning from",
        reason="Reason for removing the warning"
    )
    async def unwarn(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        if not self.has_staff_permissions(interaction.user):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return

        # Create unwarn embed
        embed = create_moderation_embed(
            action="Warning Removed",
            target=member,
            staff_member=interaction.user,
            reason=reason,
            color=Config.COLORS["success"]
        )

        # Log to moderation channel
        log_channel = self.bot.get_channel(Config.MODERATION_LOG_CHANNEL)
        if log_channel:
            await log_channel.send(embed=embed)

        # Send DM to user
        try:
            dm_embed = discord.Embed(
                title="✅ Warning Removed - Monroe Social Club",
                description=f"A warning has been removed from your record in Monroe Social Club.",
                color=Config.COLORS["success"]
            )
            dm_embed.add_field(name="Reason", value=reason, inline=False)
            dm_embed.add_field(name="Staff Member", value=interaction.user.mention, inline=True)
            dm_embed.set_footer(text="Keep up the good behavior!")
            
            await member.send(embed=dm_embed)
        except discord.Forbidden:
            pass  # User has DMs disabled

        await interaction.response.send_message(f"✅ Warning removed from {member.mention} for: {reason}", ephemeral=True)

    @app_commands.command(name="clear", description="Clear a specified number of messages")
    @app_commands.describe(
        amount="Number of messages to delete (1-100)",
        reason="Reason for clearing messages"
    )
    async def clear(self, interaction: discord.Interaction, amount: int, reason: str = "No reason provided"):
        if not self.has_staff_permissions(interaction.user):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return

        if amount < 1 or amount > 100:
            await interaction.response.send_message("❌ Amount must be between 1 and 100.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        try:
            # Delete messages
            deleted = await interaction.channel.purge(limit=amount)
            
            # Create clear embed for logging
            embed = discord.Embed(
                title="🧹 Messages Cleared - Monroe Social Club",
                description=f"Messages cleared in {interaction.channel.mention}",
                color=Config.COLORS["warning"]
            )
            
            embed.add_field(
                name="👮 Staff Member",
                value=f"**Staff:** {interaction.user.mention}\n**Username:** {interaction.user.name}#{interaction.user.discriminator}\n**User ID:** {interaction.user.id}",
                inline=True
            )
            
            embed.add_field(
                name="📝 Clear Details",
                value=f"**Messages Deleted:** {len(deleted)}\n**Channel:** {interaction.channel.mention}\n**Reason:** {reason}",
                inline=False
            )
            
            embed.set_footer(text="Monroe Social Club - Moderation System", icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
            embed.timestamp = discord.utils.utcnow()
            
            # Log to moderation channel
            log_channel = self.bot.get_channel(Config.MODERATION_LOG_CHANNEL)
            if log_channel:
                await log_channel.send(embed=embed)

            await interaction.followup.send(f"✅ Cleared {len(deleted)} messages for: {reason}", ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send("❌ I don't have permission to delete messages in this channel.", ephemeral=True)

    @app_commands.command(name="event", description="Create an event announcement")
    @app_commands.describe(
        event_type="Type of event",
        time="Event time and date",
        ping_role="Role to ping (optional)",
        notes="Additional event notes"
    )
    async def event(self, interaction: discord.Interaction, event_type: str, time: str, ping_role: discord.Role = None, notes: str = None):
        if not self.has_staff_permissions(interaction.user):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return

        announcement_channel = self.bot.get_channel(Config.ANNOUNCEMENT_CHANNEL)
        if not announcement_channel:
            await interaction.response.send_message("❌ Announcement channel not found.", ephemeral=True)
            return

        # Create event embed
        embed = discord.Embed(
            title=f"🎉 Event: {event_type}",
            description="Join us for an exciting event at Monroe Social Club!",
            color=Config.COLORS["pink"]
        )
        
        embed.add_field(
            name="⏰ Event Time",
            value=time,
            inline=True
        )
        
        if ping_role:
            embed.add_field(
                name="👥 Target Audience",
                value=ping_role.mention,
                inline=True
            )
        
        embed.add_field(
            name="🎮 Join the Game",
            value=f"[Monroe Social Club Experience]({Config.ROBLOX_GAME_LINK})",
            inline=False
        )
        
        if notes:
            embed.add_field(
                name="📝 Additional Notes",
                value=notes,
                inline=False
            )
        
        embed.set_footer(text=f"Event organized by {interaction.user.display_name}", icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
        embed.timestamp = discord.utils.utcnow()

        # Create ping message
        ping_message = "@everyone"
        if ping_role:
            ping_message += f" {ping_role.mention}"

        await announcement_channel.send(ping_message, embed=embed)
        await interaction.response.send_message(f"✅ Event '{event_type}' announced successfully!", ephemeral=True)

    @app_commands.command(name="clear_applications", description="Clear the applications database")
    async def clear_applications(self, interaction: discord.Interaction):
        if not self.has_staff_permissions(interaction.user):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return

        log_channel = self.bot.get_channel(Config.APPLICATION_LOG_CHANNEL)
        if not log_channel:
            await interaction.response.send_message("❌ Application log channel not found.", ephemeral=True)
            return

        # Confirmation embed
        embed = discord.Embed(
            title="⚠️ Clear Applications Database",
            description="Are you sure you want to clear all application messages? This action cannot be undone.",
            color=Config.COLORS["warning"]
        )
        
        view = ClearApplicationsView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name="addrules", description="Post the server rules")
    async def addrules(self, interaction: discord.Interaction):
        if not self.has_staff_permissions(interaction.user):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return

        # Create rules embed
        embed = discord.Embed(
            title="📋 Monroe Social Club Rules",
            description="Welcome to our 80s beach paradise! Please follow these rules to maintain a positive community:",
            color=Config.COLORS["info"]
        )
        
        # Group rules by severity
        severity_1 = []
        severity_2 = []
        severity_3 = []
        
        for rule_id, rule_desc in Config.SERVER_RULES.items():
            if rule_id.startswith("1."):
                severity_1.append(f"**{rule_id}** - {rule_desc}")
            elif rule_id.startswith("2."):
                severity_2.append(f"**{rule_id}** - {rule_desc}")
            elif rule_id.startswith("3."):
                severity_3.append(f"**{rule_id}** - {rule_desc}")
        
        embed.add_field(
            name="🔴 Severe Violations (Level 1)",
            value="\n".join(severity_1),
            inline=False
        )
        
        embed.add_field(
            name="🟡 Moderate Violations (Level 2)",
            value="\n".join(severity_2),
            inline=False
        )
        
        embed.add_field(
            name="🟠 Minor Violations (Level 3)",
            value="\n".join(severity_3),
            inline=False
        )
        
        embed.add_field(
            name="📌 Important Notes",
            value="• Violations are categorized by severity\n• Repeated violations may result in escalated punishments\n• Staff decisions are final\n• Appeal process available through DM to management",
            inline=False
        )
        
        embed.set_footer(text="Monroe Social Club - 80s Beach Paradise 🌴", icon_url=self.bot.user.avatar.url)
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(ModerationCog(bot))
