// components/Layout/Sidebar.jsx
import './Layout.css';

export default function Sidebar({ isOpen, currentPage, onNavigate }) {
  const navItems = [
    { icon: '🏠', label: 'Home', page: 'home' },
    { icon: '🎯', label: 'Generate Recipe', page: 'generate' },
    { icon: '📚', label: 'History', page: 'history' },
    { icon: '❤️', label: 'Favorites', page: 'favorites' },
    { icon: '👤', label: 'Profile', page: 'profile' },
    { icon: '📊', label: 'Analytics', page: 'analytics' },
  ];

  const handleClick = (page) => {
    if (onNavigate) {
      onNavigate(page);
    }
  };

  return (
    <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
      <nav className="sidebar-nav">
        {navItems.map(item => (
          <a 
            key={item.page} 
            href={`/${item.page === 'home' ? '' : item.page}`}
            className={`nav-item ${currentPage === item.page ? 'active' : ''}`}
            onClick={(e) => {
              e.preventDefault();
              handleClick(item.page);
            }}
          >
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.label}</span>
          </a>
        ))}
      </nav>
    </aside>
  );
}