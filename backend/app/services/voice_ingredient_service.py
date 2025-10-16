import google.generativeai as genai
import logging
from typing import List, Dict, Any
import os
from pathlib import Path

from app.core.config import get_settings
from app.utils.exceptions import CustomException

logger = logging.getLogger(__name__)

class VoiceIngredientService:
    """Service for extracting ingredients from voice/audio input using Gemini AI"""
    
    def __init__(self):
        self.settings = get_settings()
        self.model = None
        self.initialized = False
        
        # Common ingredient variations for validation
        self.ingredient_database = {
            # Vegetables
            'tomato', 'tomatoes', 'onion', 'onions', 'garlic', 'carrot', 'carrots',
            'potato', 'potatoes', 'sweet potato', 'bell pepper', 'peppers', 'broccoli',
            'spinach', 'lettuce', 'cucumber', 'celery', 'mushroom', 'mushrooms',
            'zucchini', 'eggplant', 'cabbage', 'cauliflower', 'peas', 'corn',
            'ginger', 'chili', 'chilies', 'green beans', 'asparagus',
            
            # Fruits
            'apple', 'apples', 'banana', 'bananas', 'orange', 'oranges', 'lemon',
            'lime', 'avocado', 'mango', 'pineapple', 'strawberry', 'strawberries',
            'grapes', 'watermelon', 'berries', 'blueberries',
            
            # Proteins
            'chicken', 'chicken breast', 'beef', 'steak', 'pork', 'bacon', 'ham',
            'fish', 'salmon', 'tuna', 'cod', 'shrimp', 'prawns', 'egg', 'eggs',
            'tofu', 'beans', 'lentils', 'chickpeas', 'paneer',
            
            # Dairy
            'milk', 'cheese', 'cheddar', 'mozzarella', 'yogurt', 'butter', 'cream',
            'heavy cream', 'sour cream', 'cottage cheese',
            
            # Grains & Pasta
            'rice', 'basmati rice', 'pasta', 'spaghetti', 'noodles', 'bread',
            'flour', 'wheat flour', 'oats', 'quinoa', 'couscous',
            
            # Herbs & Spices
            'basil', 'cilantro', 'coriander', 'parsley', 'mint', 'rosemary',
            'thyme', 'oregano', 'cumin', 'turmeric', 'paprika', 'cinnamon',
            
            # Condiments & Oils
            'olive oil', 'vegetable oil', 'coconut oil', 'salt', 'pepper',
            'soy sauce', 'vinegar', 'honey', 'sugar', 'ketchup', 'mustard',
            
            # Nuts & Seeds
            'almonds', 'cashews', 'peanuts', 'walnuts', 'sesame seeds', 'chia seeds'
        }
    
    async def initialize(self):
        """Initialize Gemini AI model"""
        try:
            genai.configure(api_key=self.settings.GEMINI_API_KEY)
            
            # Try multiple model versions for compatibility
            model_options = [
                'gemini-1.5-flash',  # Stable version
                'gemini-1.5-pro',    # Pro version
                'gemini-2.0-flash-exp'  # Experimental
            ]
            
            for model_name in model_options:
                try:
                    logger.info(f"Trying to initialize model: {model_name}")
                    self.model = genai.GenerativeModel(model_name)
                    
                    # Test the model
                    test_prompt = "Respond with 'OK' if initialized"
                    response = self.model.generate_content(test_prompt)
                    
                    if response.text.strip().upper() == 'OK':
                        self.initialized = True
                        logger.info(f"Voice Ingredient Service initialized successfully with {model_name}")
                        return
                except Exception as model_error:
                    logger.warning(f"Failed to initialize {model_name}: {model_error}")
                    continue
            
            raise Exception("All model initialization attempts failed")
                
        except Exception as e:
            logger.error(f"Failed to initialize Gemini AI: {str(e)}")
            logger.warning("Voice ingredient detection will not work")
            self.initialized = False
    
    async def transcribe_and_extract_ingredients(
        self, 
        audio_file_path: str
    ) -> List[str]:
        """
        Transcribe audio and extract ingredients using Gemini AI
        """
        try:
            if not self.initialized:
                logger.error("AI not initialized! Check your GEMINI_API_KEY")
                raise Exception("Voice service not properly initialized")
            
            logger.info(f"Processing audio file: {audio_file_path}")
            
            # Read audio file
            with open(audio_file_path, 'rb') as f:
                audio_data = f.read()
            
            logger.info(f"Audio file size: {len(audio_data)} bytes")
            
            # Create detailed prompt for ingredient extraction
            prompt = """
            You are listening to an audio recording where someone is listing food ingredients they have available.
            
            TASK:
            1. Carefully transcribe EXACTLY what you hear
            2. Extract ALL food ingredients mentioned
            3. Normalize ingredient names to singular form (e.g., "tomatoes" → "tomato")
            4. Remove quantities, measurements, and filler words
            5. Keep the ingredient names simple and standard
            
            EXAMPLES:
            Audio: "I have three tomatoes, two onions, and some garlic"
            Output: tomato, onion, garlic
            
            Audio: "chicken breast, milk, curry leaves, coriander, and basil"
            Output: chicken, milk, curry leaves, coriander, basil
            
            Audio: "I've got rice, beans, bell peppers"
            Output: rice, beans, bell pepper
            
            IMPORTANT: 
            - Return ONLY a comma-separated list of ingredients
            - Use lowercase
            - No numbers, no extra text
            - Include ALL ingredients you hear, even herbs and spices
            
            Now, listen to the audio and extract the ingredients:
            """
            
            # Prepare audio data for Gemini
            import mimetypes
            mime_type, _ = mimetypes.guess_type(audio_file_path)
            if not mime_type:
                mime_type = 'audio/wav'  # Default fallback
            
            logger.info(f"Audio MIME type: {mime_type}")
            
            # Generate response with inline audio data
            logger.info("Sending to Gemini for transcription...")
            
            # Use the correct API format with inline data
            response = self.model.generate_content(
                [
                    prompt,
                    {
                        "mime_type": mime_type,
                        "data": audio_data
                    }
                ],
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2,
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=1000,
                ),
                request_options={"timeout": 60}
            )
            
            if not response.text:
                raise Exception("Empty response from Gemini AI")
            
            logger.info(f"Raw Gemini response: {response.text}")
            
            # Parse the response
            ingredients = self._parse_ingredient_response(response.text)
            
            if not ingredients:
                raise Exception("No ingredients extracted from audio")
            
            logger.info(f"Successfully extracted ingredients: {ingredients}")
            
            return ingredients
            
        except Exception as e:
            logger.error(f"Error in audio transcription: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            # Don't use fallback - raise the error so user knows it failed
            raise Exception(f"Failed to process audio: {str(e)}")
    
    async def extract_from_text(self, text: str) -> List[str]:
        """
        Extract ingredients from text input (for manual typing fallback)
        """
        try:
            if not self.initialized:
                return self._simple_text_extraction(text)
            
            prompt = f"""
            Extract all food ingredients from this text: "{text}"
            
            Rules:
            1. Extract only actual food ingredients
            2. Normalize names (plural to singular, remove quantities)
            3. Return comma-separated list in lowercase
            4. Ignore quantities, measurements, and cooking actions
            
            Return ONLY the ingredient list.
            """
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=300,
                )
            )
            
            ingredients = self._parse_ingredient_response(response.text)
            logger.info(f"Extracted from text: {ingredients}")
            
            return ingredients
            
        except Exception as e:
            logger.error(f"Error extracting from text: {str(e)}")
            return self._simple_text_extraction(text)
    
    def _parse_ingredient_response(self, response_text: str) -> List[str]:
        """Parse AI response into clean ingredient list"""
        # Remove any markdown, extra whitespace
        cleaned = response_text.strip().lower()
        cleaned = cleaned.replace('```', '').replace('*', '').strip()
        
        # Split by common separators
        if ',' in cleaned:
            ingredients = [i.strip() for i in cleaned.split(',')]
        elif '\n' in cleaned:
            ingredients = [i.strip() for i in cleaned.split('\n')]
        else:
            ingredients = [i.strip() for i in cleaned.split()]
        
        # Clean and validate
        valid_ingredients = []
        for ing in ingredients:
            # Remove common prefixes/suffixes
            ing = ing.strip('-•. ')
            
            # Skip empty or very short strings
            if len(ing) < 2:
                continue
            
            # Skip common non-ingredients
            skip_words = ['and', 'the', 'some', 'a', 'an', 'of', 'with', 'have', 'got']
            if ing in skip_words:
                continue
            
            # Add to valid list
            valid_ingredients.append(ing)
        
        # Remove duplicates while preserving order
        seen = set()
        result = []
        for ing in valid_ingredients:
            if ing not in seen:
                seen.add(ing)
                result.append(ing)
        
        return result[:self.settings.MAX_INGREDIENTS_DETECTED]
    
    def _simple_text_extraction(self, text: str) -> List[str]:
        """Simple keyword-based extraction fallback"""
        text_lower = text.lower()
        found_ingredients = []
        
        for ingredient in self.ingredient_database:
            if ingredient in text_lower:
                # Get base form (singular)
                base = ingredient.rstrip('s')
                if base not in found_ingredients:
                    found_ingredients.append(base)
        
        if not found_ingredients:
            # Try splitting and matching
            words = text_lower.replace(',', ' ').split()
            for word in words:
                word = word.strip('.,!?')
                if word in self.ingredient_database:
                    found_ingredients.append(word)
        
        return found_ingredients[:self.settings.MAX_INGREDIENTS_DETECTED]
    
    async def _fallback_extraction(self) -> List[str]:
        """Fallback when AI is unavailable"""
        logger.warning("Using fallback ingredient list")
        return ["tomato", "onion", "garlic", "olive oil", "salt", "pepper"]
    
    async def validate_ingredients(self, ingredients: List[str]) -> Dict[str, Any]:
        """Validate and suggest corrections for ingredients"""
        validated = []
        suggestions = {}
        
        for ing in ingredients:
            ing_lower = ing.lower().strip()
            
            # Direct match
            if ing_lower in self.ingredient_database:
                validated.append(ing_lower)
            else:
                # Find similar ingredients
                similar = [
                    db_ing for db_ing in self.ingredient_database
                    if ing_lower in db_ing or db_ing in ing_lower
                ]
                
                if similar:
                    validated.append(similar[0])
                    suggestions[ing] = similar[0]
                else:
                    # Keep original if no match found
                    validated.append(ing_lower)
        
        return {
            "validated_ingredients": validated,
            "suggestions": suggestions,
            "original_count": len(ingredients),
            "validated_count": len(validated)
        }