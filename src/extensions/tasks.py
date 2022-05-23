from asyncio import tasks
from pydoc import doc
import random, discord, datetime, motor, motor.motor_asyncio, os, sys
import src.utilities as utilities
from discord.commands import slash_command
from discord.commands import Option
from discord.ext import commands, tasks
from dotenv import load_dotenv
from colorama import Fore
from mcstatus import JavaServer

#intialize error_logger & error_message
error_logger = utilities.ErrorLogger("Tasks")

#mongodb setup
try:
    load_dotenv("src\secrets\.env")
except: pass

def mongo_init():
    mongo_password=os.getenv("MONGO_PASSWORD")
    cluster = motor.motor_asyncio.AsyncIOMotorClient("mongodb+srv://TechnoTalks:"+mongo_password+"@main.rpbbi.mongodb.net/reko?retryWrites=true&w=majority")
    db = cluster.reko
    tracking_coll = db.tracking
    return tracking_coll

color=0x6bf414

guild_cache = {
    "Example": [datetime.datetime.now, ["TechnoTalks, garvinator123"]]
}


class tasksCog(commands.Cog):
    #init function
    def __init__(self, bot):
        self.bot = bot
        #ticks from start counter
        self.index = 0
        #self.{name of async looped function}
        self.tick.start()
        self.track.start()
        self.status.start()

    def cog_unload(self):
        #cancel tasks on cog unload
        self.tick.cancel()
        self.track.cancel()
        self.status.cancel()
    #Looped Tasks
    @tasks.loop(seconds=30.0)
    async def tick(self):
        tick = str(self.index)
        
        print("\n[Reko] {"+datetime.datetime.now().strftime("%H:%M:%S")+"} Tick: "+tick+f" {round(self.bot.latency * 1000)}ms")

        self.index += 1
        
    @tasks.loop(seconds=5.0)
    async def track(self):
        coll = mongo_init()
        cursor = coll.find().sort([('_id', 1)])
        docs = await cursor.to_list(length=None)

        for guild in docs:
            guild_id = guild["_id"]
            ip = guild["trackip"]
            port = guild["trackport"]
            channel_id = guild["trackchannel"]

            channel =  self.bot.get_channel(channel_id)

            if channel == None:
                return
            #print(f"[Tasks] (Debug) IP:{ip}, Port: {port}, Port Type: {type(port)} ")
            
            try:
                server = JavaServer(ip, port, 4)
                status = await server.async_status()
                player_count = status.players.online
            
            except Exception as e: 
                await channel.send(embed=utilities.error_message())
                return
            #player_count = info["players"]["online"]
            current = {guild_id: [player_count]}
            
            if guild_id in guild_cache:
                
                if player_count != guild_cache[guild_id][0]:

                    if player_count > guild_cache[guild_id][0]:
                        
                        if player_count - guild_cache[guild_id][0] == 1:
                            await channel.send(f"> A player has **joined** the server! 😁")

                        else:
                            players = player_count - guild_cache[guild_id][0]
                            await channel.send(f"> **{players}** players have **joined** the server! 😁")

                    elif player_count < guild_cache[guild_id][0]:

                        if guild_cache[guild_id][0] - player_count == 1:
                            await channel.send(f"> A player has **left** the server! 😢")
                        
                        else:
                            players = guild_cache[guild_id][0] - player_count
                            await channel.send(f"> **{players}** players have **left** the server! 😢")
                    
                    guild_cache.update(current)

            else:
                guild_cache.update(current)
    @tasks.loop(seconds=60.0)
    async def status(self):
        choice=random.randint(1,4)
        
        if choice == 1:
            await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Beta Release 🤖"))
        
        elif choice == 2:
            await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="LoFi"))
        
        elif choice ==  3:
            await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Minecraft Servers"))
        
        else:
            await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="Minecraft"))
    #Make sure to wait before bot start to begin looping tasks
    @tick.before_loop
    async def before_tick(self):
        await self.bot.wait_until_ready()
    @tick.error
    async def tickerror(self, error):
        error_logger.log("Tick", error, sys.exc_info()[-1])
    
    @track.before_loop
    async def before_track(self):
        await self.bot.wait_until_ready()
    @track.error
    async def trackerror(self, error):
        error_logger.log("Tracking", error, sys.exc_info()[-1])
    
    @status.before_loop
    async def before_status(self):
        await self.bot.wait_until_ready()
    @status.error
    async def statuserror(self, error):
        error_logger.log("Status", error, sys.exc_info()[-1])

def setup(bot):
    print("[Tasks] Loading extension...")
    bot.add_cog(tasksCog(bot))
def teardown(bot):
    print("[Tasks] Unloading extension...")