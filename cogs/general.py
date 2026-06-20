import logging
import platform
import psutil
import discord
from discord import app_commands
from discord.ext import commands

from utils.helpers import create_embed, format_uptime
from utils.logger import log

class General(commands.Cog):
    """General utility commands for monitoring bot behavior and simple greetings."""
    
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        
    @app_commands.command(name="ping", description="Check the bot's latency and response speed.")
    async def ping(self, interaction: discord.Interaction) -> None:
        """Responds with WebSocket and API roundtrip latency."""
        log.info(f"Command /ping executed by {interaction.user} in {interaction.guild}")
        
        # Calculate WebSocket latency
        latency_ms = round(self.bot.latency * 1000)
        
        embed = create_embed(
            title="🏓 Pong!",
            description=f"My heartbeat latency is **{latency_ms}ms**.",
            color_type="success"
        )
        await interaction.response.send_message(embed=embed)
        
    @app_commands.command(name="hello", description="Receive a warm greeting from Tiffany.")
    async def hello(self, interaction: discord.Interaction) -> None:
        """Greets the user politely with Tiffany's signature tone."""
        log.info(f"Command /hello executed by {interaction.user} in {interaction.guild}")
        
        message = (
            f"Hello, {interaction.user.mention}! ✨\n\n"
            "I am **Tiffany**, your intelligent companion. It is a pleasure to meet you. "
            "How may I assist you today? You can try asking me anything using `/ask`!"
        )
        
        embed = create_embed(
            title="Greetings!",
            description=message,
            color_type="info",
            thumbnail_url=self.bot.user.display_avatar.url if self.bot.user else None
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="health", description="Display system health and bot diagnostics status.")
    async def health(self, interaction: discord.Interaction) -> None:
        """Returns uptime, CPU/Memory stats, system version, and server details."""
        log.info(f"Command /health executed by {interaction.user} in {interaction.guild}")
        
        # Gather bot and system stats
        uptime_str = format_uptime(self.bot.start_time)
        guilds_count = len(self.bot.guilds)
        
        # Fetch process resource utilization
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_mb = round(memory_info.rss / (1024 * 1024), 2)
        cpu_usage = process.cpu_percent(interval=None)
        
        # Fields structure to represent clean data table
        fields = [
            {"name": "🤖 Status", "value": "Online & Healthy", "inline": True},
            {"name": "⏰ Uptime", "value": uptime_str, "inline": True},
            {"name": "💻 Python Version", "value": f"v{platform.python_version()}", "inline": True},
            {"name": "🖥️ System Platform", "value": platform.system(), "inline": True},
            {"name": "💾 Memory Usage", "value": f"{memory_mb} MB", "inline": True},
            {"name": "⚙️ CPU Usage", "value": f"{cpu_usage}%", "inline": True},
            {"name": "🌐 Server Guilds", "value": str(guilds_count), "inline": True},
            {"name": "👥 Latency", "value": f"{round(self.bot.latency * 1000)}ms", "inline": True}
        ]
        
        embed = create_embed(
            title="System Diagnostics & Health Check",
            description="Operational telemetry for Tiffany Bot.",
            color_type="info",
            fields=fields
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(General(bot))
