import asyncio
import logging
from typing import Dict, List, Optional
from google import genai
from google.genai import types
from google.genai.errors import APIError

from services.config import Config

logger = logging.getLogger("TiffanyBot")

class GeminiService:
    """
    Handles communication with Google's Gemini API, managing user conversation history,
    system personas, and providing future extensibility for RAG / Knowledge base.
    """
    
    def __init__(self) -> None:
        self.api_key: str = Config.GEMINI_API_KEY
        self.client: Optional[genai.Client] = None
        self.enabled: bool = False
        
        # User session history: dict mapping user_id (int) -> list of Content/Message objects
        # We store structured history to pass back to the API for full conversation memory.
        self.history: Dict[int, List[dict]] = {}
        
        # System instructions to establish Tiffany's persona
        self.persona = (
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
        
        # Limit history memory per user (sliding window) to control context window and token usage
        self.max_history_turns: int = 10
        
        if self.api_key:
            try:
                # Initialize Google GenAI client
                # Client initialization can be synchronous, but we'll use client.aio for async requests
                self.client = genai.Client(api_key=self.api_key)
                self.enabled = True
                logger.info("Gemini AI Service initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini AI Service client: {e}")
        else:
            logger.warning(
                "GEMINI_API_KEY not found in environment. AI commands will be disabled or run in dry-run mode."
            )
            
    async def generate_response(
        self,
        user_id: int,
        prompt: str,
        username: str,
        server_name: str,
        channel_name: str,
        timestamp: str
    ) -> str:
        """
        Sends a prompt to Gemini with user context and conversation history.
        Maintains history dynamically.
        """
        if not self.enabled or not self.client:
            return (
                "Hello! I would love to answer that, but my Gemini AI brain is not fully configured yet. "
                "Please configure `GEMINI_API_KEY` in my environment to enable chatting!"
            )
            
        try:
            # Build conversation context
            user_history = self.history.setdefault(user_id, [])
            
            # Prepare contents sequence for the model including history
            contents = []
            for message in user_history:
                contents.append(
                    types.Content(
                        role=message["role"],
                        parts=[types.Part.from_text(text=message["text"])]
                    )
                )
            
            # Inject Discord environment metadata context for current prompt
            # This helps the model respond contextually without revealing raw info unless relevant
            metadata_context = (
                f"[Context - Username: {username}, Server/Guild: {server_name}, "
                f"Channel: {channel_name}, Current Timestamp: {timestamp}]\n"
            )
            meta_prompt = f"{metadata_context}{prompt}"
            
            # Append current prompt with metadata context
            contents.append(
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=meta_prompt)]
                )
            )
            
            # Setup configuration including persona system instructions
            config = types.GenerateContentConfig(
                system_instruction=self.persona,
                temperature=0.7,
                max_output_tokens=1024,
            )
            
            logger.debug(f"Sending prompt to Gemini for user {user_id} (History depth: {len(user_history)})")
            
            # Make the async API request using client.aio
            # We use gemma-4-31b-it as the correct instruction-tuned free-tier model
            response = await self.client.aio.models.generate_content(
                model="gemma-4-31b-it",
                contents=contents,
                config=config
            )
            
            response_text = response.text
            if not response_text:
                response_text = "I received an empty response. Please try rephrasing your question."
            
            # Save transaction to history (store clean prompt without metadata block)
            user_history.append({"role": "user", "text": prompt})
            user_history.append({"role": "model", "text": response_text})
            
            # Prune history if it exceeds sliding window
            if len(user_history) > self.max_history_turns * 2:
                # Remove the oldest exchange (1 user message + 1 model response)
                self.history[user_id] = user_history[2:]
                
            return response_text
            
        except APIError as e:
            logger.error(f"Gemini API Error for user {user_id}: {e}")
            return f"My apologies, but I encountered an error communicating with my AI model: {e.message}"
        except Exception as e:
            logger.error(f"Unexpected error in Gemini service: {e}", exc_info=True)
            return "My apologies, but an unexpected error occurred while processing your request."
            
    def clear_history(self, user_id: int) -> bool:
        """Clears the history memory for a specific user."""
        if user_id in self.history:
            del self.history[user_id]
            logger.info(f"Cleared memory for user {user_id}")
            return True
        return False
        
    def set_persona(self, custom_persona: str) -> None:
        """Dynamically updates the bot's system persona."""
        self.persona = custom_persona
        logger.info("Bot persona has been updated.")
