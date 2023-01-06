import discord
import os
import sys
from discord.ext import commands
from src.model import Contributor
# from src.util.github_util import get_identities


class Client(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents, command_prefix="/")
        self.synced = False

    async def setup_hook(self):
        print(f"\033[31mLogged in as {client.user}\033[39m")

        # load cogs
        cogs_folder = f"{os.path.abspath(os.path.dirname(__file__))}/src/cogs"
        for filename in os.listdir(cogs_folder):
            if filename.startswith("cogs_") and filename.endswith(".py"):
                print(f"loading {filename}")
                await client.load_extension(f"src.cogs.{filename[:-3]}")
        await client.tree.sync()
        
        print("Cogs loaded...")


if __name__ == "__main__":
    # Create the client app
    client = Client()

    # This script takes 1 or 0 arguments. If the first argument == 1, then 
    # the database is initially fed with data from the github file.
    if len(sys.argv) > 1:
        if sys.argv[1] == "1":
            ...
            # data = get_identities()
            # print(data)
            # Contributor.load_contrib_data(data)

    # Start the client app
    client.run(os.getenv("DISCORD_BOT_SECRET"))
