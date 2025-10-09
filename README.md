AI-Powered Personalized Recipe Recommendation System - Backend
A comprehensive backend system that combines computer vision, user profiling, and generative AI to provide personalized recipe recommendations based on available ingredients and user mood.

🚀 Features
Ingredient Detection: Real-time ingredient identification using YOLOv8 computer vision
AI Recipe Generation: Creative recipe generation using Gemini AI
Mood-Based Recommendations: Personalized recipes based on user's current emotional state
Health-Aware Filtering: Recipes tailored to dietary preferences, allergies, and health goals
User Profiling: Comprehensive user management with preference tracking
Recipe History: Save and track favorite recipes and cooking history
Nutritional Analysis: Detailed nutrition information for all generated recipes
Batch Processing: Handle multiple ingredient detection and recipe generation requests
Real-time Analytics: Track user behavior and recipe popularity
🏗️ Architecture
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   MongoDB       │
│   (React)       │◄──►│   Backend       │◄──►│   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   AI Services   │
                    │                 │
                    │  ┌─────────────┐│
                    │  │  YOLOv8     ││
                    │  │ (Ingredient ││
                    │  │ Detection)  ││
                    │  └─────────────┘│
                    │                 │
                    │  ┌─────────────┐│
                    │  │  Gemini AI  ││
                    │  │  (Recipe    ││
                    │  │ Generation) ││
                    │  └─────────────┘│
                    └─────────────────┘
📋 Prerequisites
Python 3.11+
MongoDB 7.0+
Redis 7.0+ (for caching)
Docker & Docker Compose (recommended)
Gemini AI API Key
CUDA-compatible GPU (optional, for faster inference)
🛠️ Installation
Option 1: Docker Compose (Recommended)
Clone the repository:
bash
   git clone https://github.com/your-username/recipe-recommendation-backend.git
   cd recipe-recommendation-backend
Set up environment variables:
bash
   cp .env.example .env
   # Edit .env with your configuration
Start all services:
bash
   docker-compose up -d
Initialize the database:
bash
   docker-compose exec recipe-api python scripts/init_db.py
Option 2: Local Development Setup
Clone and navigate to the project:
bash
   git clone https://github.com/your-username/recipe-recommendation-backend.git
   cd recipe-recommendation-backend
Create virtual environment:
bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies:
bash
   pip install -r requirements.txt
Set up environment variables:
bash
   cp .env.example .env
   # Configure your settings in .env
Start MongoDB and Redis:
bash
   # Using Docker
   docker run -d -p 27017:27017 --name mongo mongo:7.0
   docker run -d -p 6379:6379 --name redis redis:7.2-alpine
Run the application:
bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
🔧 Configuration
Environment Variables
Key configuration options in .env:

bash
# Core Settings
ENVIRONMENT=development
SECRET_KEY=your-secret-key
GEMINI_API_KEY=your-gemini-api-key

# Database
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=recipe_recommendation_db

# AI Models
MODEL_CONFIDENCE_THRESHOLD=0.3
MAX_INGREDIENTS_DETECTED=10

# Security
ALLOWED_ORIGINS=http://localhost:3000
Model Configuration
YOLOv8 Model: Automatically downloaded on first run
Gemini AI: Requires API key from Google AI Studio
Custom Models: Place in ./models/ directory
📚 API Documentation
Authentication Endpoints
POST /auth/register - Register new user
POST /auth/login - User authentication
GET /auth/me - Get current user info
Ingredient Detection
POST /ingredients/detect - Detect ingredients from image
Recipe Generation
POST /recipes/generate - Generate personalized recipe
GET /recipes/history - Get user's recipe history
GET /recipes/favorites - Get favorite recipes
POST /recipes/{recipe_id}/favorite - Toggle favorite status
User Management
PUT /profile/update - Update user profile
GET /analytics/mood-trends - Get mood analytics
GET /analytics/ingredient-usage - Get ingredient usage stats
Interactive API Documentation
Once the server is running:

Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc
🧪 Testing
Run Tests
