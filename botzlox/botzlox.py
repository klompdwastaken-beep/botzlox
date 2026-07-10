#Pydroid run kivy
import asyncio
import discord
from discord import app_commands
import platform
import json
import os
import sys
import random

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.core.window import Window

# Apply a dark theme background to the Kivy window
Window.clearcolor = (0.12, 0.12, 0.12, 1)

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


# --- Discord Bot Implementation ---
class Bot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)
        self.bot_name = "BotzLox"
        self.icon_url = ""
        self.status_text = "botzlox.pages.dev"
        self.ui_status_callback = None

    async def setup_hook(self):
        await self.tree.sync()

    async def on_ready(self):
        custom_activity = discord.Activity(
            type=discord.ActivityType.listening, 
            name=self.status_text
        )
        await self.change_presence(activity=custom_activity)
        print(f"Logged in successfully as {self.user}")
        
        # Safely trigger UI updates from the async event loop
        if self.ui_status_callback:
            Clock.schedule_once(lambda dt: self.ui_status_callback(f"Status: Online as {self.user}"), 0)

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


# --- Kivy UI Layout ---
class BotLauncherUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 15
        self.config = load_config()
        
        # Title Element
        self.add_widget(Label(text="BotzLox", font_size='22sp', size_hint=(1, 0.15), bold=True))
        
        # Vertical Form Layout (Optimized for Mobile)
        form_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.6), spacing=5)
        
        form_layout.add_widget(Label(text="Bot Token:", size_hint=(1, None), height=30))
        self.token_input = TextInput(text=self.config.get("token", ""), password=True, multiline=False, size_hint=(1, None), height=40)
        form_layout.add_widget(self.token_input)
        
        form_layout.add_widget(Label(text="Bot Name:", size_hint=(1, None), height=30))
        self.name_input = TextInput(text=self.config.get("bot_name", "BotzLox"), multiline=False, size_hint=(1, None), height=40)
        form_layout.add_widget(self.name_input)
        
        form_layout.add_widget(Label(text="Icon URL:", size_hint=(1, None), height=30))
        self.icon_input = TextInput(text=self.config.get("icon_url", ""), multiline=False, size_hint=(1, None), height=40)
        form_layout.add_widget(self.icon_input)
        
        form_layout.add_widget(Label(text="Status Text:", size_hint=(1, None), height=30))
        self.status_input = TextInput(text=self.config.get("status_text", "botzlox.pages.dev"), multiline=False, size_hint=(1, None), height=40)
        form_layout.add_widget(self.status_input)
        
        self.add_widget(form_layout)
        
        # Dashboard Buttons and Labels
        self.save_btn = Button(text="Save Settings", size_hint=(1, 0.12), background_color=(0.2, 0.7, 0.4, 1))
        self.save_btn.bind(on_press=self.save_settings)
        self.add_widget(self.save_btn)
        
        self.status_label = Label(text="Status: Connected Interface Idle", italic=True, size_hint=(1, 0.1), color=(0.6, 0.8, 1, 1))
        self.add_widget(self.status_label)
        
        self.start_btn = Button(text="Start Bot", size_hint=(1, 0.15), background_color=(0.2, 0.6, 1, 1), bold=True, font_size='18sp')
        self.start_btn.bind(on_press=self.start_bot)
        self.add_widget(self.start_btn)
        
        # Bind the callback to the bot so it can tell the UI when it connects
        bot.ui_status_callback = self.update_status_label

    def save_settings(self, instance):
        self.config["token"] = self.token_input.text.strip()
        self.config["bot_name"] = self.name_input.text.strip()
        self.config["icon_url"] = self.icon_input.text.strip()
        self.config["status_text"] = self.status_input.text.strip()
        save_config(self.config)
        self.update_status_label("Settings updated successfully!")

    def update_status_label(self, message):
        self.status_label.text = message

    def start_bot(self, instance):
        token = self.token_input.text.strip()
        if not token:
            self.update_status_label("Error: Bot Token is missing!")
            return

        # Lock UI controls while attempting connection
        self.start_btn.disabled = True
        self.save_btn.disabled = True
        self.update_status_label("Status: Initializing Connection...")
        
        # Apply configurations to bot instance
        bot.bot_name = self.name_input.text.strip()
        bot.icon_url = self.icon_input.text.strip()
        bot.status_text = self.status_input.text.strip()
        
        # Pass control back to the App class to spawn the connection task
        App.get_running_app().start_discord_task(token)


# --- Application Entry Point ---
class BotLauncherApp(App):
    def build(self):
        # This line sets the operating system window title (visible on PC)
        self.title = "BotzLox" 
        self.main_ui = BotLauncherUI()
        return self.main_ui
        
    def start_discord_task(self, token):
        # Create an asyncio task for discord.py alongside the running Kivy app
        self.discord_task = asyncio.create_task(self.run_bot(token))
        
    async def run_bot(self, token):
        try:
            await bot.start(token)
        except Exception as e:
            # Re-enable the UI and show errors if the connection fails
            Clock.schedule_once(lambda dt: self.main_ui.update_status_label(f"Connection Error: {e}"), 0)
            Clock.schedule_once(lambda dt: setattr(self.main_ui.start_btn, 'disabled', False), 0)
            Clock.schedule_once(lambda dt: setattr(self.main_ui.save_btn, 'disabled', False), 0)

async def main():
    # Kivy's async_run integrates the UI seamlessly with Python's asyncio event loop
    app = BotLauncherApp()
    await app.async_run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Application closed.")