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

type AnalysisType = 'splash' | 'home' | 'photo' | 'size' | 'chat' | 'size-guide' | 'history';

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

  // Dinamik AI düşünme mesajları
  const [thinkingMessage, setThinkingMessage] = useState<string>('');

  // AI düşünme mesajlarını döngüsel olarak değiştir
  React.useEffect(() => {
    if (chatLoading) {
      const messages = [
        'Stil danışmanınız düşünüyor...',
        'Trendleri analiz ediyorum...',
        'Size özel öneriler hazırlıyorum...',
        'En uygun ürünleri buluyorum...',
        'Vücut tipinizi değerlendiriyorum...'
      ];
      
      let currentIndex = 0;
      setThinkingMessage(messages[0]);
      
      const interval = setInterval(() => {
        currentIndex = (currentIndex + 1) % messages.length;
        setThinkingMessage(messages[currentIndex]);
      }, 800);
      
      return () => clearInterval(interval);
    }
  }, [chatLoading]);

  // REFS FOR UNCONTROLLED INPUTS
  const brandInputRef = useRef<HTMLInputElement>(null);
  const productInputRef = useRef<HTMLInputElement>(null);
  const chatInputRef = useRef<HTMLInputElement>(null);

  // Trend analysis states
  const [trendData, setTrendData] = useState<any>(null);
  const [trendLoading, setTrendLoading] = useState(false);

  // Sosyal paylaşım states
  const [shareModalOpen, setShareModalOpen] = useState(false);
  const [shareContent, setShareContent] = useState<any>(null);

  // Sosyal paylaşım fonksiyonları
  const generateShareText = (type: string, data: any) => {
    const baseUrl = window.location.origin;
    
    switch (type) {
      case 'size_analysis':
        return `🎯 AURA AI ile beden analizimi yaptırdım!

✅ ${data.size} bedeni bana ${data.fits ? 'uyuyormuş' : 'uymuyor'}
📊 BMI hesabım: ${data.bmi?.toFixed(1)} 
👤 ${data.gender} için ${data.brand} ${data.product}
🤖 Yapay zeka önerisiyle doğru beden buldum!

#AuraAI #BedenAnalizi #AI #Fashion

${baseUrl}`;

      case 'photo_analysis':
        return `📸 AURA AI vücut tipimi analiz etti!

🔹 Vücut Tipim: ${data.bodyType || 'Analiz edildi'}
🎯 AI önerileri aldım ve hangi kıyafetlerin yakıştığını öğrendim!
🤖 Gemini Vision AI ile gerçek analiz!

#AuraAI #VücutTipi #AIAnaliz #Moda

${baseUrl}`;

      case 'chat_recommendations':
        return `🤖 AURA AI stil danışmanım harika öneriler verdi!

💭 "${data.userMessage}" dedim
✨ ${data.productCount} farklı seçenek buldu
🎯 Hem trendleri hem vücut tipimi düşündü

#AuraAI #AIAsistan #Moda #Alışveriş

${baseUrl}`;

      case 'trends':
        return `📈 AURA AI ile bu haftanın moda trendlerini keşfettim!

🔥 En trend: ${data.topTrend}
📊 Hafta ${data.weekNumber} trend analizi
🤖 AI ile kişiselleştirilmiş moda önerileri!

#AuraAI #ModaTrendi #AI #Fashion

${baseUrl}`;

      default:
        return `🤖 AURA AI ile kıyafet ve beden analizi yaptırdım!

✨ AI destekli moda önerileri
🎯 Kişiselleştirilmiş stil danışmanlığı
📊 Gerçek zamanlı trend analizi

#AuraAI #AI #Moda #Fashion

${baseUrl}`;
    }
  };

  const handleShare = async (type: string, data: any) => {
    const shareText = generateShareText(type, data);
    setShareContent({ type, data, text: shareText });
    setShareModalOpen(true);
  };

  const handleNativeShare = async () => {
    if (typeof navigator !== 'undefined' && 'share' in navigator && shareContent) {
      try {
        await navigator.share({
          title: 'AURA AI - Kıyafet & Beden Analizi',
          text: shareContent.text,
          url: window.location.origin
        });
        setShareModalOpen(false);
      } catch (error) {
        console.log('Native share failed:', error);
        // Fallback to clipboard
        handleCopyToClipboard();
      }
    } else {
      handleCopyToClipboard();
    }
  };

  const handleCopyToClipboard = async () => {
    if (shareContent) {
      try {
        await navigator.clipboard.writeText(shareContent.text);
        alert('📋 Panoya kopyalandı! Sosyal medyada paylaşabilirsiniz.');
        setShareModalOpen(false);
      } catch (error) {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = shareContent.text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        alert('📋 Panoya kopyalandı!');
        setShareModalOpen(false);
      }
    }
  };

  const handleSocialShare = (platform: string) => {
    if (!shareContent) return;
    
    const text = encodeURIComponent(shareContent.text);
    const url = encodeURIComponent(window.location.origin);
    
    let shareUrl = '';
    
    switch (platform) {
      case 'twitter':
        shareUrl = `https://twitter.com/intent/tweet?text=${text}`;
        break;
      case 'facebook':
        shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${url}&quote=${text}`;
        break;
      case 'whatsapp':
        shareUrl = `https://wa.me/?text=${text}`;
        break;
      case 'linkedin':
        shareUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${url}&summary=${text}`;
        break;
    }
    
    if (shareUrl) {
      window.open(shareUrl, '_blank', 'width=600,height=400');
      setShareModalOpen(false);
    }
  };

  // Analysis history state
  const [analysisHistory, setAnalysisHistory] = useState<any[]>([]);

  const brands = ['Zara', 'Pull & Bear', 'Stradivarius'];

  // GERÇEK BEDEN KARŞILAŞTIRMA VERİSİ (Araştırma Bazlı)
  const sizeChart = {
    kadın: {
      XS: { 
        Zara: "XS", 
        "Pull & Bear": "XXS", 
        Stradivarius: "XS", 
        "H&M": "32", 
        Mango: "XS",
        "Genel": "XS denk"
      },
      S: { 
        Zara: "S", 
        "Pull & Bear": "XS", 
        Stradivarius: "S", 
        "H&M": "34/36", 
        Mango: "S",
        "Genel": "S denk"
      },
      M: { 
        Zara: "M", 
        "Pull & Bear": "S", 
        Stradivarius: "M", 
        "H&M": "38", 
        Mango: "M",
        "Genel": "M denk"
      },
      L: { 
        Zara: "L", 
        "Pull & Bear": "M", 
        Stradivarius: "L", 
        "H&M": "40", 
        Mango: "L",
        "Genel": "L denk"
      },
      XL: { 
        Zara: "XL", 
        "Pull & Bear": "L", 
        Stradivarius: "XL", 
        "H&M": "42", 
        Mango: "XL",
        "Genel": "XL denk"
      },
      XXL: { 
        Zara: "XXL", 
        "Pull & Bear": "XL", 
        Stradivarius: "XXL", 
        "H&M": "44", 
        Mango: "XXL",
        "Genel": "XXL denk"
      }
    },
    erkek: {
      XS: { 
        Zara: "XS", 
        "Pull & Bear": "XS", 
        "H&M": "44", 
        Mango: "XS",
        "Genel": "XS denk"
      },
      S: { 
        Zara: "S", 
        "Pull & Bear": "XS", 
        "H&M": "46", 
        Mango: "S",
        "Genel": "S denk"
      },
      M: { 
        Zara: "M", 
        "Pull & Bear": "S", 
        "H&M": "48", 
        Mango: "M",
        "Genel": "M denk"
      },
      L: { 
        Zara: "L", 
        "Pull & Bear": "M", 
        "H&M": "50", 
        Mango: "L",
        "Genel": "L denk"
      },
      XL: { 
        Zara: "XL", 
        "Pull & Bear": "L", 
        "H&M": "52", 
        Mango: "XL",
        "Genel": "XL denk"
      },
      XXL: { 
        Zara: "XXL", 
        "Pull & Bear": "XL", 
        "H&M": "54", 
        Mango: "XXL",
        "Genel": "XXL denk"
      }
    }
  };

  // Analiz geçmişine ekleme fonksiyonu
  const addToHistory = (type: string, data: any) => {
    const historyItem = {
      id: Date.now(),
      type,
      data,
      timestamp: new Date().toLocaleString('tr-TR'),
      date: new Date().toLocaleDateString('tr-TR')
    };
    
    const updatedHistory = [historyItem, ...analysisHistory].slice(0, 10); // Son 10 analiz
    setAnalysisHistory(updatedHistory);
    
    // LocalStorage'a kaydet
    try {
      localStorage.setItem('aura_analysis_history', JSON.stringify(updatedHistory));
    } catch (error) {
      console.log('LocalStorage kullanılamıyor');
    }
  };

  // Trend analizi çekme fonksiyonu
  const fetchTrendData = async (category?: string, bodyType?: string) => {
    setTrendLoading(true);
    try {
      const response = await fetch('http://localhost:8000/get-trends', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          category: category || null,
          body_type: bodyType || null,
          price_range: null
        }),
      });
      
      if (response.ok) {
        const data = await response.json();
        setTrendData(data);
        console.log('✅ Trend verileri alındı:', data);
      } else {
        console.error('❌ Trend verisi alınamadı');
      }
    } catch (error) {
      console.error('❌ Trend API hatası:', error);
    } finally {
      setTrendLoading(false);
    }
  };

  // Sayfa yüklendiğinde trend verilerini al
  React.useEffect(() => {
    fetchTrendData();
  }, []);

  // Geçmişi temizleme fonksiyonu
  const clearHistory = () => {
    setAnalysisHistory([]);
    try {
      localStorage.removeItem('aura_analysis_history');
    } catch (error) {
      console.log('LocalStorage temizlenemedi');
    }
  };

  // Uygulama açılışında geçmişi yükle
  React.useEffect(() => {
    try {
      const savedHistory = localStorage.getItem('aura_analysis_history');
      if (savedHistory) {
        setAnalysisHistory(JSON.parse(savedHistory));
      }
    } catch (error) {
      console.log('Geçmiş yüklenemedi');
    }
  }, []);

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
        
        // Geçmişe ekle
        addToHistory('size_analysis', {
          gender,
          height: userHeight,
          weight: userWeight,
          brand: brandInputRef.current?.value,
          product: productInputRef.current?.value,
          size: productSize,
          bmi: data.bmi,
          result: data.recommendation
        });
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
        
        // Geçmişe ekle
        addToHistory('photo_analysis', {
          analysis: data.analysis,
          ai_type: data.ai_type,
          timestamp: new Date().toLocaleString('tr-TR')
        });
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

  // Chat send function - GERÇEK AI DÜŞÜNMİ SÜRESİ İLE
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
      // AI düşünme süresi simülasyonu (1.5-3 saniye arası)
      const thinkingTime = Math.random() * 1500 + 1500; // 1.5-3 saniye
      await new Promise(resolve => setTimeout(resolve, thinkingTime));
      
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
      if (chatInputRef.current) {
        chatInputRef.current.focus();
      }
    }
  };

  // Paylaşım Modal Komponenti
  const ShareModal = () => {
    if (!shareModalOpen || !shareContent) return null;

    return (
      <div className="share-modal-overlay" onClick={() => setShareModalOpen(false)}>
        <div className="share-modal" onClick={(e) => e.stopPropagation()}>
          <div className="share-modal-header">
            <h3>📤 Sonucunuzu Paylaşın</h3>
            <button 
              className="share-modal-close"
              onClick={() => setShareModalOpen(false)}
            >
              ✕
            </button>
          </div>
          
          <div className="share-preview">
            <p className="share-preview-text">{shareContent.text}</p>
          </div>
          
          <div className="share-options">
            {typeof navigator !== 'undefined' && 'share' in navigator && (
              <button 
                className="share-option share-native"
                onClick={handleNativeShare}
              >
                📱 Paylaş
              </button>
            )}
            
            <button 
              className="share-option share-copy"
              onClick={handleCopyToClipboard}
            >
              📋 Kopyala
            </button>
            
            <button 
              className="share-option share-twitter"
              onClick={() => handleSocialShare('twitter')}
            >
              🐦 Twitter
            </button>
            
            <button 
              className="share-option share-facebook"
              onClick={() => handleSocialShare('facebook')}
            >
              📘 Facebook
            </button>
            
            <button 
              className="share-option share-whatsapp"
              onClick={() => handleSocialShare('whatsapp')}
            >
              💬 WhatsApp
            </button>
            
            <button 
              className="share-option share-linkedin"
              onClick={() => handleSocialShare('linkedin')}
            >
              💼 LinkedIn
            </button>
          </div>
        </div>
      </div>
    );
  };

  // SPLASH SAYFASI
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
        
        {/* YENİ: Geçmiş butonu */}
        <button 
          className="history-btn"
          onClick={() => setCurrentPage('history')}
          title="Analiz Geçmişi"
        >
          📜 Geçmiş ({analysisHistory.length})
        </button>
      </div>

      {/* YENİ: Trend Analizi Bölümü */}
      <div className="trend-section">
        <h2>📈 Bu Haftanın Trendleri</h2>
        {trendLoading ? (
          <div className="trend-loading">
            <p>🔄 Trend verileri yükleniyor...</p>
          </div>
        ) : trendData && trendData.success ? (
          <div className="trend-container">
            <div className="trend-insights">
              <div className="trend-insights-card">
                <h3>🧠 AI Trend Analizi</h3>
                <p>{trendData.insights}</p>
                <div className="trend-meta">
                  <span>📅 Hafta {trendData.week_number}</span>
                  <span>🛍️ {trendData.total_products} trend ürün</span>
                </div>
              </div>
            </div>
            
            {trendData.trends && trendData.trends.length > 0 && (
              <div className="trend-products">
                <h4>🔥 En Çok Aranan Ürünler</h4>
                <div className="trend-grid">
                  {trendData.trends.slice(0, 6).map((trend: any, index: number) => (
                    <div key={index} className="trend-card">
                      <div className="trend-rank">#{index + 1}</div>
                      <div className="trend-info">
                        <h5>{trend.product_name}</h5>
                        <p className="trend-brand">{trend.brand}</p>
                        <div className="trend-stats">
                          <span className="trend-score">📊 {trend.trend_score}% trend</span>
                          {trend.price_range && (
                            <span className="trend-price">💰 {trend.price_range}</span>
                          )}
                        </div>
                      </div>
                      <div className="trend-arrow">📈</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            <div className="trend-actions">
              <button 
                className="trend-refresh-btn"
                onClick={() => fetchTrendData()}
                disabled={trendLoading}
              >
                🔄 Trendleri Yenile
              </button>
            </div>
          </div>
        ) : (
          <div className="trend-error">
            <p>⚠️ Trend verileri şu anda yüklenemiyor</p>
            <button onClick={() => fetchTrendData()}>🔄 Tekrar Dene</button>
          </div>
        )}
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
          
          <div className="analysis-card" onClick={() => setCurrentPage('size-guide')}>
            <div className="analysis-icon">📊</div>
            <div className="analysis-card-content">
              <h3>Beden Rehberi</h3>
              <p>Markalar arası beden karşılaştırması</p>
              <button className="analysis-btn">Beden Rehberi</button>
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
                
                {/* YENİ: Fotoğraf Analizi Paylaş Butonu */}
                <div className="result-actions">
                  <button 
                    className="share-btn"
                    onClick={() => handleShare('photo_analysis', {
                      bodyType: photoResult.analysis?.match(/Vücut Tipi:\*\* (.+)/)?.[1] || 'Analiz edildi',
                      aiType: photoResult.ai_type
                    })}
                  >
                    📤 Analizi Paylaş
                  </button>
                </div>
                
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
              
              {/* YENİ: Paylaşım Butonu */}
              <div className="result-actions">
                <button 
                  className="share-btn"
                  onClick={() => handleShare('size_analysis', {
                    size: productSize,
                    fits: result.recommendation?.includes('EVET'),
                    bmi: result.bmi,
                    gender: gender,
                    brand: brandInputRef.current?.value,
                    product: productInputRef.current?.value
                  })}
                >
                  📤 Sonucu Paylaş
                </button>
              </div>
              
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

  // Chat Sayfası - GELIŞMIŞ AI STİL DANIŞMANI
  const ChatPage = () => (
    <div className="analysis-page">
      <div className="page-header">
        <button className="back-btn" onClick={() => setCurrentPage('home')}>
          ← Geri Dön
        </button>
        <h1>🤖 AI Stil Danışmanı</h1>
        <div className="ai-consultant-badge">
          <span>✨ Trend + Kişisel Analiz</span>
        </div>
      </div>
      
      <div className="chat-container">
        <div className="chat-messages">
          {chatMessages.length === 0 && (
            <div className="chat-welcome">
              <h3>👋 Merhaba! Ben AURA'nın AI Stil Danışmanınızım!</h3>
              <p>Size özel stil önerileri sunuyorum. Vücut tipinizi, trendleri ve tercihlerinizi analiz ederek en uygun kıyafetleri buluyorum.</p>
              
              <div className="ai-features">
                <div className="ai-feature">
                  <span className="feature-icon">📈</span>
                  <span>Güncel trendleri takip ederim</span>
                </div>
                <div className="ai-feature">
                  <span className="feature-icon">👤</span>
                  <span>Vücut tipinize özel önerilerim</span>
                </div>
                <div className="ai-feature">
                  <span className="feature-icon">💰</span>
                  <span>Bütçenize uygun seçenekleri bulurum</span>
                </div>
                <div className="ai-feature">
                  <span className="feature-icon">🎨</span>
                  <span>Stil tercihlerinizi öğrenirim</span>
                </div>
              </div>
              
              <div className="example-messages">
                <h4>✨ Örnek sorular:</h4>
                <p><strong>"200 TL altında kış için hoodie önerisi"</strong></p>
                <p><strong>"Rectangle vücut tipim için trend elbiseler"</strong></p>
                <p><strong>"İş için şık ama rahat kıyafetler"</strong></p>
                <p><strong>"Bu sezon hangi renkler moda?"</strong></p>
              </div>
            </div>
          )}
          
          {chatMessages.map((message, index) => (
            <div key={index} className={`message ${message.role}`}>
              <div className="message-content">
                <p>{message.content}</p>
                
                {message.products && message.products.length > 0 && (
                  <div className="chat-products">
                    <h4>🛍️ Size özel stil önerilerim:</h4>
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
                    
                    {/* YENİ: Chat Önerileri Paylaş Butonu */}
                    <div className="chat-actions">
                      <button 
                        className="share-btn chat-share-btn"
                        onClick={() => {
                          const userMsg = chatMessages.find(msg => msg.role === 'user');
                          handleShare('chat_recommendations', {
                            userMessage: userMsg?.content || 'Ürün önerisi istedim',
                            productCount: message.products?.length || 0
                          });
                        }}
                      >
                        📤 Önerileri Paylaş
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
          
          {chatLoading && (
            <div className="message assistant">
              <div className="message-content">
                <div className="ai-thinking">
                  <span className="ai-avatar">🤖</span>
                  <div className="thinking-text">
                    <p>{thinkingMessage}</p>
                    <div className="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
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
              placeholder="Stil ihtiyacınızı detaylıca anlatın... (örn: 'İş için şık pantolon arıyorum, bütçem 300 TL')"
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
              title="Stil Danışmanına Sor"
            >
              {chatLoading ? '🤔' : '✨'}
            </button>
          </div>
          
          <div className="chat-tips">
            <p>💡 <strong>İpucu:</strong> Ne kadar detay verirseniz, o kadar kişisel öneriler alırsınız!</p>
          </div>
        </div>
      </div>
    </div>
  );

  // Beden Rehberi Sayfası - Stradivarius erkek için gizlendi
  const SizeGuidePage = () => (
    <div className="analysis-page">
      <div className="page-header">
        <button className="back-btn" onClick={() => setCurrentPage('home')}>
          ← Geri Dön
        </button>
        <h1>📊 Beden Rehberi</h1>
      </div>
      
      <div className="size-guide-container">
        {/* Beden Karşılaştırma Tablosu */}
        <div className="size-comparison">
          <h2>🔄 Markalar Arası Beden Karşılaştırması</h2>
          <p>Bir markada hangi bedeni giyiyorsanız, diğer markalarda hangi bedeni seçmelisiniz? <strong>Gerçek marka araştırması bazlı!</strong></p>
          
          <div className="comparison-legend">
            <h4>📋 Nasıl Kullanılır:</h4>
            <p>• <strong>Soldaki sütun:</strong> Standart beden ölçünüz</p>
            <p>• <strong>Diğer sütunlar:</strong> Her markada almanız gereken beden</p>
            <p>• <strong>Not:</strong> Pull & Bear genelde büyük gelir, H&M sayısal sistem kullanır</p>
            {gender === 'erkek' && (
              <p>• <strong>Erkek Not:</strong> Stradivarius'ta erkek koleksiyonu bulunmamaktadır</p>
            )}
          </div>
          
          <div className="gender-tabs">
            <button 
              className={`gender-tab ${gender === 'kadın' ? 'active' : ''}`}
              onClick={() => setGender('kadın')}
            >
              👩 Kadın
            </button>
            <button 
              className={`gender-tab ${gender === 'erkek' ? 'active' : ''}`}
              onClick={() => setGender('erkek')}
            >
              👨 Erkek
            </button>
          </div>

          <div className="size-chart">
            <table className="comparison-table">
              <thead>
                <tr>
                  <th>Sizin Bedeniniz</th>
                  <th>Zara</th>
                  <th>Pull & Bear</th>
                  {gender === 'kadın' && <th>Stradivarius</th>}
                  <th>H&M</th>
                  <th>Mango</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(sizeChart[gender as keyof typeof sizeChart]).map(([size, brands]) => (
                  <tr key={size}>
                    <td className="size-standard">{size}</td>
                    <td className="brand-zara">{brands.Zara}</td>
                    <td className="brand-pb">{brands["Pull & Bear"]}</td>
                    {gender === 'kadın' && (
                      <td className="brand-str">{(brands as any).Stradivarius}</td>
                    )}
                    <td className="brand-hm">{brands["H&M"]}</td>
                    <td className="brand-mango">{brands.Mango}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          <div className="size-tips">
            <h4>💡 Marka Özel İpuçları:</h4>
            <div className="brand-tips">
              <div className="tip">
                <strong>🏷️ Zara:</strong> Dar kesim, özellikle üst giyimde. Genelde 1 beden büyük alın.
              </div>
              <div className="tip">
                <strong>🐻 Pull & Bear:</strong> En geniş kesim. Genelde 1-2 beden küçük alabilirsiniz.
              </div>
              {gender === 'kadın' && (
                <div className="tip">
                  <strong>🎵 Stradivarius:</strong> Zara ile benzer ama biraz daha rahat.
                </div>
              )}
              <div className="tip">
                <strong>🏠 H&M:</strong> Sayısal sistem kullanır. {gender === 'kadın' ? 'Kadın için 36-38 ortalama M bedeni.' : 'Erkek için 48-50 ortalama M bedeni.'}
              </div>
              <div className="tip">
                <strong>🥭 Mango:</strong> Standart Avrupa bedenleri, güvenilir ölçüler.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  // YENİ: Geçmiş Sayfası
  const HistoryPage = () => (
    <div className="analysis-page">
      <div className="page-header">
        <button className="back-btn" onClick={() => setCurrentPage('home')}>
          ← Geri Dön
        </button>
        <h1>📜 Analiz Geçmişi</h1>
        {analysisHistory.length > 0 && (
          <button 
            className="clear-history-btn"
            onClick={clearHistory}
            title="Tüm geçmişi temizle"
          >
            🗑️ Geçmişi Temizle
          </button>
        )}
      </div>
      
      <div className="history-container">
        <div className="analysis-history">
          <h2>📊 Son Analizleriniz</h2>
          <p>Yaptığınız tüm analizler ve sonuçları</p>
          
          {analysisHistory.length === 0 ? (
            <div className="no-history">
              <p>Henüz analiz geçmişiniz bulunmuyor.</p>
              <p>Beden analizi veya fotoğraf analizi yaptığınızda burada görünecek!</p>
              <div className="history-actions">
                <button 
                  className="history-action-btn" 
                  onClick={() => setCurrentPage('size')}
                >
                  📏 Beden Analizi Yap
                </button>
                <button 
                  className="history-action-btn" 
                  onClick={() => setCurrentPage('photo')}
                >
                  📸 Fotoğraf Analizi Yap
                </button>
              </div>
            </div>
          ) : (
            <div className="history-list">
              {analysisHistory.map((item) => (
                <div key={item.id} className="history-item">
                  <div className="history-header">
                    <span className="history-type">
                      {item.type === 'size_analysis' ? '📏 Beden Analizi' : 
                       item.type === 'photo_analysis' ? '📸 Fotoğraf Analizi' : '🤖 Chat'}
                    </span>
                    <span className="history-date">{item.timestamp}</span>
                  </div>
                  
                  <div className="history-content">
                    {item.type === 'size_analysis' && (
                      <div className="size-history">
                        <p><strong>👤 Cinsiyet:</strong> {item.data.gender}</p>
                        <p><strong>📏 Boy/Kilo:</strong> {item.data.height}cm / {item.data.weight}kg</p>
                        <p><strong>🏷️ Ürün:</strong> {item.data.brand} {item.data.product} ({item.data.size})</p>
                        <p><strong>📊 BMI:</strong> {item.data.bmi?.toFixed(1)}</p>
                        <div className="history-result">
                          <strong>🎯 Sonuç:</strong>
                          <div className="result-preview">
                            {item.data.result?.substring(0, 200)}...
                          </div>
                        </div>
                      </div>
                    )}
                    
                    {item.type === 'photo_analysis' && (
                      <div className="photo-history">
                        <p><strong>🤖 AI Tipi:</strong> {item.data.ai_type}</p>
                        <div className="analysis-preview">
                          <strong>📊 Analiz:</strong>
                          <div className="result-preview">
                            {item.data.analysis?.substring(0, 200)}...
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
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
        {currentPage === 'size-guide' && <SizeGuidePage />}
        {currentPage === 'history' && <HistoryPage />}
      </header>
      
      {/* Sosyal Paylaşım Modal */}
      <ShareModal />
    </div>
  );
}

export default App;
