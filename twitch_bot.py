import asyncio
import os
from twitchio.ext import commands
from dotenv import load_dotenv
load_dotenv(dotenv_path="common_creds.env", override=True)
load_dotenv(dotenv_path="development.env", override=True)
ACCESS_TOKEN =os.getenv('ACCESS_TOKEN')
REFRESH_TOKEN =os.getenv('REFRESH_TOKEN')
CLIENT_ID =os.getenv('CLIENT_ID')

class Bot(commands.Bot):
    def __init__(self):
        # 1. Put your Client ID here
        # 2. prefix is what starts a command
        super().__init__(
            client_id=CLIENT_ID, 
            prefix='!', 
            initial_channels=['your_channel_name']
        )

    async def setup_hook(self):
        # This part registers your tokens so the bot can REFRESH them automatically
        # Replace these strings with your actual tokens
        await self.add_token(
            token=ACCESS_TOKEN, 
            refresh=REFRESH_TOKEN
        )

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')
        print(f'User ID is | {self.user_id}')

    # --- YOUR CUSTOM TOPIC COMMAND ---
    @commands.command()
    async def topic(self, ctx, *, message: str):
        # Logic: Only allow the Broadcaster or Mods to change the topic
        if ctx.author.is_mod or ctx.author.name.lower() == 'your_channel_name':
            print(f"New topic received: {message}")
            
            # Here you can add your API call or save to a file
            # Example: open("topic.txt", "w").write(message)
            
            await ctx.send(f"Topic has been updated to: {message}")
        else:
            await ctx.send(f"@{ctx.author.name}, only mods can use that!")

# Create and run the bot
bot = Bot()
bot.run()