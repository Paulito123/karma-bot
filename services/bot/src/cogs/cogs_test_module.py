import discord
from discord import ui, app_commands
from discord.ext import commands
from src.util import github_util


class JarryJarry(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="test", description="Testing 1 2 3")
    async def test(self, interaction: discord.Interaction, account: discord.User):
        await interaction.response.send_message("Testing works!", ephemeral=True)
        await interaction.response.defer()


async def setup(bot: commands.Bot):
    await bot.add_cog(JarryJarry(bot))
