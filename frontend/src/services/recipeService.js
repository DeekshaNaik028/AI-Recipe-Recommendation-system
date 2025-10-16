
// services/recipeService.js
import api from './api';

export const recipeService = {
  generateRecipe: async (ingredients, mood, cuisine_preference = 'any', servings = 2) => {
    const response = await api.post('/recipes/generate', {
      ingredients,
      mood,
      cuisine_preference,
      servings,
    });
    return response.data;
  },

  getHistory: async (limit = 10, skip = 0) => {
    const response = await api.get(`/recipes/history?limit=${limit}&skip=${skip}`);
    return response.data;
  },

  getRecipeById: async (id) => {
    const response = await api.get(`/recipes/history/${id}`);
    return response.data;
  },

  deleteRecipe: async (id) => {
    const response = await api.delete(`/recipes/history/${id}`);
    return response.data;
  },

  toggleFavorite: async (id) => {
    const response = await api.post(`/recipes/${id}/favorite`);
    return response.data;
  },

  getFavorites: async () => {
    const response = await api.get('/recipes/favorites');
    return response.data;
  },
};