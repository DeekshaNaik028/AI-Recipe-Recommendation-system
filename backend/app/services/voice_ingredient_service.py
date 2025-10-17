import google.generativeai as genai
import logging
from typing import List, Dict, Any
import os
import asyncio

from app.core.config import get_settings
from app.utils.exceptions import CustomException

logger = logging.getLogger(__name__)

class VoiceIngredientService:
    """Service for extracting ingredients from voice/audio input using Gemini AI"""
    
    def __init__(self):
        self.settings = get_settings()
        self.model = None
        self.initialized = False
        
        self.ingredient_database = {
            'tomato', 'tomatoes', 'onion', 'onions', 'garlic', 'carrot', 'carrots',
            'potato', 'potatoes', 'sweet potato', 'bell pepper', 'peppers', 'broccoli',
            'spinach', 'lettuce', 'cucumber', 'celery', 'mushroom', 'mushrooms',
            'zucchini', 'eggplant', 'cabbage', 'cauliflower', 'peas', 'corn',
            'ginger', 'chili', 'chilies', 'green beans', 'asparagus', 'kale',
            'apple', 'apples', 'banana', 'bananas', 'orange', 'oranges', 'lemon',
            'lime', 'avocado', 'mango', 'pineapple', 'strawberry', 'strawberries',
            'grapes', 'watermelon', 'berries', 'blueberries', 'coconut',
            'chicken', 'beef', 'steak', 'pork', 'bacon', 'ham', 'fish', 'salmon',
            'tuna', 'cod', 'shrimp', 'prawns', 'egg', 'eggs', 'tofu', 'beans',
            'lentils', 'chickpeas', 'paneer', 'milk', 'cheese', 'yogurt',
            'butter', 'cream', 'heavy cream', 'sour cream', 'cottage cheese',
            'rice', 'pasta', 'spaghetti', 'noodles', 'bread', 'flour', 'wheat flour',
            'oats', 'quinoa', 'couscous', 'basil', 'cilantro', 'coriander',
            'parsley', 'mint', 'rosemary', 'thyme', 'oregano', 'cumin',
            'turmeric', 'paprika', 'cinnamon', 'olive oil', 'vegetable oil',
            'coconut oil', 'salt', 'pepper', 'soy sauce', 'vinegar', 'honey',
            'sugar', 'ketchup', 'mustard', 'almonds', 'cashews', 'peanuts',
            'walnuts', 'sesame seeds', 'chia seeds', 'dill', 'fennel'
        }
    
    async def initialize(self):
        """Initialize Gemini AI model"""
        try:
            genai.configure(api_key=self.settings.GEMINI_API_KEY)
            
            model_options = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-2.0-flash-exp']
            
            for model_name in model_options:
                try:
                    logger.info(f"Initializing model: {model_name}")
                    self.model = genai.GenerativeModel(model_name)
                    
                    test_response = self.model.generate_content("Say OK")
                    if test_response and test_response.text:
                        self.initialized = True
                        logger.info(f"Model initialized: {model_name}")
                        return
                except Exception as e:
                    logger.warning(f"Model {model_name} failed: {e}")
                    continue
            
            raise Exception("No suitable model available")
                
        except Exception as e:
            logger.error(f"Gemini initialization failed: {str(e)}")
            self.initialized = False
    
    async def transcribe_and_extract_ingredients(self, audio_file_path: str) -> List[str]:
        """
        Extract ingredients from audio file
        CRITICAL FIX: Using synchronous API call in async context properly
        """
        try:
            if not self.initialized:
                raise Exception("AI service not initialized")
            
            logger.info(f"Processing audio: {audio_file_path}")
            
            with open(audio_file_path, 'rb') as f:
                audio_data = f.read()
            
            if len(audio_data) < 5000:
                raise Exception("Audio file too small - record for at least 2 seconds")
            
            logger.info(f"Audio size: {len(audio_data) / 1024:.1f} KB")
            
            import mimetypes
            mime_type, _ = mimetypes.guess_type(audio_file_path)
            if not mime_type or not mime_type.startswith('audio/'):
                mime_type = 'audio/wav'
            
            logger.info(f"MIME type: {mime_type}")
            
            prompt = """Extract food ingredients from this audio. 
            Return ONLY a comma-separated list of ingredient names in lowercase.
            Examples:
            - "I have tomato, onion, garlic" → tomato, onion, garlic
            - "chicken breast and rice" → chicken, rice
            
            Rules:
            - Use singular form (tomatoes → tomato)
            - Remove quantities and measurements
            - Only return ingredient names
            - Separate with commas
            """
            
            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(
                    [prompt, {"mime_type": mime_type, "data": audio_data}],
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.1,
                        max_output_tokens=500
                    )
                )
            )
            
            if not response or not response.text:
                raise Exception("No response from AI")
            
            logger.info(f"AI response: {response.text}")
            
            ingredients = self._parse_ingredient_response(response.text)
            if not ingredients:
                raise Exception("No ingredients detected")
            
            logger.info(f"Extracted: {ingredients}")
            return ingredients
            
        except Exception as e:
            logger.error(f"Audio extraction error: {str(e)}")
            raise Exception(f"Failed to process audio: {str(e)}")
    
    async def extract_from_text(self, text: str) -> List[str]:
        """Extract ingredients from text input"""
        try:
            if not text or len(text.strip()) < 2:
                raise Exception("Text too short")
            
            if not self.initialized:
                return self._simple_text_extraction(text)
            
            prompt = f"""Extract food ingredients from: "{text}"
            Return ONLY comma-separated ingredient names in lowercase.
            No extra text."""
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.1,
                        max_output_tokens=300
                    )
                )
            )
            
            ingredients = self._parse_ingredient_response(response.text)
            logger.info(f"Text extraction: {ingredients}")
            return ingredients
            
        except Exception as e:
            logger.error(f"Text extraction error: {str(e)}")
            return self._simple_text_extraction(text)
    
    def _parse_ingredient_response(self, response_text: str) -> List[str]:
        """Parse and clean ingredient response"""
        cleaned = response_text.strip().lower()
        cleaned = cleaned.replace('```', '').replace('*', '').strip()
        
        if ',' in cleaned:
            ingredients = [i.strip() for i in cleaned.split(',')]
        elif '\n' in cleaned:
            ingredients = [i.strip() for i in cleaned.split('\n') if i.strip()]
        else:
            ingredients = cleaned.split()
        
        valid = []
        seen = set()
        skip = {'and', 'the', 'some', 'a', 'an', 'of', 'with', 'or', 'is', 'are'}
        
        for ing in ingredients:
            ing = ing.strip('-•.,"\' ')
            if len(ing) > 1 and ing not in skip and ing not in seen:
                valid.append(ing)
                seen.add(ing)
        
        return valid[:self.settings.MAX_INGREDIENTS_DETECTED]
    
    def _simple_text_extraction(self, text: str) -> List[str]:
        """Fallback text extraction"""
        text_lower = text.lower()
        found = []
        seen = set()
        
        for ingredient in sorted(self.ingredient_database, key=len, reverse=True):
            if ingredient in text_lower and ingredient not in seen:
                found.append(ingredient)
                seen.add(ingredient)
        
        return found[:self.settings.MAX_INGREDIENTS_DETECTED]
    
    async def validate_ingredients(self, ingredients: List[str]) -> Dict[str, Any]:
        """Validate ingredients"""
        validated = []
        suggestions = {}
        
        for ing in ingredients:
            ing_lower = ing.lower().strip()
            if ing_lower in self.ingredient_database:
                validated.append(ing_lower)
            else:
                similar = [db_ing for db_ing in self.ingredient_database 
                          if ing_lower in db_ing or db_ing in ing_lower]
                if similar:
                    validated.append(similar[0])
                    suggestions[ing] = similar[0]
                else:
                    validated.append(ing_lower)
        
        return {
            "validated_ingredients": validated,
            "suggestions": suggestions,
            "original_count": len(ingredients),
            "validated_count": len(validated)
        }


