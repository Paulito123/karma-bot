# **KARMA BOT**
The Karma-bot is intended to support various processes in the 0L network organization. It sources from and stores data in json files on Github, making it pluggable for other applications and ensuring that no strict dependency is created between the app and the data it produces. The different functionalities of the Karma-bot are defined as modules.

***The three main modules:***
1. Identity module
2. Payments module
3. Skills module

## **Identity module**
The Identity Module enables community members to take ownership of the data involving their identity within the context of the bounty program. Only whitelisted Discord accounts are able to update their identity. OL community Key roles can whitelist (and graylist) Discord accounts.
### **Commands**
- **'/account'** - Opens a form to link a wallet address to your identity and to set other fields. This command also allows for updating one's identity.
- **'/whitelist'** - Whitelists a user for the /account command. This command is only available to Working Groups Key Roles.
- **'/graylist'** - Deactivate a user for the /account command. This command is only available to Working Groups Key Roles.
## **Payments module**
The Payment Module aims at taking away friction from the internal payment processes. It adds proactivity to the current process by notifying payers about their payments due and prevents them from having to fiddle with json files directly. Consistent and validated data is generated along the way that can be used as input for reporting applications and dashboards. This module facilitates linking transactional data with mission/task data. For now, this linkage is done manually by the payer.
## **Skills module**
Work in progress.

## **Prerequisites for running the bot**
1. Have docker installed
2. Have a copy of the karma-bot repo on Github with an Github App configured and pointed to this repo. Data is synced to the repo.
3. Have a Discord server on which the bot can be added with the appropriate roles defined.

## **Setting up Github**
https://docs.github.com/en/developers/apps/building-github-apps/authenticating-with-github-apps

## **Setting up Discord**
https://discordpy.readthedocs.io/en/stable/discord.html
## **Running the bot**
1. Duplicate the example.env files in the bot and gitsync directories and change the values according to your account credentials.
2. Create a directory .certs under gitsync and copy the .pem file that was generated on github to that directory.
3. Add your bot in the Discord developers portal to your Discord server.
4. Run the containers from the directory where your docker-compose.yml file resides:
```bash
docker compose up -d --build
```
