// src/App.jsx
import { useState, useEffect } from 'react';
import { useAuth } from './hooks/useAuth';
import './App.css';

// Layout
import Navbar from './components/Layout/Navbar';
import Sidebar from './components/Layout/Sidebar';
import Footer from './components/Layout/Footer';

// Pages
import Home from './pages/Home';
import GenerateRecipe from './pages/GenerateRecipe';
import History from './pages/History';
import Favorites from './pages/Favorites';
import Profile from './pages/Profile';
import Analytics from './pages/Analytics';
import Login from './components/Auth/Login';

// Common
import Toast from './components/Common/Toast';
import Loading from './components/Common/Loading';
import { useToast } from './hooks/useToast';

export default function App() {
  const [currentPage, setCurrentPage] = useState('home');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { isAuthenticated, loading } = useAuth();
  const { toasts, removeToast } = useToast();

  // Handle navigation
  useEffect(() => {
    const handleNavigation = (e) => {
      const href = e.target.closest('a')?.getAttribute('href');
      if (href && href.startsWith('/')) {
        e.preventDefault();
        const page = href.slice(1) || 'home';
        setCurrentPage(page);
        setSidebarOpen(false);
      }
    };

    document.addEventListener('click', handleNavigation);
    return () => document.removeEventListener('click', handleNavigation);
  }, []);

  // Close sidebar on route change
  useEffect(() => {
    setSidebarOpen(false);
  }, [currentPage]);

  const renderPage = () => {
    switch (currentPage) {
      case 'home':
        return <Home />;
      case 'generate':
        return <GenerateRecipe />;
      case 'history':
        return <History />;
      case 'favorites':
        return <Favorites />;
      case 'profile':
        return <Profile />;
      case 'analytics':
        return <Analytics />;
      default:
        return <Home />;
    }
  };

  if (loading) {
    return (
      <div className="app light">
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          minHeight: '100vh' 
        }}>
          <Loading />
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="app light">
        <Login />
        <div className="toast-container">
          {toasts.map(toast => (
            <Toast
              key={toast.id}
              message={toast.message}
              type={toast.type}
              onClose={() => removeToast(toast.id)}
            />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="app light">
      <Navbar 
        onMenuClick={() => setSidebarOpen(!sidebarOpen)} 
        currentPage={currentPage}
        onNavigate={setCurrentPage}
      />
      <div className="app-container">
        <Sidebar 
          isOpen={sidebarOpen} 
          currentPage={currentPage}
          onNavigate={setCurrentPage}
        />
        <main className="app-main">
          {renderPage()}
        </main>
      </div>
      <Footer />

      <div className="toast-container">
        {toasts.map(toast => (
          <Toast
            key={toast.id}
            message={toast.message}
            type={toast.type}
            onClose={() => removeToast(toast.id)}
          />
        ))}
      </div>
    </div>
  );
}