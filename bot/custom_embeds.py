import discord
from discord.ext import commands
from discord import app_commands
from bot.config import Config

class CustomEmbedModal(discord.ui.Modal):
    def __init__(self, fields_count, channel):
        super().__init__(title="Custom Embed Creator")
        self.fields_count = fields_count
        self.channel = channel
        
        # Title (required)
        self.title_input = discord.ui.TextInput(
            label="Embed Title",
            placeholder="Enter the embed title...",
            required=True,
            max_length=256
        )
        self.add_item(self.title_input)
        
        # Description (required)
        self.description_input = discord.ui.TextInput(
            label="Embed Description", 
            placeholder="Enter the embed description...",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=4000
        )
        self.add_item(self.description_input)
        
        # Color (optional)
        self.color_input = discord.ui.TextInput(
            label="Embed Color (hex code)",
            placeholder="e.g., #FF0000 for red, leave empty for default",
            required=False,
            max_length=7
        )
        self.add_item(self.color_input)
        
        # Author (optional)
        self.author_input = discord.ui.TextInput(
            label="Author Name (optional)",
            placeholder="Enter author name...",
            required=False,
            max_length=256
        )
        self.add_item(self.author_input)
        
        # Footer (optional)
        self.footer_input = discord.ui.TextInput(
            label="Footer Text (optional)",
            placeholder="Enter footer text...",
            required=False,
            max_length=2048
        )
        self.add_item(self.footer_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        # Create embed
        color = discord.Color.default()
        if self.color_input.value:
            try:
                color_hex = self.color_input.value.replace('#', '')
                color = discord.Color(int(color_hex, 16))
            except ValueError:
                color = discord.Color.default()
        
        embed = discord.Embed(
            title=self.title_input.value,
            description=self.description_input.value,
            color=color,
            timestamp=discord.utils.utcnow()
        )
        
        # Add author if provided
        if self.author_input.value:
            embed.set_author(name=self.author_input.value)
        
        # Add footer if provided
        if self.footer_input.value:
            embed.set_footer(text=self.footer_input.value)
        
        # Store embed info for field modal
        self.embed = embed
        
        if self.fields_count > 0:
            # Show field modal
            field_modal = FieldModal(self.embed, self.fields_count, self.channel)
            await interaction.response.send_modal(field_modal)
        else:
            # Send embed directly
            try:
                await self.channel.send(embed=embed)
                await interaction.response.send_message("✅ Custom embed sent successfully!", ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"❌ Error sending embed: {str(e)}", ephemeral=True)

class FieldModal(discord.ui.Modal):
    def __init__(self, embed, fields_count, channel):
        super().__init__(title=f"Add {fields_count} Field{'s' if fields_count > 1 else ''}")
        self.embed = embed
        self.fields_count = fields_count
        self.channel = channel
        
        # Field 1
        if fields_count >= 1:
            self.field1_name = discord.ui.TextInput(
                label="Field 1 Name",
                placeholder="Enter field 1 name...",
                required=True,
                max_length=256
            )
            self.add_item(self.field1_name)
            
            self.field1_value = discord.ui.TextInput(
                label="Field 1 Description",
                placeholder="Enter field 1 description...",
                style=discord.TextStyle.paragraph,
                required=True,
                max_length=1024
            )
            self.add_item(self.field1_value)
        
        # Field 2
        if fields_count >= 2:
            self.field2_name = discord.ui.TextInput(
                label="Field 2 Name",
                placeholder="Enter field 2 name...",
                required=True,
                max_length=256
            )
            self.add_item(self.field2_name)
            
            self.field2_value = discord.ui.TextInput(
                label="Field 2 Description", 
                placeholder="Enter field 2 description...",
                style=discord.TextStyle.paragraph,
                required=True,
                max_length=1024
            )
            self.add_item(self.field2_value)
        
        # Field 3 (only if exactly 3 fields, due to modal limit of 5 components)
        if fields_count == 3:
            self.field3_name = discord.ui.TextInput(
                label="Field 3 Name",
                placeholder="Enter field 3 name...",
                required=True,
                max_length=256
            )
            self.add_item(self.field3_name)
    
    async def on_submit(self, interaction: discord.Interaction):
        # Add fields to embed
        if self.fields_count >= 1:
            self.embed.add_field(
                name=self.field1_name.value,
                value=self.field1_value.value,
                inline=False
            )
        
        if self.fields_count >= 2:
            self.embed.add_field(
                name=self.field2_name.value,
                value=self.field2_value.value,
                inline=False
            )
        
        if self.fields_count == 3:
            # For field 3, we need another modal due to component limit
            field3_modal = Field3Modal(self.embed, self.field3_name.value, self.channel)
            await interaction.response.send_modal(field3_modal)
            return
        
        # Send embed
        try:
            await self.channel.send(embed=self.embed)
            await interaction.response.send_message("✅ Custom embed with fields sent successfully!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error sending embed: {str(e)}", ephemeral=True)

class Field3Modal(discord.ui.Modal):
    def __init__(self, embed, field3_name, channel):
        super().__init__(title="Field 3 Description")
        self.embed = embed
        self.field3_name = field3_name
        self.channel = channel
        
        self.field3_value = discord.ui.TextInput(
            label="Field 3 Description",
            placeholder="Enter field 3 description...",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=1024
        )
        self.add_item(self.field3_value)
    
    async def on_submit(self, interaction: discord.Interaction):
        # Add field 3
        self.embed.add_field(
            name=self.field3_name,
            value=self.field3_value.value,
            inline=False
        )
        
        # Send embed
        try:
            await self.channel.send(embed=self.embed)
            await interaction.response.send_message("✅ Custom embed with all fields sent successfully!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error sending embed: {str(e)}", ephemeral=True)

class ImageModal(discord.ui.Modal):
    def __init__(self, embed, channel):
        super().__init__(title="Add Image to Embed")
        self.embed = embed
        self.channel = channel
        
        self.image_url = discord.ui.TextInput(
            label="Image URL",
            placeholder="Enter image URL (must be https://...)...",
            required=True,
            max_length=2000
        )
        self.add_item(self.image_url)
    
    async def on_submit(self, interaction: discord.Interaction):
        # Add image to embed
        try:
            self.embed.set_image(url=self.image_url.value)
            await self.channel.send(embed=self.embed)
            await interaction.response.send_message("✅ Custom embed with image sent successfully!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error sending embed: {str(e)}", ephemeral=True)

class CustomEmbedsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def has_management_permissions(self, member):
        """Check if member has management permissions"""
        management_role_names = list(Config.MANAGEMENT_ROLES.keys())
        member_roles = [role.name for role in member.roles]
        return any(role in management_role_names for role in member_roles) or member.guild_permissions.manage_guild
    
    @app_commands.command(name="custom_embed", description="Create and send a custom embed (Management only)")
    @app_commands.describe(
        channel="Channel to send the embed to",
        fields="Number of fields to add (0-3)",
        image="Add an image to the embed"
    )
    @app_commands.choices(fields=[
        app_commands.Choice(name="No fields", value=0),
        app_commands.Choice(name="1 field", value=1),
        app_commands.Choice(name="2 fields", value=2),
        app_commands.Choice(name="3 fields", value=3)
    ])
    async def custom_embed(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        fields: int = 0,
        image: bool = False
    ):
        # Check permissions
        if not self.has_management_permissions(interaction.user):
            await interaction.response.send_message("❌ You don't have permission to use this command. Management only.", ephemeral=True)
            return
        
        # Check if bot can send messages in the target channel
        bot_member = interaction.guild.get_member(self.bot.user.id)
        if not bot_member or not channel.permissions_for(bot_member).send_messages:
            await interaction.response.send_message(f"❌ I don't have permission to send messages in {channel.mention}.", ephemeral=True)
            return
        
        # Store image flag for later use
        self.image_flag = image
        
        # Show modal for embed creation
        modal = CustomEmbedModal(fields, channel)
        await interaction.response.send_modal(modal)

async def setup(bot):
    await bot.add_cog(CustomEmbedsCog(bot))