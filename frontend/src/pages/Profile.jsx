// src/pages/Profile.jsx - FIXED IMPORTS
import { useEffect, useState, useCallback } from 'react';
import { User, Edit2, Save, X } from 'lucide-react';
import { authService } from '../services/authService';
import { useToast } from '../hooks/useToast';
import Card from '../components/Common/Card';
import Button from '../components/Common/Button';
import Loading from '../components/Common/Loading';
import './Pages.css';

export default function Profile() {
  const [profile, setProfile] = useState(null);
  const [editing, setEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({});
  const { addToast } = useToast();

  const loadProfile = useCallback(async () => {
    try {
      const data = await authService.getProfile();
      setProfile(data);
      setFormData(data);
    } catch (error) {
      addToast('Failed to load profile', 'error');
    } finally {
      setLoading(false);
    }
  }, [addToast]);

  useEffect(() => {
    loadProfile();
  }, [loadProfile]);

  const handleSave = async (e) => {
    e.preventDefault();
    try {
      await authService.updateProfile(formData);
      setProfile(formData);
      setEditing(false);
      addToast('Profile updated successfully!', 'success');
    } catch (error) {
      addToast('Failed to update profile', 'error');
    }
  };

  if (loading) return <Loading />;

  return (
    <div className="page profile-page">
      <div className="page-header">
        <User size={40} strokeWidth={1.5} className="header-icon" />
        <h1>Your Profile</h1>
        <p>Manage your account settings</p>
      </div>

      <Card>
        {!editing ? (
          <div className="profile-view">
            <div className="profile-item">
              <span className="profile-label">Name:</span>
              <span className="profile-value">{profile?.name}</span>
            </div>
            <div className="profile-item">
              <span className="profile-label">Email:</span>
              <span className="profile-value">{profile?.email}</span>
            </div>
            <div className="profile-item">
              <span className="profile-label">Dietary Preferences:</span>
              <span className="profile-value">
                {profile?.dietary_preferences?.join(', ') || 'None'}
              </span>
            </div>
            <div className="profile-item">
              <span className="profile-label">Allergies:</span>
              <span className="profile-value">
                {profile?.allergies?.join(', ') || 'None'}
              </span>
            </div>
            <div className="profile-item">
              <span className="profile-label">Health Goals:</span>
              <span className="profile-value">
                {profile?.health_goals?.join(', ') || 'None'}
              </span>
            </div>
            <div style={{ marginTop: '24px' }}>
              <Button 
                onClick={() => setEditing(true)} 
                variant="secondary"
                icon={Edit2}
                full
              >
                Edit Profile
              </Button>
            </div>
          </div>
        ) : (
          <form onSubmit={handleSave} className="profile-edit">
            <div className="form-group">
              <label>Name</label>
              <input
                type="text"
                value={formData.name || ''}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                required
              />
            </div>
            
            <div className="form-group">
              <label>Dietary Preferences (comma separated)</label>
              <input
                type="text"
                value={formData.dietary_preferences?.join(', ') || ''}
                onChange={(e) => setFormData({
                  ...formData, 
                  dietary_preferences: e.target.value.split(',').map(s => s.trim()).filter(Boolean)
                })}
                placeholder="e.g., vegetarian, gluten-free"
              />
            </div>

            <div className="form-group">
              <label>Allergies (comma separated)</label>
              <input
                type="text"
                value={formData.allergies?.join(', ') || ''}
                onChange={(e) => setFormData({
                  ...formData, 
                  allergies: e.target.value.split(',').map(s => s.trim()).filter(Boolean)
                })}
                placeholder="e.g., peanuts, shellfish"
              />
            </div>

            <div className="form-group">
              <label>Health Goals (comma separated)</label>
              <input
                type="text"
                value={formData.health_goals?.join(', ') || ''}
                onChange={(e) => setFormData({
                  ...formData, 
                  health_goals: e.target.value.split(',').map(s => s.trim()).filter(Boolean)
                })}
                placeholder="e.g., weight loss, muscle gain"
              />
            </div>

            <div className="form-actions">
              <Button 
                type="submit"
                icon={Save}
                variant="primary"
              >
                Save Changes
              </Button>
              <Button 
                type="button" 
                variant="secondary"
                icon={X}
                onClick={() => {
                  setFormData(profile);
                  setEditing(false);
                }}
              >
                Cancel
              </Button>
            </div>
          </form>
        )}
      </Card>
    </div>
  );
}