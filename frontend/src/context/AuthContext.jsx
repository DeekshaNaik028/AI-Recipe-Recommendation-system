import { createContext, useState, useCallback } from 'react';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [auth, setAuth] = useState({
    isAuthenticated: false,
    user: null,
    token: null,
    loading: true,
  });

  const login = useCallback((user, token) => {
    setAuth({ isAuthenticated: true, user, token, loading: false });
    localStorage.setItem('access_token', token);
  }, []);

  const logout = useCallback(() => {
    setAuth({ isAuthenticated: false, user: null, token: null, loading: false });
    localStorage.removeItem('access_token');
  }, []);

  return (
    <AuthContext.Provider value={{ ...auth, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;