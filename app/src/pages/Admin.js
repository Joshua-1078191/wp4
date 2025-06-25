import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Admin.css';

const Admin = () => {
  const [activeTab, setActiveTab] = useState('blocked');
  const [blockedEmails, setBlockedEmails] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Form states
  const [blockEmail, setBlockEmail] = useState('');
  const [blockReason, setBlockReason] = useState('');
  const [unblockEmail, setUnblockEmail] = useState('');
  const [newAdminEmail, setNewAdminEmail] = useState('');
  const [newAdminPassword, setNewAdminPassword] = useState('');
  const [newAdminName, setNewAdminName] = useState('');

  const navigate = useNavigate();

  useEffect(() => {
    fetchData();
  }, [activeTab]);

  const fetchData = async () => {
    setLoading(true);
    setError('');
    
    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const token = user.access_token;
      
      if (activeTab === 'blocked') {
        const response = await fetch('http://localhost:8000/admin/blocked-emails', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          setBlockedEmails(data);
        } else {
          throw new Error('Failed to fetch blocked emails');
        }
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleBlockEmail = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const token = user.access_token;
      const response = await fetch('http://localhost:8000/admin/block-email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          email: blockEmail,
          reason: blockReason
        })
      });

      if (response.ok) {
        setSuccess('Email blocked successfully');
        setBlockEmail('');
        setBlockReason('');
        fetchData();
      } else {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to block email');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleUnblockEmail = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const token = user.access_token;
      const response = await fetch('http://localhost:8000/admin/unblock-email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          email: unblockEmail
        })
      });

      if (response.ok) {
        setSuccess('Email unblocked successfully');
        setUnblockEmail('');
        fetchData();
      } else {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to unblock email');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAdmin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const token = user.access_token;
      const response = await fetch('http://localhost:8000/admin/create-admin', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          email: newAdminEmail,
          password: newAdminPassword,
          display_name: newAdminName
        })
      });

      if (response.ok) {
        setSuccess('Admin account created successfully');
        setNewAdminEmail('');
        setNewAdminPassword('');
        setNewAdminName('');
        fetchData();
      } else {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to create admin account');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  return (
    <div className="admin-container">
      <header className="admin-header">
        <h1>Admin Dashboard</h1>
        <button onClick={handleLogout} className="logout-btn">Uitloggen</button>
      </header>
      
      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}

      <div className="admin-tabs">
        <button 
          className={`tab-btn ${activeTab === 'blocked' ? 'active' : ''}`}
          onClick={() => setActiveTab('blocked')}
        >
          Geblokkeerde E-mails
        </button>
        <button 
          className={`tab-btn ${activeTab === 'actions' ? 'active' : ''}`}
          onClick={() => setActiveTab('actions')}
        >
          Admin Acties
        </button>
      </div>

      <div className="admin-content">
        {loading && <div className="loading">Laden...</div>}

        {activeTab === 'blocked' && (
          <div className="blocked-section">
            <h2>Geblokkeerde E-mails</h2>
            <div className="blocked-list">
              {blockedEmails.map(blocked => (
                <div key={blocked.id} className="blocked-card">
                  <div className="blocked-info">
                    <h3>{blocked.email}</h3>
                    <p>Geblokkeerd door: {blocked.blocked_by_name}</p>
                    <p>Datum: {new Date(blocked.blocked_at).toLocaleDateString()}</p>
                    {blocked.reason && <p>Reden: {blocked.reason}</p>}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'actions' && (
          <div className="actions-section">
            <div className="action-card">
              <h3>E-mail Blokkeren</h3>
              <form onSubmit={handleBlockEmail}>
                <input
                  type="email"
                  placeholder="E-mailadres (@hr.nl)"
                  value={blockEmail}
                  onChange={(e) => setBlockEmail(e.target.value)}
                  required
                />
                <textarea
                  placeholder="Reden voor blokkeren (optioneel)"
                  value={blockReason}
                  onChange={(e) => setBlockReason(e.target.value)}
                />
                <button type="submit" disabled={loading}>
                  {loading ? 'Bezig...' : 'E-mail Blokkeren'}
                </button>
              </form>
            </div>

            <div className="action-card">
              <h3>E-mail Deblokkeren</h3>
              <form onSubmit={handleUnblockEmail}>
                <input
                  type="email"
                  placeholder="E-mailadres"
                  value={unblockEmail}
                  onChange={(e) => setUnblockEmail(e.target.value)}
                  required
                />
                <button type="submit" disabled={loading}>
                  {loading ? 'Bezig...' : 'E-mail Deblokkeren'}
                </button>
              </form>
            </div>

            <div className="action-card">
              <h3>Admin Account Aanmaken</h3>
              <form onSubmit={handleCreateAdmin}>
                <input
                  type="email"
                  placeholder="E-mailadres (@hr.nl)"
                  value={newAdminEmail}
                  onChange={(e) => setNewAdminEmail(e.target.value)}
                  required
                />
                <input
                  type="text"
                  placeholder="Naam"
                  value={newAdminName}
                  onChange={(e) => setNewAdminName(e.target.value)}
                  required
                />
                <input
                  type="password"
                  placeholder="Wachtwoord"
                  value={newAdminPassword}
                  onChange={(e) => setNewAdminPassword(e.target.value)}
                  required
                />
                <button type="submit" disabled={loading}>
                  {loading ? 'Bezig...' : 'Admin Aanmaken'}
                </button>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Admin; 