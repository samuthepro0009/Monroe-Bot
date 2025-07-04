
import discord
from discord.ext import commands, tasks
from discord import app_commands
from bot.config import Config
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio

class ActivityLeaderboardCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # Session-based storage (resets when bot restarts)
        self.activity_data = defaultdict(lambda: {
            'messages': 0,
            'voice_time': 0,
            'reactions_given': 0,
            'reactions_received': 0,
            'commands_used': 0,
            'last_active': datetime.utcnow(),
            'join_time': None,
            'voice_join_time': None,
            'streak_days': 0
        })
        
        # Session achievements
        self.achievements = {
            'chatter': {'threshold': 50, 'emoji': '💬', 'name': 'Chatter'},
            'social_butterfly': {'threshold': 25, 'emoji': '🦋', 'name': 'Social Butterfly'},
            'voice_master': {'threshold': 3600, 'emoji': '🎤', 'name': 'Voice Master'},  # 1 hour
            'commander': {'threshold': 10, 'emoji': '⚡', 'name': 'Commander'},
            'popular': {'threshold': 20, 'emoji': '⭐', 'name': 'Popular'},
            'night_owl': {'threshold': 1, 'emoji': '🦉', 'name': 'Night Owl'},
            'early_bird': {'threshold': 1, 'emoji': '🐦', 'name': 'Early Bird'}
        }
        
        # Start background tasks
        self.update_leaderboard.start()
    
    def cog_unload(self):
        self.update_leaderboard.cancel()
    
    @tasks.loop(minutes=5)
    async def update_leaderboard(self):
        """Update voice channel times"""
        for guild in self.bot.guilds:
            for member in guild.members:
                if member.voice and member.voice.channel:
                    user_id = member.id
                    if self.activity_data[user_id]['voice_join_time']:
                        # Add time since last update
                        time_diff = (datetime.utcnow() - self.activity_data[user_id]['voice_join_time']).total_seconds()
                        self.activity_data[user_id]['voice_time'] += time_diff
                    self.activity_data[user_id]['voice_join_time'] = datetime.utcnow()
    
    @update_leaderboard.before_loop
    async def before_update_leaderboard(self):
        await self.bot.wait_until_ready()
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Track message activity"""
        if message.author.bot or not message.guild:
            return
        
        user_id = message.author.id
        self.activity_data[user_id]['messages'] += 1
        self.activity_data[user_id]['last_active'] = datetime.utcnow()
        
        # Check for achievements
        await self.check_achievements(message.author, message.channel)
    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """Track reaction activity"""
        if user.bot or not reaction.message.guild:
            return
        
        # User giving reaction
        self.activity_data[user.id]['reactions_given'] += 1
        
        # User receiving reaction
        if not reaction.message.author.bot:
            self.activity_data[reaction.message.author.id]['reactions_received'] += 1
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Track voice channel activity"""
        if member.bot:
            return
        
        user_id = member.id
        
        # Joined voice channel
        if after.channel and not before.channel:
            self.activity_data[user_id]['voice_join_time'] = datetime.utcnow()
        
        # Left voice channel
        elif before.channel and not after.channel:
            if self.activity_data[user_id]['voice_join_time']:
                time_diff = (datetime.utcnow() - self.activity_data[user_id]['voice_join_time']).total_seconds()
                self.activity_data[user_id]['voice_time'] += time_diff
                self.activity_data[user_id]['voice_join_time'] = None
    
    @commands.Cog.listener()
    async def on_app_command_completion(self, interaction, command):
        """Track command usage"""
        if interaction.user.bot:
            return
        
        user_id = interaction.user.id
        self.activity_data[user_id]['commands_used'] += 1
        self.activity_data[user_id]['last_active'] = datetime.utcnow()
    
    async def check_achievements(self, user, channel):
        """Check and award achievements"""
        user_id = user.id
        data = self.activity_data[user_id]
        
        achievements_earned = []
        
        # Check message-based achievements
        if data['messages'] >= self.achievements['chatter']['threshold']:
            achievements_earned.append('chatter')
        
        if data['reactions_given'] >= self.achievements['social_butterfly']['threshold']:
            achievements_earned.append('social_butterfly')
        
        if data['voice_time'] >= self.achievements['voice_master']['threshold']:
            achievements_earned.append('voice_master')
        
        if data['commands_used'] >= self.achievements['commander']['threshold']:
            achievements_earned.append('commander')
        
        if data['reactions_received'] >= self.achievements['popular']['threshold']:
            achievements_earned.append('popular')
        
        # Time-based achievements
        current_hour = datetime.utcnow().hour
        if current_hour >= 22 or current_hour <= 6:  # Night owl (10 PM - 6 AM)
            achievements_earned.append('night_owl')
        elif current_hour >= 5 and current_hour <= 9:  # Early bird (5 AM - 9 AM)
            achievements_earned.append('early_bird')
        
        # Award achievements (simplified - just track them)
        for achievement in achievements_earned:
            if achievement not in data.get('achievements', set()):
                if 'achievements' not in data:
                    data['achievements'] = set()
                data['achievements'].add(achievement)
    
    def calculate_activity_score(self, user_data):
        """Calculate activity score"""
        score = 0
        score += user_data['messages'] * 2
        score += user_data['voice_time'] // 60  # 1 point per minute
        score += user_data['reactions_given'] * 1
        score += user_data['reactions_received'] * 3
        score += user_data['commands_used'] * 5
        score += len(user_data.get('achievements', set())) * 25
        
        return score
    
    @app_commands.command(name="leaderboard", description="View the activity leaderboard")
    @app_commands.describe(category="Category to view")
    @app_commands.choices(category=[
        app_commands.Choice(name="📊 Overall Activity", value="overall"),
        app_commands.Choice(name="💬 Messages", value="messages"),
        app_commands.Choice(name="🎤 Voice Time", value="voice"),
        app_commands.Choice(name="⭐ Reactions", value="reactions"),
        app_commands.Choice(name="⚡ Commands", value="commands"),
        app_commands.Choice(name="🏆 Achievements", value="achievements")
    ])
    async def leaderboard(self, interaction: discord.Interaction, category: str = "overall"):
        """Display activity leaderboard"""
        if not self.activity_data:
            await interaction.response.send_message("No activity data available yet! Start chatting to build the leaderboard! 🌴", ephemeral=True)
            return
        
        # Filter to guild members only
        guild_members = {uid: data for uid, data in self.activity_data.items() 
                        if interaction.guild.get_member(uid)}
        
        if not guild_members:
            await interaction.response.send_message("No activity data for this server yet! 🏖️", ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"🏆 Monroe Social Club - Activity Leaderboard",
            color=Config.COLORS["pink"],
            timestamp=datetime.utcnow()
        )
        
        if category == "overall":
            # Sort by activity score
            sorted_users = sorted(guild_members.items(), 
                                key=lambda x: self.calculate_activity_score(x[1]), 
                                reverse=True)
            embed.description = "📊 **Overall Activity Rankings**"
            
            for i, (user_id, data) in enumerate(sorted_users[:10], 1):
                member = interaction.guild.get_member(user_id)
                if member:
                    score = self.calculate_activity_score(data)
                    medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                    embed.add_field(
                        name=f"{medal} {member.display_name}",
                        value=f"**Score:** {score:,}\n**Messages:** {data['messages']}\n**Voice:** {data['voice_time']//60:.0f}m",
                        inline=True
                    )
        
        elif category == "messages":
            sorted_users = sorted(guild_members.items(), 
                                key=lambda x: x[1]['messages'], 
                                reverse=True)
            embed.description = "💬 **Message Champions**"
            
            for i, (user_id, data) in enumerate(sorted_users[:10], 1):
                member = interaction.guild.get_member(user_id)
                if member:
                    medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                    embed.add_field(
                        name=f"{medal} {member.display_name}",
                        value=f"**Messages:** {data['messages']:,}",
                        inline=True
                    )
        
        elif category == "voice":
            sorted_users = sorted(guild_members.items(), 
                                key=lambda x: x[1]['voice_time'], 
                                reverse=True)
            embed.description = "🎤 **Voice Masters**"
            
            for i, (user_id, data) in enumerate(sorted_users[:10], 1):
                member = interaction.guild.get_member(user_id)
                if member:
                    hours = data['voice_time'] // 3600
                    minutes = (data['voice_time'] % 3600) // 60
                    medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                    embed.add_field(
                        name=f"{medal} {member.display_name}",
                        value=f"**Time:** {hours:.0f}h {minutes:.0f}m",
                        inline=True
                    )
        
        elif category == "reactions":
            sorted_users = sorted(guild_members.items(), 
                                key=lambda x: x[1]['reactions_received'], 
                                reverse=True)
            embed.description = "⭐ **Most Popular**"
            
            for i, (user_id, data) in enumerate(sorted_users[:10], 1):
                member = interaction.guild.get_member(user_id)
                if member:
                    medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                    embed.add_field(
                        name=f"{medal} {member.display_name}",
                        value=f"**Received:** {data['reactions_received']}\n**Given:** {data['reactions_given']}",
                        inline=True
                    )
        
        elif category == "commands":
            sorted_users = sorted(guild_members.items(), 
                                key=lambda x: x[1]['commands_used'], 
                                reverse=True)
            embed.description = "⚡ **Command Masters**"
            
            for i, (user_id, data) in enumerate(sorted_users[:10], 1):
                member = interaction.guild.get_member(user_id)
                if member:
                    medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                    embed.add_field(
                        name=f"{medal} {member.display_name}",
                        value=f"**Commands:** {data['commands_used']:,}",
                        inline=True
                    )
        
        elif category == "achievements":
            sorted_users = sorted(guild_members.items(), 
                                key=lambda x: len(x[1].get('achievements', set())), 
                                reverse=True)
            embed.description = "🏆 **Achievement Hunters**"
            
            for i, (user_id, data) in enumerate(sorted_users[:10], 1):
                member = interaction.guild.get_member(user_id)
                if member:
                    achievements = data.get('achievements', set())
                    medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                    embed.add_field(
                        name=f"{medal} {member.display_name}",
                        value=f"**Achievements:** {len(achievements)}\n{' '.join([self.achievements[a]['emoji'] for a in achievements][:5])}",
                        inline=True
                    )
        
        embed.set_footer(text="Monroe Social Club - Session Leaderboard (Resets on Bot Restart)")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="my_activity", description="View your activity stats")
    async def my_activity(self, interaction: discord.Interaction):
        """Display user's activity stats"""
        user_id = interaction.user.id
        
        if user_id not in self.activity_data:
            await interaction.response.send_message("You haven't been active yet! Start chatting to build your stats! 🌴", ephemeral=True)
            return
        
        data = self.activity_data[user_id]
        score = self.calculate_activity_score(data)
        
        embed = discord.Embed(
            title=f"📊 {interaction.user.display_name}'s Activity Stats",
            color=Config.COLORS["info"],
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="🎯 Activity Score",
            value=f"**{score:,}** points",
            inline=True
        )
        
        embed.add_field(
            name="💬 Messages",
            value=f"**{data['messages']:,}** sent",
            inline=True
        )
        
        embed.add_field(
            name="🎤 Voice Time",
            value=f"**{data['voice_time']//3600:.0f}h {(data['voice_time']%3600)//60:.0f}m**",
            inline=True
        )
        
        embed.add_field(
            name="⭐ Reactions",
            value=f"**Given:** {data['reactions_given']}\n**Received:** {data['reactions_received']}",
            inline=True
        )
        
        embed.add_field(
            name="⚡ Commands",
            value=f"**{data['commands_used']:,}** used",
            inline=True
        )
        
        achievements = data.get('achievements', set())
        if achievements:
            achievement_text = "\n".join([
                f"{self.achievements[a]['emoji']} {self.achievements[a]['name']}"
                for a in achievements
            ])
            embed.add_field(
                name="🏆 Achievements",
                value=achievement_text,
                inline=False
            )
        
        embed.set_thumbnail(url=interaction.user.avatar.url if interaction.user.avatar else None)
        embed.set_footer(text="Monroe Social Club - Your Session Stats")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(ActivityLeaderboardCog(bot))
