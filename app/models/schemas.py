from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class MoodEnum(str, Enum):
    HAPPY = "happy"
    SAD = "sad"
    ENERGETIC = "energetic"
    TIRED = "tired"
    STRESSED = "stressed"
    CALM = "calm"
    EXCITED = "excited"
    BORED = "bored"

class CuisineEnum(str, Enum):
    ITALIAN = "italian"
    CHINESE = "chinese"
    INDIAN = "indian"
    MEXICAN = "mexican"
    AMERICAN = "american"
    JAPANESE = "japanese"
    FRENCH = "french"
    THAI = "thai"
    MEDITERRANEAN = "mediterranean"
    ANY = "any"

class DietaryPreferenceEnum(str, Enum):
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    GLUTEN_FREE = "gluten_free"
    KETO = "keto"
    PALEO = "paleo"
    LOW_CARB = "low_carb"
    HIGH_PROTEIN = "high_protein"
    DAIRY_FREE = "dairy_free"
    NUT_FREE = "nut_free"

class HealthGoalEnum(str, Enum):
    WEIGHT_LOSS = "weight_loss"
    MUSCLE_GAIN = "muscle_gain"
    MAINTAIN_WEIGHT = "maintain_weight"
    HEART_HEALTH = "heart_health"
    DIABETES_MANAGEMENT = "diabetes_management"
    BALANCED_DIET = "balanced_diet"
    ENERGY_BOOST = "energy_boost"

class NutritionInfo(BaseModel):
    calories: float
    protein: float
    carbs: float
    fat: float
    fiber: float
    sugar: float
    sodium: float

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    dietary_preferences: List[DietaryPreferenceEnum] = []
    allergies: List[str] = []
    health_goals: List[HealthGoalEnum] = []
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    dietary_preferences: List[str]
    allergies: List[str]
    health_goals: List[str]
    created_at: datetime

class UserProfile(BaseModel):
    name: Optional[str] = None
    dietary_preferences: Optional[List[DietaryPreferenceEnum]] = None
    allergies: Optional[List[str]] = None
    health_goals: Optional[List[HealthGoalEnum]] = None

class RecipeResponse(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    ingredients: List[str]
    instructions: List[str]
    prep_time: int
    cook_time: int
    total_time: int
    servings: int
    difficulty: str
    cuisine_type: str
    nutrition_info: NutritionInfo
    tags: List[str] = []
    generated_at: datetime = datetime.utcnow()

class RecipeRequest(BaseModel):
    ingredients: List[str]
    mood: MoodEnum
    cuisine_preference: Optional[CuisineEnum] = CuisineEnum.ANY
    max_prep_time: Optional[int] = None
    servings: Optional[int] = 2
    
    @validator('ingredients')
    def validate_ingredients(cls, v):
        if len(v) < 1:
            raise ValueError('At least one ingredient is required')
        return v

class IngredientDetectionResponse(BaseModel):
    ingredients: List[str]
    confidence_scores: Dict[str, float]
    processing_time: float
    image_processed: bool

class MoodLog(BaseModel):
    user_id: str
    mood: MoodEnum
    timestamp: datetime = datetime.utcnow()

class RecipeHistory(BaseModel):
    user_id: str
    recipe: RecipeResponse
    ingredients_used: List[str]
    mood: MoodEnum
    created_at: datetime = datetime.utcnow()
    rating: Optional[int] = None
    notes: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int