import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './Bronnen.css';

function Bronnen() {
  const [bronnen, setBronnen] = useState([]);
  const [loading, setLoading] = useState(true);
  const [zoekTerm, setZoekTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [categorieFilter, setCategorieFilter] = useState('');

  useEffect(() => {
    haalBronnenOp();
  }, [zoekTerm, typeFilter, categorieFilter]);

  const haalBronnenOp = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (zoekTerm) params.append('search', zoekTerm);
      if (typeFilter) params.append('type_filter', typeFilter);
      if (categorieFilter) params.append('category_filter', categorieFilter);
      const response = await fetch(`http://localhost:8000/bronnen?${params}`);
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

      <div className="filters-sectie">
        <div className="zoek-box">
          <input
            type="text"
            placeholder="Zoek in bronnen..."
            value={zoekTerm}
            onChange={(e) => setZoekTerm(e.target.value)}
            className="zoek-input"
          />
        </div>

        <div className="filter-controles">
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="filter-select"
          >
            <option value="">Alle Types</option>
            <option value="boek">Boeken</option>
            <option value="video">Video's</option>
            <option value="artikel">Artikelen</option>
            <option value="cursus">Cursussen</option>
          </select>

          <select
            value={categorieFilter}
            onChange={(e) => setCategorieFilter(e.target.value)}
            className="filter-select"
          >
            <option value="">Alle Categorieën</option>
            <option value="Programmeren">Programmeren</option>
            <option value="Wiskunde">Wiskunde</option>
            <option value="Design">Design</option>
            <option value="Bedrijfskunde">Bedrijfskunde</option>
            <option value="Wetenschap">Wetenschap</option>
          </select>
        </div>
      </div>

      <div className="bronnen-grid">
        {bronnen.length === 0 ? (
          <div className="geen-bronnen">
            <p>Geen bronnen gevonden.</p>
          </div>
        ) : (
          bronnen.map((bron) => (
            <div key={bron.id} className="bron-kaart">
              <h3 className="bron-titel">{bron.title}</h3>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default Bronnen;