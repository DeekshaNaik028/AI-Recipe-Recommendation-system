
// components/Mood/MoodSelector.jsx
import { MOODS } from '../../utils/constants';
import './Mood.css';

export default function MoodSelector({ selectedMood, onMoodChange }) {
  return (
    <div className="mood-selector">
      <h3>How are you feeling? 🎭</h3>
      <div className="mood-grid">
        {MOODS.map(mood => (
          <button
            key={mood.value}
            className={`mood-button ${selectedMood === mood.value ? 'active' : ''}`}
            onClick={() => onMoodChange(mood.value)}
            title={mood.label}
          >
            <span className="mood-emoji">{mood.emoji}</span>
            <span className="mood-label">{mood.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}