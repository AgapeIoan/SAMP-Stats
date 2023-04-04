
# SAMP-Stats

SAMP Stats (formerly Nephrite Stats) is my first big Python project that helped me learn a lot of useful things.

## History

The project was started on September 2019 using AlexFlipnote's [discord_bot.py](https://github.com/AlexFlipnote/discord_bot.py) project. <br>
This repository marks the point where most of the code base was refactored as Discord started pushing their [API v9](https://discord.com/developers/docs/change-log#api-v9) and introduced the [Slash Commands](https://support.discord.com/hc/en-us/articles/1500000368501-Slash-Commands-FAQ#:~:text=Slash%20Commands%20are%20the%20new,command%20right%20the%20first%20time.).
It also marks the time I started to actively use GitHub for source control. <br>
I've cleaned the repository using [BFG](https://rtyley.github.io/bfg-repo-cleaner/) before making it public (initially it wasn't meant to be public, so I had to remove some ~~credentials and tokens~~ sensitive data). 

New features probably won't be made, at most I'll do updates with bug fixes and small changes when needed. This project was a good learning playground but it's time to move on. I enjoyed working on it and I learned **a lot** from it's challenges and feedback.
 
  ## About
SAMP Stats scrapes data from [rubypanel.nephrite.ro](https://rubypanel.nephrite.ro/) and sends it, formatted nicely to the user, via Discord.

![samp_stats_github_v1](https://user-images.githubusercontent.com/44036462/229929492-e5f63f57-2880-41dc-a3e2-f16eba2e123d.gif)

It asynchronously sends requests in order to get it's data and saves the web session for faster responses.

  ## Commands
  
  |Name                |Parameters                          |Usage                         |
|----------------|-------------------------------|-----------------------------|
|/stats            |`nickname`            |Displays player statistics with an interactive menu            |
|/id          |`nickname`|Displays online players with the matching nickname|
|/faction          |`faction_name`            |Displays faction statistics with an interactive menu            |
|/testers          |`faction_name`|Displays the faction's testers with their online status|
|/aplicatii          |`faction_name`|Displays the specified faction's applicants with an interactive menu|
|/clan          |`clan_name`|Displays clan statistics with an interactive menu|
|/raportu          |`server_name`|Displays the specified SAMP server's data|
|/leaders          ||Displays the server's leaders with their online status|

## Helpful links
- [Personal Discord development server](https://discord.agapeioan.ro)
- [Invite the bot](https://discord.com/oauth2/authorize?client_id=618076658678628383&scope=bot)
