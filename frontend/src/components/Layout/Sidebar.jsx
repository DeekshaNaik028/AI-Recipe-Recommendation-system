import { Home, Zap, BookOpen, Heart, User, BarChart3 } from 'lucide-react';
import './Layout.css';

export default function Sidebar({ isOpen, currentPage, onNavigate }) {
  const navItems = [
    { icon: Home, label: 'Home', page: 'home' },
    { icon: Zap, label: 'Generate Recipe', page: 'generate' },
    { icon: BookOpen, label: 'History', page: 'history' },
    { icon: Heart, label: 'Favorites', page: 'favorites' },
    { icon: User, label: 'Profile', page: 'profile' },
    { icon: BarChart3, label: 'Analytics', page: 'analytics' },
  ];

  const handleClick = (page) => {
    if (onNavigate) {
      onNavigate(page);
    }
  };

  return (
    <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
      <nav className="sidebar-nav">
        {navItems.map(item => {
          const IconComponent = item.icon;
          return (
            <a 
              key={item.page} 
              href={`/${item.page === 'home' ? '' : item.page}`}
              className={`nav-item ${currentPage === item.page ? 'active' : ''}`}
              onClick={(e) => {
                e.preventDefault();
                handleClick(item.page);
              }}
            >
              <IconComponent className="nav-icon" size={20} strokeWidth={2} />
              <span className="nav-label">{item.label}</span>
            </a>
          );
        })}
      </nav>
    </aside>
  );
}