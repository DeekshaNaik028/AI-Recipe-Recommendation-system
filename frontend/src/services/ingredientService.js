import api from './api';

export const ingredientService = {
  extractFromAudio: async (audioFile) => {
    const formData = new FormData();
    formData.append('file', audioFile);
    const response = await api.post('/ingredients/extract-from-audio', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  extractFromText: async (text) => {
    const response = await api.post('/ingredients/extract-from-text', { text });
    return response.data;
  },
};
