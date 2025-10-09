#main.py
from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn
from typing import List, Optional
import logging
from datetime import datetime

from app.database.mongodb import MongoDB, get_database
from app.models.schemas import (
    UserCreate, UserResponse, UserLogin, RecipeRequest, RecipeResponse,
    IngredientDetectionResponse, MoodLog, UserProfile, RecipeHistory
)
from app.services.auth_service import AuthService
from app.services.recipe_service import RecipeService
from app.services.ingredient_detection_service import IngredientDetectionService
from app.utils.exceptions import CustomException
from app.core.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()
auth_service = AuthService()
recipe_service = RecipeService()
ingredient_service = IngredientDetectionService()
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up Recipe Recommendation System...")
    db = MongoDB()
    await db.connect()
    await ingredient_service.load_model()
    await recipe_service.initialize()
    logger.info("System initialized successfully!")
    yield
    logger.info("Shutting down...")
    await db.close()

app = FastAPI(
    title="AI-Powered Recipe Recommendation System",
    description="Backend API for personalized recipe recommendations",
    version="1.0.0",
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

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat(), "version": "1.0.0"}

@app.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: MongoDB = Depends(get_database)):
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
    try:
        result = await auth_service.authenticate_user(user_credentials, db)
        return result
    except CustomException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/ingredients/detect", response_model=IngredientDetectionResponse)
async def detect_ingredients(file: UploadFile = File(...), current_user: str = Depends(get_current_user)):
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        image_data = await file.read()
        ingredients = await ingredient_service.detect_ingredients(image_data)
        return IngredientDetectionResponse(
            ingredients=ingredients,
            confidence_scores={ingredient: 0.85 for ingredient in ingredients},
            processing_time=1.2,
            image_processed=True
        )
    except Exception as e:
        logger.error(f"Ingredient detection error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to detect ingredients")

@app.post("/recipes/generate", response_model=RecipeResponse)
async def generate_recipe(
    recipe_request: RecipeRequest,
    current_user: str = Depends(get_current_user),
    db: MongoDB = Depends(get_database)
):
    try:
        user = await db.get_user_by_id(current_user)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        recipe = await recipe_service.generate_recipe(
            ingredients=recipe_request.ingredients,
            mood=recipe_request.mood,
            dietary_preferences=user.get("dietary_preferences", []),
            allergies=user.get("allergies", []),
            health_goals=user.get("health_goals", []),
            cuisine_preference=recipe_request.cuisine_preference
        )
        
        recipe_history = RecipeHistory(
            user_id=current_user,
            recipe=recipe,
            ingredients_used=recipe_request.ingredients,
            mood=recipe_request.mood,
            created_at=datetime.utcnow()
        )
        await db.save_recipe_history(recipe_history.dict())
        
        return recipe
    except Exception as e:
        logger.error(f"Recipe generation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate recipe")

@app.get("/recipes/history")
async def get_recipe_history(
    current_user: str = Depends(get_current_user),
    db: MongoDB = Depends(get_database),
    limit: int = 10,
    skip: int = 0
):
    try:
        history = await db.get_recipe_history(current_user, limit, skip)
        return {"recipes": history, "total": len(history)}
    except Exception as e:
        logger.error(f"Get recipe history error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve recipe history")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_excludes=["venv/*", "*.pyc", "__pycache__/*"],  # Add this line
        log_level="info"
    )