import { useState, useEffect } from 'react';

export function useAuth() {
  const [user, setUser] = useState<{ id: string, name: string, role: string } | null>(null);

  useEffect(() => {
    const storedUser = localStorage.getItem('sentinel_user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
  }, []);

  const login = (userData: any, token: string) => {
    localStorage.setItem('sentinel_token', token);
    localStorage.setItem('sentinel_user', JSON.stringify(userData));
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem('sentinel_token');
    localStorage.removeItem('sentinel_user');
    setUser(null);
  };

  const checkPermission = (requiredRole: string) => {
    if (!user) return false;
    if (user.role === 'ADMIN') return true;
    return user.role === requiredRole;
  };

  return { user, login, logout, checkPermission };
}
