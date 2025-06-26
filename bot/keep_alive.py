import asyncio
import aiohttp
from discord.ext import commands, tasks

class KeepAlive(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.keep_alive_task.start()
    
    def cog_unload(self):
        self.keep_alive_task.cancel()
    
    @tasks.loop(minutes=5)
    async def keep_alive_task(self):
        """Keep alive ping every 5 minutes"""
        try:
            async with aiohttp.ClientSession() as session:
                # Ping a reliable service to keep the bot alive
                async with session.get('https://httpbin.org/get') as response:
                    if response.status == 200:
                        print("🏖️ Keep alive ping successful")
        except Exception as e:
            print(f"❌ Keep alive ping failed: {e}")
    
    @keep_alive_task.before_loop
    async def before_keep_alive_task(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(KeepAlive(bot))