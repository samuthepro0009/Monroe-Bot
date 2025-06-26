import discord
from discord.ext import commands, tasks
from bot.config import Config
import aiohttp
import asyncio

class RichPresence(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_presence.start()
    
    def cog_unload(self):
        self.update_presence.cancel()
    
    async def get_roblox_game_data(self):
        """Get current player count for the Roblox game"""
        try:
            async with aiohttp.ClientSession() as session:
                # First get universe ID from place ID
                place_url = f"https://apis.roblox.com/universes/v1/places/{Config.ROBLOX_MAP_ID}/universe"
                async with session.get(place_url) as response:
                    if response.status == 200:
                        universe_data = await response.json()
                        universe_id = universe_data.get('universeId')
                        
                        if universe_id:
                            # Get game data using universe ID
                            game_url = f"https://games.roblox.com/v1/games?universeIds={universe_id}"
                            async with session.get(game_url) as game_response:
                                if game_response.status == 200:
                                    game_data = await game_response.json()
                                    if game_data.get('data') and len(game_data['data']) > 0:
                                        game_info = game_data['data'][0]
                                        playing = game_info.get('playing', 0)
                                        visits = game_info.get('visits', 0)
                                        return playing, visits
        except Exception as e:
            print(f"Failed to fetch Roblox game data: {e}")
        
        return None, None
    
    @tasks.loop(minutes=2)
    async def update_presence(self):
        """Update bot's rich presence with Roblox game info"""
        try:
            playing, visits = await self.get_roblox_game_data()
            
            if playing is not None:
                # Create clickable game activity with current player count
                activity_text = f"🏖️ Monroe Social Club | {playing} online"
                activity = discord.Game(
                    name=activity_text,
                    url=Config.ROBLOX_GAME_LINK
                )
                print(f"✅ Updated rich presence: {activity_text} | {visits:,} total visits" if visits else f"✅ Updated rich presence: {activity_text}")
            else:
                # Fallback with clickable link
                activity = discord.Game(
                    name="🏖️ Monroe Social Club | Retro 80s Beach Vibes",
                    url=Config.ROBLOX_GAME_LINK
                )
                print("✅ Updated presence with fallback (clickable link)")
            
            await self.bot.change_presence(
                status=discord.Status.online,
                activity=activity
            )
            
        except Exception as e:
            print(f"Failed to update presence: {e}")
            # Set basic presence as fallback
            try:
                activity = discord.Activity(
                    type=discord.ActivityType.watching,
                    name="Monroe Social Club"
                )
                await self.bot.change_presence(
                    status=discord.Status.online,
                    activity=activity
                )
            except:
                pass
    
    @update_presence.before_loop
    async def before_update_presence(self):
        await self.bot.wait_until_ready()
        # Wait a bit for bot to fully initialize
        await asyncio.sleep(10)

async def setup(bot):
    await bot.add_cog(RichPresence(bot))