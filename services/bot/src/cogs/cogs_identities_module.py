from discord import (
    app_commands, 
    User, 
    Interaction,
    ui,
    TextStyle,
    Object as DObject
)
from discord.ext import commands
from src.util.ol_util import is_slow_wallet
from src.connect import session
from src.model import Contributor
from typing import Tuple
from datetime import datetime
from json import loads, dumps
from src.config import Config
from src.util.emoji import Emoji


class Identities(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @app_commands.command(name="account", description="update your primary wallet address")
    async def modal(self, interaction: Interaction):
        # Show thinking message:
        # await interaction.response.defer()
        
        # check is address is known
        dbid = Contributor.get_active_contributor_by_discord_id(interaction.user.id)
        if not dbid or len(dbid) == 0:
            message = f"{Emoji.print(Emoji, emoji_name='warning')} Only whitelisted contributors can manage their warrior identity."
            await interaction.response.send_message(message, ephemeral=True)
            return
        
        # push input form
        await interaction.response.send_modal(IdentityForm(interaction, dbid))
    
    @app_commands.command(name="whitelist", description="whitelist an account")
    async def whitelist(self, interaction: Interaction, account: User):
        """This command is only available to Working Groups Key Roles."""
        # TODO: add support for type 1 accounts (groups)
        # interaction.response.send_message("bla")
        # Show thinking message:
        await interaction.response.defer()
        if not hasattr(account, 'roles') or \
            Config.ROLE_NAME_KARMA_ADMIN not in [y.name for y in interaction.user.roles]:
            await interaction.followup.send(
                f"{Emoji.print(Emoji, emoji_name='warning')} Sorry, your account is not allowed to whitelist other accounts.", 
                ephemeral=True
            )
            return
        
        # check if user account already exists
        dbid = Contributor.get_contributor_by_discord_id(account.id)
        if dbid:
            # check if already flagged as active
            if dbid[3] == 1:
                message = f"{Emoji.print(Emoji, emoji_name='shrug')} This account is already whitelisted."
            else:
                # activate account
                if Contributor.activate_contributor(Contributor, account.id):
                    message = f"{Emoji.print(Emoji, emoji_name='check')} Account [{str(account)}] has been added to the whitelist."
                else:
                    message = f"{Emoji.print(Emoji, emoji_name='cross_red')} Something went wrong, we could not whitelist account [{str(account)}]."
            await interaction.followup.send(
                message, 
                ephemeral=True
            )
            return
        
        # add the new account to the db
        Contributor.add_contributor(account.id)
        await interaction.followup.send(
            f"{Emoji.print(Emoji, emoji_name='check')} Account [{str(account)}] has been added to the whitelist.", 
            ephemeral=True
        )
        return
    
    @app_commands.command(name="graylist", description="graylist an account")
    async def graylist(self, interaction: Interaction, account: User):
        """This command is only available to Working Groups Key Roles."""
        # TODO: add support for type 1 accounts (groups)
        # Show thinking message:
        await interaction.response.defer()
        if not hasattr(account, 'roles') or \
            Config.ROLE_NAME_KARMA_ADMIN not in [y.name for y in interaction.user.roles]:
            await interaction.followup.send(
                f"{Emoji.print(Emoji, emoji_name='warning')} Sorry, your account is not allowed to graylist other accounts.", 
                ephemeral=True
            )
            return
        
        # check if user account already exists
        dbid = Contributor.get_active_contributor_by_discord_id(account.id)
        if dbid:
            # deactivate user
            if Contributor.deactivate_contributor(Contributor, account.id):
                message = f"{Emoji.print(Emoji, emoji_name='check')} Account [{str(account)}] has been added to the graylist."
            else:
                message = f"{Emoji.print(Emoji, emoji_name='cross_red')} Something went wrong, we could not graylist account [{str(account)}]."
            await interaction.followup.send(
                message, 
                ephemeral=True
            )
            return
        
        await interaction.followup.send(
            f"{Emoji.print(Emoji, emoji_name='shrug')} Account [{str(account)}] is already graylisted.", 
            ephemeral=True
        )
        return


class IdentityForm(ui.Modal):
    account = ""

    def __init__(self, interaction: Interaction, dbid: Tuple):
        super().__init__(title=f"0L Warrior Identity")
        
        self.account = "" if not dbid[1] else dbid[1]
        
        # Define the textbox input
        self.account_input = ui.TextInput(
            label="0L Address (only slow wallets)", 
            style=TextStyle.short,
            placeholder="Insert slow wallet address", 
            required=True,
            default=self.account,
            max_length=32)
        
        # Add the textbox input to the form
        self.add_item(self.account_input)

    async def on_submit(self, interaction: Interaction):
        """
            This function is called when the user submits the form.
        """
        account_input = self.account_input.value.lower()
        if len(account_input) < 32:
            await interaction.followup.send(
                f"{Emoji.print(Emoji, emoji_name='cross_red')} Address must be 32 characters long.", 
                ephemeral=True
            )
            return

        # calling this function again in case identities have changed.
        dbid = Contributor.get_active_contributor_by_discord_id(interaction.user.id)
        if not dbid or len(dbid) == 0:
            await interaction.followup.send(
                f"{Emoji.print(Emoji, emoji_name='cross_red')} Your account doesn't seem to be whitelisted.", 
                ephemeral=True
            )
            return
        
        account_db = "" if not dbid[1] else dbid[1]
        val_check = is_slow_wallet(account_input)

        if account_db == account_input:
            message = f"{Emoji.print(Emoji, emoji_name='shrug')} Nothing changed."
        elif not val_check:
            message = f"{Emoji.print(Emoji, emoji_name='cross_red')} Something went wrong. Please try again or contact one of the administrators"
        elif val_check["status"] == "Error":
            message = f"{Emoji.print(Emoji, emoji_name='cross_red')} {val_check['message']}" 
        elif val_check["status"] == "Success":
            # wallet is a confirmed slow wallet!
            if Contributor.add_address(Contributor, interaction.user.id, account_input):
                message = f"{Emoji.print(Emoji, emoji_name='check')} Your identity has been saved!"
            else:
                message = f"{Emoji.print(Emoji, emoji_name='cross_red')} Something went wrong. Please try again or contact one of the administrators"
        
        # response.send_message because?
        await interaction.response.send_message(message, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Identities(bot)) # , guild=DObject(696335510037332020)
