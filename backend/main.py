from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, status, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn
from typing import List, Optional
import logging
from datetime import datetime
import os
import shutil
from pathlib import Path
import time

from app.database.mongodb import MongoDB, get_database
from app.models.schemas import (
    UserCreate, UserResponse, UserLogin, RecipeRequest, RecipeResponse,
    VoiceIngredientRequest, IngredientExtractionResponse,
    MoodLog, UserProfile, RecipeHistory
)
from app.services.auth_service import AuthService
from app.services.recipe_service import RecipeService
from app.services.voice_ingredient_service import VoiceIngredientService
from app.utils.exceptions import CustomException
from app.core.config import get_settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()
auth_service = AuthService()
recipe_service = RecipeService()
voice_service = VoiceIngredientService()
security = HTTPBearer()

# Ensure upload directories exist
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
Path(settings.AUDIO_UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Starting up Recipe Recommendation System...")
    db = MongoDB()
    await db.connect()
    await voice_service.initialize()
    await recipe_service.initialize()
    logger.info("✅ System initialized successfully!")
    yield
    logger.info("👋 Shutting down...")
    await db.close()
    logger.info("✅ Cleanup complete")

app = FastAPI(
    title="AI-Powered Recipe Recommendation System",
    description="Backend API for personalized recipe recommendations with voice input",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token and return user ID"""
    try:
        token = credentials.credentials
        user_id = auth_service.verify_token(token)
        return user_id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# ============== HEALTH CHECK ==============

@app.get("/health")
async def health_check():
    """System health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "features": {
            "voice_input": settings.ENABLE_VOICE_INPUT,
            "recipe_generation": True,
            "user_authentication": True
        }
    }

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "AI-Powered Recipe Recommendation System API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# ============== AUTHENTICATION ==============

@app.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: MongoDB = Depends(get_database)):
    """Register a new user"""
    try:
        user = await auth_service.create_user(user_data, db)
        return UserResponse(
            id=str(user["_id"]),
            email=user["email"],
            name=user["name"],
            dietary_preferences=user["dietary_preferences"],
            allergies=user["allergies"],
            health_goals=user["health_goals"],
            created_at=user["created_at"]
        )
    except CustomException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/auth/login")
async def login_user(user_credentials: UserLogin, db: MongoDB = Depends(get_database)):
    """Login user and get access token"""
    try:
        result = await auth_service.authenticate_user(user_credentials, db)
        return result
    except CustomException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ============== INGREDIENT EXTRACTION (NEW) ==============

@app.post("/ingredients/extract-from-audio", response_model=IngredientExtractionResponse)
async def extract_ingredients_from_audio(
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user)
):
    """Extract ingredients from voice/audio input"""
    temp_path = None
    try:
        start_time = time.time()
        
        # Validate file type
        if not file.content_type or not file.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=400, 
                detail="File must be an audio file (wav, mp3, ogg, webm, m4a)"
            )
        
        # Validate file size
        content = await file.read()
        file_size = len(content)
        
        if file_size > settings.MAX_AUDIO_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum ({settings.MAX_AUDIO_FILE_SIZE} bytes)"
            )
        
        if file_size < 1000:  # Less than 1KB
            raise HTTPException(
                status_code=400,
                detail="Audio file is too small. Please record a longer message."
            )
        
        # Save file temporarily
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'wav'
        temp_filename = f"{current_user}_{int(time.time())}.{file_extension}"
        temp_path = os.path.join(settings.AUDIO_UPLOAD_DIR, temp_filename)
        
        with open(temp_path, 'wb') as f:
            f.write(content)
        
        logger.info(f"Processing audio file: {temp_filename} ({file_size} bytes)")
        
        # Extract ingredients
        try:
            ingredients = await voice_service.transcribe_and_extract_ingredients(temp_path)
        except Exception as e:
            logger.error(f"Gemini AI processing failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process audio with AI: {str(e)}. Please try again or use text input."
            )
        
        # Validate ingredients
        validation_result = await voice_service.validate_ingredients(ingredients)
        
        processing_time = time.time() - start_time
        
        logger.info(f"Successfully extracted {len(ingredients)} ingredients in {processing_time:.2f}s")
        
        return IngredientExtractionResponse(
            ingredients=ingredients,
            validated_ingredients=validation_result["validated_ingredients"],
            suggestions=validation_result["suggestions"],
            processing_time=round(processing_time, 2),
            source="audio",
            confidence=0.90
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected audio processing error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process audio file: {str(e)}"
        )
    finally:
        # Clean up temp file
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
                logger.info(f"Cleaned up temp file: {temp_path}")
            except Exception as e:
                logger.warning(f"Failed to remove temp file: {e}")

@app.post("/ingredients/extract-from-text", response_model=IngredientExtractionResponse)
async def extract_ingredients_from_text(
    request: VoiceIngredientRequest,
    current_user: str = Depends(get_current_user)
):
    """Extract ingredients from text input"""
    try:
        start_time = time.time()
        
        logger.info(f"Extracting ingredients from text: {request.text[:50]}...")
        
        # Extract ingredients
        ingredients = await voice_service.extract_from_text(request.text)
        
        # Validate ingredients
        validation_result = await voice_service.validate_ingredients(ingredients)
        
        processing_time = time.time() - start_time
        
        return IngredientExtractionResponse(
            ingredients=ingredients,
            validated_ingredients=validation_result["validated_ingredients"],
            suggestions=validation_result["suggestions"],
            transcription=request.text,
            processing_time=round(processing_time, 2),
            source="text",
            confidence=0.90
        )
        
    except Exception as e:
        logger.error(f"Text extraction error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to extract ingredients from text"
        )

# ============== RECIPE GENERATION ==============

@app.post("/recipes/generate", response_model=RecipeResponse)
async def generate_recipe(
    recipe_request: RecipeRequest,
    current_user: str = Depends(get_current_user),
    db: MongoDB = Depends(get_database)
):
    """Generate personalized recipe based on ingredients and mood"""
    try:
        # Get user profile for personalization
        user = await db.get_user_by_id(current_user)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.info(f"Generating recipe for user {current_user} with {len(recipe_request.ingredients)} ingredients")
        
        # Generate recipe
        recipe = await recipe_service.generate_recipe(
            ingredients=recipe_request.ingredients,
            mood=recipe_request.mood,
            dietary_preferences=user.get("dietary_preferences", []),
            allergies=user.get("allergies", []),
            health_goals=user.get("health_goals", []),
            cuisine_preference=recipe_request.cuisine_preference
        )
        
        # Save to history
        recipe_history = RecipeHistory(
            user_id=current_user,
            recipe=recipe,
            ingredients_used=recipe_request.ingredients,
            mood=recipe_request.mood,
            input_method="voice",  # Can be updated based on how ingredients were added
            created_at=datetime.utcnow()
        )
        await db.save_recipe_history(recipe_history.dict())
        
        # Log mood
        mood_log = MoodLog(
            user_id=current_user,
            mood=recipe_request.mood,
            timestamp=datetime.utcnow()
        )
        await db.save_mood_log(mood_log.dict())
        
        logger.info(f"✅ Recipe generated successfully: {recipe.title}")
        
        # Save to history
        try:
            recipe_history = {
                "user_id": current_user,
                "recipe": recipe.dict(),
                "ingredients_used": recipe_request.ingredients,
                "mood": recipe_request.mood.value,
                "input_method": "voice",
                "created_at": datetime.utcnow()
            }
            
            history_id = await db.save_recipe_history(recipe_history)
            logger.info(f"Recipe saved to history with ID: {history_id}")
            
        except Exception as save_error:
            logger.error(f"Failed to save recipe history: {save_error}")
            # Don't fail the request if history save fails
        
        # Log mood
        try:
            mood_log = {
                "user_id": current_user,
                "mood": recipe_request.mood.value,
                "timestamp": datetime.utcnow()
            }
            await db.save_mood_log(mood_log)
            logger.info("Mood logged successfully")
        except Exception as mood_error:
            logger.error(f"Failed to log mood: {mood_error}")
        
        return recipe
        
    except CustomException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(f"Recipe generation error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate recipe"
        )

# ============== RECIPE HISTORY ==============

@app.get("/recipes/history")
async def get_recipe_history(
    current_user: str = Depends(get_current_user),
    db: MongoDB = Depends(get_database),
    limit: int = 10,
    skip: int = 0
):
    """Get user's recipe history"""
    try:
        history = await db.get_recipe_history(current_user, limit, skip)
        
        # Convert ObjectId to string for JSON serialization
        for item in history:
            if "_id" in item:
                item["_id"] = str(item["_id"])
            if "recipe" in item and "_id" in item["recipe"]:
                item["recipe"]["_id"] = str(item["recipe"]["_id"])
        
        # Count total recipes
        total = len(history)
        
        logger.info(f"Retrieved {total} recipes for user {current_user}")
        
        return {
            "recipes": history,
            "total": total,
            "limit": limit,
            "skip": skip,
            "has_more": total == limit
        }
        
    except Exception as e:
        logger.error(f"Get recipe history error: {str(e)}")
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve recipe history"
        )

@app.get("/recipes/history/{recipe_id}")
async def get_recipe_by_id(
    recipe_id: str,
    current_user: str = Depends(get_current_user),
    db: MongoDB = Depends(get_database)
):
    """Get specific recipe from history"""
    try:
        from bson import ObjectId
        
        recipe = await db.database.recipe_history.find_one({
            "_id": ObjectId(recipe_id),
            "user_id": current_user
        })
        
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        
        recipe["_id"] = str(recipe["_id"])
        return recipe
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get recipe error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve recipe")

@app.delete("/recipes/history/{recipe_id}")
async def delete_recipe(
    recipe_id: str,
    current_user: str = Depends(get_current_user),
    db: MongoDB = Depends(get_database)
):
    """Delete recipe from history"""
    try:
        from bson import ObjectId
        
        result = await db.database.recipe_history.delete_one({
            "_id": ObjectId(recipe_id),
            "user_id": current_user
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Recipe not found")
        
        return {"message": "Recipe deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete recipe error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete recipe")

# ============== FAVORITES ==============

@app.post("/recipes/{recipe_id}/favorite")
async def toggle_favorite_recipe(
    recipe_id: str,
    current_user: str = Depends(get_current_user),
    db: MongoDB = Depends(get_database)
):
    """Add or remove recipe from favorites"""
    try:
        is_favorited = await db.toggle_favorite_recipe(current_user, recipe_id)
        
        return {
            "recipe_id": recipe_id,
            "is_favorited": is_favorited,
            "message": "Added to favorites" if is_favorited else "Removed from favorites"
        }
        
    except Exception as e:
        logger.error(f"Toggle favorite error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to update favorites"
        )

# Replace the /recipes/favorites endpoint in main.py with this:

@app.get("/recipes/favorites")
async def get_favorite_recipes(
    current_user: str = Depends(get_current_user),
    db: MongoDB = Depends(get_database)
):
    """Get user's favorite recipes"""
    try:
        # Get favorite recipe IDs
        favorite_cursor = db.database.favorites.find({"user_id": current_user})
        favorite_docs = await favorite_cursor.to_list(length=None)
        
        if not favorite_docs:
            logger.info(f"No favorites found for user {current_user}")
            return {
                "favorites": [],
                "total": 0
            }
        
        # Extract recipe IDs and convert to ObjectId
        from bson import ObjectId
        recipe_ids = []
        for doc in favorite_docs:
            try:
                recipe_id = doc.get("recipe_id")
                if recipe_id:
                    # Handle both string and ObjectId
                    if isinstance(recipe_id, str):
                        recipe_ids.append(ObjectId(recipe_id))
                    else:
                        recipe_ids.append(recipe_id)
            except Exception as e:
                logger.warning(f"Invalid recipe_id in favorites: {e}")
                continue
        
        if not recipe_ids:
            logger.info(f"No valid recipe IDs in favorites for user {current_user}")
            return {
                "favorites": [],
                "total": 0
            }
        
        # Get the actual recipes from recipe_history
        recipe_cursor = db.database.recipe_history.find({"_id": {"$in": recipe_ids}})
        recipes = await recipe_cursor.to_list(length=None)
        
        # Convert ObjectIds to strings for JSON serialization
        for recipe in recipes:
            if "_id" in recipe:
                recipe["_id"] = str(recipe["_id"])
            if "recipe" in recipe and isinstance(recipe["recipe"], dict):
                if "_id" in recipe["recipe"]:
                    recipe["recipe"]["_id"] = str(recipe["recipe"]["_id"])
        
        logger.info(f"Retrieved {len(recipes)} favorite recipes for user {current_user}")
        
        return {
            "favorites": recipes,
            "total": len(recipes)
        }
        
    except Exception as e:
        logger.error(f"Get favorites error: {str(e)}")
        logger.exception(e)
        # Return empty instead of error
        return {
            "favorites": [],
            "total": 0,
            "error": str(e)
        }

# ============== USER PROFILE ==============

@app.get("/users/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: str = Depends(get_current_user),
    db: MongoDB = Depends(get_database)
):
    """Get current user profile"""
    try:
        user = await db.get_user_by_id(current_user)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse(
            id=str(user["_id"]),
            email=user["email"],
            name=user["name"],
            dietary_preferences=user.get("dietary_preferences", []),
            allergies=user.get("allergies", []),
            health_goals=user.get("health_goals", []),
            created_at=user["created_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get profile error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve profile")

@app.put("/users/me")
async def update_user_profile(
    profile_update: UserProfile,
    current_user: str = Depends(get_current_user),
    db: MongoDB = Depends(get_database)
):
    """Update user profile"""
    try:
        update_data = profile_update.dict(exclude_unset=True)
        
        # Convert enums to strings
        if "dietary_preferences" in update_data:
            update_data["dietary_preferences"] = [
                pref.value if hasattr(pref, 'value') else pref 
                for pref in update_data["dietary_preferences"]
            ]
        
        if "health_goals" in update_data:
            update_data["health_goals"] = [
                goal.value if hasattr(goal, 'value') else goal 
                for goal in update_data["health_goals"]
            ]
        
        updated_user = await db.update_user_profile(current_user, update_data)
        
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "message": "Profile updated successfully",
            "user": {
                "id": str(updated_user["_id"]),
                "email": updated_user["email"],
                "name": updated_user["name"],
                "dietary_preferences": updated_user.get("dietary_preferences", []),
                "allergies": updated_user.get("allergies", []),
                "health_goals": updated_user.get("health_goals", [])
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update profile error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update profile")

# ============== ANALYTICS & STATISTICS ==============

@app.get("/analytics/mood-trends")
async def get_mood_trends(
    current_user: str = Depends(get_current_user),
    db: MongoDB = Depends(get_database),
    days: int = 30
):
    """Get mood trends over time"""
    try:
        trends = await db.get_mood_trends(current_user, days)
        
        return {
            "trends": trends,
            "period_days": days,
            "total_entries": len(trends)
        }
        
    except Exception as e:
        logger.error(f"Get mood trends error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve mood trends"
        )

@app.get("/analytics/ingredient-stats")
async def get_ingredient_statistics(
    current_user: str = Depends(get_current_user),
    db: MongoDB = Depends(get_database)
):
    """Get ingredient usage statistics"""
    try:
        stats = await db.get_ingredient_usage_stats(current_user)
        
        return {
            "ingredients": stats,
            "total_unique_ingredients": len(stats)
        }
        
    except Exception as e:
        logger.error(f"Get ingredient stats error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve ingredient statistics"
        )

@app.get("/analytics/dashboard")
async def get_user_dashboard(
    current_user: str = Depends(get_current_user),
    db: MongoDB = Depends(get_database)
):
    """Get comprehensive user dashboard data"""
    try:
        # Get various statistics
        history = await db.get_recipe_history(current_user, limit=100)
        mood_trends = await db.get_mood_trends(current_user, days=30)
        ingredient_stats = await db.get_ingredient_usage_stats(current_user)
        
        # Get favorites count
        favorites_cursor = db.database.favorites.find({"user_id": current_user})
        favorites = await favorites_cursor.to_list(length=None)
        
        # Calculate additional metrics
        total_recipes = len(history)
        
        # Most common cuisine
        cuisine_counts = {}
        for recipe_doc in history:
            recipe = recipe_doc.get("recipe", {})
            if recipe:
                cuisine = recipe.get("cuisine_type", "unknown")
                cuisine_counts[cuisine] = cuisine_counts.get(cuisine, 0) + 1
        
        most_used_cuisine = max(cuisine_counts.items(), key=lambda x: x[1])[0] if cuisine_counts else None
        
        # Average cooking time
        cooking_times = []
        for recipe_doc in history:
            recipe = recipe_doc.get("recipe", {})
            if recipe and recipe.get("total_time"):
                cooking_times.append(recipe.get("total_time", 0))
        
        avg_cooking_time = sum(cooking_times) / len(cooking_times) if cooking_times else 0
        
        # Recent recipes (last 5)
        recent_recipes = []
        for recipe_doc in history[:5]:
            recent_recipes.append({
                "id": str(recipe_doc.get("_id")),
                "title": recipe_doc.get("recipe", {}).get("title", "Unknown"),
                "created_at": recipe_doc.get("created_at"),
                "mood": recipe_doc.get("mood")
            })
        
        logger.info(f"Dashboard stats: {total_recipes} recipes, {len(favorites)} favorites")
        
        return {
            "total_recipes_generated": total_recipes,
            "total_favorites": len(favorites),
            "mood_trends_count": len(mood_trends),
            "unique_ingredients_used": len(ingredient_stats),
            "most_used_cuisine": most_used_cuisine,
            "avg_cooking_time_minutes": round(avg_cooking_time, 1),
            "top_ingredients": ingredient_stats[:10],
            "recent_recipes": recent_recipes
        }
        
    except Exception as e:
        logger.error(f"Get dashboard error: {str(e)}")
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve dashboard data: {str(e)}"
        )

# ============== SYSTEM INFO ==============

@app.get("/system/info")
async def get_system_info(current_user: str = Depends(get_current_user)):
    """Get system information and capabilities"""
    return {
        "version": "2.0.0",
        "features": {
            "voice_input": settings.ENABLE_VOICE_INPUT,
            "text_input": True,
            "recipe_generation": True,
            "mood_tracking": settings.ENABLE_MOOD_ANALYSIS,
            "favorites": True,
            "history": True,
            "analytics": settings.ENABLE_ANALYTICS
        },
        "supported_audio_formats": settings.SUPPORTED_AUDIO_FORMATS,
        "max_audio_file_size_mb": settings.MAX_AUDIO_FILE_SIZE / (1024 * 1024),
        "max_ingredients": settings.MAX_INGREDIENTS_DETECTED,
        "ai_services": {
            "voice_service_initialized": voice_service.initialized,
            "recipe_service_initialized": recipe_service.initialized
        }
    }

@app.post("/system/test-voice")
async def test_voice_service(current_user: str = Depends(get_current_user)):
    """Test if voice service is working properly"""
    try:
        # Test with simple text extraction
        test_result = await voice_service.extract_from_text(
            "tomato, onion, garlic, chicken"
        )
        
        return {
            "status": "success",
            "voice_service_initialized": voice_service.initialized,
            "test_extraction": test_result,
            "message": "Voice service is working correctly"
        }
    except Exception as e:
        logger.error(f"Voice service test failed: {str(e)}")
        return {
            "status": "error",
            "voice_service_initialized": voice_service.initialized,
            "error": str(e),
            "message": "Voice service is not working. Check your GEMINI_API_KEY in .env"
        }

@app.get("/system/debug-history")
async def debug_history(
    current_user: str = Depends(get_current_user),
    db: MongoDB = Depends(get_database)
):
    """Debug endpoint to check recipe history"""
    try:
        # Get raw data from database
        cursor = db.database.recipe_history.find({"user_id": current_user})
        raw_history = await cursor.to_list(length=100)
        
        # Convert ObjectIds to strings
        for item in raw_history:
            item["_id"] = str(item["_id"])
        
        # Also check total count
        total_count = await db.database.recipe_history.count_documents({"user_id": current_user})
        
        # Check if any recipes exist at all
        all_count = await db.database.recipe_history.count_documents({})
        
        return {
            "current_user_id": current_user,
            "recipes_for_user": len(raw_history),
            "total_count": total_count,
            "all_recipes_count": all_count,
            "sample_recipes": raw_history[:3] if raw_history else [],
            "message": f"Found {total_count} recipes for this user"
        }
        
    except Exception as e:
        logger.error(f"Debug history error: {str(e)}")
        return {
            "error": str(e),
            "message": "Error debugging history"
        }

@app.post("/system/test-save-recipe")
async def test_save_recipe(
    current_user: str = Depends(get_current_user),
    db: MongoDB = Depends(get_database)
):
    """Test endpoint to manually save a recipe and verify it works"""
    try:
        # Create a test recipe document
        test_recipe = {
            "user_id": current_user,
            "recipe": {
                "title": "Test Recipe",
                "description": "This is a test",
                "ingredients": ["test ingredient 1", "test ingredient 2"],
                "instructions": ["Step 1", "Step 2"],
                "prep_time": 10,
                "cook_time": 20,
                "total_time": 30,
                "servings": 2,
                "difficulty": "easy",
                "cuisine_type": "test",
                "nutrition_info": {
                    "calories": 300,
                    "protein": 20,
                    "carbs": 30,
                    "fat": 10,
                    "fiber": 5,
                    "sugar": 5,
                    "sodium": 400
                },
                "tags": ["test"]
            },
            "ingredients_used": ["test1", "test2"],
            "mood": "happy",
            "input_method": "test",
            "created_at": datetime.utcnow()
        }
        
        # Try to save
        logger.info(f"Attempting to save test recipe for user: {current_user}")
        result = await db.database.recipe_history.insert_one(test_recipe)
        saved_id = str(result.inserted_id)
        logger.info(f"Test recipe saved with ID: {saved_id}")
        
        # Try to retrieve it
        saved_recipe = await db.database.recipe_history.find_one({"_id": result.inserted_id})
        
        if saved_recipe:
            saved_recipe["_id"] = str(saved_recipe["_id"])
            return {
                "status": "success",
                "message": "Recipe saved and retrieved successfully!",
                "saved_id": saved_id,
                "retrieved": True,
                "recipe": saved_recipe
            }
        else:
            return {
                "status": "warning",
                "message": "Recipe saved but could not retrieve it",
                "saved_id": saved_id,
                "retrieved": False
            }
        
    except Exception as e:
        logger.error(f"Test save recipe error: {str(e)}")
        logger.exception(e)
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to save test recipe"
        }

# ============== ERROR HANDLERS ==============

@app.exception_handler(CustomException)
async def custom_exception_handler(request, exc: CustomException):
    """Handle custom exceptions"""
    return {
        "error": True,
        "status_code": exc.status_code,
        "detail": exc.detail,
        "error_code": exc.error_code,
        "timestamp": exc.timestamp.isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        reload_excludes=["venv/*", "*.pyc", "__pycache__/*", "uploads/*"],
        log_level=settings.LOG_LEVEL.lower()
    )