import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { getCurrentUser, logout } from '../utils/auth';
import './Home.css';

function Home() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);

  useEffect(() => {
    const currentUser = getCurrentUser();
    if (!currentUser) {
      navigate('/login');
      return;
    }
    setUser(currentUser);
  }, [navigate]);

  const handleLogout = () => {
    logout();
  };

  if (!user) {
    return <div>Loading...</div>;
  }

  return (
    <div className="home-container">
      <header className="home-header">
        <h1>Welkom bij RAcademic</h1>
        <div className="user-info">
          <span>Hallo, {user.display_name}!</span>
          <button onClick={handleLogout} className="logout-button">
            Uitloggen
          </button>
        </div>
      </header>
      <main className="home-content">
        <div className="welcome-section">
          <h2>Deel en Ontdek Studiebronnen</h2>
          <p>Maak contact met medestudenten en vind de beste studiematerialen voor je vakken.</p>
        </div>
        
        <div className="action-cards">
          <Link to="/bronnen" className="action-card">
            <div className="card-icon">📚</div>
            <h3>Bronnen Bekijken</h3>
            <p>Bekijk alle beschikbare bronnen</p>
          </Link>
          
          <Link to="/bronnen-toevoegen" className="action-card">
            <div className="card-icon">➕</div>
            <h3>Bron Toevoegen</h3>
            <p>Voeg een nieuwe bron toe</p>
          </Link>
          
          {user.is_admin && (
            <Link to="/admin" className="action-card admin-card">
              <div className="card-icon">⚙️</div>
              <h3>Admin Dashboard</h3>
              <p>Beheer gebruikers en geblokkeerde e-mails</p>
            </Link>
          )}
        </div>
        
        <div className="features-section">
          <h3>Wat je kunt doen:</h3>
          <ul className="features-list">
            <li>📖 Deel boeken, video's, artikelen en cursussen</li>
            <li>⭐ Beoordeel en review bronnen</li>
            <li>❤️ Sla je favoriete bronnen op</li>
            <li>🔍 Zoek en filter op type en categorie</li>
            <li>🏷️ Gebruik tags om content te organiseren</li>
          </ul>
        </div>
      </main>
    </div>
  );
}

export default Home; 