// Authentication utility functions

export const getAuthHeaders = () => {
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${user.access_token}`
  };
};

export const isAuthenticated = () => {
  const user = localStorage.getItem('user');
  if (!user) return false;
  
  try {
    const parsedUser = JSON.parse(user);
    return !!(parsedUser.access_token);
  } catch {
    return false;
  }
};

export const getCurrentUser = () => {
  const user = localStorage.getItem('user');
  if (!user) return null;
  
  try {
    return JSON.parse(user);
  } catch {
    return null;
  }
};

export const logout = () => {
  localStorage.removeItem('user');
  window.location.href = '/login';
};

export const handleApiError = (error) => {
  if (error.status === 401) {
    logout();
    return;
  }
  throw error;
}; 