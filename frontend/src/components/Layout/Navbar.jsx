// components/Layout/Navbar.jsx
import { useState } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { useTheme } from '../../hooks/useTheme';
import ThemeToggle from '../Theme/ThemeToggle';
import './Layout.css';

export default function Navbar({ onMenuClick }) {
  const { user, logout } = useAuth();
  const [dropdownOpen, setDropdownOpen] = useState(false);

  return (
    <nav className="navbar">
      <div className="nav-content">
        <div className="nav-left">
          <button className="menu-button" onClick={onMenuClick}>☰</button>
          <div className="nav-brand">
            <span className="brand-icon">🍳</span>
            <span className="brand-name">MoodMunch</span>
          </div>
        </div>

        <div className="nav-right">
          <ThemeToggle />
          
          <div className="dropdown">
            <button 
              className="user-button"
              onClick={() => setDropdownOpen(!dropdownOpen)}
            >
              👤 {user?.name || 'User'}
            </button>
            
            {dropdownOpen && (
              <div className="dropdown-menu">
                <a href="/profile">Profile</a>
                <a href="/analytics">Analytics</a>
                <button onClick={() => { logout(); setDropdownOpen(false); }}>
                  Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}