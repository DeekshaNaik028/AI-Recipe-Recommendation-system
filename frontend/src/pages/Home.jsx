// pages/Home.jsx
import { useEffect, useState } from 'react';
import { recipeService } from '../services/recipeService';
import { useToast } from '../hooks/useToast';
import Card from '../components/Common/Card';
import Loading from '../components/Common/Loading';
import './Pages.css';

export default function Home() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const { addToast } = useToast();

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const data = await recipeService.getHistory(5);
      setStats(data);
    } catch (error) {
      addToast('Failed to load stats', 'error');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <Loading />;

  return (
    <div className="page home-page">
      <div className="page-header">
        <h1>Welcome to MoodMunch 🍳</h1>
        <p>Your AI-powered recipe companion</p>
      </div>

      <div className="home-grid">
        <Card className="home-card">
          <h3>🎯 Generate Recipe</h3>
          <p>Tell us your ingredients and mood, and let AI create the perfect recipe for you.</p>
          <a href="/generate" className="card-link">Start Generating →</a>
        </Card>

        <Card className="home-card">
          <h3>❤️ Your Favorites</h3>
          <p>Save and organize your favorite recipes for quick access anytime.</p>
          <a href="/favorites" className="card-link">View Favorites →</a>
        </Card>

        <Card className="home-card">
          <h3>📚 Recipe History</h3>
          <p>Browse through all the recipes you've generated and revisit your favorites.</p>
          <a href="/history" className="card-link">View History →</a>
        </Card>

        <Card className="home-card">
          <h3>📊 Analytics</h3>
          <p>Track your mood trends and ingredient preferences over time.</p>
          <a href="/analytics" className="card-link">View Analytics →</a>
        </Card>
      </div>

      {stats?.recipes && stats.recipes.length > 0 && (
        <Card className="recent-recipes">
          <h3>📖 Recently Generated</h3>
          <div className="recent-list">
            {stats.recipes.map((recipe, idx) => (
              <div key={idx} className="recent-item">
                <span>{recipe.recipe?.title || 'Recipe'}</span>
                <span className="mood-tag">{recipe.mood}</span>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}