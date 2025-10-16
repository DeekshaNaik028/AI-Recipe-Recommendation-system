import api from './api';

export const analyticsService = {
  getMoodTrends: async (days = 30) => {
    const response = await api.get(`/analytics/mood-trends?days=${days}`);
    return response.data;
  },

  getIngredientStats: async () => {
    const response = await api.get('/analytics/ingredient-stats');
    return response.data;
  },

  getDashboard: async () => {
    const response = await api.get('/analytics/dashboard');
    return response.data;
  },
};