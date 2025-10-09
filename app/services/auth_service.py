#auth_service.py
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

# FIXED IMPORTS - Add 'app.' prefix
from app.models.schemas import UserCreate, UserLogin, Token
from app.database.mongodb import MongoDB
from app.core.config import get_settings
from app.utils.exceptions import CustomException

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self):
        self.settings = get_settings()
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 60 * 24  # 24 hours
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def _verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def _create_access_token(self, user_id: str) -> Dict[str, Any]:
        """Create JWT access token"""
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode = {
            "user_id": user_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        encoded_jwt = jwt.encode(
            to_encode, 
            self.settings.SECRET_KEY, 
            algorithm=self.algorithm
        )
        
        return {
            "access_token": encoded_jwt,
            "token_type": "bearer",
            "expires_in": self.access_token_expire_minutes * 60,
            "expires_at": expire.isoformat()
        }
    
    def verify_token(self, token: str) -> str:
        """Verify JWT token and return user_id"""
        try:
            payload = jwt.decode(
                token, 
                self.settings.SECRET_KEY, 
                algorithms=[self.algorithm]
            )
            
            user_id = payload.get("user_id")
            if user_id is None:
                raise CustomException(status_code=401, detail="Invalid token")
            
            # Check if token is expired
            exp = payload.get("exp")
            if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
                raise CustomException(status_code=401, detail="Token expired")
            
            return user_id
            
        except jwt.ExpiredSignatureError:
            raise CustomException(status_code=401, detail="Token expired")
        except jwt.JWTError:
            raise CustomException(status_code=401, detail="Invalid token")
    
    async def create_user(self, user_data: UserCreate, db: MongoDB) -> Dict[str, Any]:
        """Create a new user account"""
        try:
            # Check if user already exists
            existing_user = await db.get_user_by_email(user_data.email)
            if existing_user:
                raise CustomException(status_code=400, detail="Email already registered")
            
            # Hash password
            hashed_password = self._hash_password(user_data.password)
            
            # Prepare user document
            user_doc = {
                "name": user_data.name,
                "email": user_data.email,
                "hashed_password": hashed_password,
                "dietary_preferences": [pref.value for pref in user_data.dietary_preferences],
                "allergies": user_data.allergies,
                "health_goals": [goal.value for goal in user_data.health_goals]
            }
            
            # Create user in database
            created_user = await db.create_user(user_doc)
            
            logger.info(f"New user created: {user_data.email}")
            return created_user
            
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise CustomException(status_code=500, detail="Failed to create user")
    
    async def authenticate_user(self, credentials: UserLogin, db: MongoDB) -> Dict[str, Any]:
        """Authenticate user and return access token"""
        try:
            # Get user from database
            user = await db.get_user_by_email(credentials.email)
            if not user:
                raise CustomException(status_code=401, detail="Invalid email or password")
            
            # Verify password
            if not self._verify_password(credentials.password, user["hashed_password"]):
                raise CustomException(status_code=401, detail="Invalid email or password")
            
            # Check if user is active
            if not user.get("is_active", True):
                raise CustomException(status_code=401, detail="Account is deactivated")
            
            # Create access token
            token_data = self._create_access_token(str(user["_id"]))
            
            # Update last login
            await db.database.users.update_one(
                {"_id": user["_id"]},
                {"$set": {"last_login": datetime.utcnow()}}
            )
            
            # Prepare response
            response = {
                **token_data,
                "user": {
                    "id": str(user["_id"]),
                    "email": user["email"],
                    "name": user["name"],
                    "dietary_preferences": user.get("dietary_preferences", []),
                    "allergies": user.get("allergies", []),
                    "health_goals": user.get("health_goals", [])
                }
            }
            
            logger.info(f"User authenticated: {credentials.email}")
            return response
            
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error authenticating user: {str(e)}")
            raise CustomException(status_code=500, detail="Authentication failed")
    
    async def refresh_token(self, token: str, db: MongoDB) -> Dict[str, Any]:
        """Refresh access token"""
        try:
            # Verify current token
            user_id = self.verify_token(token)
            
            # Check if user still exists and is active
            user = await db.get_user_by_id(user_id)
            if not user or not user.get("is_active", True):
                raise CustomException(status_code=401, detail="User not found or inactive")
            
            # Create new token
            token_data = self._create_access_token(user_id)
            
            logger.info(f"Token refreshed for user: {user_id}")
            return token_data
            
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            raise CustomException(status_code=500, detail="Failed to refresh token")
    
    async def change_password(self, user_id: str, current_password: str, new_password: str, db: MongoDB) -> bool:
        """Change user password"""
        try:
            # Get user
            user = await db.get_user_by_id(user_id)
            if not user:
                raise CustomException(status_code=404, detail="User not found")
            
            # Verify current password
            if not self._verify_password(current_password, user["hashed_password"]):
                raise CustomException(status_code=400, detail="Current password is incorrect")
            
            # Hash new password
            new_hashed_password = self._hash_password(new_password)
            
            # Update password in database
            await db.database.users.update_one(
                {"_id": user["_id"]},
                {
                    "$set": {
                        "hashed_password": new_hashed_password,
                        "updated_at": datetime.utcnow(),
                        "password_changed_at": datetime.utcnow()
                    }
                }
            )
            
            logger.info(f"Password changed for user: {user_id}")
            return True
            
        except CustomException:
            raise
        except Exception as e:
            logger.error(f"Error changing password: {str(e)}")
            raise CustomException(status_code=500, detail="Failed to change password")