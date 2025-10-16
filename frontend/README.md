# 🍳 MoodMunch Frontend

**Tagline:** Cook What You Feel! 💕

A beautiful, modern React frontend for the AI-powered recipe recommendation system. Generate personalized recipes based on your mood, available ingredients, and dietary preferences.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![React](https://img.shields.io/badge/react-18.2.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## ✨ Features

- 🎤 **Voice Input** - Speak your ingredients naturally
- ⌨️ **Text Input** - Type ingredients manually
- 😊 **Mood-Based Recipes** - Get recipes that match your emotional state
- ❤️ **Favorites System** - Save your loved recipes
- 📊 **Analytics Dashboard** - Track your cooking journey
- 🌙 **Dark/Light Mode** - Beautiful themes for any time
- 📱 **Fully Responsive** - Works on all devices
- 🎨 **Cute UI** - Pink gradient theme with smooth animations

## 🚀 Quick Start

### Prerequisites

- Node.js 14+ and npm/yarn
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd moodmunch-frontend

# Install dependencies
npm install
# or
yarn install

# Create environment file
cp .env.example .env

# Edit .env with your backend URL
nano .env  # or use any text editor

# Start development server
npm start
# or
yarn start
```

The app will open at `http://localhost:3000`

## 📁 Project Structure

```
moodmunch-frontend/
├── public/                  # Static files
├── src/
│   ├── components/         # Reusable UI components
│   │   ├── Auth/          # Login/Register
│   │   ├── Layout/        # Navbar, Sidebar, Footer
│   │   ├── Ingredients/   # Voice & Text input
│   │   ├── Recipe/        # Recipe cards & details
│   │   ├── Mood/          # Mood selector
│   │   ├── Common/        # Buttons, Cards, Loading
│   │   └── Theme/         # Dark/Light toggle
│   │
│   ├── pages/             # Main application pages
│   │   ├── Home.jsx
│   │   ├── GenerateRecipe.jsx
│   │   ├── History.jsx
│   │   ├── Favorites.jsx
│   │   ├── Analytics.jsx
│   │   └── Profile.jsx
│   │
│   ├── services/          # API integration
│   │   ├── api.js
│   │   ├── authService.js
│   │   ├── recipeService.js
│   │   ├── ingredientService.js
│   │   └── analyticsService.js
│   │
│   ├── context/           # React Context
│   │   ├── AuthContext.jsx
│   │   ├── ThemeContext.jsx
│   │   └── ToastContext.jsx
│   │
│   ├── hooks/             # Custom hooks
│   │   ├── useAuth.js
│   │   ├── useTheme.js
│   │   ├── useToast.js
│   │   └── useLocalStorage.js
│   │
│   ├── utils/             # Helper functions
│   ├── assets/            # Images, icons
│   ├── App.jsx            # Main app
│   └── index.jsx          # Entry point
│
├── package.json
├── .env.example
├── .gitignore
└── README.md
```

## 🎯 Available Scripts

### Development

```bash
# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test

# Eject from Create React App (⚠️ irreversible)
npm run eject
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_APP_NAME=MoodMunch
REACT_APP_ENABLE_VOICE_INPUT=true
```

See `.env.example` for all available options.

## 📱 Pages Overview

### 1. Home (`/`)
- Dashboard with stats
- Quick access to features
- Recent activity

### 2. Generate Recipe (`/generate`)
- Choose input method (Voice/Text)
- Add ingredients
- Select mood
- Generate personalized recipe

### 3. History (`/history`)
- View all generated recipes
- Search and filter
- Delete recipes

### 4. Favorites (`/favorites`)
- Your saved recipes
- Quick access to loved meals

### 5. Analytics (`/analytics`)
- Mood distribution chart
- Top ingredients
- Cooking statistics
- Weekly activity

### 6. Profile (`/profile`)
- User information
- Dietary preferences
- Allergies
- Health goals

## 🎨 Design System

### Colors (Light Mode)
```css
Primary: #FF6B9D (Pink)
Secondary: #FFC75F (Yellow)
Accent: #6BCF7F (Green)
Background: #FFF5F7 (Soft Pink)
Surface: #FFFFFF (White)
```

### Colors (Dark Mode)
```css
Primary: #FF6B9D (Pink)
Secondary: #FFB74D (Amber)
Accent: #81C784 (Light Green)
Background: #1A1A2E (Dark Blue)
Surface: #2D2D44 (Dark Purple)
```

### Typography
- **Headings:** Poppins (Bold)
- **Body:** Inter (Regular)
- **Accent:** Fredoka One (Cute)

## 🔌 API Integration

The app connects to the backend API at `REACT_APP_API_URL`.

### API Services

```javascript
// Example: Generate Recipe
import { recipeAPI } from './services/api';

const recipe = await recipeAPI.generate({
  ingredients: ['chicken', 'tomato'],
  mood: 'happy',
  cuisine_preference: 'italian'
});
```

### Authentication

JWT token is stored in localStorage and automatically added to API requests.

```javascript
// Login
const { token, user } = await authAPI.login(email, password);
localStorage.setItem('token', token);

// Logout
localStorage.removeItem('token');
```

## 🎤 Voice Recording

Uses Web Audio API for recording:

```javascript
// Start recording
const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
const mediaRecorder = new MediaRecorder(stream);
mediaRecorder.start();

// Stop and upload
mediaRecorder.stop();
const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
await ingredientAPI.extractFromAudio(audioBlob);
```

## 🌙 Theme System

Toggle between light and dark modes:

```javascript
import { useTheme } from './context/ThemeContext';

const { isDark, setIsDark } = useTheme();
setIsDark(!isDark);
```

## 📊 State Management

Uses React Context for global state:

- **AuthContext** - User authentication
- **ThemeContext** - Dark/Light mode
- **ToastContext** - Notifications

## 🧪 Testing

```bash
# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Generate coverage report
npm test -- --coverage
```

## 📦 Building for Production

```bash
# Create optimized production build
npm run build

# The build folder will contain:
# - Minified JavaScript
# - Optimized CSS
# - Compressed assets
```

## 🚀 Deployment

### Deploy to Vercel

```bash
npm install -g vercel
vercel
```

### Deploy to Netlify

```bash
npm run build
# Drag and drop the build folder to Netlify
```

### Deploy to GitHub Pages

```bash
npm install gh-pages --save-dev

# Add to package.json:
# "homepage": "https://yourusername.github.io/moodmunch"
# "predeploy": "npm run build"
# "deploy": "gh-pages -d build"

npm run deploy
```

## 🐛 Troubleshooting

### CORS Errors

Make sure backend CORS settings allow your frontend URL:

```python
# In backend config.py
ALLOWED_ORIGINS_STR=http://localhost:3000,https://yourdomain.com
```

### Audio Recording Not Working

Check browser permissions and ensure HTTPS (required for production).

### API Connection Failed

Verify `REACT_APP_API_URL` in `.env` matches your backend URL.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open a Pull Request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Icons by [Lucide React](https://lucide.dev/)
- Fonts by [Google Fonts](https://fonts.google.com/)
- Inspired by modern food apps

## 📧 Support

For issues or questions, please open a GitHub issue or contact [your-email].

---

**Made with 💕 by Your Team**

Happy Cooking! 🍳✨