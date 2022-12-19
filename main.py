import discord
import requests
import random
import asyncio
import settings

from bs4 import BeautifulSoup
from lxml import etree
from discord.ext import commands
from discord import app_commands

intent = discord.Intents.default()
client = discord.Client(intents=intent)
tree = app_commands.CommandTree(client)

colors = [0x1abc9c, 0x11806a, 0x2ecc71, 0x1f8b4c, 0x3498db, 0x206694, 0x9b59b6, 0x71368a, 0xe91e63,
          0xad1457, 0xf1c40f, 0xc27c0e, 0xe67e22, 0x95a5a6, 0x607d8b, 0x99aab5, 0x546e7a, 0x7289da,
          0x99aab5, 0x2c2f33, 0x23272a]

@client.event
async def on_ready():
    await tree.sync()
    await client.change_presence(status=discord.Status.do_not_disturb, activity=discord.Activity(type=discord.ActivityType.watching, name="the next sale 💸"))
    
    print(f'{client.user} has connected to Discord!')


# SteamCharts Player Count Command
@tree.command(name='player-count', description='Show the amount of players online in a steam game.')
async def player_count(ctx, appid: str):

    await ctx.response.defer()

    url = f"https://steamcharts.com/app/{appid}"

    r = requests.get(url)

    soup = BeautifulSoup(r.content, "html.parser")
    dom = etree.HTML(str(soup))

    try:

        playing_now = dom.xpath('/html/body/div[3]/div[3]/div[1]/span').pop().text
        daily_peak = dom.xpath('/html/body/div[3]/div[3]/div[2]/span').pop().text
        all_time = dom.xpath('/html/body/div[3]/div[3]/div[3]/span').pop().text

        game_name = dom.xpath('/html/body/div[3]/h1/a').pop().text

        format_playing_now = "{:,}".format(int(playing_now))
        format_daily_peak = "{:,}".format(int(daily_peak))
        format_all_time = "{:,}".format(int(all_time))

    except IndexError:
        await ctx.followup.send(f"Game not found. Use a valid APP ID.")

    # TO DO: Make this cleaner lol.

    if playing_now == None or playing_now == "":
        await ctx.followup.send(f"Game not found.")

    else:
        embed = discord.Embed(
            title="Player Count - APPID: " + appid,
            description="Current amount of players online on " + game_name + ".",
            color=random.choice(colors),
            url=url
        )

        embed.add_field(name="Playing Now", value=f"👤 {format_playing_now}", inline=True)
        embed.add_field(name="Daily Peak", value=f"👥 {format_daily_peak}", inline=True)
        embed.add_field(name="All Time", value=f"⏰ {format_all_time}", inline=True)

    await ctx.followup.send(embed=embed)

@tree.command(name='search-game', description='Show the information about a steam game.')
async def search_game(ctx, *, appid: int):
    await ctx.response.defer()

    headers = {
        "Accept-Language": "en-US,en;q=0.5",
    }

    url = f"https://store.steampowered.com/api/appdetails?appids={appid}"

    r = requests.get(url, headers=headers)

    if r.status_code == 200:
        data = r.json()

        # TO DO: Refactor to work with the new API.

        if data[str(appid)]['success'] == True:
            game_name = data[str(appid)]['data']['name']
            game_description = data[str(appid)]['data']['short_description']
            game_url = f"https://store.steampowered.com/app/{appid}/"
            game_image = data[str(appid)]['data']['header_image']
            main_image = data[str(appid)]['data']['screenshots'][0]['path_full']
            try: 
                game_price = data[str(appid)]['data']['price_overview']['final_formatted']
            except KeyError:
                game_price = "Free to Play"

            embed = discord.Embed(
                title=game_name + " - APPID: " + str(appid),
                description=game_description,
                color=random.choice(colors),
                url=game_url
            )

            embed.set_thumbnail(url=main_image)
            embed.set_image(url=game_image)
            embed.add_field(name="Price", value=game_price, inline=False)

            await ctx.followup.send(embed=embed)

        else:
            await ctx.followup.send(f"Game not found. Use a valid APP ID.")
        
    else:
        await ctx.followup.send(f"Game not found. Use a valid APP ID.")


@tree.command(name="user-summary", description="Show the summary of a steam user.")
async def user_summary(ctx, *, steamid: str):
    await ctx.response.defer()

    url = f"https://steamcommunity.com/profiles/{steamid}/?xml=1"

    r = requests.get(url)

    soup = BeautifulSoup(r.content, "html.parser")
    dom = etree.HTML(str(soup))

    # TO DO: FIX THIS MESS
    

    if r.status_code == 200:
        user_avi = r.text.split("<avatarFull>")[1].split("</avatarFull>")[0]
        user_name = r.text.split("<steamID>")[1].split("</steamID>")[0]
        user_real_name = r.text.split("<realname>")[1].split("</realname>")[0]
        user_country = "Brazil"
        user_custom_url = r.text.split("<customURL>")[1].split("</customURL>")[0]
        user_member_since = r.text.split("<memberSince>")[1].split("</memberSince>")[0]
        user_profile_url = f"https://steamcommunity.com/profiles/{steamid}/"

        embed = discord.Embed(
            title=user_name,
            description="User Summary",
            color=random.choice(colors),
            url=user_profile_url
        )

        print(user_avi)

        embed.set_thumbnail(url=user_avi)
        embed.add_field(name="Real Name", value=user_real_name, inline=True)
        embed.add_field(name="Country", value=user_country, inline=True)
        embed.add_field(name="Custom URL", value=user_custom_url, inline=True)
        embed.add_field(name="Member Since", value=user_member_since, inline=True)

        await ctx.followup.send(embed=embed)






if __name__ == '__main__':
    client.run(settings.discord_token)