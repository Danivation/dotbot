import discord
from discord import app_commands
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client=client)

headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {os.getenv("DOTLIST_JWT")}',
}

userCount = json.loads(requests.get('https://sensible-hawk-744.convex.site/users', headers={"X-API-KEY": os.getenv("DOTLIST_DEV_KEY")}).text).get("totalUsers")

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Activity(name=f"custom", type=discord.ActivityType.custom, state=f"dotlisting with {userCount} users"))
    await tree.sync()
    print(f'Logged in as {client.user}')
    
@tree.command(name="test", description="A test command")
async def test_command(interaction: discord.Interaction):
    params = {

    }
    response = requests.get(
        'https://polished-beagle-841.convex.site/health',
        params=params,
        headers=headers
    )
    try: 
        await interaction.response.send_message(json.dumps(json.loads(response.text), indent=4))
    except Exception as e:
        await interaction.response.send_message(response.text)

    print(f'Command run by {interaction.user.name}')

client.run(os.getenv("BOT_TOKEN"))
