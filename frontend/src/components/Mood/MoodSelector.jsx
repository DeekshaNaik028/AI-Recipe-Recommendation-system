import { 
  Smile, 
  Frown, 
  Zap, 
  Moon, 
  AlertCircle, 
  Wind, 
  Sparkles, 
  Meh 
} from 'lucide-react';
import { MOODS } from '../../utils/constants';
import './Mood.css';

const moodIcons = {
  happy: Smile,
  sad: Frown,
  energetic: Zap,
  tired: Moon,
  stressed: AlertCircle,
  calm: Wind,
  excited: Sparkles,
  bored: Meh,
};

export default function MoodSelector({ selectedMood, onMoodChange }) {
  return (
    <div className="mood-selector">
      <h3>How are you feeling?</h3>
      <div className="mood-grid">
        {MOODS.map(mood => {
          const IconComponent = moodIcons[mood.value];
          return (
            <button
              key={mood.value}
              className={`mood-button ${selectedMood === mood.value ? 'active' : ''}`}
              onClick={() => onMoodChange(mood.value)}
              title={mood.label}
            >
              {IconComponent ? (
                <IconComponent className="mood-icon" size={32} strokeWidth={1.5} />
              ) : (
                <span className="mood-emoji">{mood.emoji}</span>
              )}
              <span className="mood-label">{mood.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
