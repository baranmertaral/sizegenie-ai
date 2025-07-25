import React, { useState } from 'react';
import './App.css';

interface SizeRequest {
  user_height: number;
  user_weight: number;
  product_name: string;
  product_size: string;
  brand: string;
}

function App() {
  const [formData, setFormData] = useState<SizeRequest>({
    user_height: 175,
    user_weight: 70,
    product_name: '',
    product_size: 'M',
    brand: ''
  });
  
  const [result, setResult] = useState<any>(null);
  const [photoResult, setPhotoResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [photoLoading, setPhotoLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await fetch('http://localhost:8000/analyze-size', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePhotoUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    setPhotoLoading(true);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch('http://localhost:8000/analyze-photo', {
        method: 'POST',
        body: formData,
      });
      
      const data = await response.json();
      setPhotoResult(data);
    } catch (error) {
      console.error('Photo analysis error:', error);
    } finally {
      setPhotoLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🎯 SizeGenie AI</h1>
        <p>AI-powered clothing size recommendation with photo analysis</p>
        
        {/* Fotoğraf Analizi Bölümü */}
        <div className="photo-section">
          <h2>📸 Fotoğraf Analizi</h2>
          <p>Vücut tipinizi analiz etmek için fotoğrafınızı yükleyin</p>
          <input
            type="file"
            accept="image/*"
            onChange={handlePhotoUpload}
            className="photo-input"
          />
          {photoLoading && <p className="loading">🤖 Fotoğraf analiz ediliyor...</p>}
          
          {photoResult && (
            <div className="result photo-result">
              <h3>📊 Vücut Analizi:</h3>
              <pre>{photoResult.analysis}</pre>
            </div>
          )}
        </div>
        
        {/* Beden Analizi Formu */}
        <form onSubmit={handleSubmit} className="size-form">
          <h2>👕 Beden Analizi</h2>
          
          <div className="form-group">
            <label>Boy (cm):</label>
            <input
              type="number"
              value={formData.user_height}
              onChange={(e) => setFormData({...formData, user_height: Number(e.target.value)})}
            />
          </div>
          
          <div className="form-group">
            <label>Kilo (kg):</label>
            <input
              type="number"
              value={formData.user_weight}
              onChange={(e) => setFormData({...formData, user_weight: Number(e.target.value)})}
            />
          </div>
          
          <div className="form-group">
            <label>Marka:</label>
            <input
              type="text"
              value={formData.brand}
              onChange={(e) => setFormData({...formData, brand: e.target.value})}
              placeholder="örn: Zara, H&M, Nike"
            />
          </div>
          
          <div className="form-group">
            <label>Ürün:</label>
            <input
              type="text"
              value={formData.product_name}
              onChange={(e) => setFormData({...formData, product_name: e.target.value})}
              placeholder="örn: Basic T-Shirt, Jeans"
            />
          </div>
          
          <div className="form-group">
            <label>Beden:</label>
            <select
              value={formData.product_size}
              onChange={(e) => setFormData({...formData, product_size: e.target.value})}
            >
              <option value="XS">XS</option>
              <option value="S">S</option>
              <option value="M">M</option>
              <option value="L">L</option>
              <option value="XL">XL</option>
              <option value="XXL">XXL</option>
            </select>
          </div>
          
          <button type="submit" disabled={loading}>
            {loading ? '🤖 AI Analiz Ediyor...' : '🎯 Bedeni Analiz Et'}
          </button>
        </form>
        
        {result && (
          <div className="result">
            <h3>📊 AI Önerisi:</h3>
            <pre>{result.recommendation}</pre>
          </div>
        )}
      </header>
    </div>
  );
}

export default App;
