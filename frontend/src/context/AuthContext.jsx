// src/context/AuthContext.jsx
import { createContext, useState, useCallback, useEffect } from 'react';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [auth, setAuth] = useState({
    isAuthenticated: false,
    user: null,
    token: null,
    loading: true,
  });

  // Initialize auth state on mount
  useEffect(() => {
    const initAuth = () => {
      const token = localStorage.getItem('access_token');
      const user = localStorage.getItem('user');
      
      if (token && user) {
        try {
          setAuth({
            isAuthenticated: true,
            user: JSON.parse(user),
            token,
            loading: false,
          });
        } catch (error) {
          console.error('Failed to parse user data:', error);
          localStorage.removeItem('access_token');
          localStorage.removeItem('user');
          setAuth({
            isAuthenticated: false,
            user: null,
            token: null,
            loading: false,
          });
        }
      } else {
        setAuth({
          isAuthenticated: false,
          user: null,
          token: null,
          loading: false,
        });
      }
    };

    initAuth();
  }, []);

  const login = useCallback((user, token) => {
    setAuth({ isAuthenticated: true, user, token, loading: false });
    localStorage.setItem('access_token', token);
    localStorage.setItem('user', JSON.stringify(user));
  }, []);

  const logout = useCallback(() => {
    setAuth({ isAuthenticated: false, user: null, token: null, loading: false });
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  }, []);

  return (
    <AuthContext.Provider value={{ ...auth, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;