// pages/Analytics.jsx
import { useEffect, useState } from 'react';
import { analyticsService } from '../services/analyticsService';
import { useToast } from '../hooks/useToast';
import Card from '../components/Common/Card';
import Loading from '../components/Common/Loading';
import './Pages.css';

export default function Analytics() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const { addToast } = useToast();

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      const data = await analyticsService.getDashboard();
      setAnalytics(data);
    } catch (error) {
      addToast('Failed to load analytics', 'error');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <Loading />;

  return (
    <div className="page analytics-page">
      <div className="page-header">
        <h1>Your Analytics 📊</h1>
        <p>Track your cooking journey</p>
      </div>

      <div className="stats-grid">
        <Card className="stat-card">
          <h3>Recipes Generated</h3>
          <p className="stat-value">{analytics?.total_recipes_generated || 0}</p>
        </Card>
        <Card className="stat-card">
          <h3>Favorites</h3>
          <p className="stat-value">{analytics?.total_favorites || 0}</p>
        </Card>
        <Card className="stat-card">
          <h3>Unique Ingredients</h3>
          <p className="stat-value">{analytics?.unique_ingredients_used || 0}</p>
        </Card>
        <Card className="stat-card">
          <h3>Avg Cook Time</h3>
          <p className="stat-value">{Math.round(analytics?.avg_cooking_time_minutes || 0)}m</p>
        </Card>
      </div>

      {analytics?.top_ingredients && analytics.top_ingredients.length > 0 && (
        <Card>
          <h2>Top Ingredients</h2>
          <div className="top-list">
            {analytics.top_ingredients.map((ing, idx) => (
              <div key={idx} className="top-item">
                <span className="rank">#{idx + 1}</span>
                <span className="name">{ing.ingredient}</span>
                <span className="count">{ing.usage_count}x</span>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
