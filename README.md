# 🎯 AURA AI - Yapay Zeka Destekli Moda ve Beden Analiz Platformu

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-4.5+-3178C6.svg)](https://typescriptlang.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com)
[![Gemini AI](https://img.shields.io/badge/Gemini_AI-Integrated-4285F4.svg)](https://ai.google.dev)

> **"Auranı değiştirelim mi?"** - AI destekli kişisel moda danışmanın

## 📋 İçindekiler

1. [Proje Hakkında](#-proje-hakkında)
2. [Temel Özellikler](#-temel-özellikler)
3. [Teknoloji Yığını](#-teknoloji-yığını)
4. [Kurulum ve Çalıştırma](#-kurulum-ve-çalıştırma)
5. [Detaylı Özellik Açıklamaları](#-detaylı-özellik-açıklamaları)
6. [API Endpoint'leri](#-api-endpointleri)
7. [Kullanıcı Rehberi](#-kullanıcı-rehberi)
8. [Teknik Mimari](#-teknik-mimari)
9. [Ekran Görüntüleri](#-ekran-görüntüleri)
10. [Katkıda Bulunma](#-katkıda-bulunma)

---

## 🎯 Proje Hakkında

**AURA AI**, modern moda dünyasında kişiselleştirilmiş alışveriş deneyimi sunan, yapay zeka destekli kapsamlı bir moda platformudur. Google'ın Gemini AI teknolojisini kullanarak kullanıcılara beden analizi, vücut tipi tespiti ve kişiselleştirilmiş ürün önerileri sunar.

### 🌟 Projenin Vizyonu
- **Kişiselleştirme**: Her kullanıcıya özel moda önerileri
- **Teknoloji**: En gelişmiş AI teknolojilerinin moda ile buluşması  
- **Erişilebilirlik**: Herkesin kullanabileceği sade ve kullanıcı dostu arayüz
- **Doğruluk**: Gerçek marka verileri ile desteklenen analiz sistemi

---

## ✨ Temel Özellikler

### 🤖 AI Destekli Sistemler
- **Gemini Vision AI** ile fotoğraf analizi
- **Gemini AI** ile beden uygunluk analizi  
- **Cinsiyet bazlı** kişiselleştirilmiş chat sistemi
- **Gerçek zamanlı** trend analizi

### 👥 Kullanıcı Deneyimi
- **Cinsiyet seçimi** ile kişiselleştirilmiş deneyim
- **LocalStorage** ile kullanıcı tercihlerinin hatırlanması
- **Responsive tasarım** (mobil & desktop uyumlu)
- **Sosyal paylaşım** sistemi

### 🛍️ E-Ticaret Entegrasyonu
- **4 büyük marka** desteği (Zara, Trendyol, H&M, Bershka)
- **Çalışan ürün linkleri** ile direkt alışveriş
- **Gerçek zamanlı fiyat** bilgileri
- **Marka bazlı beden karşılaştırması**

### 📊 Analiz Sistemleri
- **BMI hesaplama** ve sağlık önerileri
- **Vücut tipi tespiti** (Rectangle, Pear, Apple, Hourglass, Athletic)
- **Beden uygunluk analizi** (Bu beden bana uyar mı?)
- **Marka karşılaştırma** sistemi

---

## 🛠️ Teknoloji Yığını

### Frontend (React + TypeScript)
```
├── React 18+ (Modern UI Framework)
├── TypeScript (Type Safety)
├── CSS3 (Professional Styling)
├── Responsive Design (Mobile-First)
└── LocalStorage (User Preferences)
```

### Backend (Python + FastAPI)
```
├── FastAPI (High-Performance API)
├── Python 3.8+ (Core Logic)
├── Pydantic (Data Validation)
├── SQLite (Trend Analytics)
└── CORS (Cross-Origin Support)
```

### AI & External Services
```
├── Google Gemini AI (Vision & Text Analysis)
├── Google Gemini Vision (Photo Analysis)
├── Web Scraping (Product Data)
└── Real-time Trend Analysis
```

### DevOps & Tools
```
├── Git (Version Control)
├── GitHub (Repository Management)
├── Environment Variables (Secure Configuration)
└── Professional Documentation
```

---

## 🚀 Kurulum ve Çalıştırma

### Ön Gereksinimler
- **Node.js** 16+ 
- **Python** 3.8+
- **Google Gemini API Key** ([Buradan alın](https://ai.google.dev))

### 1. Repository'yi Klonlayın
```bash
git clone https://github.com/yourusername/aura-ai.git
cd aura-ai
```

### 2. Backend Kurulumu
```bash
# Backend dizinine gidin
cd backend

# Python sanal ortamı oluşturun
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Gerekli paketleri yükleyin
pip install -r requirements.txt

# Environment dosyası oluşturun
cp .env.example .env
# .env dosyasına GEMINI_API_KEY'inizi ekleyin

# Backend'i başlatın
python main.py
```

### 3. Frontend Kurulumu
```bash
# Ana dizine dönün
cd ..

# Node.js paketlerini yükleyin
npm install

# Frontend'i başlatın
npm start
```

### 4. Erişim
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 📖 Detaylı Özellik Açıklamaları

### 🎭 1. Splash Screen (Hoş Geldin Ekranı)
**Amaç**: Kullanıcıyı karşılayan etkileyici giriş sayfası

**Özellikler**:
- **AURA logosu** ile marka kimliği
- **Animasyonlu tasarım** ile profesyonel görünüm
- **"Auranı değiştirelim mi?"** sloganı
- **Smooth geçiş** ana sayfaya

### 🏠 2. Ana Sayfa (Dashboard)
**Amaç**: Tüm özelliklere erişim merkezi

**Bileşenler**:
- **Trend Analizi Bölümü**: Bu haftanın popüler ürünleri
- **Analiz Seçim Kartları**: 4 ana özelliğe hızlı erişim
- **Geçmiş Butonu**: Kullanıcının analiz geçmişi
- **Responsive Grid**: Mobil uyumlu kart düzeni

### 📸 3. Fotoğraf Analizi Sistemi
**Amaç**: Gemini Vision AI ile vücut tipi analizi

**Teknoloji**: Google Gemini Vision API

**İşleyiş**:
1. **Fotoğraf Yükleme**: Drag & drop veya click to upload
2. **AI Analizi**: Gemini Vision ile görsel işleme
3. **Vücut Tipi Tespiti**: Rectangle, Pear, Apple, Hourglass, Athletic
4. **Kıyafet Önerileri**: Vücut tipine uygun stil tavsiyeleri
5. **Marka Seçimi**: 4 büyük markadan ürün önerisi
6. **Paylaşım**: Sosyal medyada analiz sonucu paylaşma

**Vücut Tipleri**:
- **Rectangle**: Düz vücut hatları, bel vurgusu önerileri
- **Pear**: Alt genişlik, omuz detaylı kıyafet önerileri
- **Apple**: Üst genişlik, empire bel önerileri
- **Hourglass**: Kum saati, fitted kıyafet önerileri  
- **Athletic**: Atletik yapı, feminen detay önerileri

### 📏 4. Beden Analizi Sistemi
**Amaç**: "Bu beden bana uyar mı?" sorusuna AI cevabı

**Input Parametreleri**:
- **Cinsiyet**: Kadın/Erkek seçimi
- **Boy**: cm cinsinden (100-250)
- **Kilo**: kg cinsinden (30-200)
- **Marka**: Zara, Trendyol, H&M, Bershka
- **Ürün**: Ürün adı (tişört, jean, elbise vb.)
- **Beden**: XS, S, M, L, XL, XXL

**AI Analizi**:
- **BMI Hesaplama**: Vücut kitle indeksi
- **Marka Özellikleri**: Her markanın kesim özelliklerini dikkate alma
- **Beden Uygunluğu**: Seçilen bedenin uygunluk oranı
- **Alternatif Öneriler**: Daha uygun beden tavsiyeleri
- **Sağlık Tavsiyeleri**: BMI bazlı genel sağlık önerileri

### 🤖 5. AI Stil Danışmanı (Chat Sistemi)
**Amaç**: Kişiselleştirilmiş moda danışmanlığı

**Yenilikçi Özellikler**:
#### 👥 Cinsiyet Bazlı Sistem
- **Cinsiyet Seçimi**: İlk girişte kadın/erkek seçimi
- **Kişiselleştirilmiş Arayüz**: Seçilen cinsiyete göre özelleşen UI
- **LocalStorage Hafıza**: Kullanıcı tercihinin hatırlanması
- **Cinsiyet Değiştirme**: İstediğinde farklı kategoriye geçiş

#### 💬 Gelişmiş Chat Arayüzü
- **AI Düşünme Animasyonları**: Gerçekçi bekleme deneyimi
- **Dinamik Mesajlar**: "Stil danışmanınız düşünüyor..." rotasyonu
- **Typing Indicator**: Yazma animasyonu
- **Mesaj Geçmişi**: Konuşma hafızası

#### 🛍️ Akıllı Ürün Önerileri
- **Cinsiyet Bazlı Arama**: Seçilen cinsiyete göre ürün filtreleme
- **Çalışan Linkler**: Tüm ürün linkleri gerçek sitelere yönlendirme
- **Match Score**: Ürün uygunluk yüzdesi
- **Marka Çeşitliliği**: 4 farklı markadan seçenekler

**Örnek Kullanım Senaryoları**:
```
👩 Kadın Kullanıcı:
"200 TL altında yaz için hafif elbiseler"
→ AI: Kadın kategorisinden elbise önerileri

👨 Erkek Kullanıcı:  
"İş için düz renk gömlekler"
→ AI: Erkek kategorisinden gömlek önerileri
```

### 📊 6. Beden Rehberi Sistemi
**Amaç**: Markalar arası beden karşılaştırması

**Kapsamlı Veri**:
- **Gerçek Araştırma**: Her marka için gerçek beden ölçümleri
- **Cinsiyet Ayrımı**: Kadın ve erkek için ayrı tablolar
- **Marka Özel İpuçları**: Her markanın kesim özelliklerini açıklama
- **İnteraktif Tablolar**: Hover efektleri ile gelişmiş UX

**Desteklenen Markalar ve Özellikler**:
- **Zara**: Dar kesim, 1 beden büyük önerisi
- **Trendyol**: Geniş kesim, 1-2 beden küçük önerisi
- **H&M**: Sayısal sistem, standart Avrupa bedenleri
- **Bershka**: Genç kesim, standart ölçüler

### 📈 7. Trend Analizi Sistemi
**Amaç**: Gerçek zamanlı moda trend takibi

**Teknoloji**:
- **SQLite Veritabanı**: Trend verilerinin saklanması
- **Haftalık Analiz**: Haftanın popüler ürünleri
- **AI Trend Yorumları**: Gemini AI ile trend analizi
- **Dinamik Güncellemeler**: Gerçek zamanlı veri

**Trend Verileri**:
- **Ürün Adı**: En çok aranan ürünler
- **Marka Dağılımı**: Hangi marka ne kadar popüler
- **Trend Skoru**: Popülerlik yüzdesi
- **Fiyat Aralıkları**: Trend ürünlerin fiyat bantları

### 📱 8. Sosyal Paylaşım Sistemi
**Amaç**: Analiz sonuçlarının sosyal medyada paylaşılması

**Paylaşım Türleri**:
- **Beden Analizi**: BMI ve beden uygunluk sonuçları
- **Fotoğraf Analizi**: Vücut tipi analiz sonuçları
- **Chat Önerileri**: AI'ın ürün önerilerini paylaşma
- **Trend Analizleri**: Haftalık trend verilerini paylaşma

**Desteklenen Platformlar**:
- **Native Share API**: Mobil cihazlarda sistem paylaşımı
- **Twitter**: Direkt tweet özelliği
- **Facebook**: Facebook paylaşımı
- **WhatsApp**: Mesaj olarak paylaşım
- **LinkedIn**: Profesyonel ağda paylaşım
- **Clipboard**: Kopyala-yapıştır

### 📜 9. Analiz Geçmişi Sistemi
**Amaç**: Kullanıcının tüm analizlerinin saklanması

**Saklanan Veriler**:
- **Beden Analizleri**: Tarih, ölçüler, sonuçlar
- **Fotoğraf Analizleri**: Vücut tipi, AI yorumları
- **Zaman Damgaları**: Türkçe tarih formatında
- **Sonuç Özetleri**: Hızlı görüntüleme için kısa özet

**Özellikler**:
- **LocalStorage**: Tarayıcı bazlı saklama
- **Son 10 Analiz**: Performans için sınırlı saklama
- **Geçmiş Temizleme**: İsteğe bağlı tüm geçmişi silme
- **Detaylı Görüntüleme**: Her analizin tam detayları

---

## 🔌 API Endpoint'leri

### Ana Endpoint'ler

#### `POST /analyze-size`
**Amaç**: Beden uygunluk analizi
```json
{
  "user_height": 175,
  "user_weight": 70,
  "product_name": "Basic T-Shirt",
  "product_size": "M",
  "brand": "Zara",
  "gender": "kadın"
}
```

#### `POST /analyze-photo`
**Amaç**: Fotoğraf analizi (Multipart form-data)
```
Form-data:
- file: Image file (JPG, PNG)
```

#### `POST /get-products`
**Amaç**: Marka bazlı ürün önerileri
```json
{
  "brand": "Zara",
  "body_type": "Rectangle",
  "category": "woman"
}
```

#### `POST /chat-product-search`
**Amaç**: AI chat sistemi
```json
{
  "message": "200 TL altında tişört arıyorum",
  "conversation_id": "optional",
  "user_gender": "kadın"
}
```

#### `POST /get-trends`
**Amaç**: Trend analizi
```json
{
  "category": "optional",
  "body_type": "optional", 
  "price_range": "optional"
}
```

### Hata Yönetimi
- **429**: Rate limit aşıldı (Gemini API quota)
- **503**: AI servisi geçici olarak kullanılamıyor
- **400**: Geçersiz input parametreleri
- **500**: Sunucu hatası

---

## 👤 Kullanıcı Rehberi

### 🚀 İlk Kullanım
1. **Splash Screen**: "Hadi" butonuna tıklayın
2. **Ana Sayfa**: İstediğiniz analiz türünü seçin
3. **Özellik Kullanımı**: Rehberleri takip edin

### 📸 Fotoğraf Analizi Nasıl Yapılır?
1. **Fotoğraf Analizi** kartına tıklayın
2. **Fotoğraf seçin** (iyi ışıklı, tam vücut fotoğrafı önerilir)
3. **AI analizini bekleyin** (15-30 saniye)
4. **Sonuçları inceleyin** (vücut tipi, öneriler)
5. **Marka seçin** ürün önerileri için
6. **Paylaşın** veya başka analiz yapın

### 📏 Beden Analizi Nasıl Yapılır?
1. **Beden Analizi** kartına tıklayın
2. **Bilgilerinizi girin**:
   - Cinsiyet seçin
   - Boy ve kilo bilgilerinizi girin
   - İlgilendiğiniz markayı yazın
   - Ürün adını belirtin
   - Denemek istediğiniz bedeni seçin
3. **AI analizi bekleyin**
4. **BMI ve beden uygunluk** sonuçlarını inceleyin
5. **Paylaşın** veya tekrar analiz yapın

### 🤖 AI Chat Nasıl Kullanılır?
1. **AI Ürün Asistanı** kartına tıklayın
2. **Cinsiyetinizi seçin** (Kadın/Erkek)
3. **İstediğiniz ürünü tanımlayın**:
   - "200 TL altında casual tişört"
   - "İş için şık pantolon" 
   - "Yaz için hafif elbiseler"
4. **AI önerilerini inceleyin**
5. **Ürün linklerine tıklayarak** alışveriş yapın
6. **Cinsiyeti değiştirme** butonuyla farklı kategorilere geçin

### 📊 Beden Rehberi Nasıl Kullanılır?
1. **Beden Rehberi** kartına tıklayın
2. **Cinsiyetinizi seçin** (tablo değişir)
3. **Soldaki sütundan** bildiğiniz bedeninizi bulun
4. **Sağdaki sütunlarda** diğer markalardaki karşılığını görün
5. **Marka özel ipuçlarını** okuyun

---

## 🏗️ Teknik Mimari

### Frontend Mimarisi
```
src/
├── App.tsx              # Ana component ve state yönetimi
├── App.css              # Professional CSS architecture
└── index.tsx            # React DOM root
```

**State Management**:
- **React Hooks**: useState, useEffect, useRef
- **LocalStorage**: Kullanıcı tercihleri
- **Component State**: Sayfa bazlı state yönetimi

### Backend Mimarisi
```
backend/
├── main.py              # FastAPI ana uygulaması
├── product_scraper.py   # Web scraping ve ürün veritabanı
├── requirements.txt     # Python dependencies
└── .env                 # Environment variables
```

**Database Schema**:
```sql
-- Trend takibi
CREATE TABLE product_trends (
    id INTEGER PRIMARY KEY,
    product_name TEXT,
    brand TEXT,
    category TEXT,
    search_count INTEGER,
    body_type TEXT,
    week_number INTEGER
);

-- Trend analitiği
CREATE TABLE trend_analytics (
    id INTEGER PRIMARY KEY,
    trend_type TEXT,
    trend_data TEXT,
    week_number INTEGER,
    created_at TIMESTAMP
);
```

### AI Entegrasyonu
**Gemini AI Kullanımı**:
- **Vision API**: Fotoğraf analizi için
- **Text API**: Beden analizi ve chat için
- **Error Handling**: Quota ve hata yönetimi
- **Fallback Systems**: AI servis kesildiğinde alternatif cevaplar

### Güvenlik ve Performans
- **API Key Security**: Environment variables ile korunma
- **CORS Configuration**: Cross-origin güvenliği
- **Rate Limiting**: API abuse korunması
- **Input Validation**: Pydantic ile veri doğrulama
- **Error Boundaries**: Frontend hata yakalama

---

## 🎨 Tasarım ve UX

### Renk Paleti (Brown Minimalist Theme)
```css
--primary: #8B4513        /* Ana kahverengi */
--primary-light: #A0522D  /* Açık kahverengi */
--surface: #FEFCF8        /* Ana yüzey */
--background: #F8F6F0     /* Arka plan */
--text-primary: #2D1B14   /* Ana metin */
```

### Typography
- **Font Family**: Inter (Modern, clean, readable)
- **Font Weights**: 300, 400, 500, 600, 700
- **Line Height**: 1.5 (optimal readability)
- **Letter Spacing**: Başlıklarda özel spacing

### Animasyonlar
- **Splash Animations**: Logo rotation, glow effects
- **Page Transitions**: Smooth slide animations
- **Loading States**: Realistic AI thinking animations
- **Hover Effects**: Interactive feedback
- **Micro-interactions**: Button animations, card lifts

### Responsive Design
- **Mobile First**: 480px, 768px, 1024px breakpoints
- **Flexible Grids**: CSS Grid ve Flexbox
- **Touch Friendly**: 44px minimum touch targets
- **Readable Fonts**: Scalable typography

---

## 📱 Ekran Görüntüleri

### Desktop Görünümler
- **Splash Screen**: Etkileyici giriş sayfası
- **Dashboard**: Trend analizi ve özellik kartları
- **Photo Analysis**: Fotoğraf yükleme ve AI analizi
- **Size Analysis**: Form ve sonuç ekranları
- **Chat Interface**: Cinsiyet seçimi ve AI chat
- **Size Guide**: İnteraktif beden tabloları

### Mobile Görünümler
- **Responsive Layout**: Tüm ekranlar mobil uyumlu
- **Touch Navigation**: Mobil dostu navigasyon
- **Optimized Forms**: Mobil form deneyimi
- **Native Sharing**: Mobil paylaşım API'si

---

## 🚀 Performans ve Optimizasyon

### Frontend Performansı
- **Code Splitting**: Lazy loading implementasyonu
- **Image Optimization**: Optimized placeholder images
- **CSS Optimization**: Minimal CSS, no unused styles
- **Bundle Size**: Optimized React build

### Backend Performansı
- **FastAPI**: High-performance async framework
- **Database Optimization**: Indexed queries
- **Caching**: In-memory conversation storage
- **Error Handling**: Graceful error responses

### AI Optimizasyonu
- **Prompt Engineering**: Optimized AI prompts
- **Response Caching**: Similar query caching
- **Fallback Systems**: Non-AI alternatives
- **Quota Management**: Smart API usage

---

## 🔮 Gelecek Planları

### Kısa Vadeli (1-3 Ay)
- **Daha Fazla Marka**: Mango, Pull&Bear, Stradivarius ekleme
- **Gelişmiş AI**: Daha detaylı vücut analizi
- **Mobil App**: React Native uygulaması
- **User Authentication**: Kullanıcı hesap sistemi

### Orta Vadeli (3-6 Ay)
- **Sanal Provam**: AR ile sanal giyim denemesi
- **Kişisel Stil Profili**: Uzun vadeli stil analizi
- **Sosyal Özellikler**: Kullanıcı toplulukları
- **Premium Features**: Abonelik modeli

### Uzun Vadeli (6+ Ay)
- **Global Expansion**: Uluslararası marka desteği
- **AI Fashion Designer**: AI ile tasarım önerileri
- **Sustainability Score**: Sürdürülebilirlik analizi
- **Enterprise Solutions**: B2B çözümler

---

## 🤝 Katkıda Bulunma

### Nasıl Katkıda Bulunabilirsiniz?
1. **Fork** edin repository'yi
2. **Feature branch** oluşturun (`git checkout -b feature/amazing-feature`)
3. **Commit** edin değişikliklerinizi (`git commit -m 'Add amazing feature'`)
4. **Push** edin branch'inizi (`git push origin feature/amazing-feature`)
5. **Pull Request** açın

### Geliştirme Rehberi
- **Code Style**: TypeScript ve Python best practices
- **Testing**: Unit testler ekleyin
- **Documentation**: README'yi güncelleyin
- **AI Ethics**: Responsible AI practices

---

## 📄 Lisans ve Telif Hakkı

Bu proje **MIT Lisansı** altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakınız.

### Kullanılan Teknolojiler
- **React**: Meta (Facebook) - MIT License
- **FastAPI**: Sebastián Ramirez - MIT License  
- **Google Gemini AI**: Google LLC - Terms of Service
- **Inter Font**: Rasmus Andersson - SIL Open Font License

---

## 📞 İletişim ve Destek

### Proje Geliştiricisi
- **GitHub**: [@yourusername](https://github.com/yourusername)
- **Email**: your.email@example.com
- **LinkedIn**: [Your LinkedIn Profile](https://linkedin.com/in/yourprofile)

### Destek ve Geri Bildirim
- **Issues**: GitHub Issues üzerinden bug raporu
- **Feature Requests**: Yeni özellik önerileri
- **General Questions**: Email veya LinkedIn üzerinden

---

## 🏆 Teşekkürler

### Kullanılan Açık Kaynak Projeleri
- **React Ecosystem**: Modern web development
- **Python Community**: Backend development
- **Google AI**: Gemini API access
- **Open Source Contributors**: Inspiration and tools

### Özel Teşekkürler
Bu projeyi geliştirirken ilham aldığımız tüm açık kaynak projelerine, AI/ML topluluğuna ve moda teknolojisi alanındaki yenilikçilere teşekkürlerimi sunarım.

---

<div align="center">

**🎯 AURA AI - "Auranı değiştirelim mi?"**

[![GitHub Stars](https://img.shields.io/github/stars/yourusername/aura-ai?style=social)](https://github.com/yourusername/aura-ai/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/yourusername/aura-ai?style=social)](https://github.com/yourusername/aura-ai/network/members)

*Made with ❤️ by Baran Mert Aral - Türkiye*

</div>
