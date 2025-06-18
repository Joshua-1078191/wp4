import React, { useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import './Home.css';

function Home() {
  const navigate = useNavigate();

  useEffect(() => {
    const user = localStorage.getItem('user');
    if (!user) {
      navigate('/login');
    }
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('user');
    navigate('/login');
  };

  return (
    <div className="home-container">
      <header className="home-header">
        <h1>Welkom bij RAcademic</h1>
        <button onClick={handleLogout} className="logout-button">
          Uitloggen
        </button>
      </header>
      <main className="home-content">
      <div className="welcome-section">
          <h2>Deel en Ontdek Studiebronnen</h2>
          <p>Maak contact met medestudenten en vind de beste studiematerialen voor je vakken.</p>
        </div>
        
        <div className="action-cards">
          <Link to="/bronnen" className="action-card">
            <div className="card-icon">📚</div>
            <h3>Bekijk Bronnen</h3>
            <p>Ontdek studiematerialen gedeeld door andere studenten</p>
          </Link>
          
          <Link to="/bron-toevoegen" className="action-card">
            <div className="card-icon">➕</div>
            <h3>Deel Bron</h3>
            <p>Help anderen door een bron te delen die jou heeft geholpen</p>
          </Link>
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