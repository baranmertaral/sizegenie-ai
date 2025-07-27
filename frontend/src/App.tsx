import React, { useState } from 'react';
import './App.css';

interface SizeRequest {
  user_height: number;
  user_weight: number;
  product_name: string;
  product_size: string;
  brand: string;
}

interface Product {
  name: string;
  price: string;
  image: string;
  url: string;
  brand: string;
}

type AnalysisType = 'home' | 'photo' | 'size';

function App() {
  // Ana state - hangi sayfada olduğumuzu takip eder
  const [currentPage, setCurrentPage] = useState<AnalysisType>('home');
  
  // Existing states
  const [formData, setFormData] = useState<SizeRequest>({
    user_height: 175,
    user_weight: 70,
    product_name: '',
    product_size: 'M',
    brand: ''
  });
  
  const [result, setResult] = useState<any>(null);
  const [photoResult, setPhotoResult] = useState<any>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [selectedBrand, setSelectedBrand] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [photoLoading, setPhotoLoading] = useState(false);
  const [productsLoading, setProductsLoading] = useState(false);

  const brands = ['Zara', 'Pull & Bear', 'Stradivarius'];

  // Existing functions
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    
    try {
      const response = await fetch('http://localhost:8000/analyze-size', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      
      if (response.status === 429) {
        setResult({
          success: false,
          error_type: "quota_exceeded",
          title: "🚨 AI Beden Analiz Limiti Aşıldı",
          message: "Günlük AI analiz limitine ulaşıldı. Lütfen 24 saat sonra tekrar deneyin.",
          retry_info: "Gerçek Gemini AI quota resetlenince aktif olacak.",
          is_error: true
        });
      } else if (response.status === 503) {
        setResult({
          success: false,
          error_type: "service_unavailable",
          title: "⚠️ AI Beden Analiz Servisi Geçici Olarak Kullanılamıyor", 
          message: "Gemini AI şu anda erişilemiyor. Lütfen daha sonra tekrar deneyin.",
          is_error: true
        });
      } else if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      } else {
        const data = await response.json();
        setResult(data);
      }
      
    } catch (error) {
      console.error('Size analysis error:', error);
      setResult({
        success: false,
        error_type: "network_error",
        title: "🔌 Bağlantı Hatası",
        message: "AI beden analiz servisiyle bağlantı kurulamadı.",
        is_error: true
      });
    } finally {
      setLoading(false);
    }
  };

  const handlePhotoUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    setPhotoLoading(true);
    setPhotoResult(null);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch('http://localhost:8000/analyze-photo', {
        method: 'POST',
        body: formData,
      });
      
      if (response.status === 429) {
        setPhotoResult({
          success: false,
          error_type: "quota_exceeded",
          title: "🚨 AI Analiz Limiti Aşıldı",
          message: "Günlük AI Vision analiz limitine ulaşıldı. Lütfen 24 saat sonra tekrar deneyin.",
          retry_info: "Quota yarın resetlenecek ve gerçek AI analizleri tekrar aktif olacak.",
          is_error: true
        });
      } else if (response.status === 503) {
        setPhotoResult({
          success: false,
          error_type: "service_unavailable", 
          title: "⚠️ AI Servisi Geçici Olarak Kullanılamıyor",
          message: "Gemini Vision AI şu anda erişilemiyor. Lütfen daha sonra tekrar deneyin.",
          is_error: true
        });
      } else if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      } else {
        const data = await response.json();
        setPhotoResult(data);
      }
      
    } catch (error) {
      console.error('Photo analysis error:', error);
      setPhotoResult({
        success: false,
        error_type: "network_error",
        title: "🔌 Bağlantı Hatası", 
        message: "AI servisiyle bağlantı kurulamadı. İnternet bağlantınızı kontrol edin.",
        is_error: true
      });
    } finally {
      setPhotoLoading(false);
    }
  };

  const handleBrandSelect = async (brand: string) => {
    setSelectedBrand(brand);
    setProductsLoading(true);
    setProducts([]);
    
    try {
      let analysisText = "Rectangle";
      
      if (currentPage === 'photo' && photoResult && photoResult.analysis) {
        analysisText = photoResult.analysis;
      } else if (currentPage === 'size' && result && result.recommendation) {
        analysisText = result.recommendation;
      }
      
      console.log(`🛍️ ${brand} için dinamik ürünler getiriliyor...`);
      
      const response = await fetch('http://localhost:8000/get-products', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          brand: brand,
          body_type: analysisText,
          category: 'woman'
        }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const data = await response.json();
      console.log(`✅ ${data.product_count || 0} dinamik ürün geldi`);
      setProducts(data.products || []);
      
    } catch (error) {
      console.error('Products error:', error);
      alert(`${brand} ürünleri yüklenirken hata oluştu. Lütfen tekrar deneyin.`);
    } finally {
      setProductsLoading(false);
    }
  };

  // Ana Sayfa Component
  const HomePage = () => (
    <div className="home-page">
      <h1>🎯 SizeGenie AI</h1>
      <p className="home-subtitle">AI destekli kıyafet beden önerisi ve ürün analizi</p>
      
      <div className="analysis-selection">
        <h2>🤔 Hangi analizi yapmak istiyorsunuz?</h2>
        
        <div className="analysis-options">
          <div className="analysis-card" onClick={() => setCurrentPage('photo')}>
            <div className="analysis-icon">📸</div>
            <h3>Fotoğraf Analizi</h3>
            <p>Vücut tipinizi analiz etmek için fotoğrafınızı yükleyin</p>
            <button className="analysis-btn">Fotoğraf Yükle</button>
          </div>
          
          <div className="analysis-card" onClick={() => setCurrentPage('size')}>
            <div className="analysis-icon">📏</div>
            <h3>Beden Analizi</h3>
            <p>Boy ve kilo bilgilerinizle beden önerisi alın</p>
            <button className="analysis-btn">Beden Analizi</button>
          </div>
        </div>
      </div>
    </div>
  );

  // Fotoğraf Analizi Sayfası
  const PhotoAnalysisPage = () => (
    <div className="analysis-page">
      <div className="page-header">
        <button className="back-btn" onClick={() => setCurrentPage('home')}>
          ← Geri Dön
        </button>
        <h1>📸 Fotoğraf Analizi</h1>
      </div>
      
      <div className="photo-section">
        <p>Vücut tipinizi analiz etmek için fotoğrafınızı yükleyin</p>
        <input
          type="file"
          accept="image/*"
          onChange={handlePhotoUpload}
          className="photo-input"
        />
        {photoLoading && <p className="loading">🤖 Fotoğraf analiz ediliyor...</p>}
        
        {photoResult && (
          <div className={`result ${photoResult.is_error ? 'error-result' : 'photo-result'}`}>
            {photoResult.is_error ? (
              <div className="error-content">
                <h3>{photoResult.title}</h3>
                <p className="error-message">{photoResult.message}</p>
                {photoResult.retry_info && (
                  <p className="retry-info">💡 {photoResult.retry_info}</p>
                )}
                {photoResult.error_type === "quota_exceeded" && (
                  <div className="quota-info">
                    <p>🤖 <strong>Bu gerçek AI sistemi!</strong></p>
                    <p>Fotoğrafınızı Gemini Vision AI gerçekten analiz ediyor.</p>
                    <p>Quota sınırı teknolojinin gücünün kanıtı! 🚀</p>
                  </div>
                )}
              </div>
            ) : (
              <>
                <h3>📊 Gerçek AI Vücut Analizi:</h3>
                <pre>{photoResult.analysis}</pre>
                
                <div className="brand-selection">
                  <h4>🛍️ Hangi markadan öneri istiyorsunuz?</h4>
                  <div className="brand-buttons">
                    {brands.map(brand => (
                      <button
                        key={brand}
                        onClick={() => handleBrandSelect(brand)}
                        className={`brand-btn ${selectedBrand === brand ? 'active' : ''}`}
                      >
                        {brand}
                      </button>
                    ))}
                  </div>
                </div>
              </>
            )}
          </div>
        )}
      </div>
      
      {/* Products Section */}
      {productsLoading && (
        <div className="loading-products">
          <p>🛒 {selectedBrand} ürünleri getiriliyor...</p>
        </div>
      )}

      {products.length > 0 && (
        <div className="products-section">
          <h2>🛍️ {selectedBrand} Önerileri</h2>
          <div className="products-grid">
            {products.map((product, index) => (
              <div key={index} className="product-card" onClick={() => window.open(product.url, '_blank')}>
                <img src={product.image} alt={product.name} />
                <div className="product-info">
                  <h4>{product.name}</h4>
                  <p className="price">{product.price}</p>
                  <span className="brand-tag">{product.brand}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  // Beden Analizi Sayfası
  const SizeAnalysisPage = () => (
    <div className="analysis-page">
      <div className="page-header">
        <button className="back-btn" onClick={() => setCurrentPage('home')}>
          ← Geri Dön
        </button>
        <h1>📏 Beden Analizi</h1>
      </div>
      
      <form onSubmit={handleSubmit} className="size-form">
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
        <div className={`result ${result.is_error ? 'error-result' : ''}`}>
          {result.is_error ? (
            <div className="error-content">
              <h3>{result.title}</h3>
              <p className="error-message">{result.message}</p>
              {result.retry_info && (
                <p className="retry-info">💡 {result.retry_info}</p>
              )}
              {result.error_type === "quota_exceeded" && (
                <div className="quota-info">
                  <p>🤖 <strong>Bu gerçek AI beden analiz sistemi!</strong></p>
                  <p>Ölçülerinizi Gemini AI gerçekten hesaplıyor.</p>
                  <p>Quota sınırı sistemin gerçekliğinin kanıtı! 🚀</p>
                </div>
              )}
            </div>
          ) : (
            <>
              <h3>📊 AI Beden Önerisi:</h3>
              <pre>{result.recommendation}</pre>
              
              {/* Marka Seçimi */}
              <div className="brand-selection">
                <h4>🛍️ Hangi markadan öneri istiyorsunuz?</h4>
                <div className="brand-buttons">
                  {brands.map(brand => (
                    <button
                      key={brand}
                      onClick={() => handleBrandSelect(brand)}
                      className={`brand-btn ${selectedBrand === brand ? 'active' : ''}`}
                    >
                      {brand}
                    </button>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>
      )}
      
      {/* Products Section */}
      {productsLoading && (
        <div className="loading-products">
          <p>🛒 {selectedBrand} ürünleri getiriliyor...</p>
        </div>
      )}

      {products.length > 0 && (
        <div className="products-section">
          <h2>🛍️ {selectedBrand} Önerileri</h2>
          <div className="products-grid">
            {products.map((product, index) => (
              <div key={index} className="product-card" onClick={() => window.open(product.url, '_blank')}>
                <img src={product.image} alt={product.name} />
                <div className="product-info">
                  <h4>{product.name}</h4>
                  <p className="price">{product.price}</p>
                  <span className="brand-tag">{product.brand}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  // Ana render
  return (
    <div className="App">
      <header className="App-header">
        {currentPage === 'home' && <HomePage />}
        {currentPage === 'photo' && <PhotoAnalysisPage />}
        {currentPage === 'size' && <SizeAnalysisPage />}
      </header>
    </div>
  );
}

export default App;
