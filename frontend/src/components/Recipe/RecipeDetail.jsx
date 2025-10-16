// components/Recipe/RecipeDetail.jsx
import { formatTime } from '../../utils/formatters';
import './Recipe.css';

export default function RecipeDetail({ recipe, onClose }) {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content recipe-detail" onClick={e => e.stopPropagation()}>
        <button className="close-button" onClick={onClose}>✕</button>

        <div className="detail-header">
          <h2>{recipe.title}</h2>
          <div className="detail-meta">
            <span>⏱️ {formatTime(recipe.total_time)}</span>
            <span>👥 {recipe.servings} servings</span>
            <span>📊 {recipe.difficulty}</span>
          </div>
        </div>

        <p className="detail-description">{recipe.description}</p>

        <div className="detail-section">
          <h3>Ingredients</h3>
          <ul className="ingredients-list">
            {recipe.ingredients.map((ing, idx) => (
              <li key={idx}>
                <span className="ingredient-item">{ing}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="detail-section">
          <h3>Instructions</h3>
          <ol className="instructions-list">
            {recipe.instructions.map((instr, idx) => (
              <li key={idx}>{instr}</li>
            ))}
          </ol>
        </div>

        <div className="detail-section">
          <h3>Nutrition Information (per serving)</h3>
          <div className="nutrition-grid">
            <div className="nutrition-card">
              <span className="nutrition-label">Calories</span>
              <span className="nutrition-value">{Math.round(recipe.nutrition_info.calories)}</span>
            </div>
            <div className="nutrition-card">
              <span className="nutrition-label">Protein</span>
              <span className="nutrition-value">{Math.round(recipe.nutrition_info.protein)}g</span>
            </div>
            <div className="nutrition-card">
              <span className="nutrition-label">Carbs</span>
              <span className="nutrition-value">{Math.round(recipe.nutrition_info.carbs)}g</span>
            </div>
            <div className="nutrition-card">
              <span className="nutrition-label">Fat</span>
              <span className="nutrition-value">{Math.round(recipe.nutrition_info.fat)}g</span>
            </div>
            <div className="nutrition-card">
              <span className="nutrition-label">Fiber</span>
              <span className="nutrition-value">{Math.round(recipe.nutrition_info.fiber)}g</span>
            </div>
            <div className="nutrition-card">
              <span className="nutrition-label">Sugar</span>
              <span className="nutrition-value">{Math.round(recipe.nutrition_info.sugar)}g</span>
            </div>
          </div>
        </div>

        {recipe.tags && recipe.tags.length > 0 && (
          <div className="detail-section">
            <h3>Tags</h3>
            <div className="tags-list">
              {recipe.tags.map(tag => (
                <span key={tag} className="tag">{tag}</span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
