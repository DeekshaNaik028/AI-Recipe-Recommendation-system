#mongodb.py
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError
from bson import ObjectId
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from app.core.config import get_settings

logger = logging.getLogger(__name__)

class MongoDB:
    def __init__(self):
        self.settings = get_settings()
        self.client: Optional[AsyncIOMotorClient] = None
        self.database = None
        
    async def connect(self):
        try:
            self.client = AsyncIOMotorClient(self.settings.MONGODB_URL)
            self.database = self.client[self.settings.DATABASE_NAME]
            await self.client.admin.command('ping')
            await self._create_indexes()
            logger.info("Connected to MongoDB successfully")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
    
    async def close(self):
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def _create_indexes(self):
        try:
            await self.database.users.create_index("email", unique=True)
            await self.database.users.create_index("created_at")
            await self.database.recipes.create_index("user_id")
            await self.database.recipes.create_index("created_at")
            await self.database.recipe_history.create_index("user_id")
            await self.database.recipe_history.create_index("created_at")
            await self.database.recipe_history.create_index([("user_id", 1), ("created_at", -1)])
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating indexes: {str(e)}")
    
    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            user_data["created_at"] = datetime.utcnow()
            user_data["updated_at"] = datetime.utcnow()
            user_data["is_active"] = True
            user_data["favorite_recipes"] = []
            result = await self.database.users.insert_one(user_data)
            user_data["_id"] = result.inserted_id
            return user_data
        except DuplicateKeyError:
            raise ValueError("Email already registered")
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        try:
            return await self.database.users.find_one({"email": email, "is_active": True})
        except Exception as e:
            logger.error(f"Error getting user by email: {str(e)}")
            raise
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        try:
            return await self.database.users.find_one({"_id": ObjectId(user_id), "is_active": True})
        except Exception as e:
            logger.error(f"Error getting user by ID: {str(e)}")
            raise
    
    async def save_recipe_history(self, history_data: Dict[str, Any]) -> str:
        try:
            result = await self.database.recipe_history.insert_one(history_data)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error saving recipe history: {str(e)}")
            raise
    
    async def get_recipe_history(self, user_id: str, limit: int = 10, skip: int = 0) -> List[Dict[str, Any]]:
        try:
            cursor = self.database.recipe_history.find(
                {"user_id": user_id}
            ).sort("created_at", -1).skip(skip).limit(limit)
            return await cursor.to_list(length=limit)
        except Exception as e:
            logger.error(f"Error getting recipe history: {str(e)}")
            raise
    
    async def update_user_profile(self, user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            update_data["updated_at"] = datetime.utcnow()
            result = await self.database.users.find_one_and_update(
                {"_id": ObjectId(user_id)},
                {"$set": update_data},
                return_document=True
            )
            return result
        except Exception as e:
            logger.error(f"Error updating user profile: {str(e)}")
            raise
    
    async def toggle_favorite_recipe(self, user_id: str, recipe_id: str) -> bool:
        try:
            existing_favorite = await self.database.favorites.find_one(
                {"user_id": user_id, "recipe_id": recipe_id}
            )
            if existing_favorite:
                await self.database.favorites.delete_one(
                    {"user_id": user_id, "recipe_id": recipe_id}
                )
                return False
            else:
                await self.database.favorites.insert_one({
                    "user_id": user_id,
                    "recipe_id": recipe_id,
                    "created_at": datetime.utcnow()
                })
                return True
        except Exception as e:
            logger.error(f"Error toggling favorite recipe: {str(e)}")
            raise
    
    async def get_favorite_recipes(self, user_id: str) -> List[Dict[str, Any]]:
        try:
            favorite_cursor = self.database.favorites.find({"user_id": user_id})
            favorite_docs = await favorite_cursor.to_list(length=None)
            recipe_ids = [ObjectId(doc["recipe_id"]) for doc in favorite_docs]
            if not recipe_ids:
                return []
            recipe_cursor = self.database.recipes.find({"_id": {"$in": recipe_ids}})
            return await recipe_cursor.to_list(length=None)
        except Exception as e:
            logger.error(f"Error getting favorite recipes: {str(e)}")
            raise
    
    async def save_mood_log(self, mood_data: Dict[str, Any]) -> str:
        try:
            result = await self.database.mood_logs.insert_one(mood_data)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error saving mood log: {str(e)}")
            raise
    
    async def get_mood_trends(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            pipeline = [
                {"$match": {"user_id": user_id, "timestamp": {"$gte": start_date}}},
                {
                    "$group": {
                        "_id": {
                            "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                            "mood": "$mood"
                        },
                        "count": {"$sum": 1}
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "date": "$_id.date",
                        "mood": "$_id.mood",
                        "count": 1
                    }
                },
                {"$sort": {"date": 1, "mood": 1}}
            ]
            cursor = self.database.mood_logs.aggregate(pipeline)
            return await cursor.to_list(length=None)
        except Exception as e:
            logger.error(f"Error getting mood trends: {str(e)}")
            raise
    
    async def get_ingredient_usage_stats(self, user_id: str) -> List[Dict[str, Any]]:
        try:
            pipeline = [
                {"$match": {"user_id": user_id}},
                {"$unwind": "$ingredients_used"},
                {
                    "$group": {
                        "_id": "$ingredients_used",
                        "usage_count": {"$sum": 1},
                        "last_used": {"$max": "$created_at"}
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "ingredient": "$_id",
                        "usage_count": 1,
                        "last_used": 1
                    }
                },
                {"$sort": {"usage_count": -1}}
            ]
            cursor = self.database.recipe_history.aggregate(pipeline)
            return await cursor.to_list(length=None)
        except Exception as e:
            logger.error(f"Error getting ingredient usage stats: {str(e)}")
            raise

async def get_database() -> MongoDB:
    db = MongoDB()
    if not db.client:
        await db.connect()
    return db