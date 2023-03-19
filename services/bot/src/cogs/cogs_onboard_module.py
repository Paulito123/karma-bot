from discord import (
    app_commands, 
    User, 
    Interaction,
    ui,
    TextStyle
)
from discord.ext import commands
from src.util.ol_util import is_valid_address_format
from src.model import OnboardLog
from src.config import Config
from src.util.emoji import Emoji
from re import search


class Onboard(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @app_commands.command(name="onboard", description="onboard an account")
    async def onboard(self, interaction: Interaction):
        req_cnt_24h = OnboardLog.get_req_cnt_24h()
        if req_cnt_24h >= Config.DAILY_ONBOARD_QUOTA:
            message = f"{Emoji.print(Emoji, emoji_name='warning')} Only whitelisted contributors can manage their warrior address."
            await interaction.response.send_message(message, ephemeral=True)

        # push input form
        await interaction.response.send_modal(AuthKeyForm(interaction))


class AuthKeyForm(ui.Modal):
    
    def __init__(self, interaction: Interaction):
        """ AuthKeyForm contructor """

        super().__init__(title=f"Onboard my account")

        # Define the textbox input
        self.auth_account_input = ui.TextInput(
            label="Please insert auth key (64 chars)", 
            style=TextStyle.long,
            placeholder="Insert authentication key (64 chars) here...", 
            required=True,
            max_length=64)
        
        # Add the textbox input to the form
        self.add_item(self.auth_account_input)

    async def on_submit(self, interaction: Interaction):
        """ This function is called when the user submits the form. """

        # checkking account address validity
        account_input = self.auth_account_input.value.lower()
        if not is_valid_address_format(account_input, 64):
            await interaction.response.send_message(
                f"{Emoji.print(Emoji, emoji_name='cross_red')} Input must be a valid 0L authentication address.", 
                ephemeral=True
            )
            return
        
        # Try to put the address in the queue
        message = OnboardLog.queue_onboard_request(
            interaction.user.id,
            interaction.user.name,
            account_input
        )

        if not message:
            # error happened when trying to use tools to access chain
            message = f"{Emoji.print(Emoji, emoji_name='cross_red')} Something went wrong. Please try again or contact one of the administrators."
        elif message["status"] == "Error":
            # pass message that is returned from chain tools
            message = f"{Emoji.print(Emoji, emoji_name='cross_red')} {message['message']}" 
        elif message["status"] == "Success":
            # auth account has been added to the queue for onboarding
            message = f"{Emoji.print(Emoji, emoji_name='check')} Your address has been added to the queue. It can take up to 1 minute before your address is onboarded!"
        
        # send message back
        await interaction.response.send_message(message, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(AuthKeyForm(bot))
    # await bot.add_cog(Identities(bot), guild=DObject(int(Config.DISCORD_BOT_CHANNEL_ID)))
