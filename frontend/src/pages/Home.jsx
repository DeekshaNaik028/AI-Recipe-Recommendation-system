// src/pages/Home.jsx - FIXED IMPORTS
import { useEffect, useState, useCallback } from 'react';
import { Zap, Heart, BookOpen, BarChart3, Home as HomeIcon } from 'lucide-react';
import { recipeService } from '../services/recipeService';
import { useToast } from '../hooks/useToast';
import Card from '../components/Common/Card';
import Loading from '../components/Common/Loading';
import './Pages.css';

export default function Home() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const { addToast } = useToast();

  const loadStats = useCallback(async () => {
    try {
      const data = await recipeService.getHistory(5);
      setStats(data);
    } catch (error) {
      addToast('Failed to load stats', 'error');
    } finally {
      setLoading(false);
    }
  }, [addToast]);

  useEffect(() => {
    loadStats();
  }, [loadStats]);

  if (loading) return <Loading />;

  const features = [
    {
      icon: Zap,
      title: 'Generate Recipe',
      description: 'Tell us your ingredients and mood, and let AI create the perfect recipe for you.',
      href: '/generate',
      color: 'gradient-warm'
    },
    {
      icon: Heart,
      title: 'Your Favorites',
      description: 'Save and organize your favorite recipes for quick access anytime.',
      href: '/favorites',
      color: 'gradient-secondary'
    },
    {
      icon: BookOpen,
      title: 'Recipe History',
      description: 'Browse through all the recipes you\'ve generated and revisit your favorites.',
      href: '/history',
      color: 'gradient-cool'
    },
    {
      icon: BarChart3,
      title: 'Analytics',
      description: 'Track your mood trends and ingredient preferences over time.',
      href: '/analytics',
      color: 'gradient-primary'
    },
  ];

  return (
    <div className="page home-page">
      <div className="page-header hero-header">
        <HomeIcon size={40} strokeWidth={1.5} className="header-icon" />
        <h1>Welcome to MoodMunch</h1>
        <p>Your AI-powered recipe companion</p>
      </div>

      <div className="home-grid">
        {features.map((feature, idx) => {
          const IconComponent = feature.icon;
          return (
            <Card key={idx} className={`home-card ${feature.color}`}>
              <div className="feature-icon">
                <IconComponent size={32} strokeWidth={1.5} />
              </div>
              <h3>{feature.title}</h3>
              <p>{feature.description}</p>
              <a href={feature.href} className="card-link">
                Explore →
              </a>
            </Card>
          );
        })}
      </div>

      {stats?.recipes && stats.recipes.length > 0 && (
        <Card className="recent-recipes">
          <h2>Recently Generated</h2>
          <div className="recent-list">
            {stats.recipes.map((recipe, idx) => (
              <div key={idx} className="recent-item">
                <div className="recent-info">
                  <span className="recent-title">{recipe.recipe?.title || 'Recipe'}</span>
                  <span className="recent-mood">{recipe.mood}</span>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}