import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { getAuthHeaders, handleApiError } from '../utils/auth';
import './BronToevoegen.css';

function BronToevoegen() {
  const navigate = useNavigate();
  const location = useLocation();
  const [isEditing, setIsEditing] = useState(false);
  const [editId, setEditId] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    url: '',
    type: 'boek',
    category: '',
    tags: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Check if we're editing an existing bron
  useEffect(() => {
    const urlParams = new URLSearchParams(location.search);
    const editData = urlParams.get('edit');
    
    if (editData) {
      try {
        const bron = JSON.parse(decodeURIComponent(editData));
        setFormData({
          title: bron.title || '',
          description: bron.description || '',
          url: bron.url || '',
          type: bron.type || 'boek',
          category: bron.category || '',
          tags: bron.tags || ''
        });
        setEditId(bron.id);
        setIsEditing(true);
      } catch (error) {
        console.error('Error parsing edit data:', error);
      }
    }
  }, [location.search]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const url = isEditing 
        ? `http://localhost:8000/bronnen/${editId}`
        : 'http://localhost:8000/bronnen';
      
      const method = isEditing ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method: method,
        headers: getAuthHeaders(),
        body: JSON.stringify(formData),
      });

      if (response.status === 401) {
        handleApiError({ status: 401 });
        return;
      }

      if (response.ok) {
        navigate('/bronnen');
      } else {
        const errorData = await response.json();
        setError(errorData.detail || `Fout bij ${isEditing ? 'bewerken' : 'aanmaken'} van bron`);
      }
    } catch (error) {
      setError('Netwerkfout. Probeer het opnieuw.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bron-toevoegen-container">
      <div className="bron-toevoegen-box">
        <header className="bron-toevoegen-header">
          <h1>{isEditing ? 'Bewerk Studiebron' : 'Deel een Studiebron'}</h1>
          <p>{isEditing ? 'Bewerk de details van je bron.' : 'Help je medestudenten door een bron te delen die jou heeft geholpen!'}</p>
        </header>

        <form onSubmit={handleSubmit} className="bron-toevoegen-form">
          <div className="form-group">
            <label htmlFor="title">Brontitel *</label>
            <input
              type="text"
              id="title"
              name="title"
              value={formData.title}
              onChange={handleChange}
              placeholder="bijv. React Tutorial voor Beginners"
              required
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="type">Brontype *</label>
            <div className="type-selector">
              {[
                { value: 'boek', label: 'Boek', icon: '📚' },
                { value: 'video', label: 'Video', icon: '🎥' },
                { value: 'artikel', label: 'Artikel', icon: '📄' },
                { value: 'cursus', label: 'Cursus', icon: '🎓' }
              ].map((type) => (
                <button
                  key={type.value}
                  type="button"
                  className={`type-option ${formData.type === type.value ? 'selected' : ''}`}
                  onClick={() => setFormData(prev => ({ ...prev, type: type.value }))}
                >
                  <span className="type-icon">{type.icon}</span>
                  <span className="type-label">{type.label}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="description">Beschrijving</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="Vermeld bij:
📘 Boek: de titel, ISBN en een korte samenvatting
🎥 Video: de speelduur en een korte inhoud
📰 Artikel/cursus: de hoofdpunten of wat je eruit hebt gehaald"
              rows="4"
              className="form-textarea"
            />
          </div>

          <div className="form-group">
            <label htmlFor="url">URL (Optioneel)</label>
            <input
              type="url"
              id="url"
              name="url"
              value={formData.url}
              onChange={handleChange}
              placeholder="https://SlavaOsipenko.com/Voorbeeld"
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="category">Categorie</label>
            <select
              id="category"
              name="category"
              value={formData.category}
              onChange={handleChange}
              className="form-select"
            >
              <option value="">Selecteer een categorie</option>
              <option value="Programmeren">Programmeren</option>
              <option value="Wiskunde">Wiskunde</option>
              <option value="Design">Design</option>
              <option value="Bedrijfskunde">Bedrijfskunde</option>
              <option value="Wetenschap">Wetenschap</option>
              <option value="Taal">Taal</option>
              <option value="Geschiedenis">Geschiedenis</option>
              <option value="Overig">Overig</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="tags">Tags (Optioneel)</label>
            <input
              type="text"
              id="tags"
              name="tags"
              value={formData.tags}
              onChange={handleChange}
              placeholder="react, javascript, tutorial (komma gescheiden)"
              className="form-input"
            />
            <small className="form-help">Scheid tags met komma's</small>
          </div>

          {error && <div className="error-message">{error}</div>}

          <div className="form-actions">
            <button
              type="button"
              onClick={() => navigate('/bronnen')}
              className="cancel-btn"
              disabled={loading}
            >
              Annuleren
            </button>
            <button
              type="submit"
              className="submit-btn"
              disabled={loading}
            >
              {loading ? (isEditing ? 'Bewerken...' : 'Bron Delen...') : (isEditing ? 'Bron Bewerken' : 'Bron Delen')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default BronToevoegen;