import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import asyncio
from bot.config import Config

class RobloxCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_rover_data(self, discord_id):
        """Get Roblox data from Rover API"""
        try:
            async with aiohttp.ClientSession() as session:
                # Get Discord to Roblox mapping from Rover
                async with session.get(f"{Config.ROVER_API_BASE}/guilds/{Config.ROBLOX_GROUP_ID}/discord-to-roblox/{discord_id}") as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    return None
        except Exception as e:
            print(f"Error fetching Rover data: {e}")
            return None

    async def get_roblox_user_info(self, roblox_id):
        """Get Roblox user information"""
        try:
            async with aiohttp.ClientSession() as session:
                # Get user info from Roblox API
                async with session.get(f"https://users.roblox.com/v1/users/{roblox_id}") as response:
                    if response.status == 200:
                        return await response.json()
                    return None
        except Exception as e:
            print(f"Error fetching Roblox user info: {e}")
            return None

    async def get_roblox_avatar_headshot(self, roblox_id):
        """Get Roblox user avatar headshot"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={roblox_id}&size=420x420&format=Png&isCircular=false") as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("data") and len(data["data"]) > 0:
                            return data["data"][0].get("imageUrl")
                    return None
        except Exception as e:
            print(f"Error fetching Roblox avatar: {e}")
            return None

    async def get_group_info(self, group_id):
        """Get Roblox group information"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://groups.roblox.com/v1/groups/{group_id}") as response:
                    if response.status == 200:
                        return await response.json()
                    return None
        except Exception as e:
            print(f"Error fetching group info: {e}")
            return None

    async def get_user_group_role(self, roblox_id, group_id):
        """Get user's role in a specific group"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://groups.roblox.com/v2/users/{roblox_id}/groups/roles") as response:
                    if response.status == 200:
                        data = await response.json()
                        for group in data.get("data", []):
                            if group.get("group", {}).get("id") == group_id:
                                return group.get("role", {})
                    return None
        except Exception as e:
            print(f"Error fetching user group role: {e}")
            return None

    @app_commands.command(name="verify", description="Link your Discord account with your Roblox account")
    async def verify(self, interaction: discord.Interaction):
        """Help users verify their Roblox account"""
        embed = discord.Embed(
            title="🔗 Roblox Account Verification",
            description="To link your Roblox account with Discord, please use RoVer!",
            color=Config.COLORS["info"]
        )
        
        embed.add_field(
            name="📝 How to Verify",
            value="1. Visit [RoVer](https://rover.link/)\n2. Log in with Discord\n3. Link your Roblox account\n4. Use `/get_profile` to view your info!",
            inline=False
        )
        
        embed.add_field(
            name="🏖️ Monroe Social Club Group",
            value=f"Group ID: {Config.ROBLOX_GROUP_ID}\nJoin our group for exclusive perks!",
            inline=True
        )
        
        embed.add_field(
            name="🎮 Experience Our Game",
            value=f"Map ID: {Config.ROBLOX_MAP_ID}\nJoin the ultimate 80s beach party!",
            inline=True
        )
        
        embed.set_footer(text="Monroe Social Club - Verification System")
        embed.timestamp = discord.utils.utcnow()
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="get_profile", description="Get a user's Roblox profile information")
    @app_commands.describe(user="The Discord user to get Roblox info for (leave empty for yourself)")
    async def get_profile(self, interaction: discord.Interaction, user: discord.Member = None):
        target_user = user or interaction.user
        
        # Defer response as this might take a moment
        await interaction.response.defer()
        
        # Get Rover data
        rover_data = await self.get_rover_data(target_user.id)
        if not rover_data:
            embed = discord.Embed(
                title="❌ Account Not Verified",
                description=f"{target_user.mention} hasn't linked their Roblox account yet.",
                color=Config.COLORS["error"]
            )
            embed.add_field(
                name="🔗 How to Verify",
                value="Use `/verify` to learn how to link your Roblox account!",
                inline=False
            )
            await interaction.followup.send(embed=embed)
            return

        roblox_id = rover_data.get("robloxId")
        if not roblox_id:
            embed = discord.Embed(
                title="❌ No Roblox ID Found",
                description="Could not retrieve Roblox ID from verification data.",
                color=Config.COLORS["error"]
            )
            await interaction.followup.send(embed=embed)
            return

        # Get Roblox user info
        roblox_info = await self.get_roblox_user_info(roblox_id)
        if not roblox_info:
            embed = discord.Embed(
                title="❌ Roblox Profile Not Found",
                description="Could not retrieve Roblox profile information.",
                color=Config.COLORS["error"]
            )
            await interaction.followup.send(embed=embed)
            return

        # Get avatar headshot
        avatar_url = await self.get_roblox_avatar_headshot(roblox_id)
        
        # Get group role
        group_role = await self.get_user_group_role(roblox_id, Config.ROBLOX_GROUP_ID)
        
        # Create profile embed
        embed = discord.Embed(
            title=f"🎮 Roblox Profile - {roblox_info['displayName']}",
            description=f"Profile information for {target_user.mention}",
            color=Config.COLORS["info"],
            url=f"https://www.roblox.com/users/{roblox_id}/profile"
        )
        
        embed.add_field(
            name="👤 Username",
            value=f"@{roblox_info['name']}",
            inline=True
        )
        
        embed.add_field(
            name="🆔 User ID",
            value=str(roblox_id),
            inline=True
        )
        
        embed.add_field(
            name="📝 Display Name",
            value=roblox_info['displayName'],
            inline=True
        )
        
        if roblox_info.get('description'):
            embed.add_field(
                name="📄 Bio",
                value=roblox_info['description'][:1000] + ("..." if len(roblox_info['description']) > 1000 else ""),
                inline=False
            )
        
        # Add group role if in Monroe Social Club
        if group_role:
            embed.add_field(
                name="🏖️ Monroe Social Club Role",
                value=f"**{group_role.get('name', 'Member')}**\nRank: {group_role.get('rank', 0)}",
                inline=True
            )
        else:
            embed.add_field(
                name="🏖️ Monroe Social Club",
                value="Not a member\n[Join our group!](https://www.roblox.com/groups/35828136)",
                inline=True
            )
        
        if roblox_info.get('created'):
            embed.add_field(
                name="📅 Account Created",
                value=roblox_info['created'][:10],  # Just the date part
                inline=True
            )
        
        # Set avatar if available
        if avatar_url:
            embed.set_thumbnail(url=avatar_url)
        
        embed.set_footer(text="Monroe Social Club - Roblox Integration", icon_url=self.bot.user.avatar.url)
        embed.timestamp = discord.utils.utcnow()
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="group_info", description="Get information about the Monroe Social Club Roblox group")
    async def group_info(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        group_info = await self.get_group_info(Config.ROBLOX_GROUP_ID)
        if not group_info:
            embed = discord.Embed(
                title="❌ Group Not Found",
                description="Could not retrieve group information.",
                color=Config.COLORS["error"]
            )
            await interaction.followup.send(embed=embed)
            return

        embed = discord.Embed(
            title=f"🏖️ {group_info['name']}",
            description=group_info.get('description', 'Welcome to Monroe Social Club!'),
            color=Config.COLORS["info"],
            url=f"https://www.roblox.com/groups/{Config.ROBLOX_GROUP_ID}"
        )
        
        embed.add_field(
            name="👥 Members",
            value=f"{group_info.get('memberCount', 0):,}",
            inline=True
        )
        
        embed.add_field(
            name="🆔 Group ID",
            value=str(Config.ROBLOX_GROUP_ID),
            inline=True
        )
        
        embed.add_field(
            name="👑 Owner",
            value=group_info.get('owner', {}).get('displayName', 'Unknown'),
            inline=True
        )
        
        embed.add_field(
            name="🎮 Game Experience",
            value=f"Map ID: {Config.ROBLOX_MAP_ID}\nJoin the 80s beach party!",
            inline=False
        )
        
        if group_info.get('shout'):
            shout = group_info['shout']
            embed.add_field(
                name="📢 Latest Shout",
                value=f"**{shout.get('poster', {}).get('displayName', 'Unknown')}**: {shout.get('body', 'No shout available')}",
                inline=False
            )
        
        embed.set_footer(text="Monroe Social Club - 80s Beach Vibes 🌴")
        embed.timestamp = discord.utils.utcnow()
        
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(RobloxCog(bot))
