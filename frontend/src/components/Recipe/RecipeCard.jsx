// components/Recipe/RecipeCard.jsx
import { formatTime } from '../../utils/formatters';
import './Recipe.css';

export default function RecipeCard({ recipe, onToggleFavorite, isFavorite }) {
  return (
    <div className="recipe-card">
      <div className="recipe-header">
        <h3>{recipe.title}</h3>
        <button
          className={`favorite-btn ${isFavorite ? 'active' : ''}`}
          onClick={() => onToggleFavorite(recipe.id)}
          title={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
        >
          {isFavorite ? '❤️' : '🤍'}
        </button>
      </div>

      <p className="recipe-description">{recipe.description}</p>

      <div className="recipe-meta">
        <span className="meta-item">
          ⏱️ {formatTime(recipe.total_time)}
        </span>
        <span className="meta-item">
          👥 {recipe.servings} servings
        </span>
        <span className="meta-item">
          📊 {recipe.difficulty}
        </span>
      </div>

      <div className="recipe-nutrition">
        <div className="nutrition-item">
          <span className="nutrition-label">Calories</span>
          <span className="nutrition-value">{Math.round(recipe.nutrition_info.calories)}</span>
        </div>
        <div className="nutrition-item">
          <span className="nutrition-label">Protein</span>
          <span className="nutrition-value">{Math.round(recipe.nutrition_info.protein)}g</span>
        </div>
        <div className="nutrition-item">
          <span className="nutrition-label">Carbs</span>
          <span className="nutrition-value">{Math.round(recipe.nutrition_info.carbs)}g</span>
        </div>
        <div className="nutrition-item">
          <span className="nutrition-label">Fat</span>
          <span className="nutrition-value">{Math.round(recipe.nutrition_info.fat)}g</span>
        </div>
      </div>
    </div>
  );
}