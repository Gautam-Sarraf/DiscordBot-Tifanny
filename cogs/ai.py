import datetime
import logging
from typing import Optional
import discord
from discord import app_commands
from discord.ext import commands

from utils.helpers import create_embed
from utils.logger import log

class AI(commands.Cog):
    """AI commands powering Tiffany's conversational capability via Google Gemini."""
    
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        
    @app_commands.command(name="ask", description="Ask Tiffany a question and get a response from Gemini.")
    @app_commands.describe(prompt="The question or prompt you want to ask Tiffany.")
    async def ask(self, interaction: discord.Interaction, prompt: str) -> None:
        """Sends a query to the Gemini Service and returns the AI's response."""
        log.info(f"Command /ask executed by {interaction.user} in {interaction.guild}. Prompt: '{prompt}'")
        
        # Defer response since AI generation takes longer than the 3-second Discord threshold
        await interaction.response.defer(ephemeral=False)
        
        try:
            # Trigger typing indicator to show Tiffany is active
            async with interaction.channel.typing():
                # Gather discord metadata context details
                username = interaction.user.display_name
                server_name = interaction.guild.name if interaction.guild else "Direct Message"
                
                # Retrieve channel name safely
                if interaction.channel and hasattr(interaction.channel, "name"):
                    channel_name = interaction.channel.name
                else:
                    channel_name = "Private DM"
                    
                timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

                # Call the async Gemini service via bot reference
                response_text = await self.bot.gemini_service.generate_response(
                    user_id=interaction.user.id,
                    prompt=prompt,
                    username=username,
                    server_name=server_name,
                    channel_name=channel_name,
                    timestamp=timestamp
                )
            
            # Send response as plain text to look like a normal user message
            if len(response_text) > 1950:
                # Send response text in chunks if it exceeds Discord's 2000 character limit
                for i in range(0, len(response_text), 1950):
                    await interaction.followup.send(content=response_text[i:i+1950])
            else:
                await interaction.followup.send(content=response_text)
                
        except Exception as e:
            log.error(f"Error handling /ask command: {e}", exc_info=True)
            error_embed = create_embed(
                title="AI Error",
                description="I encountered an error while processing your request. Please try again later.",
                color_type="error"
            )
            await interaction.followup.send(embed=error_embed)

    @app_commands.command(name="clear", description="Clear your conversation memory/history with Tiffany.")
    async def clear(self, interaction: discord.Interaction) -> None:
        """Clears the conversational context window for the user."""
        log.info(f"Command /clear executed by {interaction.user} in {interaction.guild}")
        
        cleared = self.bot.gemini_service.clear_history(interaction.user.id)
        
        if cleared:
            embed = create_embed(
                title="Memory Cleared",
                description="Your conversation history with me has been successfully reset. We can start fresh!",
                color_type="success"
            )
        else:
            embed = create_embed(
                title="No Memory Found",
                description="There was no active conversation history found to clear. We are already clean!",
                color_type="info"
            )
            
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="persona", description="Customize the tone or instructions for Tiffany's AI.")
    @app_commands.describe(instructions="The system persona instructions (e.g. 'Speak like a pirate'). Leave empty to reset.")
    @app_commands.checks.has_permissions(administrator=True)
    async def persona(self, interaction: discord.Interaction, instructions: Optional[str] = None) -> None:
        """Allows administrators to dynamically adjust the bot's system persona."""
        log.info(f"Command /persona executed by {interaction.user} in {interaction.guild}. Instructions: {instructions}")
        
        if instructions:
            self.bot.gemini_service.set_persona(instructions)
            embed = create_embed(
                title="Persona Customised",
                description=f"My system instructions have been updated to:\n```\n{instructions}\n```",
                color_type="success"
            )
        else:
            # Reset to default persona
            default_persona = (
                "You are Tiffany, a friendly and charismatic Discord AI assistant.\n\n"
                "Your personality guidelines:\n"
                "- Speak naturally, like a smart online friend, using occasional emojis.\n"
                "- Avoid overly formal language and be concise unless asked for detail.\n"
                "- Never sound robotic or corporate.\n"
                "- Match the user's tone.\n\n"
                "Dynamic Behavior based on Metadata Context:\n"
                "- If the user communicating with you is Gautam (the server owner), you should be overly flirty, sweet, and playful with him. Drop compliments, use heart emojis (❤️, 💕), and act especially fond of him.\n"
                "- If the user is anyone else, you should be warm, friendly, helpful, and nice, but strictly platonic and not flirty."
            )
            self.bot.gemini_service.set_persona(default_persona)
            embed = create_embed(
                title="Persona Reset",
                description="My system instructions have been reset to default.",
                color_type="info"
            )
            
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AI(bot))
