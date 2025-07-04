
import discord
from discord.ext import commands
from discord import app_commands
from bot.config import Config
import json
import os

class AnnouncementTemplates(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="addrules", description="Add server rules to a channel")
    @app_commands.describe(channel="Channel to send rules to")
    async def add_rules(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        """Add comprehensive server rules to specified channel"""
        
        # Check if user has permission (admin or manage_guild)
        if not interaction.user.guild_permissions.administrator and not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ You need administrator permissions to use this command.", ephemeral=True)
            return

        target_channel = channel or interaction.channel

        # Create rules embed
        embed = discord.Embed(
            title="📋 Monroe Social Club - Server Rules",
            description="Welcome to Monroe Social Club! Please read and follow these rules to maintain our retro 80s beach paradise. 🏖️",
            color=Config.COLORS["info"],
            timestamp=discord.utils.utcnow()
        )

        # Add rules by severity
        severity_1_rules = []
        severity_2_rules = []
        severity_3_rules = []

        for rule_code, rule_desc in Config.SERVER_RULES.items():
            if rule_code.startswith("1."):
                severity_1_rules.append(f"**{rule_code}** - {rule_desc}")
            elif rule_code.startswith("2."):
                severity_2_rules.append(f"**{rule_code}** - {rule_desc}")
            elif rule_code.startswith("3."):
                severity_3_rules.append(f"**{rule_code}** - {rule_desc}")

        # Add severity 1 rules
        embed.add_field(
            name="🟡 Severity 1 - Minor Infractions",
            value="\n".join(severity_1_rules[:10]) + ("..." if len(severity_1_rules) > 10 else ""),
            inline=False
        )

        # Add severity 2 rules  
        embed.add_field(
            name="🟠 Severity 2 - Moderate Infractions", 
            value="\n".join(severity_2_rules[:10]) + ("..." if len(severity_2_rules) > 10 else ""),
            inline=False
        )

        # Add severity 3 rules
        embed.add_field(
            name="🔴 Severity 3 - Serious Infractions",
            value="\n".join(severity_3_rules[:10]) + ("..." if len(severity_3_rules) > 10 else ""),
            inline=False
        )

        embed.add_field(
            name="🏖️ Remember",
            value="Monroe Social Club is a place for fun, friendship, and 80s nostalgia. Let's keep it groovy! 🌴",
            inline=False
        )

        embed.set_footer(text="Rules enforced by Monroe Social Club Staff • Stay rad! 🕶️")

        try:
            await target_channel.send(embed=embed)
            await interaction.response.send_message(f"✅ Rules successfully posted to {target_channel.mention}!", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message(f"❌ I don't have permission to send messages in {target_channel.mention}.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ An error occurred: {str(e)}", ephemeral=True)

    @app_commands.command(name="template", description="Create an announcement using a template")
    @app_commands.describe(
        template_type="Type of announcement template",
        title="Custom title for the announcement",
        content="Content of the announcement",
        channel="Channel to send to (optional)"
    )
    @app_commands.choices(template_type=[
        app_commands.Choice(name="Event", value="event"),
        app_commands.Choice(name="Update", value="update"),
        app_commands.Choice(name="Maintenance", value="maintenance"),
        app_commands.Choice(name="Celebration", value="celebration"),
        app_commands.Choice(name="Welcome", value="welcome"),
        app_commands.Choice(name="Rules", value="rules"),
        app_commands.Choice(name="Partnership", value="partnership"),
        app_commands.Choice(name="Giveaway", value="giveaway")
    ])
    async def create_template(self, interaction: discord.Interaction, template_type: str, title: str, content: str, channel: discord.TextChannel = None):
        """Create an announcement using predefined templates"""
        
        # Check permissions
        if not interaction.user.guild_permissions.administrator and not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ You need administrator permissions to use this command.", ephemeral=True)
            return

        target_channel = channel or interaction.channel
        template = Config.ANNOUNCEMENT_TEMPLATES.get(template_type)
        
        if not template:
            await interaction.response.send_message("❌ Invalid template type.", ephemeral=True)
            return

        # Create embed with template styling
        embed = discord.Embed(
            title=f"{template['emoji']} {title}",
            description=content,
            color=template['color'],
            timestamp=discord.utils.utcnow()
        )
        
        embed.set_author(
            name=f"Monroe Social Club {template['title']}", 
            icon_url=interaction.guild.icon.url if interaction.guild.icon else None
        )
        
        embed.set_footer(
            text=f"Posted by {interaction.user.display_name} • 80s Beach Vibes 🏖️",
            icon_url=interaction.user.display_avatar.url
        )

        try:
            await target_channel.send(embed=embed)
            await interaction.response.send_message(f"✅ {template['title']} posted to {target_channel.mention}!", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message(f"❌ I don't have permission to send messages in {target_channel.mention}.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ An error occurred: {str(e)}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AnnouncementTemplates(bot))

class AnnouncementTemplateModal(discord.ui.Modal):
    def __init__(self, template_name, template_data=None):
        super().__init__(title=f"{'Edit' if template_data else 'Create'} Template: {template_name}")
        self.template_name = template_name
        
        # Title input
        self.title_input = discord.ui.TextInput(
            label="Announcement Title",
            placeholder="Enter the announcement title...",
            default=template_data.get('title', '') if template_data else '',
            max_length=100
        )
        self.add_item(self.title_input)
        
        # Content input
        self.content_input = discord.ui.TextInput(
            label="Announcement Content",
            placeholder="Enter the announcement content...",
            style=discord.TextStyle.paragraph,
            default=template_data.get('content', '') if template_data else '',
            max_length=2000
        )
        self.add_item(self.content_input)
        
        # Color input
        self.color_input = discord.ui.TextInput(
            label="Embed Color (hex)",
            placeholder="e.g., #FF0000 or leave empty for default",
            default=template_data.get('color', '') if template_data else '',
            required=False,
            max_length=7
        )
        self.add_item(self.color_input)
        
        # Ping input
        self.ping_input = discord.ui.TextInput(
            label="Ping (@everyone, @here, or role name)",
            placeholder="Enter ping type or leave empty",
            default=template_data.get('ping', '') if template_data else '',
            required=False,
            max_length=50
        )
        self.add_item(self.ping_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        template_data = {
            'title': self.title_input.value,
            'content': self.content_input.value,
            'color': self.color_input.value or '#7c3aed',
            'ping': self.ping_input.value,
            'created_by': interaction.user.id,
            'created_at': discord.utils.utcnow().isoformat()
        }
        
        # Save template to file
        templates_file = 'announcement_templates.json'
        templates = {}
        
        if os.path.exists(templates_file):
            with open(templates_file, 'r') as f:
                templates = json.load(f)
        
        templates[self.template_name] = template_data
        
        with open(templates_file, 'w') as f:
            json.dump(templates, f, indent=2)
        
        await interaction.response.send_message(f"✅ Template '{self.template_name}' saved successfully!", ephemeral=True)

class AnnouncementTemplatesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.templates_file = 'announcement_templates.json'
    
    def has_staff_permissions(self, member):
        """Check if member has staff permissions"""
        if member.guild_permissions.administrator:
            return True
        staff_role_names = list(Config.MANAGEMENT_ROLES.keys())
        member_roles = [role.name for role in member.roles]
        return any(role in staff_role_names for role in member_roles)
    
    def load_templates(self):
        """Load templates from file"""
        if os.path.exists(self.templates_file):
            with open(self.templates_file, 'r') as f:
                return json.load(f)
        return {}
    
    @app_commands.command(name="create_template", description="Create a new announcement template")
    @app_commands.describe(name="Name for the template")
    async def create_template(self, interaction: discord.Interaction, name: str):
        if not self.has_staff_permissions(interaction.user):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return
        
        modal = AnnouncementTemplateModal(name)
        await interaction.response.send_modal(modal)
    
    @app_commands.command(name="edit_template", description="Edit an existing announcement template")
    @app_commands.describe(name="Name of the template to edit")
    async def edit_template(self, interaction: discord.Interaction, name: str):
        if not self.has_staff_permissions(interaction.user):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return
        
        templates = self.load_templates()
        if name not in templates:
            await interaction.response.send_message(f"❌ Template '{name}' not found.", ephemeral=True)
            return
        
        modal = AnnouncementTemplateModal(name, templates[name])
        await interaction.response.send_modal(modal)
    
    @app_commands.command(name="use_template", description="Use a template to send an announcement")
    @app_commands.describe(name="Name of the template to use")
    async def use_template(self, interaction: discord.Interaction, name: str):
        if not self.has_staff_permissions(interaction.user):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return
        
        templates = self.load_templates()
        if name not in templates:
            await interaction.response.send_message(f"❌ Template '{name}' not found.", ephemeral=True)
            return
        
        template = templates[name]
        
        # Get announcement channel
        announcement_channel = self.bot.get_channel(Config.ANNOUNCEMENT_CHANNEL)
        if not announcement_channel:
            await interaction.response.send_message("❌ Announcement channel not found.", ephemeral=True)
            return
        
        # Parse color
        try:
            color_hex = template['color'].replace('#', '')
            color = discord.Color(int(color_hex, 16))
        except:
            color = discord.Color(0x7c3aed)
        
        # Create embed
        embed = discord.Embed(
            title=f"📢 {template['title']}",
            description=template['content'],
            color=color,
            timestamp=discord.utils.utcnow()
        )
        embed.set_author(name=f"Sent by {interaction.user.display_name}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
        embed.set_footer(text="Monroe Social Club - Official Announcement")
        
        # Send announcement
        ping_text = ""
        if template['ping']:
            if template['ping'] == '@everyone':
                ping_text = "@everyone"
            elif template['ping'] == '@here':
                ping_text = "@here"
            else:
                # Look for role
                role = discord.utils.get(interaction.guild.roles, name=template['ping'])
                if role:
                    ping_text = role.mention
        
        await announcement_channel.send(content=ping_text, embed=embed)
        await interaction.response.send_message(f"✅ Announcement sent using template '{name}'!", ephemeral=True)
    
    @app_commands.command(name="list_templates", description="List all available announcement templates")
    async def list_templates(self, interaction: discord.Interaction):
        if not self.has_staff_permissions(interaction.user):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return
        
        templates = self.load_templates()
        if not templates:
            await interaction.response.send_message("No templates found. Use `/create_template` to create one!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="📋 Announcement Templates",
            description="Available templates for announcements",
            color=Config.COLORS["info"]
        )
        
        for name, template in templates.items():
            embed.add_field(
                name=f"📝 {name}",
                value=f"**Title:** {template['title']}\n**Content:** {template['content'][:50]}{'...' if len(template['content']) > 50 else ''}",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(AnnouncementTemplatesCog(bot))
