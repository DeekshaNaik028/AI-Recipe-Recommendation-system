import { useState } from 'react';
import { Eye, EyeOff, LogIn, ChefHat } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import { useToast } from '../../hooks/useToast';
import { authService } from '../../services/authService';
import { validateEmail, validatePassword } from '../../utils/validators';
import Register from './Register';
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
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '12px', marginBottom: '12px' }}>
            <ChefHat size={40} strokeWidth={2} style={{ color: '#861657' }} />
            <h1>MoodMunch</h1>
          </div>
          <p>Cook What You Feel</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              placeholder="your@email.com"
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
                placeholder="••••••••"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="toggle-password"
                aria-label="Toggle password visibility"
              >
                {showPassword ? (
                  <EyeOff size={18} strokeWidth={2} />
                ) : (
                  <Eye size={18} strokeWidth={2} />
                )}
              </button>
            </div>
          </div>

          <Button 
            type="submit" 
            disabled={loading} 
            full
            icon={LogIn}
          >
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