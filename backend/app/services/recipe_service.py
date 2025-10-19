import google.generativeai as genai
import json
import re
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
import asyncio

from app.models.schemas import RecipeResponse, NutritionInfo, MoodEnum
from app.core.config import get_settings
from app.utils.exceptions import CustomException

logger = logging.getLogger(__name__)

class RecipeService:
    def __init__(self):
        self.settings = get_settings()
        self.model = None
        self.initialized = False
    
    async def initialize(self):
        try:
            # Configure Gemini API
            genai.configure(api_key=self.settings.GEMINI_API_KEY)
            
            # Use the working model
            model_name = 'gemini-2.0-flash-exp'
            
            logger.info(f"Initializing recipe model: {model_name}")
            self.model = genai.GenerativeModel(model_name)
            
            # Test the model
            test_prompt = "Respond with 'OK' if working."
            response = self.model.generate_content(test_prompt)
            
            if response and response.text and 'OK' in response.text.upper():
                self.initialized = True
                logger.info(f"✅ Recipe service initialized successfully with {model_name}")
            else:
                raise Exception("Model test failed")
                    
        except Exception as e:
            logger.error(f"Failed to initialize Gemini AI: {str(e)}")
            logger.warning("Recipe generation will use fallback mode")
            self.initialized = False
    
    def _create_recipe_prompt(
        self, 
        ingredients: List[str], 
        mood: MoodEnum, 
        dietary_preferences: List[str],
        allergies: List[str], 
        health_goals: List[str],
        cuisine_preference: Optional[str] = None
    ) -> str:
        mood_context = {
            MoodEnum.HAPPY: "energizing and colorful dishes that bring joy",
            MoodEnum.SAD: "comforting and warming foods that provide emotional comfort",
            MoodEnum.ENERGETIC: "protein-rich and nutritious meals that sustain energy",
            MoodEnum.TIRED: "easy-to-make, nourishing dishes that require minimal effort",
            MoodEnum.STRESSED: "calming and simple recipes with soothing flavors",
            MoodEnum.CALM: "light and refreshing meals that maintain tranquility",
            MoodEnum.EXCITED: "bold and adventurous dishes with exciting flavors",
            MoodEnum.BORED: "creative and unique recipes to spark culinary interest"
        }
        
        ingredients_list = '\n'.join([f"- {ing}" for ing in ingredients])
        
        prompt = f"""
You are an expert chef. Create a REAL, PRACTICAL recipe using the ingredients provided.

USER'S AVAILABLE INGREDIENTS:
{ingredients_list}

USER PREFERENCES:
- Mood: {mood.value} ({mood_context.get(mood, 'balanced dishes')})
- Dietary Preferences: {', '.join(dietary_preferences) if dietary_preferences else 'None'}
- Allergies to AVOID: {', '.join(allergies) if allergies else 'None'}
- Health Goals: {', '.join(health_goals) if health_goals else 'General wellness'}
- Cuisine Preference: {cuisine_preference if cuisine_preference and cuisine_preference != 'any' else 'Any cuisine'}
- Servings: 2

CRITICAL RULES:
1. Use ONLY the ingredients listed above as main ingredients
2. You MAY add common pantry staples: salt, pepper, oil, water, basic spices
3. Create a REAL recipe that can actually be cooked
4. Include ALL user's ingredients in the recipe
5. Make it practical and delicious

Return ONLY valid JSON (no markdown, no extra text):

{{
  "title": "Recipe Name",
  "description": "Brief description (1-2 sentences)",
  "ingredients": [
    "500g ingredient1",
    "2 medium ingredient2",
    "1 tbsp oil",
    "1 tsp salt"
  ],
  "instructions": [
    "Step 1 instruction",
    "Step 2 instruction",
    "Step 3 instruction"
  ],
  "prep_time": 15,
  "cook_time": 30,
  "total_time": 45,
  "servings": 2,
  "difficulty": "easy",
  "cuisine_type": "italian",
  "nutrition_info": {{
    "calories": 380,
    "protein": 35,
    "carbs": 18,
    "fat": 16,
    "fiber": 4,
    "sugar": 8,
    "sodium": 480
  }},
  "tags": ["mood-based", "homemade"]
}}

Generate a real, cookable recipe now:
"""
        return prompt.strip()
    
    def _parse_recipe_response(self, response_text: str) -> RecipeResponse:
        try:
            # Clean up the response
            cleaned_text = response_text.strip()
            
            # Remove markdown code blocks
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]
            elif cleaned_text.startswith('```'):
                cleaned_text = cleaned_text[3:]
            
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]
            
            cleaned_text = cleaned_text.strip()
            
            # Try to extract JSON object
            json_match = re.search(r'\{.*\}', cleaned_text, re.DOTALL)
            if json_match:
                cleaned_text = json_match.group()
            
            # Fix common JSON errors
            cleaned_text = re.sub(r',(\s*[}\]])', r'\1', cleaned_text)
            cleaned_text = re.sub(r'"\s*\n\s*"', '",\n"', cleaned_text)
            
            logger.info(f"Parsing JSON response (length: {len(cleaned_text)} chars)")
            
            try:
                recipe_data = json.loads(cleaned_text)
            except json.JSONDecodeError as json_error:
                logger.error(f"JSON decode error at position {json_error.pos}")
                # Try more aggressive cleaning
                start = cleaned_text.find('{')
                end = cleaned_text.rfind('}')
                if start != -1 and end != -1:
                    cleaned_text = cleaned_text[start:end+1]
                    recipe_data = json.loads(cleaned_text)
                else:
                    raise
            
            # Extract and validate fields
            nutrition_data = recipe_data.get('nutrition_info', {})
            
            nutrition_info = NutritionInfo(
                calories=float(nutrition_data.get('calories', 300)),
                protein=float(nutrition_data.get('protein', 15)),
                carbs=float(nutrition_data.get('carbs', 30)),
                fat=float(nutrition_data.get('fat', 10)),
                fiber=float(nutrition_data.get('fiber', 5)),
                sugar=float(nutrition_data.get('sugar', 5)),
                sodium=float(nutrition_data.get('sodium', 400))
            )
            
            recipe = RecipeResponse(
                title=recipe_data.get('title', 'Generated Recipe'),
                description=recipe_data.get('description', 'A delicious recipe'),
                ingredients=recipe_data.get('ingredients', []),
                instructions=recipe_data.get('instructions', []),
                prep_time=int(recipe_data.get('prep_time', 15)),
                cook_time=int(recipe_data.get('cook_time', 30)),
                total_time=int(recipe_data.get('total_time', 45)),
                servings=int(recipe_data.get('servings', 2)),
                difficulty=recipe_data.get('difficulty', 'medium'),
                cuisine_type=recipe_data.get('cuisine_type', 'fusion'),
                nutrition_info=nutrition_info,
                tags=recipe_data.get('tags', [])
            )
            
            logger.info(f"✅ Successfully parsed recipe: {recipe.title}")
            return recipe
            
        except Exception as e:
            logger.error(f"Recipe parsing error: {str(e)}")
            raise Exception(f"Failed to parse recipe: {str(e)}")
    
    def _create_fallback_recipe(self, ingredients: List[str], mood: MoodEnum) -> RecipeResponse:
        """Only used if AI is completely unavailable"""
        mood_titles = {
            MoodEnum.HAPPY: "Cheerful",
            MoodEnum.SAD: "Comforting",
            MoodEnum.ENERGETIC: "Power-Packed",
            MoodEnum.TIRED: "Easy",
            MoodEnum.STRESSED: "Soothing",
            MoodEnum.CALM: "Gentle",
            MoodEnum.EXCITED: "Adventure",
            MoodEnum.BORED: "Creative"
        }
        
        title = f"{mood_titles.get(mood, 'Simple')} {ingredients[0].title()} Dish"
        
        return RecipeResponse(
            title=title,
            description=f"A simple {mood.value} recipe using {', '.join(ingredients[:3])}.",
            ingredients=[f"{ingredient} (as needed)" for ingredient in ingredients] + ["Salt and pepper to taste"],
            instructions=[
                "Prepare all available ingredients.",
                "Heat oil in a pan over medium heat.",
                "Add main ingredients and cook until done.",
                "Season with salt and pepper to taste.",
                "Serve hot and enjoy!"
            ],
            prep_time=10,
            cook_time=20,
            total_time=30,
            servings=2,
            difficulty="easy",
            cuisine_type="home-style",
            nutrition_info=NutritionInfo(
                calories=250, protein=12, carbs=25, fat=10,
                fiber=4, sugar=6, sodium=400
            ),
            tags=[mood.value, "simple", "homemade"]
        )
    
    async def generate_recipe(
        self,
        ingredients: List[str],
        mood: MoodEnum,
        dietary_preferences: List[str] = [],
        allergies: List[str] = [],
        health_goals: List[str] = [],
        cuisine_preference: Optional[str] = None,
        max_retries: int = 3
    ) -> RecipeResponse:
        
        if not ingredients:
            raise CustomException(status_code=400, detail="At least one ingredient is required")
        
        # Check if AI is initialized
        if not self.initialized:
            logger.error("❌ AI not initialized - check your GEMINI_API_KEY in .env file")
            raise CustomException(
                status_code=503, 
                detail="AI service not available. Please check API configuration."
            )
        
        prompt = self._create_recipe_prompt(
            ingredients=ingredients,
            mood=mood,
            dietary_preferences=dietary_preferences,
            allergies=allergies,
            health_goals=health_goals,
            cuisine_preference=cuisine_preference
        )
        
        for attempt in range(max_retries):
            try:
                logger.info(f"🔄 Generating recipe (attempt {attempt + 1}/{max_retries})")
                
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.7,
                        top_p=0.8,
                        top_k=40,
                        max_output_tokens=2048,
                    ),
                    request_options={"timeout": 120}
                )
                
                if not response or not response.text:
                    raise Exception("Empty response from AI model")
                
                logger.info(f"📥 Received response from Gemini ({len(response.text)} chars)")
                
                recipe = self._parse_recipe_response(response.text)
                
                # Validate recipe has minimum required data
                if not recipe.ingredients or not recipe.instructions:
                    raise Exception("Recipe missing essential data")
                
                logger.info(f"✅ Real recipe generated: {recipe.title}")
                return recipe
                    
            except Exception as e:
                logger.error(f"❌ Attempt {attempt + 1} failed: {str(e)}")
                
                if attempt == max_retries - 1:
                    logger.error("All attempts failed")
                    raise CustomException(
                        status_code=500,
                        detail="Failed to generate recipe. Please try again."
                    )
                
                await asyncio.sleep(1)
        
        # This should never be reached
        raise CustomException(status_code=500, detail="Recipe generation failed")