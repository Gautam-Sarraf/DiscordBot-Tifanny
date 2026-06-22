import asyncio
import datetime
import os
import sys
import discord
from discord.ext import commands
from discord import app_commands

from services.config import Config
from services.gemini_service import GeminiService
from utils.logger import log
from utils.helpers import create_embed

# Validate configurations before startup
try:
    Config.validate()
except ValueError as e:
    log.critical(str(e))
    sys.exit(1)

class TiffanyBot(commands.Bot):
    """Core Bot class extending commands.Bot to implement modern slash command behaviors."""
    
    def __init__(self) -> None:
        # Define intents required by the bot
        # For slash commands, default intents are sufficient.
        intents = discord.Intents.default()
        intents.guilds = True
        intents.message_content = True
        
        super().__init__(
            command_prefix="!",  # Backup prefix, not primary as we use Slash commands
            intents=intents,
            help_command=None    # Disable default help command to use slash help if desired
        )
        
        # Instantiate services & variables
        self.start_time: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)
        self.gemini_service: GeminiService = GeminiService()
        
    async def setup_hook(self) -> None:
        """Asynchronous setup hook called before login."""
        log.info("Starting up Tiffany Bot...")
        
        # Dynamically load all Cogs in the cogs directory
        cogs_dir = os.path.join(os.path.dirname(__file__), "cogs")
        for filename in os.listdir(cogs_dir):
            # Load file if it is a python module and not an initializer/private script
            if filename.endswith(".py") and not filename.startswith("_"):
                cog_name = f"cogs.{filename[:-3]}"
                try:
                    await self.load_extension(cog_name)
                    log.info(f"Loaded extension: {cog_name}")
                except Exception as e:
                    log.error(f"Failed to load extension {cog_name}: {e}", exc_info=True)
                    
        # Setup global application command error handler
        self.tree.on_error = self.on_app_command_error
        
        # Sync slash commands globally
        log.info("Syncing application command tree globally...")
        try:
            synced = await self.tree.sync()
            log.info(f"Successfully synced {len(synced)} global slash commands.")
        except Exception as e:
            log.error(f"Failed to sync slash commands: {e}", exc_info=True)

    async def on_ready(self) -> None:
        """Fires when the client is logged in and ready."""
        guild_count = len(self.guilds)
        user_count = sum(guild.member_count for guild in self.guilds if guild.member_count)
        
        log.info(f"Logged in as {self.user} (ID: {self.user.id})")
        log.info(f"Connected to {guild_count} guilds serving ~{user_count} users.")
        
        # Set bot presence status
        activity = discord.Activity(
            type=discord.ActivityType.listening,
            name="/ask | Tiffany Bot"
        )
        await self.change_presence(status=discord.Status.online, activity=activity)
        log.info("Bot presence successfully updated.")

    async def on_app_command_error(
        self, 
        interaction: discord.Interaction, 
        error: app_commands.AppCommandError
    ) -> None:
        """Global error handler for slash commands."""
        log.error(f"Slash command error in /{interaction.command.name if interaction.command else 'unknown'}: {error}")
        
        # Handle specific error sub-types if desired
        if isinstance(error, app_commands.CommandOnCooldown):
            message = f"This command is on cooldown. Please retry in {error.retry_after:.2f} seconds."
            embed = create_embed("On Cooldown", message, "warning")
        elif isinstance(error, app_commands.MissingPermissions):
            perms = ", ".join(error.missing_permissions)
            message = f"You require the following permission(s) to use this: `{perms}`."
            embed = create_embed("Permission Denied", message, "error")
        elif isinstance(error, app_commands.BotMissingPermissions):
            perms = ", ".join(error.missing_permissions)
            message = f"I require the following permission(s) to run this: `{perms}`."
            embed = create_embed("Bot Permission Error", message, "error")
        else:
            # Fallback error response
            message = "An unexpected error occurred while executing this command. The developers have been alerted."
            embed = create_embed("Execution Error", message, "error")
            
        # Respond to interaction
        try:
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            log.error(f"Failed to send error response to interaction: {e}")

    async def close(self) -> None:
        """Override close to perform custom cleanup operations on shutdown."""
        log.info("Shutting down bot. Releasing active client and database structures...")
        # Add future services shutdown operations here
        await super().close()
        log.info("Bot process finished gracefully.")

# Define runner main
def main() -> None:
    bot = TiffanyBot()
    try:
        # Run bot utilizing blocking method
        bot.run(Config.DISCORD_BOT_TOKEN, log_handler=None)
    except discord.LoginFailure:
        log.critical("Failed to log in: Invalid token supplied.")
    except Exception as e:
        log.critical(f"Fatal error during bot execution: {e}", exc_info=True)

if __name__ == "__main__":
    main()
