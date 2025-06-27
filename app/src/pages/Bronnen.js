import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { getAuthHeaders, handleApiError } from '../utils/auth';
import './Bronnen.css';

function Bronnen() {
  const [bronnen, setBronnen] = useState([]);
  const [loading, setLoading] = useState(true);
  const [zoekTerm, setZoekTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [categorieFilter, setCategorieFilter] = useState('');
  const [pendingZoekTerm, setPendingZoekTerm] = useState('');
  const [pendingTypeFilter, setPendingTypeFilter] = useState('');
  const [pendingCategorieFilter, setPendingCategorieFilter] = useState('');

  const haalBronnenOp = useCallback(async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (zoekTerm) params.append('search', zoekTerm);
      if (typeFilter) params.append('type_filter', typeFilter);
      if (categorieFilter) params.append('category_filter', categorieFilter);

      const response = await fetch(`http://localhost:8000/bronnen?${params}`, {
        headers: getAuthHeaders()
      });
      
      if (response.status === 401) {
        handleApiError({ status: 401 });
        return;
      }
      
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
  }, [zoekTerm, typeFilter, categorieFilter]);

  useEffect(() => {
    haalBronnenOp();
  }, [haalBronnenOp]);

  const handleBeoordeel = async (bronId, beoordeling) => {
    try {
      const response = await fetch(`http://localhost:8000/bronnen/${bronId}/beoordeel`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ rating: beoordeling }),
      });
      
      if (response.status === 401) {
        handleApiError({ status: 401 });
        return;
      }
      
      if (response.ok) {
        haalBronnenOp();
      }
    } catch (error) {
      console.error('Fout bij beoordelen van bron:', error);
    }
  };

  const handleFavoriet = async (bronId) => {
    try {
      const response = await fetch(`http://localhost:8000/bronnen/${bronId}/favoriet`, {
        method: 'POST',
        headers: getAuthHeaders(),
      });
      
      if (response.status === 401) {
        handleApiError({ status: 401 });
        return;
      }
      
      if (response.ok) {
        haalBronnenOp();
      }
    } catch (error) {
      console.error('Fout bij favoriet toevoegen:', error);
    }
  };

  const handleDelete = async (bronId) => {
    if (!window.confirm('Weet je zeker dat je deze bron wilt verwijderen?')) {
      return;
    }
    
    try {
      const response = await fetch(`http://localhost:8000/bronnen/${bronId}`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
      });
      
      if (response.status === 401) {
        handleApiError({ status: 401 });
        return;
      }
      
      if (response.ok) {
        haalBronnenOp();
      } else {
        const data = await response.json();
        alert(data.detail || 'Fout bij verwijderen van bron');
      }
    } catch (error) {
      console.error('Fout bij verwijderen van bron:', error);
      alert('Fout bij verwijderen van bron');
    }
  };

  const handleEdit = (bron) => {
    // Navigate to edit page with bron data
    const bronData = encodeURIComponent(JSON.stringify(bron));
    window.location.href = `/bron-toevoegen?edit=${bronData}`;
  };

  const getTypeIcoon = (type) => {
    switch (type) {
      case 'boek': return '📚';
      case 'video': return '🎥';
      case 'artikel': return '📄';
      case 'cursus': return '🎓';
      default: return '📖';
    }
  };

  const renderSterren = (gemiddeldeBeoordeling) => {
    if (!gemiddeldeBeoordeling) return 'Nog geen beoordelingen';
    const sterren = '⭐'.repeat(Math.round(gemiddeldeBeoordeling));
    return `${sterren} (${gemiddeldeBeoordeling.toFixed(1)})`;
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
          <div className="filter-controles">
            <input
              type="text"
              placeholder="Zoek in bronnen..."
              value={pendingZoekTerm}
              onChange={(e) => setPendingZoekTerm(e.target.value)}
              className="zoek-input"
            />
            <select
              value={pendingTypeFilter}
              onChange={(e) => setPendingTypeFilter(e.target.value)}
              className="filter-select"
            >
              <option value="">Alle Types</option>
              <option value="boek">Boeken</option>
              <option value="video">Video's</option>
              <option value="artikel">Artikelen</option>
              <option value="cursus">Cursussen</option>
            </select>
            <select
              value={pendingCategorieFilter}
              onChange={(e) => setPendingCategorieFilter(e.target.value)}
              className="filter-select"
            >
              <option value="">Alle Categorieën</option>
              <option value="Programmeren">Programmeren</option>
              <option value="Wiskunde">Wiskunde</option>
              <option value="Design">Design</option>
              <option value="Bedrijfskunde">Bedrijfskunde</option>
              <option value="Wetenschap">Wetenschap</option>
            </select>
            <button
              className="zoek-btn"
              onClick={() => {
                setZoekTerm(pendingZoekTerm);
                setTypeFilter(pendingTypeFilter);
                setCategorieFilter(pendingCategorieFilter);
              }}
            >
              Zoek
            </button>
          </div>
        </div>
      </div>

      <div className="bronnen-grid">
        {bronnen.length === 0 ? (
          <div className="geen-bronnen">
            <p>Geen bronnen gevonden. Wees de eerste om een bron te delen!</p>
          </div>
        ) : (
          bronnen.map((bron) => (
            <div key={bron.id} className="bron-kaart">
              <div className="bron-header">
                <span className="bron-type-icoon">{getTypeIcoon(bron.type)}</span>
                <span className="bron-type">{bron.type}</span>
              </div>
              
              <h3 className="bron-titel">{bron.title}</h3>
              
              {bron.description && (
                <p className="bron-beschrijving">{bron.description}</p>
              )}
              
              <div className="bron-meta">
                <span className="bron-auteur">door {bron.user_display_name}</span>
                <span className="bron-datum">
                  {new Date(bron.created_at).toLocaleDateString('nl-NL')}
                </span>
              </div>
              
              {bron.category && (
                <span className="bron-categorie">{bron.category}</span>
              )}
              
              {bron.tags && (
                <div className="bron-tags">
                  {bron.tags.split(',').map((tag, index) => (
                    <span key={index} className="tag">{tag.trim()}</span>
                  ))}
                </div>
              )}
              
              <div className="bron-statistieken">
                <div className="beoordeling-sectie">
                  <span className="beoordeling-tekst">{renderSterren(bron.average_rating)}</span>
                  <span className="beoordeling-aantal">({bron.ratings_count} beoordelingen)</span>
                </div>
                <div className="favorieten-sectie">
                  <span className="favorieten-aantal">❤️ {bron.favorites_count}</span>
                </div>
              </div>
              
              <div className="bron-acties">
                <div className="beoordeling-knoppen">
                  {[1, 2, 3, 4, 5].map((beoordeling) => (
                    <button
                      key={beoordeling}
                      onClick={() => handleBeoordeel(bron.id, beoordeling)}
                      className="beoordeling-btn"
                    >
                      {beoordeling}
                    </button>
                  ))}
                </div>
                
                <button
                  onClick={() => handleFavoriet(bron.id)}
                  className={`favoriet-btn ${bron.is_favorited ? 'favoriet' : ''}`}
                >
                  {bron.is_favorited ? '❤️' : '🤍'} Favoriet
                </button>
                
                {bron.url && (
                  <a
                    href={bron.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="bekijk-bron-btn"
                  >
                    Bekijk Bron
                  </a>
                )}

                {/* Edit and Delete buttons */}
                <div className="bron-owner-actions">
                  {bron.can_edit && (
                    <button
                      onClick={() => handleEdit(bron)}
                      className="edit-bron-btn"
                    >
                      ✏️ Bewerken
                    </button>
                  )}
                  
                  {bron.can_delete && (
                    <button
                      onClick={() => handleDelete(bron.id)}
                      className="delete-bron-btn"
                    >
                      🗑️ Verwijderen
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default Bronnen; 