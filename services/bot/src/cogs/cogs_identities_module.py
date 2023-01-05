import discord
from discord import ui, app_commands
from discord.ext import commands
from src.util import github_util


class Identities(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="account", description="add or update your registered wallet address")
    # TODO: add lock to prevent multiple submissions at the same time.
    # TODO: add limit to prevent spamming.
    async def modal(self, interaction: discord.Interaction):
        if not github_util.is_in_identities(interaction.user.id):
            message = "Only enlisted contributors can add an account. Ask a key role to whitelist your account."
            await interaction.response.send_message(message, ephemeral=True)
            return
        await interaction.response.send_modal(IdentityForm(interaction))

    @app_commands.command(name="whitelist", description="whitelist an account")
    async def whitelist(self, interaction: discord.Interaction, account: discord.User):
        """This command is only available to Working Groups Key Roles."""
        # TODO: add support for type 1 accounts (groups)
        if "Working Groups Key Role" not in [y.name for y in interaction.user.roles]:
            await interaction.response.send_message("You are not allowed to whitelist accounts.", ephemeral=True)
            return
        if github_util.is_in_identities(interaction.user.id):
            await interaction.response.send_message("This account is already whitelisted.", ephemeral=True)
            return
        await interaction.response.defer()
        github_util.add_identity("None", 0, account.id, str(account), None, None)
        await interaction.followup.send(f"We have added {str(account)} to the whitelist.", ephemeral=True)


class IdentityForm(ui.Modal):
    account = ""
    github_id = ""
    twitter_id = ""
    identity = {}

    def __init__(self, interaction: discord.Interaction):
        super().__init__(title=f"0L Identity Form: {interaction.user}")
        self.identities = github_util.get_identities()
        self.discord_id = interaction.user.id
        self.discord_name = str(interaction.user)
        for index, i in enumerate(self.identities):
            if i["details"]["discordId"] == interaction.user.id:
                self.identity_index = index
                self.account = i["account"]
                if "githubId" in i["details"]:
                    self.github_id = i["details"]["githubId"]
                if "twitterId" in i["details"]:
                    self.twitter_id = i["details"]["twitterId"]
                break

        self.account_input = discord.ui.TextInput(label="0L Address (slow wallet!)", style=discord.TextStyle.short,
                                                  placeholder="This should be a slow wallet address!", required=True,
                                                  default=self.account, min_length=32, max_length=32)
        self.github_id_input = discord.ui.TextInput(label="Your Github ID", style=discord.TextStyle.short,
                                                    placeholder="optional", required=False,
                                                    default=self.github_id)
        self.twitter_id_input = discord.ui.TextInput(label="Your Twitter ID", style=discord.TextStyle.short,
                                                     placeholder="optional", required=False,
                                                     default=self.twitter_id)
        self.add_item(self.account_input)
        self.add_item(self.github_id_input)
        self.add_item(self.twitter_id_input)

    async def on_submit(self, interaction: discord.Interaction):
        """This function is called when the user submits the form.
        TODO: add check slow wallet function."""
        # calling this function again in case identities have changed.
        self.identities = github_util.get_identities()
        self.identities[self.identity_index]["account"] = self.account_input.value
        self.identities[self.identity_index]["details"]["discordId"] = self.discord_id
        self.identities[self.identity_index]["details"]["discordName"] = self.discord_name
        if self.github_id_input.value != "":
            self.identities[self.identity_index]["details"]["githubId"] = self.github_id_input.value
        if self.twitter_id_input.value != "":
            self.identities[self.identity_index]["details"]["twitterId"] = self.twitter_id_input.value

        github_util.push_identities(self.identities)

        await interaction.response.send_message("Thanks for submitting your identity!", ephemeral=True)


async def setup(client: commands.Bot):
    await client.add_cog(Identities(client)) #, guild=discord.Object(696335510037332020)
