// components/Layout/Navbar.jsx
import { useState, useRef, useEffect } from 'react';
import { useAuth } from '../../hooks/useAuth';
import ThemeToggle from '../Theme/ThemeToggle';
import './Layout.css';

export default function Navbar({ onMenuClick, currentPage, onNavigate }) {
  const { user, logout } = useAuth();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setDropdownOpen(false);
      }
    };

    if (dropdownOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [dropdownOpen]);

  const handleNavigation = (page) => {
    if (onNavigate) {
      onNavigate(page);
    }
    setDropdownOpen(false);
  };

  return (
    <nav className="navbar">
      <div className="nav-content">
        <div className="nav-left">
          <button className="menu-button" onClick={onMenuClick}>☰</button>
          <div 
            className="nav-brand"
            onClick={() => handleNavigation('home')}
            style={{ cursor: 'pointer' }}
          >
            <span className="brand-icon">🍳</span>
            <span className="brand-name">MoodMunch</span>
          </div>
        </div>

        <div className="nav-right">
          <ThemeToggle />
          
          <div className="dropdown" ref={dropdownRef}>
            <button 
              className="user-button"
              onClick={() => setDropdownOpen(!dropdownOpen)}
            >
              👤 {user?.name || 'User'}
            </button>
            
            {dropdownOpen && (
              <div className="dropdown-menu">
                <a 
                  href="/profile" 
                  onClick={(e) => {
                    e.preventDefault();
                    handleNavigation('profile');
                  }}
                >
                  Profile
                </a>
                <a 
                  href="/analytics" 
                  onClick={(e) => {
                    e.preventDefault();
                    handleNavigation('analytics');
                  }}
                >
                  Analytics
                </a>
                <button 
                  onClick={() => { 
                    logout(); 
                    setDropdownOpen(false); 
                  }}
                >
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