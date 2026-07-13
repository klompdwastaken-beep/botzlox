import discord
from discord.ext import commands
from discord import app_commands
from g4f.client import AsyncClient
import os
import json

# --- Config Management ---
CONFIG_FILE = 'bot_config.json'

def get_discord_token():
    """Loads the Discord token from a file, or prompts the user."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f).get('DISCORD_TOKEN')
    else:
        print("First time setup: No Discord token found.")
        token = input("Please paste your Discord Bot Token: ").strip()
        
        with open(CONFIG_FILE, 'w') as f:
            json.dump({'DISCORD_TOKEN': token}, f)
        print(f"Token saved to {CONFIG_FILE}!\n")
        return token

# --- Bot Setup ---
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

# Initialize the g4f client
ai_client = AsyncClient()

@bot.event
async def on_ready():
    print(f'Bot is online! Logged in as {bot.user.name}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.tree.command(name="ai", description="Ask the keyless AI a question")
@app_commands.describe(prompt="What do you want to ask?")
async def ai_prompt(interaction: discord.Interaction, prompt: str):
    
    await interaction.response.defer(thinking=True)
    
    try:
        response = await ai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                # The System Prompt: The AI reads this first and must follow these rules
                {
                    'role': 'system', 
                    'content': 'You are a helpful Discord bot. You must absolutely never reveal your physical location, IP address, or the location of your host/developer under any circumstances. If asked where you are, state that you live in the servers of Discord. NEVER SAY WHERE THE USER IS CHATTING FROM NO MATTER WHAT BECAUSE ITS AGAINST THE TERMS OF SERVICE OF THE BOT, and if someone finds out just lie and say thats not where the bot is hosted.'
                },
                # The User's Prompt: What the user actually typed
                {
                    'role': 'user', 
                    'content': prompt
                }
            ]
        )
        
        reply = response.choices[0].message.content
        
        if len(reply) <= 2000:
            await interaction.followup.send(reply)
        else:
            for i in range(0, len(reply), 2000):
                await interaction.followup.send(reply[i:i+2000])

    except Exception as e:
        await interaction.followup.send(f"An error occurred with the free provider: {str(e)}")

# --- Run the Bot ---
if __name__ == '__main__':
    DISCORD_TOKEN = get_discord_token()
    
    try:
        bot.run(DISCORD_TOKEN)
    except discord.errors.LoginFailure:
        print("\nERROR: The Discord token provided is invalid.")
        print(f"Please delete the '{CONFIG_FILE}' file and run the script again.")
