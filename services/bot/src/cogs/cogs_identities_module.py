from discord import (
    app_commands, 
    User, 
    Interaction,
    ui,
    TextStyle,
    Object as DObject
)
from discord.ext import commands
from src.util.ol_util import is_slow_wallet_as, is_valid_address_format
from src.model import Contributor
from typing import Tuple
from src.config import Config
from src.util.emoji import Emoji


class Identities(commands.Cog):
    def __init__(self, client):
        self.client = client
    
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
                f"{Emoji.print(Emoji, emoji_name='warning')} Sorry, your account does not have enough previleges to whitelist other accounts.", 
                ephemeral=True
            )
            return
        
        # check if user account already exists
        dbid = Contributor.get_contributor_by_discord_id(account.id)
        if dbid:
            # check if already flagged as active
            if dbid[3] == 1:
                message = f"{Emoji.print(Emoji, emoji_name='shrug')} [{str(account)}] is already whitelisted."
            else:
                # activate account
                if Contributor.activate_contributor(Contributor, account.id):
                    message = f"{Emoji.print(Emoji, emoji_name='check')} [{str(account)}] has been added to the whitelist."
                else:
                    message = f"{Emoji.print(Emoji, emoji_name='cross_red')} Something went wrong, [{str(account)}] could not be whitelisted."
            await interaction.followup.send(
                message, 
                ephemeral=True
            )
            return
        
        # add the new account to the db
        Contributor.add_contributor(account)
        await interaction.followup.send(
            f"{Emoji.print(Emoji, emoji_name='check')} [{str(account)}] has been added to the whitelist.", 
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
                f"{Emoji.print(Emoji, emoji_name='warning')} Sorry, your account does not have the previlege to graylist other accounts.", 
                ephemeral=True
            )
            return
        
        # check if user account already exists
        dbid = Contributor.get_active_contributor_by_discord_id(account.id)
        if dbid:
            # deactivate user
            if Contributor.deactivate_contributor(Contributor, account.id):
                message = f"{Emoji.print(Emoji, emoji_name='check')} [{str(account)}] has been added to the graylist."
            else:
                message = f"{Emoji.print(Emoji, emoji_name='cross_red')} Something went wrong, [{str(account)}] could not be graylisted."
            await interaction.followup.send(
                message, 
                ephemeral=True
            )
            return
        
        await interaction.followup.send(
            f"{Emoji.print(Emoji, emoji_name='shrug')} [{str(account)}] is already graylisted.", 
            ephemeral=True
        )
        return
    
    @app_commands.command(name="account", description="update your primary wallet address")
    async def modal(self, interaction: Interaction):
        # check if address is known
        dbid = Contributor.get_active_contributor_by_discord_id(interaction.user.id)
        if not dbid or len(dbid) == 0:
            message = f"{Emoji.print(Emoji, emoji_name='warning')} Only whitelisted contributors can manage their warrior identity."
            await interaction.response.send_message(message, ephemeral=True)
            return
        
        # Show thinking message:
        # Error: Command 'account' raised an exception: InteractionResponded: This interaction has already been responded to before
        # await interaction.response.defer()

        # push input form
        await interaction.response.send_modal(IdentityForm(interaction, dbid))


class IdentityForm(ui.Modal):
    account = ""

    def __init__(self, interaction: Interaction, dbid: Tuple):
        """ IdentityForm contructor """

        super().__init__(title=f"0L Warrior Identity")

        self.account = "" if not dbid[1] else dbid[1]
        self.twitter_handle = "" if not dbid[3] else dbid[3]

        # Define the textbox input
        self.account_input = ui.TextInput(
            label="0L Address (only slow wallets)", 
            style=TextStyle.short,
            placeholder="Your slow wallet address", 
            required=True,
            default=self.account,
            max_length=32)
        
        self.twitter_input = ui.TextInput(
            label="Twitter handle (optional)", 
            style=TextStyle.short,
            placeholder="https://twitter.com/You", 
            required=False,
            default=self.twitter_handle,
            max_length=35)
        
        # Add the textbox input to the form
        self.add_item(self.account_input)
        self.add_item(self.twitter_input)

    async def on_submit(self, interaction: Interaction):
        """ This function is called when the user submits the form. """

        # checkking account validity
        account_input = self.account_input.value.lower()
        if not is_valid_address_format(account_input):
            await interaction.response.send_message(
                f"{Emoji.print(Emoji, emoji_name='cross_red')} Input must be a valid 0L address.", 
                ephemeral=True
            )
            return
        
        # getting twitter input
        twitter_handle = self.twitter_input.value.lower() if self.twitter_input.value.lower() else ""

        # Even though this is checked in the parent function, we want to check 
        # again because we don't know how much time is between calling the 
        # /account command and submitting the form.
        dbid = Contributor.get_active_contributor_by_discord_id(interaction.user.id)
        if not dbid or len(dbid) == 0:
            await interaction.response.send_message(
                f"{Emoji.print(Emoji, emoji_name='cross_red')} Only whitelisted contributors can manage their warrior identity.", 
                ephemeral=True
            )
            return
        
        # check the input
        account_db = "" if not dbid[1] else dbid[1]
        twitter_db = "" if not dbid[3] else dbid[3]

        if account_db == account_input and twitter_handle == twitter_db:
            message = f"{Emoji.print(Emoji, emoji_name='shrug')} No changes detected."
            await interaction.response.send_message(message, ephemeral=True)
            return

        # check if wallet is slow wallet
        val_check = await is_slow_wallet_as(account_input)

        if not val_check:
            # error happened when trying to use tools to access chain
            message = f"{Emoji.print(Emoji, emoji_name='cross_red')} Something went wrong. Please try again or contact one of the administrators"
        elif val_check["status"] == "Error":
            # pass message that is returned from chain tools
            message = f"{Emoji.print(Emoji, emoji_name='cross_red')} {val_check['message']}" 
        elif val_check["status"] == "Success":
            # wallet is a confirmed slow wallet!
            if Contributor.submit_form(Contributor, interaction.user.id, account_input, twitter_handle):
                message = f"{Emoji.print(Emoji, emoji_name='check')} Your identity has been saved!"
            else:
                # error happened when trying to update database
                message = f"{Emoji.print(Emoji, emoji_name='cross_red')} Something went wrong. Please try again or contact one of the administrators"
        
        # response.send_message because followup.send raises an error:
        # Error: Command 'account' raised an exception: InteractionResponded: 
        # This interaction has already been responded to before...
        await interaction.response.send_message(message, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Identities(bot))
    # await bot.add_cog(Identities(bot), guild=DObject(int(Config.DISCORD_BOT_CHANNEL_ID)))
