# 🍳 AI-Powered Recipe Recommendation System

A personalized recipe recommendation system that uses **voice input**, **mood tracking**, and **AI** to generate customized recipes based on available ingredients, dietary preferences, and health goals.

## 🎯 Key Features

- ✅ **Voice Input for Ingredients** - Speak your available ingredients naturally
- ✅ **Text Input Alternative** - Type ingredients if preferred
- ✅ **Mood-Based Recipe Generation** - Get recipes tailored to your emotional state
- ✅ **AI-Powered Recipe Creation** - Using Google's Gemini AI
- ✅ **User Profiles** - Save dietary preferences, allergies, and health goals
- ✅ **Recipe History** - Track all generated recipes
- ✅ **Favorites System** - Save your best recipes
- ✅ **Analytics Dashboard** - View mood trends and ingredient usage stats

## 🏗️ Project Structure

```
recipe-recommendation-backend/
├── main.py                          # Main FastAPI application
├── .env                             # Environment variables (create from .env.example)
├── .env.example                     # Environment template
├── requirements.txt                 # Python dependencies
├── app/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py               # Configuration settings
│   ├── database/
│   │   ├── __init__.py
│   │   └── mongodb.py              # MongoDB operations
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py              # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py         # Authentication
│   │   ├── recipe_service.py       # Recipe generation
│   │   └── voice_ingredient_service.py  # Voice/text ingredient extraction
│   └── utils/
│       ├── __init__.py
│       └── exceptions.py           # Custom exceptions
└── uploads/                         # Upload directory (auto-created)
    └── audio/                       # Audio files storage
```

## 📋 Prerequisites

- Python 3.9+
- MongoDB (local or cloud)
- Google Gemini API Key

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd recipe-recommendation-backend
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup MongoDB

**Option A: Local MongoDB**
```bash
# Install MongoDB Community Edition
# Start MongoDB service
mongod --dbpath /path/to/data/directory
```

**Option B: MongoDB Atlas (Cloud)**
1. Create free account at [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Create a cluster
3. Get connection string

### 5. Get Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create new API key
3. Copy the key

### 6. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env file with your values
nano .env  # or use any text editor
```

**Required .env Configuration:**

```bash
# CRITICAL: Change these values!
SECRET_KEY=your-very-long-secret-key-at-least-32-characters-here
GEMINI_API_KEY=your-actual-gemini-api-key-here

# Database
MONGODB_URL=mongodb://localhost:27017
# OR for MongoDB Atlas:
# MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/

# CORS (add your frontend URLs)
ALLOWED_ORIGINS_STR=http://localhost:3000,http://localhost:3001
```

### 7. Run the Application

```bash
# Development mode (with auto-reload)
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## 📡 API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login user |

### Ingredient Extraction (NEW)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ingredients/extract-from-audio` | Extract ingredients from voice/audio |
| POST | `/ingredients/extract-from-text` | Extract ingredients from text |

### Recipe Generation

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/recipes/generate` | Generate personalized recipe |
| GET | `/recipes/history` | Get recipe history |
| GET | `/recipes/history/{id}` | Get specific recipe |
| DELETE | `/recipes/history/{id}` | Delete recipe |

### Favorites

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/recipes/{id}/favorite` | Toggle favorite |
| GET | `/recipes/favorites` | Get all favorites |

### User Profile

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users/me` | Get current user profile |
| PUT | `/users/me` | Update user profile |

### Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/analytics/mood-trends` | Get mood trends |
| GET | `/analytics/ingredient-stats` | Get ingredient usage stats |
| GET | `/analytics/dashboard` | Get comprehensive dashboard |

## 🎤 Using Voice Input

### Example: Extract Ingredients from Audio

```bash
curl -X POST "http://localhost:8000/ingredients/extract-from-audio" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@ingredients_audio.wav"
```

**Response:**
```json
{
  "ingredients": ["tomato", "onion", "garlic", "chicken"],
  "validated_ingredients": ["tomato", "onion", "garlic", "chicken"],
  "suggestions": {},
  "processing_time": 2.45,
  "source": "audio",
  "confidence": 0.85
}
```

### Example: Extract from Text

```bash
curl -X POST "http://localhost:8000/ingredients/extract-from-text" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I have tomatoes, onions, garlic, and some chicken breast"
  }'
```

## 🔧 Testing the API

### 1. Register a User

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "SecurePass123",
    "dietary_preferences": ["vegetarian"],
    "allergies": ["peanuts"],
    "health_goals": ["weight_loss"]
  }'
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123"
  }'
```

Save the `access_token` from the response.

### 3. Generate Recipe

```bash
curl -X POST "http://localhost:8000/recipes/generate" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ingredients": ["tomato", "onion", "garlic", "pasta"],
    "mood": "happy",
    "cuisine_preference": "italian",
    "servings": 2
  }'
```

## 🎨 Frontend Integration

### Voice Recording (Web)

```javascript
// Frontend example - Record audio for ingredient extraction
const recordIngredients = async () => {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  const mediaRecorder = new MediaRecorder(stream);
  const audioChunks = [];

  mediaRecorder.ondataavailable = (event) => {
    audioChunks.push(event.data);
  };

  mediaRecorder.onstop = async () => {
    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
    const formData = new FormData();
    formData.append('file', audioBlob, 'ingredients.wav');

    const response = await fetch('http://localhost:8000/ingredients/extract-from-audio', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    });

    const result = await response.json();
    console.log('Extracted ingredients:', result.ingredients);
  };

  mediaRecorder.start();
  
  // Stop after 5 seconds
  setTimeout(() => mediaRecorder.stop(), 5000);
};
```

## 🐛 Troubleshooting

### Common Issues

**1. MongoDB Connection Error**
```
Failed to connect to MongoDB
```
**Solution:** Ensure MongoDB is running and connection string is correct in `.env`

**2. Gemini API Error**
```
Failed to initialize Gemini AI
```
**Solution:** Check your `GEMINI_API_KEY` in `.env` file

**3. Audio Processing Error**
```
Failed to process audio file
```
**Solution:** Ensure audio file is in supported format (wav, mp3, ogg, webm, m4a)

**4. CORS Error**
```
Access to fetch blocked by CORS policy
```
**Solution:** Add your frontend URL to `ALLOWED_ORIGINS_STR` in `.env`

## 📊 Database Collections

The system creates these MongoDB collections:

- `users` - User accounts and profiles
- `recipe_history` - Generated recipes
- `favorites` - Favorited recipes
- `mood_logs` - Mood tracking data

## 🔒 Security Notes

- Always use strong `SECRET_KEY` in production (32+ characters)
- Never commit `.env` file to version control
- Use HTTPS in production
- Implement rate limiting for API endpoints
- Regularly update dependencies

## 🚀 Deployment

### Production Checklist

- [ ] Set `DEBUG=False` in `.env`
- [ ] Use strong `SECRET_KEY`
- [ ] Configure production MongoDB
- [ ] Set up HTTPS/SSL
- [ ] Configure proper CORS origins
- [ ] Set up logging and monitoring
- [ ] Implement rate limiting
- [ ] Set up backup strategy

## 📝 License

[Your License Here]

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## 📧 Support

For issues or questions, please open a GitHub issue or contact [naikdeeksh24912@gmail.com].

---

**Happy Cooking! 🍽️**