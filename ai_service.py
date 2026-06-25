import os
import logging
from dotenv import load_dotenv
import google.generativeai as genai

# Setup logging
logger = logging.getLogger(__name__)

# Load local environment variables (.env file)
load_dotenv()

class AIService:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AIService, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.is_gemini_available = False
        self.model_name = "gemini-1.5-flash"
        
        if self.api_key:
            # Clean key
            self.api_key = self.api_key.strip()
            # Check for placeholder string
            if "YOUR_KEY" in self.api_key or "YOUR_GEMINI_API_KEY" in self.api_key or not self.api_key:
                logger.warning("Gemini API key is a placeholder or empty. Defaulting to Demo Mode.")
            else:
                try:
                    genai.configure(api_key=self.api_key)
                    self.is_gemini_available = True
                    logger.info("Successfully configured Gemini API. Online AI Mode is active.")
                except Exception as e:
                    logger.error(f"Error configuring Gemini API key: {e}. Defaulting to Offline Demo Mode.")
        else:
            logger.info("No Gemini API key found in environment. Defaulting to Offline Demo Mode.")
            
        self._initialized = True

    def generate_text(self, prompt, system_instruction=None):
        """
        Attempts to generate text using the Gemini API.
        Returns the generated text on success, or None on failure/if in Demo Mode.
        """
        if not self.is_gemini_available:
            return None
            
        try:
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_instruction
            )
            response = model.generate_content(prompt)
            if response and response.text:
                return response.text
            return None
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}. Falling back to Demo Mode.")
            return None

# Singleton instance
ai_service = AIService()
