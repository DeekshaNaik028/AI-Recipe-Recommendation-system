// components/Auth/Register.jsx
import { useState } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { useToast } from '../../hooks/useToast';
import { authService } from '../../services/authService';
import { validateEmail, validatePassword } from '../../utils/validators';
import { DIETARY_PREFS } from '../../utils/constants';
import Button from '../Common/Button';
import './AuthForm.css';

export default function Register({ onBack }) {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    dietary_preferences: [],
    allergies: '',
    health_goals: [],
  });
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const { addToast } = useToast();

  const handlePreferenceChange = (pref) => {
    setFormData(prev => ({
      ...prev,
      dietary_preferences: prev.dietary_preferences.includes(pref)
        ? prev.dietary_preferences.filter(p => p !== pref)
        : [...prev.dietary_preferences, pref]
    }));
  };

  const handleHealthGoalChange = (goal) => {
    setFormData(prev => ({
      ...prev,
      health_goals: prev.health_goals.includes(goal)
        ? prev.health_goals.filter(g => g !== goal)
        : [...prev.health_goals, goal]
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (step === 1) {
      if (!formData.name || formData.name.length < 2) {
        addToast('Name must be at least 2 characters', 'error');
        return;
      }
      if (!validateEmail(formData.email)) {
        addToast('Invalid email address', 'error');
        return;
      }
      if (!validatePassword(formData.password)) {
        addToast('Password must be at least 8 characters', 'error');
        return;
      }
      if (formData.password !== formData.confirmPassword) {
        addToast('Passwords do not match', 'error');
        return;
      }
      setStep(2);
      return;
    }

    setLoading(true);
    try {
      await authService.register(
        formData.name,
        formData.email,
        formData.password,
        formData.dietary_preferences,
        formData.allergies.split(',').map(a => a.trim()).filter(Boolean),
        formData.health_goals
      );
      
      const response = await authService.login(formData.email, formData.password);
      login(response.user, response.access_token);
      addToast('Registration successful!', 'success');
    } catch (error) {
      addToast(error.response?.data?.detail || 'Registration failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <button type="button" onClick={onBack} className="back-button">← Back</button>
          <h1>Join MoodMunch 🍳</h1>
          <p>Step {step} of 2</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          {step === 1 ? (
            <>
              <div className="form-group">
                <label>Full Name</label>
                <input
                  type="text"
                  placeholder="Enter your name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  placeholder="Enter your email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label>Password</label>
                <input
                  type="password"
                  placeholder="At least 8 characters"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label>Confirm Password</label>
                <input
                  type="password"
                  placeholder="Confirm your password"
                  value={formData.confirmPassword}
                  onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                  required
                />
              </div>
            </>
          ) : (
            <>
              <div className="form-group">
                <label>Dietary Preferences</label>
                <div className="checkbox-group">
                  {DIETARY_PREFS.map(pref => (
                    <label key={pref} className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={formData.dietary_preferences.includes(pref)}
                        onChange={() => handlePreferenceChange(pref)}
                      />
                      {pref.replace('_', ' ')}
                    </label>
                  ))}
                </div>
              </div>

              <div className="form-group">
                <label>Allergies (comma separated)</label>
                <input
                  type="text"
                  placeholder="e.g., peanuts, shellfish"
                  value={formData.allergies}
                  onChange={(e) => setFormData({ ...formData, allergies: e.target.value })}
                />
              </div>

              <div className="form-group">
                <label>Health Goals</label>
                <div className="checkbox-group">
                  {['weight_loss', 'muscle_gain', 'heart_health', 'balanced_diet'].map(goal => (
                    <label key={goal} className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={formData.health_goals.includes(goal)}
                        onChange={() => handleHealthGoalChange(goal)}
                      />
                      {goal.replace('_', ' ')}
                    </label>
                  ))}
                </div>
              </div>
            </>
          )}

          <Button type="submit" disabled={loading} full>
            {loading ? 'Creating account...' : step === 1 ? 'Continue' : 'Create Account'}
          </Button>
        </form>
      </div>
    </div>
  );
}