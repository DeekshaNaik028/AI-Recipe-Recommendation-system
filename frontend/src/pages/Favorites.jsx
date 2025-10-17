import { useEffect, useState } from 'react';
import { Heart, Eye } from 'lucide-react';
import { recipeService } from '../../services/recipeService';
import { useToast } from '../../hooks/useToast';
import RecipeCard from '../../components/Recipe/RecipeCard';
import RecipeDetail from '../../components/Recipe/RecipeDetail';
import Loading from '../../components/Common/Loading';
import Button from '../../components/Common/Button';
import './Pages.css';

export default function Favorites() {
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedRecipe, setSelectedRecipe] = useState(null);
  const { addToast } = useToast();

  useEffect(() => {
    loadFavorites();
  }, []);

  const loadFavorites = async () => {
    try {
      const data = await recipeService.getFavorites();
      setFavorites(data.favorites);
    } catch (error) {
      addToast('Failed to load favorites', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveFavorite = async (id) => {
    try {
      await recipeService.toggleFavorite(id);
      setFavorites(prev => prev.filter(r => r._id !== id));
      addToast('Removed from favorites', 'success');
    } catch (error) {
      addToast('Failed to remove favorite', 'error');
    }
  };

  if (loading) return <Loading />;

  return (
    <div className="page favorites-page">
      <div className="page-header">
        <Heart size={40} strokeWidth={1.5} className="header-icon" />
        <h1>Favorite Recipes</h1>
        <p>Your saved recipes</p>
      </div>

      {favorites.length === 0 ? (
        <div className="empty-state">
          <Heart size={48} strokeWidth={1.5} className="empty-icon" />
          <p>No favorites yet.</p>
          <Button href="/generate">Generate and save recipes!</Button>
        </div>
      ) : (
        <div className="recipes-grid">
          {favorites.map(recipe => (
            <div key={recipe._id} className="recipe-item">
              <RecipeCard
                recipe={recipe.recipe}
                onToggleFavorite={() => handleRemoveFavorite(recipe._id)}
                isFavorite={true}
              />
              <Button 
                onClick={() => setSelectedRecipe(recipe.recipe)}
                variant="primary"
                size="sm"
                icon={Eye}
                full
              >
                View Full Recipe
              </Button>
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
