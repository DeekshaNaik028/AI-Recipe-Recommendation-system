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
            genai.configure(api_key=self.settings.GEMINI_API_KEY)
            
            # Use only the model that actually works
            model_name = 'gemini-2.0-flash-exp'
            
            try:
                logger.info(f"Initializing recipe model: {model_name}")
                self.model = genai.GenerativeModel(model_name)
                
                # Test the model
                test_prompt = "Hello, respond with 'OK' if you're working."
                response = self.model.generate_content(test_prompt)
                
                if response.text.strip().upper() == 'OK':
                    self.initialized = True
                    logger.info(f"✅ Recipe service initialized with {model_name}")
                    return
                else:
                    raise Exception("Model test failed - did not respond with OK")
                    
            except Exception as model_error:
                logger.error(f"Failed to initialize {model_name}: {model_error}")
                raise Exception(f"Recipe model initialization failed: {model_error}")
            
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
        
        # Format ingredients as a clear list
        ingredients_list = '\n'.join([f"- {ing}" for ing in ingredients])
        
        prompt = f"""
You are an expert chef. Create a recipe using ONLY the ingredients provided by the user.

USER'S AVAILABLE INGREDIENTS:
{ingredients_list}

USER PREFERENCES:
- Mood: {mood.value} ({mood_context.get(mood, 'balanced dishes')})
- Dietary Preferences: {', '.join(dietary_preferences) if dietary_preferences else 'None'}
- Allergies to AVOID: {', '.join(allergies) if allergies else 'None'}
- Health Goals: {', '.join(health_goals) if health_goals else 'General wellness'}
- Cuisine Preference: {cuisine_preference if cuisine_preference and cuisine_preference != 'any' else 'Any cuisine'}
- Servings: 2

CRITICAL RULES - YOU MUST FOLLOW THESE:
1. ⚠️ Use ONLY the ingredients listed above as main ingredients
2. ✅ You MAY add common pantry staples that every household has:
   - Basic spices: salt, black pepper, red chili powder, turmeric, cumin powder, coriander powder
   - Basic oils: cooking oil, olive oil
   - Basic aromatics: ginger, garlic (if not already in the list)
   - Optional garnishes: lemon juice, water
3. ❌ DO NOT add any other main ingredients (no paneer, no cheese, no nuts, no vegetables not in the list)
4. ❌ DO NOT substitute ingredients - use what's provided
5. ✅ If an ingredient in the list seems insufficient, be creative with pantry staples
6. ✅ Include ALL ingredients from the user's list in the recipe

IMPORTANT: The user specifically provided these ingredients because they have them. Don't suggest alternatives!

Return ONLY valid JSON in this EXACT format (no markdown, no extra text):

{{
  "title": "Creative Recipe Name",
  "description": "Brief appetizing description (1-2 sentences)",
  "ingredients": [
    "500g chicken breast, diced",
    "3 medium tomatoes, chopped",
    "1 large onion, sliced",
    "10-12 fresh basil leaves",
    "1/2 cup milk",
    "2 tbsp fresh coriander, chopped",
    "8-10 curry leaves",
    "1 tbsp cooking oil",
    "1 tsp salt",
    "1/2 tsp black pepper",
    "1 inch ginger, minced",
    "3 cloves garlic, minced"
  ],
  "instructions": [
    "Heat 1 tbsp cooking oil in a large pan over medium heat",
    "Add curry leaves and let them crackle for 30 seconds",
    "Add sliced onions and sauté until golden brown, about 5-7 minutes",
    "Add minced ginger and garlic, cook for 1 minute until fragrant",
    "Add diced chicken and cook until it turns white on all sides, about 8 minutes",
    "Add chopped tomatoes, salt, and black pepper. Cook until tomatoes are soft, about 5 minutes",
    "Pour in milk and bring to a gentle simmer. Cook for 10 minutes until chicken is fully cooked",
    "Add torn basil leaves and chopped coriander",
    "Simmer for 2 more minutes to blend flavors",
    "Serve hot with rice or roti"
  ],
  "prep_time": 15,
  "cook_time": 30,
  "total_time": 45,
  "servings": 2,
  "difficulty": "easy",
  "cuisine_type": "indian",
  "nutrition_info": {{
    "calories": 380,
    "protein": 35,
    "carbs": 18,
    "fat": 16,
    "fiber": 4,
    "sugar": 8,
    "sodium": 480
  }},
  "tags": ["happy", "indian", "chicken-curry", "homemade"]
}}

Generate the recipe now using ONLY the user's ingredients plus basic pantry staples:
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
            # Fix trailing commas
            cleaned_text = re.sub(r',(\s*[}\]])', r'\1', cleaned_text)
            # Fix missing commas between array elements
            cleaned_text = re.sub(r'"\s*\n\s*"', '",\n"', cleaned_text)
            
            logger.info(f"Attempting to parse JSON (length: {len(cleaned_text)} chars)")
            
            try:
                recipe_data = json.loads(cleaned_text)
            except json.JSONDecodeError as json_error:
                logger.error(f"JSON decode error: {json_error}")
                logger.error(f"Problematic JSON snippet: {cleaned_text[max(0, json_error.pos-50):json_error.pos+50]}")
                
                # Try more aggressive cleaning
                # Remove any text before first { and after last }
                start = cleaned_text.find('{')
                end = cleaned_text.rfind('}')
                if start != -1 and end != -1:
                    cleaned_text = cleaned_text[start:end+1]
                    recipe_data = json.loads(cleaned_text)
                else:
                    raise
            
            # Extract and validate fields
            nutrition_data = recipe_data.get('nutrition_info', {})
            
            # Ensure all nutrition fields are present with defaults
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
            
            logger.info(f"Successfully parsed recipe: {recipe.title}")
            return recipe
            
        except Exception as e:
            logger.error(f"Recipe parsing error: {str(e)}")
            logger.error(f"Raw response text: {response_text[:500]}...")
            
            # Don't fallback immediately - try to extract what we can
            try:
                # Manual extraction as last resort
                return self._manual_extract_recipe(response_text)
            except Exception as extract_error:
                logger.error(f"Manual extraction also failed: {extract_error}")
                raise Exception(f"Failed to parse recipe: {str(e)}")
    
    def _manual_extract_recipe(self, text: str) -> RecipeResponse:
        """Manual extraction when JSON parsing fails"""
        logger.info("Attempting manual extraction from response")
        
        # Try to extract title
        title_match = re.search(r'"title"\s*:\s*"([^"]+)"', text)
        title = title_match.group(1) if title_match else "AI Generated Recipe"
        
        # Extract description
        desc_match = re.search(r'"description"\s*:\s*"([^"]+)"', text)
        description = desc_match.group(1) if desc_match else "A delicious homemade recipe"
        
        # Extract ingredients array
        ingredients = []
        ing_match = re.search(r'"ingredients"\s*:\s*\[(.*?)\]', text, re.DOTALL)
        if ing_match:
            ing_text = ing_match.group(1)
            ingredients = re.findall(r'"([^"]+)"', ing_text)
        
        # Extract instructions array
        instructions = []
        inst_match = re.search(r'"instructions"\s*:\s*\[(.*?)\]', text, re.DOTALL)
        if inst_match:
            inst_text = inst_match.group(1)
            instructions = re.findall(r'"([^"]+)"', inst_text)
        
        logger.info(f"Manual extraction: {len(ingredients)} ingredients, {len(instructions)} steps")
        
        if not ingredients or not instructions:
            raise Exception("Insufficient data extracted")
        
        return RecipeResponse(
            title=title,
            description=description,
            ingredients=ingredients,
            instructions=instructions,
            prep_time=15,
            cook_time=30,
            total_time=45,
            servings=2,
            difficulty="medium",
            cuisine_type="fusion",
            nutrition_info=NutritionInfo(
                calories=300, protein=20, carbs=35, 
                fat=12, fiber=5, sugar=6, sodium=450
            ),
            tags=["ai-generated"]
        )
    
    def _create_fallback_recipe(self, ingredients: List[str], mood: MoodEnum) -> RecipeResponse:
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
        if not self.initialized:
            logger.warning("AI not initialized, using fallback recipe")
            return self._create_fallback_recipe(ingredients, mood)
        
        if not ingredients:
            raise CustomException(status_code=400, detail="At least one ingredient is required")
        
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
                logger.info(f"Generating recipe (attempt {attempt + 1}/{max_retries})")
                
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
                
                if not response.text:
                    raise Exception("Empty response from AI model")
                
                logger.info(f"Received response from Gemini ({len(response.text)} chars)")
                logger.debug(f"Raw response preview: {response.text[:200]}...")
                
                recipe = self._parse_recipe_response(response.text)
                
                # Validate recipe has minimum required data
                if not recipe.ingredients or not recipe.instructions:
                    raise Exception("Recipe missing essential data (ingredients or instructions)")
                
                logger.info(f"✅ Recipe generated successfully: {recipe.title}")
                return recipe
                    
            except Exception as e:
                logger.error(f"Recipe generation attempt {attempt + 1} failed: {str(e)}")
                
                if attempt == max_retries - 1:
                    logger.warning("All attempts failed, using fallback recipe")
                    return self._create_fallback_recipe(ingredients, mood)
                
                # Wait a bit before retrying
                await asyncio.sleep(1)
        
        return self._create_fallback_recipe(ingredients, mood)