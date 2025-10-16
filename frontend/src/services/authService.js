
// services/authService.js
import api from './api';

export const authService = {
  register: async (name, email, password, dietary_preferences = [], allergies = [], health_goals = []) => {
    const response = await api.post('/auth/register', {
      name,
      email,
      password,
      dietary_preferences,
      allergies,
      health_goals,
    });
    return response.data;
  },

  login: async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },

  getProfile: async () => {
    const response = await api.get('/users/me');
    return response.data;
  },

  updateProfile: async (profileData) => {
    const response = await api.put('/users/me', profileData);
    return response.data;
  },
};
