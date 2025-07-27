import discord
from discord import app_commands
import requests
import json
import os
from dotenv import load_dotenv
import keyring
import jwt
import datetime
import cryptography
from convex import ConvexClient

convex_client = ConvexClient("https://sensible-hawk-744.convex.cloud")

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client=client)

userCount = json.loads(requests.get('https://sensible-hawk-744.convex.site/users', headers={"X-API-KEY": os.getenv("DOTLIST_DEV_KEY")}).text).get("totalUsers")


def authenticate(userId: str, login: bool = False):
    currentToken = keyring.get_password("dotbot", userId)
    try:
        decoded = jwt.decode(currentToken, algorithms="RS256", key=os.getenv("DOTLIST_PUBLIC_KEY"), audience="convex").get("exp")
    except Exception as e:
        decoded = 0
        #raise e
    if currentToken == None and login == False:
        print("Not logged in")
    elif currentToken == None or decoded <= int(datetime.datetime.now().timestamp()):
        print("Generating new token")
        payload = {
            "sub": userId,
            "iss": "https://sensible-hawk-744.convex.site",
            "aud": "convex",
            "iat": int(datetime.datetime.now().timestamp()),
            "exp": int((datetime.datetime.now() + datetime.timedelta(hours=1)).timestamp())
        }
        print(f'iat: {payload.get("iat")}')
        print(f'exp: {payload.get("exp")}')
        header = {
            "alg": "RS256"
        }
        newToken = jwt.encode(payload=payload, key=os.getenv("DOTLIST_PRIVATE_KEY"), headers=header)
        keyring.set_password("dotbot", userId, newToken)
    else:
        print("Using old token")

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Activity(name=f"custom", type=discord.ActivityType.custom, state=f"dotlisting with {userCount} users"))
    await tree.sync()
    print(f'Logged in as {client.user}')

@tree.command(name="login", description="Log in to Dotbot")
@app_commands.describe(username="Your Dotlist username")
async def login_cmd(interaction: discord.Interaction, username: str):
    user = convex_client.query("main:findUserByUsername", {"username": username})

    try:
        userId = user.get("userId")
    except Exception as e:
        await interaction.response.send_message("Could not login. No user exists with that username.")
        #raise e
    else:
        try:
            authenticate(userId, True)
        except Exception as e:
            await interaction.response.send_message("Error authenticating. Please try again.")
            #raise e
        else:
            await interaction.response.send_message(f"Logged in as {user.get("username")}")

    print(f'Command `login` run by {interaction.user.name} returned {user}')

@tree.command(name="test", description="A test command")
async def test_command(interaction: discord.Interaction):
    params = {

    }
    response = requests.get(
        'https://polished-beagle-841.convex.site/health',
        params=params
    )
    try:
        await interaction.response.send_message(json.dumps(json.loads(response.text), indent=4))
    except Exception as e:
        await interaction.response.send_message(response.text)

    print(f'Command `test` run by {interaction.user.name} returned {response.text}')

@tree.command(name="user", description="Get info about your user profile")
async def user_cmd(interaction: discord.Interaction):
    params = {

    }
    response = requests.get(
        'https://polished-beagle-841.convex.site/api/user',
        params=params
    )
    user = convex_client.query("main:findUserByUsername", {"username": "danivation"})
    print(f'Convex: {user}')
    try:
        await interaction.response.send_message(json.dumps(json.loads(response.text), indent=4))
    except Exception as e:
        await interaction.response.send_message(response.text)

    print(f'Command `user` run by {interaction.user.name} returned {response.text}')


client.run(os.getenv("BOT_TOKEN"))
