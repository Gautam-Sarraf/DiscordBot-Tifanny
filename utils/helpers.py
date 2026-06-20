import datetime
import discord
from typing import Optional

def format_uptime(start_time: datetime.datetime) -> str:
    """Calculates and returns a human-readable uptime duration."""
    now = datetime.datetime.now(datetime.timezone.utc)
    # Ensure start_time is timezone-aware
    if start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo=datetime.timezone.utc)
        
    delta = now - start_time
    
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")
    
    return " ".join(parts)


def create_embed(
    title: str,
    description: str,
    color_type: str = "info",
    fields: Optional[list[dict[str, str]]] = None,
    footer_text: Optional[str] = None,
    thumbnail_url: Optional[str] = None
) -> discord.Embed:
    """
    Creates a styled, premium Discord embed.
    
    Colors:
    - info: #FFB7C5 (Cherry Blossom Pink)
    - success: #2ecc71 (Emerald Green)
    - warning: #f1c40f (Sun Yellow)
    - error: #e74c3c (Alizarin Red)
    """
    colors = {
        "info": 0xFFB7C5,      # Aesthetic Cherry Blossom Pink
        "success": 0x2ECC71,   # Vibrant Green
        "warning": 0xF1C40F,   # Muted Yellow
        "error": 0xE74C3C      # Bright Red
    }
    
    color = colors.get(color_type, colors["info"])
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )
    
    if fields:
        for field in fields:
            inline = field.get("inline", False)
            embed.add_field(name=field["name"], value=field["value"], inline=inline)
            
    if footer_text:
        embed.set_footer(text=footer_text)
    else:
        embed.set_footer(text="Tiffany Bot • Elegant & Intelligent")
        
    if thumbnail_url:
        embed.set_thumbnail(url=thumbnail_url)
        
    return embed
