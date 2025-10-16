from google.cloud import vision
import logging
from typing import List, Dict, Any
import asyncio
from PIL import Image
import io
import os

from app.core.config import get_settings
from app.utils.exceptions import CustomException

logger = logging.getLogger(__name__)

class IngredientDetectionService:
    def __init__(self):
        self.settings = get_settings()
        self.vision_client = None
        self.loaded = False
        self.monthly_usage_count = 0
        
        # Comprehensive ingredient mapping database
        self.ingredient_categories = {
            # Vegetables
            'tomato': ['tomato', 'tomatoes', 'cherry tomato', 'plum tomato'],
            'onion': ['onion', 'onions', 'red onion', 'white onion', 'yellow onion', 'spring onion'],
            'garlic': ['garlic', 'garlic clove'],
            'carrot': ['carrot', 'carrots'],
            'potato': ['potato', 'potatoes', 'sweet potato'],
            'bell pepper': ['bell pepper', 'capsicum', 'pepper', 'sweet pepper'],
            'broccoli': ['broccoli'],
            'spinach': ['spinach', 'leafy greens', 'greens'],
            'lettuce': ['lettuce', 'salad', 'iceberg'],
            'cucumber': ['cucumber'],
            'celery': ['celery'],
            'mushroom': ['mushroom', 'mushrooms', 'button mushroom'],
            'zucchini': ['zucchini', 'courgette'],
            'eggplant': ['eggplant', 'aubergine'],
            'cabbage': ['cabbage'],
            'cauliflower': ['cauliflower'],
            'peas': ['peas', 'green peas'],
            'corn': ['corn', 'maize', 'sweet corn'],
            'ginger': ['ginger', 'ginger root'],
            'chili': ['chili', 'chilli', 'hot pepper'],
            
            # Fruits
            'apple': ['apple', 'apples'],
            'banana': ['banana', 'bananas'],
            'orange': ['orange', 'oranges', 'citrus'],
            'lemon': ['lemon', 'lemons'],
            'lime': ['lime', 'limes'],
            'avocado': ['avocado', 'avocados'],
            'mango': ['mango', 'mangoes'],
            'pineapple': ['pineapple'],
            'strawberry': ['strawberry', 'strawberries'],
            'grapes': ['grapes', 'grape'],
            
            # Proteins
            'chicken': ['chicken', 'poultry', 'chicken breast', 'chicken thigh'],
            'beef': ['beef', 'steak', 'meat'],
            'pork': ['pork', 'bacon', 'ham'],
            'fish': ['fish', 'salmon', 'tuna', 'cod', 'seafood'],
            'shrimp': ['shrimp', 'prawn', 'prawns'],
            'egg': ['egg', 'eggs'],
            'tofu': ['tofu', 'bean curd'],
            'beans': ['beans', 'kidney beans', 'black beans'],
            'lentils': ['lentils', 'dal'],
            
            # Dairy
            'milk': ['milk', 'dairy'],
            'cheese': ['cheese', 'cheddar', 'mozzarella'],
            'yogurt': ['yogurt', 'yoghurt', 'curd'],
            'butter': ['butter'],
            'cream': ['cream', 'heavy cream'],
            
            # Grains & Pasta
            'rice': ['rice', 'basmati', 'jasmine rice'],
            'pasta': ['pasta', 'spaghetti', 'noodle', 'macaroni'],
            'bread': ['bread', 'loaf', 'baguette'],
            'flour': ['flour', 'wheat flour'],
            'oats': ['oats', 'oatmeal'],
            
            # Herbs & Spices
            'basil': ['basil'],
            'cilantro': ['cilantro', 'coriander', 'coriander leaves'],
            'parsley': ['parsley'],
            'mint': ['mint'],
            'rosemary': ['rosemary'],
            'thyme': ['thyme'],
            
            # Condiments & Others
            'olive oil': ['olive oil', 'oil', 'cooking oil'],
            'salt': ['salt', 'sea salt'],
            'pepper': ['pepper', 'black pepper'],
            'soy sauce': ['soy sauce', 'soya sauce'],
            'vinegar': ['vinegar'],
            'honey': ['honey'],
            'sugar': ['sugar'],
        }
    
    async def load_model(self):
        """Initialize Google Cloud Vision API"""
        try:
            if not self.settings.GOOGLE_VISION_CREDENTIALS_PATH or not self.settings.ENABLE_VISION_API:
                logger.warning("Google Vision API not configured, using mock detection")
                self.loaded = False
                return
            
            logger.info("Initializing Google Cloud Vision API...")
            
            # Verify credentials file exists
            if not os.path.exists(self.settings.GOOGLE_VISION_CREDENTIALS_PATH):
                raise FileNotFoundError(f"Credentials file not found: {self.settings.GOOGLE_VISION_CREDENTIALS_PATH}")
            
            # Set credentials path as environment variable
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.settings.GOOGLE_VISION_CREDENTIALS_PATH
            
            # Initialize Vision API client
            self.vision_client = vision.ImageAnnotatorClient()
            
            # Test the connection with a simple request
            logger.info("Testing Vision API connection...")
            test_image = vision.Image()
            # Use a public test image
            test_image.source.image_uri = "gs://cloud-samples-data/vision/label/wakeupcat.jpg"
            
            try:
                response = self.vision_client.label_detection(image=test_image)
                if response.label_annotations:
                    self.loaded = True
                    logger.info("Google Cloud Vision API initialized and tested successfully")
                else:
                    raise Exception("Test request returned no results")
            except Exception as test_error:
                logger.warning(f"Vision API test failed: {test_error}")
                logger.info("Attempting to initialize without test...")
                self.loaded = True  # Still mark as loaded, will fail on actual use if credentials wrong
            
        except FileNotFoundError as e:
            logger.error(f"Credentials file not found: {str(e)}")
            logger.warning("Please place your Google Cloud credentials JSON file in the specified path")
            self.loaded = False
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Vision API: {str(e)}")
            logger.warning("Falling back to mock ingredient detection")
            self.loaded = False
    
    async def detect_ingredients(self, image_data: bytes) -> List[str]:
        """Detect ingredients from image"""
        try:
            # Check if Vision API is available and within quota
            if self.loaded and self.monthly_usage_count < self.settings.VISION_API_MONTHLY_LIMIT:
                logger.info("Attempting Vision API detection...")
                ingredients = await self._detect_with_vision_api(image_data)
                
                if ingredients:
                    self.monthly_usage_count += 1
                    logger.info(f"Vision API usage: {self.monthly_usage_count}/{self.settings.VISION_API_MONTHLY_LIMIT}")
                    logger.info(f"Detected ingredients: {ingredients}")
                    return ingredients
                else:
                    logger.warning("Vision API returned no ingredients, using fallback")
            elif self.loaded:
                logger.warning(f"Vision API monthly limit reached ({self.monthly_usage_count}/{self.settings.VISION_API_MONTHLY_LIMIT})")
            
            # Fallback to mock detection
            logger.info("Using mock ingredient detection")
            return await self._mock_ingredient_detection(image_data)
            
        except Exception as e:
            logger.error(f"Ingredient detection error: {str(e)}")
            return await self._mock_ingredient_detection(image_data)
    
    async def _detect_with_vision_api(self, image_data: bytes) -> List[str]:
        """Detect ingredients using Google Cloud Vision API"""
        try:
            # Prepare image for Vision API
            image = vision.Image(content=image_data)
            
            detected_ingredients = set()
            
            # Perform label detection (costs 1 unit)
            logger.info("Performing label detection...")
            label_response = self.vision_client.label_detection(image=image)
            
            if label_response.error.message:
                raise Exception(f"Vision API error: {label_response.error.message}")
            
            labels = label_response.label_annotations
            
            # Process labels
            for label in labels:
                if label.score > self.settings.MODEL_CONFIDENCE_THRESHOLD:
                    ingredient = self._map_to_ingredient(label.description.lower())
                    if ingredient:
                        detected_ingredients.add(ingredient)
                        logger.info(f"Label: '{label.description}' -> '{ingredient}' (confidence: {label.score:.2f})")
            
            # Perform object localization for better accuracy (costs 5 units)
            # Only if we have budget and found few ingredients
            if len(detected_ingredients) < 3 and self.monthly_usage_count < (self.settings.VISION_API_MONTHLY_LIMIT - 5):
                logger.info("Performing object localization...")
                try:
                    object_response = self.vision_client.object_localization(image=image)
                    objects = object_response.localized_object_annotations
                    
                    for obj in objects:
                        if obj.score > self.settings.MODEL_CONFIDENCE_THRESHOLD:
                            ingredient = self._map_to_ingredient(obj.name.lower())
                            if ingredient:
                                detected_ingredients.add(ingredient)
                                logger.info(f"Object: '{obj.name}' -> '{ingredient}' (confidence: {obj.score:.2f})")
                except Exception as obj_error:
                    logger.warning(f"Object localization failed: {obj_error}")
            
            result = list(detected_ingredients)
            
            # If very few ingredients detected, add common suggestions
            if len(result) < 2:
                logger.info("Few ingredients detected, adding common suggestions")
                common_additions = ["onion", "garlic", "olive oil"]
                result.extend(common_additions)
                result = list(set(result))  # Remove duplicates
            
            return result[:self.settings.MAX_INGREDIENTS_DETECTED]  # Limit to max
            
        except Exception as e:
            logger.error(f"Vision API detection error: {str(e)}")
            return []
    
    def _map_to_ingredient(self, detected_name: str) -> str:
        """Map Vision API detection to standard ingredient name"""
        detected_lower = detected_name.lower().strip()
        
        # Direct match in variations
        for ingredient, variations in self.ingredient_categories.items():
            if detected_lower in variations:
                return ingredient
            
            # Check if any variation is contained in detected name
            for variation in variations:
                if variation in detected_lower or detected_lower in variation:
                    return ingredient
        
        # Check for food-related terms
        food_keywords = {
            'vegetable': ['vegetable', 'veggie', 'produce'],
            'fruit': ['fruit'],
            'meat': ['meat', 'protein'],
            'dairy': ['dairy'],
            'grain': ['grain', 'cereal'],
            'herb': ['herb', 'spice'],
        }
        
        for category, keywords in food_keywords.items():
            if any(keyword in detected_lower for keyword in keywords):
                # Try to extract specific ingredient
                for ingredient in self.ingredient_categories.keys():
                    if ingredient in detected_lower:
                        return ingredient
        
        # If it looks like food but not in our database, log it
        food_indicators = ['food', 'dish', 'meal', 'cuisine', 'ingredient']
        if any(indicator in detected_lower for indicator in food_indicators):
            logger.info(f"Detected food-related term not in database: '{detected_name}'")
        
        return None
    
    async def _mock_ingredient_detection(self, image_data: bytes) -> List[str]:
        """Mock ingredient detection for fallback"""
        try:
            await asyncio.sleep(0.3)
            
            # Analyze image to provide semi-realistic results
            image = Image.open(io.BytesIO(image_data))
            width, height = image.size
            
            # Use image properties for consistent results
            import random
            random.seed(hash(image_data) % 1000)
            
            # Common ingredients that work in many recipes
            common_ingredients = [
                "tomato", "onion", "garlic", "bell pepper", 
                "carrot", "potato", "chicken", "olive oil"
            ]
            
            num_ingredients = random.randint(3, 5)
            mock_detections = random.sample(
                common_ingredients, 
                min(num_ingredients, len(common_ingredients))
            )
            
            logger.info(f"Mock detection returned: {mock_detections}")
            return mock_detections
            
        except Exception as e:
            logger.error(f"Mock detection error: {str(e)}")
            return ["tomato", "onion", "garlic", "olive oil"]
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get API usage statistics"""
        return {
            "vision_api_enabled": self.loaded,
            "vision_api_configured": bool(self.settings.GOOGLE_VISION_CREDENTIALS_PATH),
            "monthly_usage": self.monthly_usage_count,
            "monthly_limit": self.settings.VISION_API_MONTHLY_LIMIT,
            "remaining": self.settings.VISION_API_MONTHLY_LIMIT - self.monthly_usage_count,
            "percentage_used": round((self.monthly_usage_count / self.settings.VISION_API_MONTHLY_LIMIT) * 100, 2)
        }
    
    async def reset_monthly_usage(self):
        """Reset monthly usage counter (call this at the start of each month)"""
        self.monthly_usage_count = 0
        logger.info("Monthly Vision API usage counter reset to 0")