import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './Bronnen.css';

function Bronnen() {
  const [bronnen, setBronnen] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    haalBronnenOp();
  }, []);

  const haalBronnenOp = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/bronnen');
      if (response.ok) {
        const data = await response.json();
        setBronnen(data);
      } else {
        console.error('Fout bij ophalen van bronnen');
      }
    } catch (error) {
      console.error('Fout bij ophalen van bronnen:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="bronnen-container">Bronnen laden...</div>;
  }

  return (
    <div className="bronnen-container">
      <header className="bronnen-header">
        <h1>Studiebronnen</h1>
        <Link to="/bron-toevoegen" className="bron-toevoegen-btn">
          + Bron Toevoegen
        </Link>
      </header>
      <div className="bronnen-grid">
        {bronnen.length === 0 ? (
          <div className="geen-bronnen">
            <p>Geen bronnen gevonden. Wees de eerste om een bron te delen!</p>
          </div>
        ) : (
          bronnen.map((bron) => (
            <div key={bron.id} className="bron-kaart">
              <div className="bron-header">
                <span className="bron-type-icoon">📖</span>
                <span className="bron-type">{bron.type}</span>
              </div>
              <h3 className="bron-titel">{bron.title}</h3>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default Bronnen;