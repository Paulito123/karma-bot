import discord
from discord import ui, app_commands
from discord.ext import commands
from util import github_util


class Payments(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="payment", description="manually add a payment")
    async def payment(self, interaction: discord.Interaction, account: discord.User):
        """This command is only available to Working Groups Key Roles."""
        if "Working Groups Key Role" not in [y.name for y in interaction.user.roles]:
            await interaction.response.send_message("You are not allowed to add payments.", ephemeral=True)
            return
        await interaction.response.send_modal(PaymentForm(interaction, discord_user=account))

    @commands.command()
    async def spawn(self, ctx) -> None:
        # TODO: add limitation to only allow this command to be used by X
        # TODO: automatically send these issues at the end of the month
        # TODO: use better formatting to get the issue data. This is just a quick and dirty way to get the data.
        closed_issues = github_util.get_closed_issues()
        # to check if there are any closed issues that are already paid
        payments = github_util.get_payments()
        paid_issues = [p["issue_link"] for p in payments]

        for issue in closed_issues:
            if issue.html_url not in paid_issues:
                # regex to check if string has exactly three commas with text in between
                if issue.body.count(',') == 2:
                    i = list(map(str.strip, issue.body.split(",")))
                    msg = f"{issue.html_url}, {i[0]}, {i[1]}, {i[2]}"
                    await send_embed(ctx, msg, "Finished Bounty")

        return


class PaymentButton(ui.Button):
    def __init__(self):
        super().__init__(label="Pay now", style=discord.ButtonStyle.green)

    async def callback(self, interaction: discord.Interaction):
        # TODO: only allow this to be used by certain roles
        # TODO: use better formatting to get the data from message.
        # get the content of the message that this button belongs to
        message = interaction.message.embeds[0].description
        # the content should contain:
        # - the issue link
        # - the account (and/or user) to pay
        # - the bounty amount
        # - the task description
        content = list(map(str.strip, message.split(",")))
        issue_link = content[0]
        discord_name = content[1]
        bounty = content[2]
        task_description = content[3]
        await interaction.response.send_modal(
            PaymentForm(interaction, discord_name=discord_name, bounty=bounty, issue_link=issue_link,
                        task_description=task_description))


class PaymentForm(ui.Modal):
    def __init__(self, interaction: discord.Interaction, discord_user=None, discord_name=None, bounty=None, issue_link=None,
                 task_description=None):
        self.bounty = bounty
        self.issue_link = issue_link
        self.task_description = task_description
        if discord_user is None:
            self.identity = github_util.get_identity(discord_name=discord_name)
            self.discord_name = discord_name
        else:
            self.identity = github_util.get_identity(discord_id=discord_user.id)
            self.discord_name = str(discord_user)
        if self.identity is None:
            self.address = ""
        else:
            self.address = self.identity["account"]
        super().__init__(title=f"0L Payment Form: {str(self.discord_name)}")

        # We can only have 5 items in a modal.
        # self.discord_name_field = discord.ui.TextInput(label="Discord Name", default=self.discord_name,
        #                                                style=discord.TextStyle.short, required=False)
        self.account_field = discord.ui.TextInput(label="0L Address", style=discord.TextStyle.short,
                                                  placeholder="The recipient", required=True,
                                                  default=self.address, min_length=32, max_length=32)
        self.amount_field = discord.ui.TextInput(label="Bounty amount", style=discord.TextStyle.short,
                                                 placeholder="optional", required=True,
                                                 default=self.bounty)
        self.issue_link_field = discord.ui.TextInput(label="The issue link", style=discord.TextStyle.short,
                                                     placeholder="optional", required=False,
                                                     default=self.issue_link)
        # self.task_description_field = discord.ui.TextInput(label="Task description", style=discord.TextStyle.short,
        #                                                    placeholder="short task description", required=False,
        #                                                    default=self.task_description)
        self.memo_field = discord.ui.TextInput(label="Memo", style=discord.TextStyle.short,
                                               placeholder="optional", required=False,
                                               default="")
        self.tx_hash_field = discord.ui.TextInput(label="Transaction hash", style=discord.TextStyle.long,
                                                  placeholder="TX HASH", required=True)

        # self.add_item(self.discord_name_field)
        self.add_item(self.account_field)
        self.add_item(self.amount_field)
        self.add_item(self.issue_link_field)
        # self.add_item(self.task_description_field)
        self.add_item(self.memo_field)
        self.add_item(self.tx_hash_field)

    async def on_submit(self, interaction: discord.Interaction):
        """This function is called when the user submits the form."""
        await interaction.response.defer()
        payments = github_util.get_payments()
        payment = {
            "address": self.account_field.value,
            "discord_name": self.discord_name,
            "issue_link": self.issue_link_field.value,
            "task_description": self.task_description,
            "amount": self.amount_field.value,
            "memo": self.memo_field.value,
            "tx_hash": self.tx_hash_field.value
        }
        payments.append(payment)
        github_util.push_payments(payments)

        await interaction.followup.send(f"Bounty has been paid: {self.amount_field.value} GAS to {self.discord_name}")


async def send_embed(channel, message, title):
    embed = discord.Embed(
        title=title,
        description=message,
        colour=discord.Colour.gold()
    )

    button = PaymentButton()
    view = discord.ui.View()
    view.add_item(button)
    await channel.send(embed=embed, view=view)


async def setup(client):
    print("Payments module loaded")
    await client.add_cog(Payments(client))
