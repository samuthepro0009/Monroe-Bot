import discord
from discord.ext import commands, tasks
from bot.config import Config
import random
import asyncio

class QOTDSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.qotd_task.start()
        self.chat_revive_task.start()
    
    def cog_unload(self):
        self.qotd_task.cancel()
        self.chat_revive_task.cancel()
    
    @tasks.loop(hours=24)
    async def qotd_task(self):
        """Send random QOTD at random times"""
        # Random delay between 0-23 hours
        delay = random.randint(0, 23 * 3600)
        await asyncio.sleep(delay)
        
        channel = self.bot.get_channel(Config.QOTD_CHAT_REVIVE_CHANNEL)
        if not channel:
            return
        
        question = random.choice(Config.QOTD_QUESTIONS)
        
        embed = discord.Embed(
            title="🌴 Question of the Day! 🌴",
            description=question,
            color=Config.COLORS["pink"]
        )
        embed.set_footer(text="Share your thoughts! Everyone's welcome to answer 💭")
        embed.timestamp = discord.utils.utcnow()
        
        await channel.send("@everyone", embed=embed)
    
    @tasks.loop(hours=12)
    async def chat_revive_task(self):
        """Send random chat revive messages"""
        # Random delay between 0-11 hours
        delay = random.randint(0, 11 * 3600)
        await asyncio.sleep(delay)
        
        channel = self.bot.get_channel(Config.QOTD_CHAT_REVIVE_CHANNEL)
        if not channel:
            return
        
        # Check if channel has been inactive (no messages in last 2 hours)
        try:
            last_message = None
            async for message in channel.history(limit=1):
                last_message = message
                break
            
            if last_message:
                time_since_last = discord.utils.utcnow() - last_message.created_at
                if time_since_last.total_seconds() < 7200:  # 2 hours
                    return  # Channel is active, don't revive
        except:
            pass  # If we can't check, continue anyway
        
        message = random.choice(Config.CHAT_REVIVE_MESSAGES)
        
        embed = discord.Embed(
            description=message,
            color=Config.COLORS["info"]
        )
        embed.set_footer(text="Monroe Social Club - Keeping the vibes alive! 🏖️")
        
        await channel.send("@everyone", embed=embed)
    
    @qotd_task.before_loop
    async def before_qotd_task(self):
        await self.bot.wait_until_ready()
    
    @chat_revive_task.before_loop
    async def before_chat_revive_task(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(QOTDSystem(bot))