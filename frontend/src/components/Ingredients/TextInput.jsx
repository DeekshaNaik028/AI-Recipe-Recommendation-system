// components/Ingredients/TextInput.jsx
import { useState } from 'react';
import { ingredientService } from '../../services/ingredientService';
import { useToast } from '../../hooks/useToast';
import './Ingredients.css';

export default function TextInput({ onExtract }) {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const { addToast } = useToast();

  const handleExtract = async (e) => {
    e.preventDefault();
    if (!text.trim()) {
      addToast('Please enter some ingredients', 'warning');
      return;
    }

    setLoading(true);
    try {
      const response = await ingredientService.extractFromText(text);
      onExtract(response.ingredients);
      setText('');
      addToast(`Extracted ${response.ingredients.length} ingredients!`, 'success');
    } catch (error) {
      addToast(error.response?.data?.detail || 'Failed to extract ingredients', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="text-input">
      <h3>⌨️ Manual Input</h3>
      <form onSubmit={handleExtract} className="text-form">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Type your ingredients... e.g., tomato, onion, garlic, chicken"
          disabled={loading}
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Processing...' : 'Extract Ingredients'}
        </button>
      </form>
    </div>
  );
}