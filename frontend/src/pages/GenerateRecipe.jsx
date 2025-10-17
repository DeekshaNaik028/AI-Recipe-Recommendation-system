// src/pages/GenerateRecipe.jsx - FIXED VERSION
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
  // State management - CRITICAL: Keep recipe in state, don't navigate
  const [ingredients, setIngredients] = useState([]);
  const [selectedMood, setSelectedMood] = useState('happy');
  const [selectedCuisine, setSelectedCuisine] = useState('any');
  const [servings, setServings] = useState(2);
  const [recipe, setRecipe] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showDetail, setShowDetail] = useState(false);
  const [isFavorite, setIsFavorite] = useState(false);
  const { addToast } = useToast();

  // Handle voice/text ingredient extraction
  const handleExtractIngredients = (extracted) => {
    if (!extracted || extracted.length === 0) {
      addToast('No ingredients extracted', 'warning');
      return;
    }

    setIngredients(prev => {
      const combined = [...prev, ...extracted];
      const unique = [...new Set(combined)];
      addToast(`Added ${extracted.length} ingredient(s)`, 'success');
      return unique;
    });
  };

  // Remove ingredient from list
  const handleRemoveIngredient = (index) => {
    const removed = ingredients[index];
    setIngredients(prev => prev.filter((_, i) => i !== index));
    addToast(`Removed "${removed}"`, 'info');
  };

  // Manually add ingredient
  const handleAddIngredient = (ingredient) => {
    const cleaned = ingredient.toLowerCase().trim();
    
    if (!cleaned) {
      addToast('Please enter an ingredient', 'warning');
      return;
    }
    
    if (ingredients.includes(cleaned)) {
      addToast(`"${ingredient}" already added`, 'warning');
      return;
    }
    
    setIngredients(prev => [...prev, cleaned]);
    addToast(`Added "${ingredient}"`, 'success');
  };

  // CRITICAL FIX: Generate recipe WITHOUT navigation
  const handleGenerateRecipe = async (e) => {
    e.preventDefault();

    if (ingredients.length === 0) {
      addToast('Please add at least one ingredient', 'warning');
      return;
    }

    setLoading(true);
    
    try {
      console.log('Generating recipe with:', {
        ingredients,
        mood: selectedMood,
        cuisine: selectedCuisine,
        servings
      });

      const data = await recipeService.generateRecipe(
        ingredients,
        selectedMood,
        selectedCuisine,
        servings
      );

      console.log('Recipe generated:', data);
      
      setRecipe(data);
      setIsFavorite(false);
      addToast('Recipe generated successfully!', 'success');
      
      // Scroll to recipe
      setTimeout(() => {
        document.querySelector('.recipe-result-section')?.scrollIntoView({ 
          behavior: 'smooth',
          block: 'start'
        });
      }, 100);

    } catch (error) {
      console.error('Recipe generation error:', error);
      const errorMsg = error.response?.data?.detail || error.message || 'Failed to generate recipe';
      addToast(errorMsg, 'error');
    } finally {
      setLoading(false);
    }
  };

  // Toggle favorite
  const handleToggleFavorite = async () => {
    try {
      await recipeService.toggleFavorite(recipe.id || Date.now());
      setIsFavorite(!isFavorite);
      addToast(isFavorite ? 'Removed from favorites' : 'Added to favorites', 'success');
    } catch (error) {
      addToast('Failed to update favorite', 'error');
    }
  };

  // Reset form to generate another recipe
  const handleGenerateAnother = () => {
    setRecipe(null);
    setIsFavorite(false);
  };

  return (
    <div className="page generate-recipe-page">
      <div className="page-header">
        <h1>Create Your Recipe</h1>
        <p>Add ingredients and select your mood to generate a personalized recipe</p>
      </div>

      <div className="generate-container">
        {/* INPUT SECTION - Always visible unless recipe is generated */}
        <div className={`generate-form ${!recipe ? 'active' : 'hidden'}`}>
          <Card className="input-card">
            <form onSubmit={handleGenerateRecipe}>
              {/* Voice Recorder */}
              <div className="input-section">
                <h3>Record Ingredients</h3>
                <VoiceRecorder onExtract={handleExtractIngredients} />
              </div>

              {/* Divider */}
              <div className="section-divider">
                <span>or</span>
              </div>

              {/* Text Input */}
              <div className="input-section">
                <h3>Type Ingredients</h3>
                <TextInput onExtract={handleExtractIngredients} />
              </div>

              {/* Ingredient List */}
              <IngredientList
                ingredients={ingredients}
                onRemove={handleRemoveIngredient}
                onAdd={handleAddIngredient}
              />

              {/* Mood Selector */}
              <MoodSelector 
                selectedMood={selectedMood} 
                onMoodChange={setSelectedMood} 
              />

              {/* Cuisine & Servings */}
              <div className="form-row">
                <div className="form-group">
                  <label>Cuisine Type</label>
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
              </div>

              {/* Generate Button */}
              <Button 
                type="submit" 
                disabled={loading || ingredients.length === 0}
                full
                className="generate-btn"
              >
                {loading ? 'Generating...' : 'Generate Recipe'}
              </Button>
            </form>
          </Card>
        </div>

        {/* RESULT SECTION */}
        {recipe && (
          <div className="recipe-result-section">
            {loading && (
              <Card>
                <Loading />
              </Card>
            )}

            {!loading && recipe && (
              <>
                <Card>
                  <RecipeCard
                    recipe={recipe}
                    onToggleFavorite={handleToggleFavorite}
                    isFavorite={isFavorite}
                  />
                </Card>

                <div className="result-actions">
                  <Button 
                    onClick={() => setShowDetail(true)}
                    full
                    className="view-recipe-btn"
                  >
                    View Full Recipe
                  </Button>
                  
                  <Button 
                    onClick={handleGenerateAnother}
                    variant="secondary"
                    full
                  >
                    Generate Another
                  </Button>
                </div>
              </>
            )}
          </div>
        )}
      </div>

      {/* Recipe Detail Modal */}
      {showDetail && recipe && (
        <RecipeDetail recipe={recipe} onClose={() => setShowDetail(false)} />
      )}
    </div>
  );
}