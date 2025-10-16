
// pages/History.jsx
import { useEffect, useState } from 'react';
import { recipeService } from '../services/recipeService';
import { useToast } from '../hooks/useToast';
import RecipeCard from '../components/Recipe/RecipeCard';
import RecipeDetail from '../components/Recipe/RecipeDetail';
import Loading from '../components/Common/Loading';
import './Pages.css';

export default function History() {
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedRecipe, setSelectedRecipe] = useState(null);
  const { addToast } = useToast();

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const data = await recipeService.getHistory(50);
      setRecipes(data.recipes);
    } catch (error) {
      addToast('Failed to load history', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this recipe?')) {
      try {
        await recipeService.deleteRecipe(id);
        setRecipes(prev => prev.filter(r => r._id !== id));
        addToast('Recipe deleted', 'success');
      } catch (error) {
        addToast('Failed to delete recipe', 'error');
      }
    }
  };

  const handleToggleFavorite = async (id) => {
    try {
      await recipeService.toggleFavorite(id);
      addToast('Favorite updated', 'success');
    } catch (error) {
      addToast('Failed to update favorite', 'error');
    }
  };

  if (loading) return <Loading />;

  return (
    <div className="page history-page">
      <div className="page-header">
        <h1>Recipe History 📚</h1>
        <p>All your generated recipes</p>
      </div>

      {recipes.length === 0 ? (
        <div className="empty-state">
          <p>No recipes yet. <a href="/generate">Generate your first recipe!</a></p>
        </div>
      ) : (
        <div className="recipes-grid">
          {recipes.map(recipe => (
            <div key={recipe._id} className="recipe-item">
              <RecipeCard
                recipe={recipe.recipe}
                onToggleFavorite={() => handleToggleFavorite(recipe._id)}
              />
              <div className="recipe-actions">
                <button 
                  onClick={() => setSelectedRecipe(recipe.recipe)}
                  className="action-btn"
                >
                  📖 View Full
                </button>
                <button 
                  onClick={() => handleDelete(recipe._id)}
                  className="action-btn danger"
                >
                  🗑️ Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {selectedRecipe && (
        <RecipeDetail recipe={selectedRecipe} onClose={() => setSelectedRecipe(null)} />
      )}
    </div>
  );
}