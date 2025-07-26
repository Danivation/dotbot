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

userCount = json.loads(requests.get('https://polished-beagle-841.convex.site/users').text).get("totalUsers")

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Activity(name=f"custom", type=discord.ActivityType.custom, state=f"dotbotting with {userCount} users"))
    await tree.sync()
    print(f'Logged in as {client.user}')
    
@tree.command(name="test", description="A test command")
async def test_command(interaction: discord.Interaction):
    params = {

    }
    response = requests.get(
        'https://polished-beagle-841.convex.site/lists/k97bff2sazfcygnhyddgtx5r857mc207/items',
        params=params,
        headers=headers
    )
    await interaction.response.send_message(json.dumps(json.loads(response.text), indent=4))
    print(f'Command run by {interaction.user.name}')

client.run(os.getenv("BOT_TOKEN"))
