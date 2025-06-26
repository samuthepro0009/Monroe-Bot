import discord
from discord.ext import commands
from discord import app_commands
from bot.config import Config
import asyncio

class ApplicationModal(discord.ui.Modal):
    def __init__(self, role_type):
        super().__init__(title=f"{role_type} Application - Monroe Social Club")
        self.role_type = role_type
        
        # Common questions for both Staff and Security
        self.age_question = discord.ui.TextInput(
            label="What is your age?",
            placeholder="Enter your age...",
            required=True,
            max_length=3
        )
        
        self.experience_question = discord.ui.TextInput(
            label=f"Do you have {role_type.lower()} experience?",
            placeholder=f"Describe your {role_type.lower()} experience in Discord servers or similar roles...",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=1000
        )
        
        self.timezone_question = discord.ui.TextInput(
            label="What is your timezone?",
            placeholder="e.g., EST, PST, GMT+2, etc.",
            required=True,
            max_length=50
        )
        
        self.availability_question = discord.ui.TextInput(
            label="When are you usually active?",
            placeholder="Describe your typical online hours and days...",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=500
        )
        
        self.motivation_question = discord.ui.TextInput(
            label=f"Why do you want to be {role_type}?",
            placeholder=f"Explain your motivation for applying to {role_type} role...",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=1000
        )
        
        # Add all questions to the modal
        self.add_item(self.age_question)
        self.add_item(self.experience_question)
        self.add_item(self.timezone_question)
        self.add_item(self.availability_question)
        self.add_item(self.motivation_question)

    async def on_submit(self, interaction: discord.Interaction):
        # Create application embed
        embed = discord.Embed(
            title=f"📝 {self.role_type} Application",
            description=f"New application from {interaction.user.mention}",
            color=Config.COLORS["info"]
        )
        
        # User information
        embed.add_field(
            name="👤 Applicant Info",
            value=f"**User:** {interaction.user.mention}\n**Username:** {interaction.user.name}\n**User ID:** {interaction.user.id}",
            inline=False
        )
        
        # Application answers
        embed.add_field(
            name="🎂 Age",
            value=self.age_question.value,
            inline=True
        )
        
        embed.add_field(
            name="🌍 Timezone",
            value=self.timezone_question.value,
            inline=True
        )
        
        embed.add_field(
            name="⏰ Availability",
            value=self.availability_question.value,
            inline=False
        )
        
        embed.add_field(
            name=f"💼 {self.role_type} Experience",
            value=self.experience_question.value,
            inline=False
        )
        
        embed.add_field(
            name="💭 Motivation",
            value=self.motivation_question.value,
            inline=False
        )
        
        # Set user avatar
        embed.set_thumbnail(url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
        embed.set_footer(text="Monroe Social Club - Application System", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.timestamp = discord.utils.utcnow()
        
        # Send to application log channel
        log_channel = interaction.client.get_channel(Config.APPLICATION_LOG_CHANNEL)
        if log_channel:
            await log_channel.send(embed=embed)
        
        # Respond to user
        success_embed = discord.Embed(
            title="✅ Application Submitted!",
            description=f"Your {self.role_type} application has been submitted successfully!",
            color=Config.COLORS["success"]
        )
        success_embed.add_field(
            name="📋 What's Next?",
            value="• Your application is now under review\n• Management will review your responses\n• You'll be contacted if selected\n• Thank you for your interest!",
            inline=False
        )
        success_embed.set_footer(text="Monroe Social Club - 80s Beach Vibes 🌴")
        
        await interaction.response.send_message(embed=success_embed, ephemeral=True)

class ApplicationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Apply for Staff", style=discord.ButtonStyle.primary, emoji="👨‍💼")
    async def staff_application(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ApplicationModal("Staff")
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Apply for Security", style=discord.ButtonStyle.secondary, emoji="🛡️")
    async def security_application(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ApplicationModal("Security")
        await interaction.response.send_modal(modal)

class ApplicationsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def has_staff_permissions(self, member):
        """Check if member has staff permissions"""
        if member.guild_permissions.administrator:
            return True
        
        staff_role_ids = Config.STAFF_ROLES
        member_roles = [role.id for role in member.roles]
        return any(role_id in member_roles for role_id in staff_role_ids)

    @app_commands.command(name="create_applications", description="Create the application system message")
    async def create_applications(self, interaction: discord.Interaction):
        if not self.has_staff_permissions(interaction.user):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return

        # Create main application embed
        embed = discord.Embed(
            title="📝 Monroe Social Club Applications",
            description="Join our management team and help maintain the ultimate 80s beach experience!",
            color=Config.COLORS["pink"]
        )
        
        embed.add_field(
            name="👨‍💼 Staff Position",
            value="• Help manage the community\n• Moderate chat and voice channels\n• Assist with events and activities\n• Support new members",
            inline=True
        )
        
        embed.add_field(
            name="🛡️ Security Position", 
            value="• Maintain server security\n• Monitor for rule violations\n• Handle reports and incidents\n• Protect community members",
            inline=True
        )
        
        embed.add_field(
            name="📋 Application Process",
            value="1. Click the appropriate button below\n2. Fill out the application form\n3. Wait for management review\n4. Get contacted if selected",
            inline=False
        )
        
        embed.add_field(
            name="⚡ Requirements",
            value="• Must be mature and responsible\n• Active in the community\n• Good understanding of Discord\n• Respectful attitude towards all members",
            inline=False
        )
        
        embed.set_footer(text="Monroe Social Club - Join Our Team! 🌴", icon_url=self.bot.user.avatar.url)
        embed.timestamp = discord.utils.utcnow()
        
        # Create view with buttons
        view = ApplicationView()
        
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="application_stats", description="View application statistics")
    async def application_stats(self, interaction: discord.Interaction):
        if not self.has_staff_permissions(interaction.user):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return

        log_channel = self.bot.get_channel(Config.APPLICATION_LOG_CHANNEL)
        if not log_channel:
            await interaction.response.send_message("❌ Application log channel not found.", ephemeral=True)
            return

        await interaction.response.defer()

        # Count applications in the last 100 messages
        staff_applications = 0
        security_applications = 0
        total_applications = 0

        async for message in log_channel.history(limit=100):
            if message.embeds:
                embed = message.embeds[0]
                if "Staff Application" in embed.title:
                    staff_applications += 1
                    total_applications += 1
                elif "Security Application" in embed.title:
                    security_applications += 1
                    total_applications += 1

        # Create stats embed
        embed = discord.Embed(
            title="📊 Application Statistics",
            description="Recent application data for Monroe Social Club",
            color=Config.COLORS["info"]
        )
        
        embed.add_field(
            name="📈 Total Applications",
            value=f"**{total_applications}** applications",
            inline=True
        )
        
        embed.add_field(
            name="👨‍💼 Staff Applications",
            value=f"**{staff_applications}** applications",
            inline=True
        )
        
        embed.add_field(
            name="🛡️ Security Applications",
            value=f"**{security_applications}** applications",
            inline=True
        )
        
        embed.add_field(
            name="📝 Note",
            value="Statistics based on last 100 messages in application log channel.",
            inline=False
        )
        
        embed.set_footer(text="Monroe Social Club - Application System", icon_url=self.bot.user.avatar.url)
        embed.timestamp = discord.utils.utcnow()
        
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ApplicationsCog(bot))
