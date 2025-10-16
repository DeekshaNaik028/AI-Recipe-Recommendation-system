// components/Layout/Sidebar.jsx
import './Layout.css';

export default function Sidebar({ isOpen }) {
  const navItems = [
    { icon: '🏠', label: 'Home', href: '/' },
    { icon: '🎯', label: 'Generate Recipe', href: '/generate' },
    { icon: '📚', label: 'History', href: '/history' },
    { icon: '❤️', label: 'Favorites', href: '/favorites' },
    { icon: '👤', label: 'Profile', href: '/profile' },
    { icon: '📊', label: 'Analytics', href: '/analytics' },
  ];

  return (
    <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
      <nav className="sidebar-nav">
        {navItems.map(item => (
          <a key={item.href} href={item.href} className="nav-item">
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.label}</span>
          </a>
        ))}
      </nav>
    </aside>
  );
}