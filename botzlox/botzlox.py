import discord
from discord import app_commands
import platform
import json
import os
import sys
import random
import tkinter as tk
from tkinter import messagebox
import threading
import asyncio

class Bot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)
        
        # Default fallback values for configuration
        self.bot_name = "BotzLox"
        self.icon_url = "https://ia902809.us.archive.org/21/items/untitled-project_202607/Untitled%20Project.jpg"
        self.status_text = "botzlox.pages.dev"

    async def setup_hook(self):
        # Keeps command syncing here before the connection fully finishes loading
        await self.tree.sync()

    async def on_ready(self):
        # FIX: Updating status inside on_ready guarantees the connection is live
        custom_activity = discord.Activity(
            type=discord.ActivityType.listening, 
            name=self.status_text
        )
        await self.change_presence(activity=custom_activity)
        print(f"Logged in successfully as {self.user}")

bot = Bot()

@bot.tree.command(name="crossout", description="crosses out a text")
async def crossout(interaction: discord.Interaction, text: str):
    await interaction.response.send_message(f"~~{text}~~")

@bot.tree.command(name="fancy", description="makes text fancy")
async def fancy(interaction: discord.Interaction, text: str):
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    fancy_map = "𝓪𝓫𝓬𝓭𝓮𝓯𝓰𝓱𝓲𝓳𝓴𝓵𝓶𝓷𝓸𝓹𝓺𝓻𝓼𝓽𝓾𝓿𝔀𝔁𝔂𝔃𝓐𝓑𝓒𝓓𝓔𝓕𝓖𝓗𝓘𝓙𝓚𝓛𝓜𝓝𝓞𝓟P𝓡𝓢𝓣𝓤𝓥𝓦𝓧𝓨𝓩０１２３４５６７８９"
    res = "".join(fancy_map[chars.find(c)] if c in chars else c for c in text)
    await interaction.response.send_message(res)

@bot.tree.command(name="info", description="gives info about the bot")
async def info(interaction: discord.Interaction):
    os_name = platform.system()
    os_version = platform.release()
    
    if os_name == "Windows":
        if sys.getwindowsversion().build >= 22000:
            os_version = "11"
            
    embed = discord.Embed(
        title="System Information", 
        color=discord.Color.teal()
    )
    
    embed.set_author(
        name=f"{bot.bot_name} Status", 
        icon_url=bot.icon_url
    )
    
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


# --- Configuration Management System ---
CONFIG_FILE = "config.json"

def load_config():
    defaults = {
        "token": "",
        "bot_name": "BotzLox",
        "icon_url": "https://ia902809.us.archive.org/21/items/untitled-project_202607/Untitled%20Project.jpg",
        "status_text": "botzlox.pages.dev"
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as file:
                data = json.load(file)
                for key, val in defaults.items():
                    data.setdefault(key, val)
                return data
        except json.JSONDecodeError:
            return defaults
    return defaults

def save_config(config_data):
    with open(CONFIG_FILE, "w") as file:
        json.dump(config_data, file, indent=4)


# --- Launcher GUI Setup ---
def run_launcher():
    config = load_config()

    root = tk.Tk()
    root.title("BotZlox")
    root.geometry("350x220")
    root.resizable(False, False)

    def open_settings():
        settings_win = tk.Toplevel(root)
        settings_win.title("Configure your BotZlox Based Bot")
        settings_win.geometry("450x350")
        settings_win.resizable(False, False)

        tk.Label(settings_win, text="Bot Token:", font=("Arial", 10, "bold")).pack(pady=(10, 2))
        token_entry = tk.Entry(settings_win, width=50, show="*")
        token_entry.insert(0, config.get("token", ""))
        token_entry.pack(pady=2)

        tk.Label(settings_win, text="Bot Name (Displayed in /info):", font=("Arial", 10, "bold")).pack(pady=5)
        name_entry = tk.Entry(settings_win, width=50)
        name_entry.insert(0, config.get("bot_name", "BotzLox"))
        name_entry.pack(pady=2)

        tk.Label(settings_win, text="Direct Image URL for Author Icon:", font=("Arial", 10, "bold")).pack(pady=5)
        icon_entry = tk.Entry(settings_win, width=50)
        icon_entry.insert(0, config.get("icon_url", ""))
        icon_entry.pack(pady=2)

        tk.Label(settings_win, text="Bot Status (Listening to...):", font=("Arial", 10, "bold")).pack(pady=5)
        status_entry = tk.Entry(settings_win, width=50)
        status_entry.insert(0, config.get("status_text", "botzlox.pages.dev"))
        status_entry.pack(pady=2)

        def save_and_close():
            config["token"] = token_entry.get().strip()
            config["bot_name"] = name_entry.get().strip()
            config["icon_url"] = icon_entry.get().strip()
            config["status_text"] = status_entry.get().strip()
            save_config(config)
            messagebox.showinfo("Success", "Settings updated successfully!")
            settings_win.destroy()

        tk.Button(settings_win, text="Save Settings", font=("Arial", 10), bg="#2ecc71", fg="white", command=save_and_close, width=15).pack(pady=15)

    def start_bot():
        current_config = load_config()
        if not current_config.get("token"):
            messagebox.showerror("Error", "You must provide a valid Bot Token in Settings first!")
            return
        
        bot.bot_name = current_config.get("bot_name", "BotzLox")
        bot.icon_url = current_config.get("icon_url", "")
        bot.status_text = current_config.get("status_text", "botzlox.pages.dev")

        start_btn.config(state=tk.DISABLED)
        settings_btn.config(state=tk.DISABLED)
        status_label.config(text="Status: Bot is Running...", fg="#2ecc71")

        def bot_worker():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(bot.start(current_config["token"]))
            except Exception as e:
                messagebox.showerror("Runtime Connection Error", f"Failed execution flow:\n{e}")
                root.after(0, lambda: start_btn.config(state=tk.NORMAL))
                root.after(0, lambda: settings_btn.config(state=tk.NORMAL))
                root.after(0, lambda: status_label.config(text="Status: Process Terminated", fg="#e74c3c"))

        bot_thread = threading.Thread(target=bot_worker, daemon=True)
        bot_thread.start()

    # GUI Dashboard Elements
    status_label = tk.Label(root, text="Status: Connected Interface Idle", fg="#7f8c8d", font=("Arial", 11, "italic"))
    status_label.pack(pady=(15, 5))

    start_btn = tk.Button(root, text="🤖 Start Bot", font=("Arial", 11, "bold"), bg="#3498db", fg="white", width=22, height=2, command=start_bot)
    start_btn.pack(pady=10)

    settings_btn = tk.Button(root, text="⚙️ Settings", font=("Arial", 11), bg="#95a5a6", fg="white", width=22, height=2, command=open_settings)
    settings_btn.pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    run_launcher()