import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { getCurrentUser, getAuthHeaders, handleApiError } from '../utils/auth';
import './Account.css';

function Account() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [formData, setFormData] = useState({
    display_name: '',
    current_password: '',
    new_password: '',
    confirm_password: ''
  });
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const currentUser = getCurrentUser();
    if (!currentUser) {
      navigate('/login');
      return;
    }
    setUser(currentUser);
    setFormData(prev => ({
      ...prev,
      display_name: currentUser.display_name || ''
    }));
  }, [navigate]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleUpdateName = async (e) => {
    e.preventDefault();
    if (!formData.display_name.trim()) {
      setMessage('Naam mag niet leeg zijn');
      return;
    }

    setIsLoading(true);
    setMessage('');

    try {
      const response = await fetch('/api/user/update-name', {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          display_name: formData.display_name.trim()
        })
      });

      if (response.ok) {
        const updatedUser = { ...user, display_name: formData.display_name.trim() };
        localStorage.setItem('user', JSON.stringify(updatedUser));
        setUser(updatedUser);
        setMessage('Naam succesvol bijgewerkt!');
        setFormData(prev => ({
          ...prev,
          display_name: formData.display_name.trim()
        }));
      } else {
        const error = await response.json();
        setMessage(error.message || 'Er is een fout opgetreden');
      }
    } catch (error) {
      setMessage('Er is een fout opgetreden bij het bijwerken van je naam');
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdatePassword = async (e) => {
    e.preventDefault();
    if (!formData.current_password || !formData.new_password || !formData.confirm_password) {
      setMessage('Vul alle wachtwoordvelden in');
      return;
    }

    if (formData.new_password !== formData.confirm_password) {
      setMessage('Nieuwe wachtwoorden komen niet overeen');
      return;
    }

    if (formData.new_password.length < 6) {
      setMessage('Nieuw wachtwoord moet minimaal 6 karakters lang zijn');
      return;
    }

    setIsLoading(true);
    setMessage('');

    try {
      const response = await fetch('/api/user/update-password', {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          current_password: formData.current_password,
          new_password: formData.new_password
        })
      });

      if (response.ok) {
        setMessage('Wachtwoord succesvol bijgewerkt!');
        setFormData(prev => ({
          ...prev,
          current_password: '',
          new_password: '',
          confirm_password: ''
        }));
      } else {
        const error = await response.json();
        setMessage(error.message || 'Er is een fout opgetreden');
      }
    } catch (error) {
      setMessage('Er is een fout opgetreden bij het bijwerken van je wachtwoord');
    } finally {
      setIsLoading(false);
    }
  };

  if (!user) {
    return <div>Loading...</div>;
  }

  return (
    <div className="account-container">
      <header className="account-header">
        <h1>Account Instellingen</h1>
        <Link to="/home" className="back-button">
          ← Terug naar Home
        </Link>
      </header>

      <main className="account-content">
        {message && (
          <div className={`message ${message.includes('succesvol') ? 'success' : 'error'}`}>
            {message}
          </div>
        )}

        <div className="account-section">
          <h2>Profiel Informatie</h2>
          <div className="info-item">
            <label>Email:</label>
            <span>{user.email}</span>
          </div>
        </div>

        <div className="account-section">
          <h2>Naam Wijzigen</h2>
          <form onSubmit={handleUpdateName} className="account-form">
            <div className="form-group">
              <label htmlFor="display_name">Naam:</label>
              <input
                type="text"
                id="display_name"
                name="display_name"
                value={formData.display_name}
                onChange={handleInputChange}
                placeholder="Jouw naam"
                required
              />
            </div>
            <button 
              type="submit" 
              className="update-button"
              disabled={isLoading}
            >
              {isLoading ? 'Bezig...' : 'Naam Bijwerken'}
            </button>
          </form>
        </div>

        <div className="account-section">
          <h2>Wachtwoord Wijzigen</h2>
          <form onSubmit={handleUpdatePassword} className="account-form">
            <div className="form-group">
              <label htmlFor="current_password">Huidig Wachtwoord:</label>
              <input
                type="password"
                id="current_password"
                name="current_password"
                value={formData.current_password}
                onChange={handleInputChange}
                placeholder="Huidig wachtwoord"
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="new_password">Nieuw Wachtwoord:</label>
              <input
                type="password"
                id="new_password"
                name="new_password"
                value={formData.new_password}
                onChange={handleInputChange}
                placeholder="Nieuw wachtwoord (min. 6 karakters)"
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="confirm_password">Bevestig Nieuw Wachtwoord:</label>
              <input
                type="password"
                id="confirm_password"
                name="confirm_password"
                value={formData.confirm_password}
                onChange={handleInputChange}
                placeholder="Bevestig nieuw wachtwoord"
                required
              />
            </div>
            <button 
              type="submit" 
              className="update-button"
              disabled={isLoading}
            >
              {isLoading ? 'Bezig...' : 'Wachtwoord Bijwerken'}
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}

export default Account; 