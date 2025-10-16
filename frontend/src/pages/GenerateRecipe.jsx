// pages/GenerateRecipe.jsx
import { useState } from 'react';
import { recipeService } from '../services/recipeService';
import { useToast } from '../hooks/useToast';
import { CUISINES } from '../utils/constants';
import VoiceRecorder from '../components/Ingredients/VoiceRecorder';
import TextInput from '../components/Ingredients/TextInput';
import IngredientList from '../components/Ingredients/IngredientList';
import MoodSelector from '../components/Mood/MoodSelector';
import RecipeCard from '../components/Recipe/RecipeCard';
import RecipeDetail from '../components/Recipe/RecipeDetail';
import Button from '../components/Common/Button';
import Card from '../components/Common/Card';
import Loading from '../components/Common/Loading';
import './Pages.css';

export default function GenerateRecipe() {
  const [ingredients, setIngredients] = useState([]);
  const [selectedMood, setSelectedMood] = useState('happy');
  const [selectedCuisine, setSelectedCuisine] = useState('any');
  const [servings, setServings] = useState(2);
  const [recipe, setRecipe] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showDetail, setShowDetail] = useState(false);
  const [isFavorite, setIsFavorite] = useState(false);
  const { addToast } = useToast();

  const handleExtractIngredients = (extracted) => {
    setIngredients(prev => {
      const newIngredients = [...new Set([...prev, ...extracted])];
      return newIngredients;
    });
  };

  const handleRemoveIngredient = (index) => {
    setIngredients(prev => prev.filter((_, i) => i !== index));
  };

  const handleAddIngredient = (ingredient) => {
    if (!ingredients.includes(ingredient.toLowerCase())) {
      setIngredients(prev => [...prev, ingredient.toLowerCase()]);
    }
  };

  const handleGenerateRecipe = async (e) => {
    e.preventDefault();

    if (ingredients.length === 0) {
      addToast('Please add at least one ingredient', 'warning');
      return;
    }

    setLoading(true);
    try {
      const data = await recipeService.generateRecipe(
        ingredients,
        selectedMood,
        selectedCuisine,
        servings
      );
      setRecipe(data);
      setIsFavorite(false);
      addToast('Recipe generated successfully!', 'success');
    } catch (error) {
      addToast(error.response?.data?.detail || 'Failed to generate recipe', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleFavorite = async () => {
    try {
      await recipeService.toggleFavorite(recipe.id || Date.now());
      setIsFavorite(!isFavorite);
      addToast(isFavorite ? 'Removed from favorites' : 'Added to favorites', 'success');
    } catch (error) {
      addToast('Failed to toggle favorite', 'error');
    }
  };

  return (
    <div className="page generate-recipe-page">
      <div className="page-header">
        <h1>Generate Your Perfect Recipe 🎯</h1>
        <p>Tell us about your mood and ingredients</p>
      </div>

      <div className="generate-layout">
        <div className="generate-form">
          <Card>
            <form onSubmit={handleGenerateRecipe}>
              <VoiceRecorder onExtract={handleExtractIngredients} />
              <TextInput onExtract={handleExtractIngredients} />

              <IngredientList
                ingredients={ingredients}
                onRemove={handleRemoveIngredient}
                onAdd={handleAddIngredient}
              />

              <MoodSelector 
                selectedMood={selectedMood} 
                onMoodChange={setSelectedMood} 
              />

              <div className="form-group">
                <label>Cuisine Preference</label>
                <select 
                  value={selectedCuisine} 
                  onChange={(e) => setSelectedCuisine(e.target.value)}
                >
                  {CUISINES.map(cuisine => (
                    <option key={cuisine} value={cuisine}>
                      {cuisine.charAt(0).toUpperCase() + cuisine.slice(1)}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Servings</label>
                <input
                  type="number"
                  min="1"
                  max="10"
                  value={servings}
                  onChange={(e) => setServings(parseInt(e.target.value))}
                />
              </div>

              <Button 
                type="submit" 
                disabled={loading || ingredients.length === 0}
                full
              >
                {loading ? '✨ Generating...' : '✨ Generate Recipe'}
              </Button>
            </form>
          </Card>
        </div>

        <div className="generate-result">
          {loading && <Loading />}
          {recipe && !loading && (
            <>
              <RecipeCard
                recipe={recipe}
                onToggleFavorite={handleToggleFavorite}
                isFavorite={isFavorite}
              />
              <Button 
                onClick={() => setShowDetail(true)}
                full
                variant="secondary"
              >
                View Full Recipe →
              </Button>
            </>
          )}
        </div>
      </div>

      {showDetail && recipe && (
        <RecipeDetail recipe={recipe} onClose={() => setShowDetail(false)} />
      )}
    </div>
  );
}