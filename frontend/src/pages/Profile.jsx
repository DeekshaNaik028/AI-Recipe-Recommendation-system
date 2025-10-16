// pages/Profile.jsx
import { useEffect, useState } from 'react';
import { authService } from '../services/authService';
import { useToast } from '../hooks/useToast';
import Card from '../components/Common/Card';
import Button from '../components/Common/Button';
import './Pages.css';

export default function Profile() {
  const [profile, setProfile] = useState(null);
  const [editing, setEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({});
  const { addToast } = useToast();

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const data = await authService.getProfile();
      setProfile(data);
      setFormData(data);
    } catch (error) {
      addToast('Failed to load profile', 'error');
    } finally {
      setLoading(false);
    }
  };

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

  if (loading) return <div>Loading...</div>;

  return (
    <div className="page profile-page">
      <div className="page-header">
        <h1>Your Profile 👤</h1>
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
            <Button onClick={() => setEditing(true)} variant="secondary">
              ✏️ Edit Profile
            </Button>
          </div>
        ) : (
          <form onSubmit={handleSave} className="profile-edit">
            <div className="form-group">
              <label>Name</label>
              <input
                type="text"
                value={formData.name || ''}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
              />
            </div>
            <div className="form-actions">
              <Button type="submit">Save Changes</Button>
              <Button 
                type="button" 
                variant="secondary"
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