// components/Ingredients/IngredientList.jsx
import { useState } from 'react';
import './Ingredients.css';

export default function IngredientList({ ingredients, onRemove, onAdd }) {
  const [newIngredient, setNewIngredient] = useState('');

  const handleAdd = (e) => {
    e.preventDefault();
    if (newIngredient.trim()) {
      onAdd(newIngredient.trim());
      setNewIngredient('');
    }
  };

  return (
    <div className="ingredient-list">
      <h3>Ingredients Selected</h3>
      <div className="ingredients-display">
        {ingredients.length === 0 ? (
          <p className="empty-message">No ingredients added yet</p>
        ) : (
          ingredients.map((ing, idx) => (
            <div key={idx} className="ingredient-badge">
              <span>{ing}</span>
              <button
                type="button"
                onClick={() => onRemove(idx)}
                className="remove-btn"
              >
                ✕
              </button>
            </div>
          ))
        )}
      </div>

      <form onSubmit={handleAdd} className="add-ingredient-form">
        <input
          type="text"
          value={newIngredient}
          onChange={(e) => setNewIngredient(e.target.value)}
          placeholder="Add more ingredients..."
        />
        <button type="submit">+ Add</button>
      </form>
    </div>
  );
}