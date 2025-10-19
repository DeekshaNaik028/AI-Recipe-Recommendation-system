// src/components/Layout/Navbar.jsx - UPDATED
import { useState, useRef, useEffect } from 'react';
import { Menu, LogOut, Settings, Moon, Sun, User, ChefHat } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import { useTheme } from '../../hooks/useTheme';
import './Layout.css';

export default function Navbar({ onMenuClick, currentPage, onNavigate }) {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

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
          <button 
            className="menu-button" 
            onClick={onMenuClick}
            aria-label="Toggle menu"
          >
            <Menu size={24} strokeWidth={2} />
          </button>
          <div 
            className="nav-brand"
            onClick={() => handleNavigation('home')}
            style={{ cursor: 'pointer' }}
          >
            <ChefHat className="brand-icon" size={32} strokeWidth={2} />
            <span className="brand-name">MoodMunch</span>
          </div>
        </div>

        <div className="nav-right">
          <button 
            className="theme-toggle"
            onClick={toggleTheme}
            aria-label="Toggle theme"
            title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
          >
            {theme === 'light' ? <Moon size={20} strokeWidth={2} /> : <Sun size={20} strokeWidth={2} />}
          </button>
          
          <div className="dropdown" ref={dropdownRef}>
            <button 
              className="user-button"
              onClick={() => setDropdownOpen(!dropdownOpen)}
            >
              <User size={18} strokeWidth={2} />
              <span>{user?.name || 'User'}</span>
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
                  <Settings size={16} strokeWidth={2} />
                  Profile
                </a>
                <button 
                  onClick={() => { 
                    logout(); 
                    setDropdownOpen(false); 
                  }}
                >
                  <LogOut size={16} strokeWidth={2} />
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