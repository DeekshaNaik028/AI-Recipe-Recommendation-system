// components/Auth/Login.jsx
import { useState } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { useToast } from '../../hooks/useToast';
import { authService } from '../../services/authService';
import { validateEmail, validatePassword } from '../../utils/validators';
import Register from './Register';  // ADD THIS IMPORT
import Button from '../Common/Button';
import './AuthForm.css';

export default function Login() {
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const { login } = useAuth();
  const { addToast } = useToast();
  const [currentPage, setCurrentPage] = useState('login');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateEmail(formData.email)) {
      addToast('Invalid email address', 'error');
      return;
    }
    
    if (!validatePassword(formData.password)) {
      addToast('Password must be at least 8 characters', 'error');
      return;
    }

    setLoading(true);
    try {
      const response = await authService.login(formData.email, formData.password);
      login(response.user, response.access_token);
      addToast('Login successful!', 'success');
    } catch (error) {
      addToast(error.response?.data?.detail || 'Login failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  if (currentPage === 'register') {
    return <Register onBack={() => setCurrentPage('login')} />;
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1>🍳 MoodMunch</h1>
          <p>AI-Powered Recipe Recommendations</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
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
            <div className="password-input">
              <input
                type={showPassword ? 'text' : 'password'}
                placeholder="Enter your password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="toggle-password"
              >
                {showPassword ? '👁️' : '👁️‍🗨️'}
              </button>
            </div>
          </div>

          <Button type="submit" disabled={loading} full>
            {loading ? 'Logging in...' : 'Login'}
          </Button>
        </form>

        <div className="auth-footer">
          <p>Don't have an account?</p>
          <button 
            type="button"
            onClick={() => setCurrentPage('register')}
            className="link-button"
          >
            Sign up here
          </button>
        </div>
      </div>
    </div>
  );
}