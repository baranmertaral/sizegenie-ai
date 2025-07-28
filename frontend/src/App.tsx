import React, { useState, useRef } from 'react';
import './App.css';

interface SizeRequest {
  user_height: number;
  user_weight: number;
  product_name: string;
  product_size: string;
  brand: string;
  gender: string;
}

interface Product {
  name: string;
  price: string;
  image: string;
  url: string;
  brand: string;
  match_score?: number;
}

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  products?: Product[];
  timestamp: number;
}

type AnalysisType = 'splash' | 'home' | 'photo' | 'size' | 'chat';

function App() {
  // Ana state - splash ile başlıyor
  const [currentPage, setCurrentPage] = useState<AnalysisType>('splash');
  
  // Size analysis states - KONTROL EDİLEN DEĞERLER
  const [userHeight, setUserHeight] = useState<number>(175);
  const [userWeight, setUserWeight] = useState<number>(70);
  const [productSize, setProductSize] = useState<string>('M');
  const [gender, setGender] = useState<string>('kadın');
  
  const [result, setResult] = useState<any>(null);
  const [photoResult, setPhotoResult] = useState<any>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [selectedBrand, setSelectedBrand] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [photoLoading, setPhotoLoading] = useState(false);
  const [productsLoading, setProductsLoading] = useState(false);

  // Chat states
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatLoading, setChatLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string>('');

  // REFS FOR UNCONTROLLED INPUTS
  const brandInputRef = useRef<HTMLInputElement>(null);
  const productInputRef = useRef<HTMLInputElement>(null);
  const chatInputRef = useRef<HTMLInputElement>(null);

  const brands = ['Zara', 'Pull & Bear', 'Stradivarius'];

  // Splash'tan ana sayfaya geçiş
  const handleSplashToHome = () => {
    setCurrentPage('home');
  };

  // Size analysis function - "BU BEDEN BANA UYAR MI?" SORGUSU
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    
    const formData = {
      user_height: userHeight,
      user_weight: userWeight,
      product_name: productInputRef.current?.value || '',
      product_size: productSize,
      brand: brandInputRef.current?.value || '',
      gender: gender
    };
    
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

  // Photo analysis function
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

  // Brand selection function
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

  // Chat send function - REF'DEN DEĞER AL
  const handleChatSend = async () => {
    const chatInput = chatInputRef.current?.value?.trim();
    if (!chatInput || chatLoading) return;
    
    // Input'u temizle
    if (chatInputRef.current) {
      chatInputRef.current.value = '';
    }
    
    setChatLoading(true);
    
    const newUserMessage: ChatMessage = {
      role: 'user',
      content: chatInput,
      timestamp: Date.now()
    };
    setChatMessages(prev => [...prev, newUserMessage]);
    
    try {
      const response = await fetch('http://localhost:8000/chat-product-search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: chatInput,
          conversation_id: conversationId || undefined
        }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.conversation_id && !conversationId) {
        setConversationId(data.conversation_id);
      }
      
      const aiMessage: ChatMessage = {
        role: 'assistant',
        content: data.ai_response,
        products: data.products || [],
        timestamp: Date.now()
      };
      setChatMessages(prev => [...prev, aiMessage]);
      
      console.log(`🤖 ${data.products?.length || 0} ürün önerisi geldi`);
      
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: 'Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.',
        timestamp: Date.now()
      };
      setChatMessages(prev => [...prev, errorMessage]);
    } finally {
      setChatLoading(false);
      // Focus'u geri ver
      if (chatInputRef.current) {
        chatInputRef.current.focus();
      }
    }
  };

  // SPLASH SAYFASI - YENİ!
  const SplashPage = () => (
    <div className="splash-page">
      <div className="splash-content">
        <div className="aura-logo">
          <h1>AURA</h1>
          <div className="aura-glow"></div>
        </div>
        
        <div className="splash-text">
          <p>Auranı değiştirelim mi?</p>
        </div>
        
        <button className="splash-btn" onClick={handleSplashToHome}>
          Hadi
        </button>
      </div>
    </div>
  );

  // Ana Sayfa Component
  const HomePage = () => (
    <div className="home-page">
      <div className="home-header">
        <div className="aura-logo-small">AURA</div>
        <p className="home-subtitle">AI destekli kıyafet beden önerisi ve ürün analizi</p>
      </div>
      
      <div className="analysis-selection">
        <h2>🤔 Hangi analizi yapmak istiyorsunuz?</h2>
        
        <div className="analysis-options">
          <div className="analysis-card" onClick={() => setCurrentPage('photo')}>
            <div className="analysis-icon">📸</div>
            <div className="analysis-card-content">
              <h3>Fotoğraf Analizi</h3>
              <p>Vücut tipinizi analiz etmek için fotoğrafınızı yükleyin</p>
              <button className="analysis-btn">Fotoğraf Yükle</button>
            </div>
          </div>
          
          <div className="analysis-card" onClick={() => setCurrentPage('size')}>
            <div className="analysis-icon">📏</div>
            <div className="analysis-card-content">
              <h3>Beden Analizi</h3>
              <p>Boy ve kilo bilgilerinizle beden önerisi alın</p>
              <button className="analysis-btn">Beden Analizi</button>
            </div>
          </div>
          
          <div className="analysis-card" onClick={() => setCurrentPage('chat')}>
            <div className="analysis-icon">🤖</div>
            <div className="analysis-card-content">
              <h3>AI Ürün Asistanı</h3>
              <p>Hayalinizdeki ürünü tarif edin, size bulalım!</p>
              <button className="analysis-btn">Chat Başlat</button>
            </div>
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
                        data-brand={brand}
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

  // Beden Analizi Sayfası - "BU BEDEN BANA UYAR MI?"
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
          <label>Cinsiyet:</label>
          <select
            value={gender}
            onChange={(e) => setGender(e.target.value)}
            className="gender-select"
          >
            <option value="kadın">👩 Kadın</option>
            <option value="erkek">👨 Erkek</option>
          </select>
        </div>

        <div className="form-group">
          <label>Boy (cm):</label>
          <input
            type="number"
            value={userHeight}
            onChange={(e) => setUserHeight(Number(e.target.value))}
          />
        </div>
        
        <div className="form-group">
          <label>Kilo (kg):</label>
          <input
            type="number"
            value={userWeight}
            onChange={(e) => setUserWeight(Number(e.target.value))}
          />
        </div>
        
        <div className="form-group">
          <label>Marka:</label>
          <input
            ref={brandInputRef}
            type="text"
            placeholder="örn: Zara, H&M, Nike"
            autoComplete="off"
          />
        </div>
        
        <div className="form-group">
          <label>Ürün:</label>
          <input
            ref={productInputRef}
            type="text"
            placeholder="örn: Basic T-Shirt, Jeans"
            autoComplete="off"
          />
        </div>
        
        <div className="form-group">
          <label>Denemek İstediğim Beden:</label>
          <select
            value={productSize}  
            onChange={(e) => setProductSize(e.target.value)}
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
          {loading ? '🤖 AI Analiz Ediyor...' : '🎯 Bu Beden Bana Uyar mı?'}
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
              <h3>📊 AI Beden Uygunluk Analizi:</h3>
              <pre>{result.recommendation}</pre>
              
              <div className="next-step-info">
                <h4>🎯 Diğer Özellikler:</h4>
                <p>• <strong>Fotoğraf Analizi</strong> ile vücut tipinizi keşfedin</p>
                <p>• <strong>AI Asistanı</strong> ile farklı ürün önerileri alın</p>
                <div className="action-buttons">
                  <button 
                    className="next-action-btn" 
                    onClick={() => setCurrentPage('photo')}
                  >
                    📸 Fotoğraf Analizi
                  </button>
                  <button 
                    className="next-action-btn" 
                    onClick={() => setCurrentPage('chat')}
                  >
                    🤖 AI Asistanı
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );

  // Chat Sayfası - UNCONTROLLED INPUT
  const ChatPage = () => (
    <div className="analysis-page">
      <div className="page-header">
        <button className="back-btn" onClick={() => setCurrentPage('home')}>
          ← Geri Dön
        </button>
        <h1>🤖 AI Ürün Asistanı</h1>
      </div>
      
      <div className="chat-container">
        <div className="chat-messages">
          {chatMessages.length === 0 && (
            <div className="chat-welcome">
              <h3>👋 Merhaba! Size nasıl yardımcı olabilirim?</h3>
              <p>İstediğiniz ürünü detaylıca tarif edin, size en uygun seçenekleri bulayım.</p>
              <div className="example-messages">
                <p><strong>Örnek:</strong> "Beyaz, oversize, vintage tarzı bir tişört istiyorum"</p>
                <p><strong>Örnek:</strong> "Yüksek bel, wide leg bir jean arıyorum"</p>
              </div>
            </div>
          )}
          
          {chatMessages.map((message, index) => (
            <div key={index} className={`message ${message.role}`}>
              <div className="message-content">
                <p>{message.content}</p>
                
                {message.products && message.products.length > 0 && (
                  <div className="chat-products">
                    <h4>🛍️ Sizin için bulduğum ürünler:</h4>
                    <div className="chat-products-grid">
                      {message.products.map((product, pIndex) => (
                        <div key={pIndex} className="chat-product-card" onClick={() => window.open(product.url, '_blank')}>
                          <img src={product.image} alt={product.name} />
                          <div className="chat-product-info">
                            <h5>{product.name}</h5>
                            <p className="price">{product.price}</p>
                            <span className="brand">{product.brand}</span>
                            {product.match_score && (
                              <span className="match-score">✨ {product.match_score}% uyum</span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
          
          {chatLoading && (
            <div className="message assistant">
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
        </div>
        
        <div className="chat-input-area">
          <div className="chat-input-container">
            <input
              ref={chatInputRef}
              type="text"
              placeholder="İstediğiniz ürünü tarif edin..."
              className="chat-input"
              disabled={chatLoading}
              autoComplete="off"
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !chatLoading) {
                  e.preventDefault();
                  handleChatSend();
                }
              }}
            />
            <button 
              onClick={handleChatSend}
              disabled={chatLoading}
              className="chat-send-btn"
            >
              {chatLoading ? '⏳' : '📤'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  // Ana render
  return (
    <div className="App">
      <header className="App-header">
        {currentPage === 'splash' && <SplashPage />}
        {currentPage === 'home' && <HomePage />}
        {currentPage === 'photo' && <PhotoAnalysisPage />}
        {currentPage === 'size' && <SizeAnalysisPage />}
        {currentPage === 'chat' && <ChatPage />}
      </header>
    </div>
  );
}

export default App;
