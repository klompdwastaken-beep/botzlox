import json
import asyncio
import threading
import discord
from discord import app_commands
from discord.ext import commands
import yt_dlp
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty

# --- FFMPEG CONFIGURATION ---
FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe" 

# --- KIVY UI DESIGN ---
KV = """
ScreenManager:
    MainScreen:
    SettingsScreen:

<MainScreen>:
    name: 'main'
    BoxLayout:
        orientation: 'vertical'
        padding: 30
        spacing: 15
        canvas.before:
            Color:
                rgba: 0.1, 0.1, 0.12, 1
            Rectangle:
                pos: self.pos
                size: self.size
        
        Label:
            text: "MusicalLox"
            font_size: 32
            bold: True
            color: 1, 0.6, 0, 1

        Label:
            text: root.status
            font_size: 20
            color: 0.8, 0.8, 0.8, 1
        
        Widget:
            size_hint_y: 0.2

        Button:
            text: "START BOT"
            background_color: 0.2, 0.8, 0.3, 1
            bold: True
            size_hint_y: None
            height: 70
            on_press: root.start_bot()
            
        Button:
            text: "Settings (Token)"
            size_hint_y: None
            height: 60
            on_release: root.manager.current = 'settings'

<SettingsScreen>:
    name: 'settings'
    BoxLayout:
        orientation: 'vertical'
        padding: 30
        spacing: 15
        Label:
            text: "Bot Settings"
            font_size: 26
        
        Label: 
            text: "Bot Token (Saved in config.json):"
            size_hint_y: None
            height: 30
            
        TextInput:
            id: token_input
            text: app.bot_token
            password: True
            multiline: False
            size_hint_y: None
            height: 45
            
        Button:
            text: "Save & Apply"
            background_color: 0.2, 0.8, 0.3, 1
            size_hint_y: None
            height: 55
            on_press: root.save_settings()
            
        Button:
            text: "Back"
            size_hint_y: None
            height: 50
            on_release: root.manager.current = 'main'
"""

# --- YOUTUBE / FFMPEG LOGIC ---
ytdl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'default_search': 'ytsearch',
    'quiet': True,
    'no_warnings': True,
    'source_address': '0.0.0.0'
}

ffmpeg_opts = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

ytdl = yt_dlp.YoutubeDL(ytdl_opts)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')

    @classmethod
    async def from_url(cls, search, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(search, download=not stream))
        if 'entries' in data:
            data = data['entries'][0]
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, executable=FFMPEG_PATH, **ffmpeg_opts), data=data)

# --- DISCORD BOT CORE ---
class WolfBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()

# --- KIVY SCREENS LOGIC ---
class MainScreen(Screen):
    status = StringProperty("Bot Status: Offline")

    def start_bot(self):
        app = App.get_running_app()
        if not app.bot_token:
            self.status = "Error: Set token in Settings!"
            return
        if not app.bot_thread or not app.bot_thread.is_alive():
            app.start_bot_thread()
            self.status = "Status: Bot is Live"

class SettingsScreen(Screen):
    def save_settings(self):
        token = self.ids.token_input.text.strip()
        with open("config.json", "w") as f:
            json.dump({"token": token}, f)
        App.get_running_app().bot_token = token

# --- MAIN APPLICATION ---
class BotManagerApp(App):
    bot_token = StringProperty("")
    
    def build(self):
        self.load_config()
        self.bot = WolfBot()
        self.register_slash_commands()
        self.bot_thread = None
        return Builder.load_string(KV)

    def load_config(self):
        try:
            with open("config.json", "r") as f:
                self.bot_token = json.load(f).get("token", "")
        except: pass

    def register_slash_commands(self):
        @self.bot.tree.command(name="ping", description="Check latency")
        async def ping(interaction: discord.Interaction):
            await interaction.response.send_message(f"🏓 Pong! {round(self.bot.latency * 1000)}ms")

        @self.bot.tree.command(name="join", description="Join your Voice Channel")
        async def join(interaction: discord.Interaction):
            if interaction.user.voice:
                channel = interaction.user.voice.channel
                if interaction.guild.voice_client:
                    await interaction.guild.voice_client.move_to(channel)
                else:
                    await channel.connect()
                await interaction.response.send_message(f"🐺 Joined {channel.name}")
            else:
                await interaction.response.send_message("You are not in a VC!")

        @self.bot.tree.command(name="play", description="Search and play music")
        async def play(interaction: discord.Interaction, search: str):
            await interaction.response.defer()
            if not interaction.guild.voice_client:
                if interaction.user.voice:
                    await interaction.user.voice.channel.connect()
                else:
                    return await interaction.followup.send("Join a VC first!")
            
            try:
                player = await YTDLSource.from_url(search, loop=self.bot.loop, stream=True)
                interaction.guild.voice_client.play(player)
                await interaction.followup.send(f"🎶 **Playing:** {player.title}")
            except Exception as e:
                await interaction.followup.send(f"Playback Error: {e}")

        @self.bot.tree.command(name="stop", description="Stop music and leave")
        async def stop(interaction: discord.Interaction):
            if interaction.guild.voice_client:
                await interaction.guild.voice_client.disconnect()
                await interaction.response.send_message("Leaving channel. Goodbye!")
            else:
                await interaction.response.send_message("I'm not in a VC.")

    def start_bot_thread(self):
        self.bot_thread = threading.Thread(target=self.run_bot, daemon=True)
        self.bot_thread.start()

    def run_bot(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.bot.start(self.bot_token))
        except Exception as e:
            print(f"Bot failed: {e}")

if __name__ == '__main__':
    BotManagerApp().run()