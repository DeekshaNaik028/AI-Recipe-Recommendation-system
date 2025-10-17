// src/pages/History.jsx - FIXED IMPORTS
import { useEffect, useState } from 'react';
import { BookOpen, Trash2, Eye } from 'lucide-react';
import { recipeService } from '../services/recipeService';
import { useToast } from '../hooks/useToast';
import RecipeCard from '../components/Recipe/RecipeCard';
import RecipeDetail from '../components/Recipe/RecipeDetail';
import Loading from '../components/Common/Loading';
import Button from '../components/Common/Button';
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
        <BookOpen size={40} strokeWidth={1.5} className="header-icon" />
        <h1>Recipe History</h1>
        <p>All your generated recipes</p>
      </div>

      {recipes.length === 0 ? (
        <div className="empty-state">
          <BookOpen size={48} strokeWidth={1.5} className="empty-icon" />
          <p>No recipes yet.</p>
          <Button href="/generate">Generate your first recipe</Button>
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
                <Button 
                  onClick={() => setSelectedRecipe(recipe.recipe)}
                  variant="primary"
                  size="sm"
                  icon={Eye}
                  full
                >
                  View Full
                </Button>
                <Button 
                  onClick={() => handleDelete(recipe._id)}
                  variant="danger"
                  size="sm"
                  icon={Trash2}
                  full
                >
                  Delete
                </Button>
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