import discord
from discord.ext import commands
from discord import app_commands
from bot.config import Config
from bot.embeds import create_moderation_embed, create_error_embed, create_success_embed
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
        elif self.action_type == "Kick":
            color = Config.COLORS["error"]
            try:
                await self.target.kick(reason=f"Kicked by {self.staff_member} - {reason}")
            except discord.Forbidden:
                await interaction.response.send_message("❌ I don't have permission to kick this user.", ephemeral=True)
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

        # Log to moderation log channel
        log_channel = interaction.client.get_channel(getattr(Config, 'MODERATION_LOG_CHANNEL', None))
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
            elif self.action_type == "Ban":
                dm_embed = discord.Embed(
                    title="🔨 Banned - Monroe Social Club",
                    description=f"You have been banned from Monroe Social Club.",
                    color=color
                )
            elif self.action_type == "Kick":
                dm_embed = discord.Embed(
                    title="👢 Kicked - Monroe Social Club",
                    description=f"You have been kicked from Monroe Social Club.",
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
        elif self.action_type == "Kick":
            color = Config.COLORS["error"]
            try:
                await self.target.kick(reason=f"Kicked by {self.staff_member} - {reason}")
            except discord.Forbidden:
                await interaction.response.send_message("❌ I don't have permission to kick this user.", ephemeral=True)
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

        # Log to moderation log channel
        log_channel = interaction.client.get_channel(getattr(Config, 'MODERATION_LOG_CHANNEL', None))
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
            elif self.action_type == "Ban":
                dm_embed = discord.Embed(
                    title="🔨 Banned - Monroe Social Club",
                    description=f"You have been banned from Monroe Social Club.",
                    color=color
                )
            elif self.action_type == "Kick":
                dm_embed = discord.Embed(
                    title="👢 Kicked - Monroe Social Club",
                    description=f"You have been kicked from Monroe Social Club.",
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
        print(f"🛡️ ModerationCog initialized")

    async def cog_load(self):
        print(f"🛡️ ModerationCog loaded successfully")

        # Debug: Print all app commands in this cog
        app_commands = getattr(self, '__cog_app_commands__', [])
        print(f"🛡️ ModerationCog has {len(app_commands)} app commands: {[cmd.name for cmd in app_commands]}")

        # Verify warn command exists
        warn_cmd = None
        for cmd in app_commands:
            if cmd.name == 'warn':
                warn_cmd = cmd
                break

        if warn_cmd:
            print(f"🛡️ Warn command found: {warn_cmd.name} - {warn_cmd.description}")
        else:
            print(f"❌ Warn command NOT found in cog app commands")

    @app_commands.command(name="warn", description="Warn a user")
    @app_commands.describe(user="The user to warn", reason="Reason for the warning")
    @app_commands.default_permissions(kick_members=True)
    async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
        try:
            # Check permissions
            if not interaction.user.guild_permissions.kick_members:
                embed = create_error_embed("Permission Denied", "You don't have permission to warn users.")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            # Send DM to user
            dm_sent = False
            try:
                dm_embed = discord.Embed(
                    title="⚠️ Warning - Monroe Social Club",
                    description=f"You have been warned in {interaction.guild.name}",
                    color=Config.COLORS["warning"],
                    timestamp=datetime.datetime.utcnow()
                )
                dm_embed.add_field(name="Reason", value=reason, inline=False)
                dm_embed.add_field(name="Staff Member", value=interaction.user.mention, inline=True)
                dm_embed.set_footer(text="Please follow server rules to avoid further action.")

                await user.send(embed=dm_embed)
                dm_sent = True
            except Exception as e:
                print(f"❌ Could not send DM to {user}: {e}")

            # Create moderation log
            log_embed = create_moderation_embed(
                action="Warning",
                target=user,
                staff_member=interaction.user,
                reason=reason,
                color=Config.COLORS["warning"]
            )

            # Log to moderation log channel
            log_channel = self.bot.get_channel(getattr(Config, 'MODERATION_LOG_CHANNEL', None))
            if log_channel:
                await log_channel.send(embed=log_embed)

            # Response to staff member
            response = f"✅ {user.mention} has been warned for: {reason}"
            if not dm_sent:
                response += "\n⚠️ Could not send DM to user."

            embed = create_success_embed("Warning Issued", response)
            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            print(f"❌ Error in warn command: {e}")
            embed = create_error_embed("Command Error", f"An error occurred: {str(e)}")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="kick", description="Kick a user from the server")
    @app_commands.describe(user="The user to kick", reason="Reason for the kick")
    @app_commands.default_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
        try:
            # Check permissions
            if not interaction.user.guild_permissions.kick_members:
                embed = create_error_embed("Permission Denied", "You don't have permission to kick users.")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            # Open the rule selection panel
            view = RuleViolationView("Kick", user, interaction.user)
            await interaction.response.send_message("Select the rules violated:", view=view, ephemeral=True)

        except Exception as e:
            print(f"❌ Error in kick command: {e}")
            embed = create_error_embed("Command Error", f"An error occurred: {str(e)}")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="ban", description="Ban a user from the server")
    @app_commands.describe(user="The user to ban", reason="Reason for the ban")
    @app_commands.default_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
        try:
            # Check permissions
            if not interaction.user.guild_permissions.ban_members:
                embed = create_error_embed("Permission Denied", "You don't have permission to ban users.")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

             # Open the rule selection panel
            view = RuleViolationView("Ban", user, interaction.user)
            await interaction.response.send_message("Select the rules violated:", view=view, ephemeral=True)

        except Exception as e:
            print(f"❌ Error in ban command: {e}")
            embed = create_error_embed("Command Error", f"An error occurred: {str(e)}")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="announce", description="Send an announcement to the announcement channel")
    @app_commands.describe(message="The announcement message to send")
    async def announce(self, interaction: discord.Interaction, message: str):
        if not self.has_staff_permissions(interaction.user):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return

        announcement_channel = self.bot.get_channel(getattr(Config, 'ANNOUNCEMENT_CHANNEL', None))
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
            log_channel = self.bot.get_channel(getattr(Config, 'MODERATION_LOG_CHANNEL', None))
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
        log_channel = self.bot.get_channel(getattr(Config, 'MODERATION_LOG_CHANNEL', None))
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
            log_channel = self.bot.get_channel(getattr(Config, 'MODERATION_LOG_CHANNEL', None))
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

        announcement_channel = self.bot.get_channel(getattr(Config, 'ANNOUNCEMENT_CHANNEL', None))
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

    @app_commands.command(name="addrules", description="Display server rules")
    async def addrules(self, interaction: discord.Interaction):
        """Display comprehensive server rules"""
        if not any(role.id in Config.STAFF_ROLES for role in interaction.user.roles) and not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return

        embed = discord.Embed(
            title="📋 Monroe Social Club Rules",
            description="Complete list of server rules organized by severity",
            color=Config.COLORS["info"],
            timestamp=discord.utils.utcnow()
        )

        try:
            # Group rules by severity level
            severity_1_rules = []
            severity_2_rules = []
            severity_3_rules = []

            for rule_id, description in Config.SERVER_RULES.items():
                if rule_id.startswith("1."):  # Severity 1
                    severity_1_rules.append(f"**{rule_id}**: {description}")
                elif rule_id.startswith("2."):  # Severity 2
                    severity_2_rules.append(f"**{rule_id}**: {description}")
                elif rule_id.startswith("3."):  # Severity 3
                    severity_3_rules.append(f"**{rule_id}**: {description}")

            # Add fields for each severity level (split if too long)
            if severity_1_rules:
                rules_text = "\n".join(severity_1_rules)
                if len(rules_text) > 1024:
                    # Split into multiple fields if too long
                    mid_point = len(severity_1_rules) // 2
                    embed.add_field(
                        name="⚠️ Severity 1 Rules (Part 1)",
                        value="\n".join(severity_1_rules[:mid_point]),
                        inline=False
                    )
                    embed.add_field(
                        name="⚠️ Severity 1 Rules (Part 2)",
                        value="\n".join(severity_1_rules[mid_point:]),
                        inline=False
                    )
                else:
                    embed.add_field(
                        name="⚠️ Severity 1 Rules",
                        value=rules_text,
                        inline=False
                    )

            if severity_2_rules:
                rules_text = "\n".join(severity_2_rules)
                if len(rules_text) > 1024:
                    mid_point = len(severity_2_rules) // 2
                    embed.add_field(
                        name="⚡ Severity 2 Rules (Part 1)",
                        value="\n".join(severity_2_rules[:mid_point]),
                        inline=False
                    )
                    embed.add_field(
                        name="⚡ Severity 2 Rules (Part 2)",
                        value="\n".join(severity_2_rules[mid_point:]),
                        inline=False
                    )
                else:
                    embed.add_field(
                        name="⚡ Severity 2 Rules",
                        value=rules_text,
                        inline=False
                    )

            if severity_3_rules:
                rules_text = "\n".join(severity_3_rules)
                if len(rules_text) > 1024:
                    mid_point = len(severity_3_rules) // 2
                    embed.add_field(
                        name="🚨 Severity 3 Rules (Part 1)",
                        value="\n".join(severity_3_rules[:mid_point]),
                        inline=False
                    )
                    embed.add_field(
                        name="🚨 Severity 3 Rules (Part 2)",
                        value="\n".join(severity_3_rules[mid_point:]),
                        inline=False
                    )
                else:
                    embed.add_field(
                        name="🚨 Severity 3 Rules",
                        value=rules_text,
                        inline=False
                    )

            embed.set_footer(text="Monroe Social Club • Use rule IDs for moderation actions")
            await interaction.response.send_message(embed=embed)

        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Error Loading Rules",
                description=f"There was an error loading the server rules: {str(e)}",
                color=Config.COLORS["error"]
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)

    def has_staff_permissions(self, user: discord.Member):
        """Check if a user has staff permissions based on roles."""
        if any(role.id in getattr(Config, 'STAFF_ROLES', []) for role in user.roles) or user.guild_permissions.manage_messages:
            return True
        return False

async def setup(bot):
    await bot.add_cog(ModerationCog(bot))