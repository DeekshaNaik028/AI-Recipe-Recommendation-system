#recipe_service.py
import google.generativeai as genai
import json
import re
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

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
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            test_prompt = "Hello, respond with 'OK' if you're working."
            response = self.model.generate_content(test_prompt)
            if response.text.strip().upper() == 'OK':
                self.initialized = True
                logger.info("Gemini AI model initialized successfully")
            else:
                raise Exception("Model test failed")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini AI: {str(e)}")
            logger.warning("Continuing without AI - will use mock responses")
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
        
        prompt = f"""
        You are an expert chef and nutritionist. Create a personalized recipe based on:

        Available Ingredients: {', '.join(ingredients)}
        Current Mood: {mood.value} - Focus on {mood_context.get(mood, 'balanced dishes')}
        Dietary Preferences: {', '.join(dietary_preferences) if dietary_preferences else 'None'}
        Allergies: {', '.join(allergies) if allergies else 'None'}
        Health Goals: {', '.join(health_goals) if health_goals else 'General wellness'}
        Cuisine: {cuisine_preference if cuisine_preference and cuisine_preference != 'any' else 'Any'}

        Return ONLY valid JSON in this exact format:
        {{
            "title": "Recipe name",
            "description": "Brief description",
            "ingredients": ["ingredient 1 with quantity", "ingredient 2 with quantity"],
            "instructions": ["Step 1", "Step 2", "Step 3"],
            "prep_time": 15,
            "cook_time": 30,
            "total_time": 45,
            "servings": 2,
            "difficulty": "easy",
            "cuisine_type": "italian",
            "nutrition_info": {{
                "calories": 350,
                "protein": 20,
                "carbs": 45,
                "fat": 12,
                "fiber": 5,
                "sugar": 8,
                "sodium": 500
            }},
            "tags": ["mood-tag", "dietary-tag"]
        }}
        """
        return prompt.strip()
    
    def _parse_recipe_response(self, response_text: str) -> RecipeResponse:
        try:
            cleaned_text = response_text.strip()
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]
            
            json_match = re.search(r'\{.*\}', cleaned_text, re.DOTALL)
            if json_match:
                cleaned_text = json_match.group()
            
            recipe_data = json.loads(cleaned_text)
            nutrition_data = recipe_data.get('nutrition_info', {})
            nutrition_info = NutritionInfo(
                calories=float(nutrition_data.get('calories', 0)),
                protein=float(nutrition_data.get('protein', 0)),
                carbs=float(nutrition_data.get('carbs', 0)),
                fat=float(nutrition_data.get('fat', 0)),
                fiber=float(nutrition_data.get('fiber', 0)),
                sugar=float(nutrition_data.get('sugar', 0)),
                sodium=float(nutrition_data.get('sodium', 0))
            )
            
            recipe = RecipeResponse(
                title=recipe_data.get('title', 'Generated Recipe'),
                description=recipe_data.get('description', ''),
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
            return recipe
        except Exception as e:
            logger.error(f"Recipe parsing error: {str(e)}")
            return self._create_fallback_recipe(ingredients, mood)
    
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
                    )
                )
                
                if not response.text:
                    raise Exception("Empty response from AI model")
                
                recipe = self._parse_recipe_response(response.text)
                logger.info(f"Recipe generated successfully: {recipe.title}")
                return recipe
                    
            except Exception as e:
                logger.error(f"Recipe generation attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    return self._create_fallback_recipe(ingredients, mood)
        
        return self._create_fallback_recipe(ingredients, mood)