import discord
from discord import app_commands
import platform
import json
import os
import sys
import random

class Bot(discord.Client):
    def __init__(self):
        # --- Added Presence Status ---
        # This sets the bot's status to "Listening to botzlox.pages.dev"
        custom_activity = discord.Activity(
            type=discord.ActivityType.listening, 
            name="botzlox.pages.dev"
        )
        
        super().__init__(intents=discord.Intents.default(), activity=custom_activity)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

bot = Bot()

@bot.tree.command(name="crossout", description="crosses out a text")
async def crossout(interaction: discord.Interaction, text: str):
    await interaction.response.send_message(f"~~{text}~~")

@bot.tree.command(name="fancy", description="makes text fancy")
async def fancy(interaction: discord.Interaction, text: str):
    fancy_text = "".join(f"ℱ {char} ℱ" for char in text) if len(text) < 10 else "𝓕𝓪𝓷𝓬𝔂: " + text
    # Simplified fancy logic for broad compatibility
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    fancy_map = "𝓪𝓫𝓬𝓭𝓮𝓯𝓰𝓱𝓲𝓳𝓴𝓵𝓶𝓷𝓸𝓹𝓺𝓻𝓼𝓽𝓾𝓿𝔀𝔁𝔂𝔃𝓐𝓑𝓒𝓓𝓔𝓕𝓖𝓗𝓘𝓙𝓚𝓛𝓜𝓝𝓞𝓟P𝓡𝓢𝓣𝓤𝓥𝓦𝓧𝓨𝓩０１２３４５６７８９"
    res = "".join(fancy_map[chars.find(c)] if c in chars else c for c in text)
    await interaction.response.send_message(res)

@bot.tree.command(name="info", description="gives info about the bot")
async def info(interaction: discord.Interaction):
    os_name = platform.system()
    os_version = platform.release()
    
    # --- Windows 11 Fix ---
    if os_name == "Windows":
        # Check if the Windows build number is 22000 or higher (which means Windows 11)
        if sys.getwindowsversion().build >= 22000:
            os_version = "11"
            
    # Initialize the embed with a title and a color
    embed = discord.Embed(
        title="System Information", 
        color=discord.Color.teal()
    )
    
    # Places the icon at the very top of the embed
    embed.set_author(
        name="BotzLox Status", 
        icon_url="https://ia902809.us.archive.org/21/items/untitled-project_202607/Untitled%20Project.jpg"
    )
    
    # Adds the OS and Version side-by-side
    embed.add_field(name="Operating System", value=os_name, inline=True)
    embed.add_field(name="Version", value=os_version, inline=True)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="dice", description="rolls an 18-sided dice")
async def dice(interaction: discord.Interaction):
    result = random.randint(1, 18)
    await interaction.response.send_message(f"🎲 You rolled an **{result}**!")

@bot.tree.command(name="echo", description="Repeats what you say")
async def echo(interaction: discord.Interaction, message: str):
    await interaction.response.send_message(message)

# --- Token Management System ---
TOKEN_FILE = "bot_token.json"

def get_token():
    # Check if the token file already exists
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as file:
            data = json.load(file)
            return data.get("token")
    else:
        # If it doesn't exist, prompt the user and save it
        print("No token found. Let's set one up!")
        new_token = input("Enter your Discord bot token: ").strip()
        
        with open(TOKEN_FILE, "w") as file:
            json.dump({"token": new_token}, file, indent=4)
            
        print("Token saved successfully to 'bot_token.json'. Starting bot...")
        return new_token

if __name__ == "__main__":
    # Retrieve the token and start the client
    token = get_token()
    
    if token:
        bot.run(token)
    else:
        print("Error: No token provided.")