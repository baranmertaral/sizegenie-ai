from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import google.generativeai as genai
from PIL import Image
import io
import os
import uuid
import time
import json
import re
import sqlite3
from datetime import datetime, timedelta
from collections import Counter
from dotenv import load_dotenv
from product_scraper import ProductScraper

# Environment variables yükle
load_dotenv()

# GEMINI_API_KEY kontrolü
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_AVAILABLE = False

if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        vision_model = genai.GenerativeModel('gemini-1.5-flash')
        GEMINI_AVAILABLE = True
        print("✅ Gemini Vision AI aktif - Gerçek analiz hazır!")
    except Exception as e:
        print(f"⚠️ Gemini API hatası: {e}")
        GEMINI_AVAILABLE = False
else:
    print("⚠️ GEMINI_API_KEY bulunamadı - AI özellikleri sınırlı!")

app = FastAPI()

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Product scraper instance
scraper = ProductScraper()

# Database initialization for trends
def init_trends_db():
    conn = sqlite3.connect('trends.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS product_trends (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT,
        brand TEXT,
        category TEXT,
        search_count INTEGER DEFAULT 1,
        body_type TEXT,
        price_range TEXT,
        colors TEXT,
        date_added DATE,
        week_number INTEGER
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS trend_analytics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trend_type TEXT,
        trend_data TEXT,
        week_number INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

# App başlangıcında trends database'ini başlat
init_trends_db()

# Trend tracking fonksiyonları
def track_product_search(product_name, brand, category, body_type=None, price_range=None):
    """Her ürün aramasını kaydet"""
    try:
        conn = sqlite3.connect('trends.db')
        cursor = conn.cursor()
        
        current_week = datetime.now().isocalendar()[1]  # Haftanın numarası
        
        # Aynı ürün bu hafta aranmış mı?
        cursor.execute('''
        SELECT id, search_count FROM product_trends 
        WHERE product_name = ? AND brand = ? AND week_number = ?
        ''', (product_name, brand, current_week))
        
        existing = cursor.fetchone()
        
        if existing:
            # Arama sayısını artır
            cursor.execute('''
            UPDATE product_trends 
            SET search_count = search_count + 1 
            WHERE id = ?
            ''', (existing[0],))
        else:
            # Yeni kayıt ekle
            cursor.execute('''
            INSERT INTO product_trends 
            (product_name, brand, category, body_type, price_range, date_added, week_number)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (product_name, brand, category, body_type, price_range, datetime.now().date(), current_week))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Trend tracking error: {e}")
        return False

def get_weekly_trends(category=None, body_type=None, limit=10):
    """Bu haftanın trend ürünlerini getir"""
    try:
        conn = sqlite3.connect('trends.db')
        cursor = conn.cursor()
        
        current_week = datetime.now().isocalendar()[1]
        
        query = '''
        SELECT product_name, brand, category, SUM(search_count) as total_searches,
               body_type, price_range
        FROM product_trends 
        WHERE week_number = ?
        '''
        params = [current_week]
        
        if category:
            query += ' AND category LIKE ?'
            params.append(f'%{category}%')
            
        if body_type:
            query += ' AND body_type = ?'
            params.append(body_type)
        
        query += ' GROUP BY product_name, brand ORDER BY total_searches DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        trends = []
        for row in results:
            trends.append({
                'product_name': row[0],
                'brand': row[1],
                'category': row[2],
                'search_count': row[3],
                'body_type': row[4],
                'price_range': row[5],
                'trend_score': min(100, (row[3] * 10))  # Basit trend skoru
            })
        
        conn.close()
        return trends
    except Exception as e:
        print(f"Get trends error: {e}")
        return []

# UPDATED: Full SizeRequest - specific product analysis
class SizeRequest(BaseModel):
    user_height: int
    user_weight: int
    product_name: str
    product_size: str
    brand: str
    gender: str

class ProductRequest(BaseModel):
    brand: str
    body_type: str
    category: str = "woman"

# YENİ: Trend Request Model
class TrendRequest(BaseModel):
    category: Optional[str] = None
    body_type: Optional[str] = None
    price_range: Optional[str] = None

# Chat models
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    user_feedback: Optional[str] = None

class ChatResponse(BaseModel):
    ai_response: str
    products: List[dict]  
    conversation_id: str
    success: bool

# Conversation memory
conversation_memory = {}

@app.post("/analyze-size")
def analyze_size(request: SizeRequest):
    """AI beden analizi endpoint'i - 'BU BEDEN BANA UYAR MI?' SORGUSU"""
    try:
        # Trend tracking ekle
        track_product_search(
            product_name=request.product_name,
            brand=request.brand,
            category="size_analysis",
            body_type=f"{request.gender}_{request.user_height}_{request.user_weight}"
        )
        
        # Cinsiyet bilgisini kullan
        gender_text = "kadın" if request.gender == "kadın" else "erkek"
        
        # Cinsiyet-spesifik beden analizi
        if request.gender == "kadın":
            gender_advice = """
            Kadın beden ölçümleri için dikkat edilecekler:
            - Göğüs, bel ve kalça ölçüleri arasındaki uyum
            - Vücut tipine göre (armut, elma, kum saati) farklı uyum
            - Kadın kıyafetları genelde vücut formuna göre tasarlanır
            """
        else:
            gender_advice = """
            Erkek beden ölçümleri için dikkat edilecekler:
            - Omuzlar ve göğüs genişliği temel ölçüm
            - Bel çevresi daha stabil olur
            - Erkek kıyafetları genelde daha geniş kesimli
            """
        
        if GEMINI_AVAILABLE:
            prompt = f"""
            Sen bir kıyafet beden uzmanısın. Kullanıcı belirli bir ürün ve beden için uygunluk analizi istiyor.

            Kullanıcı Bilgileri:
            - Cinsiyet: {gender_text}
            - Boy: {request.user_height} cm
            - Kilo: {request.user_weight} kg
            - İstediği Marka: {request.brand}
            - İstediği Ürün: {request.product_name} 
            - Denemek İstediği Beden: {request.product_size}

            {gender_advice}

            SORU: "{request.brand} markasının {request.product_name} ürününde {request.product_size} bedeni bu {gender_text}'a uyar mı?"

            Lütfen:
            1. BMI hesapla ve değerlendir
            2. Bu {gender_text} için {request.product_size} bedeninin uygun olup olmadığını söyle
            3. {request.brand} markasının beden özelliklerini biliyorsen dikkate al
            4. Alternatif beden önerileri yap (daha büyük/küçük)
            5. Bu ürün türü için özel tavsiyelerde bulun
            6. MARKA ÖNERİSİ YAPMA - sadece verilen markadaki ürün için analiz yap

            "EVET uyar" veya "HAYIR uyar" şeklinde net cevap ver, sonra açıklama yap.
            Türkçe, samimi ve yardımsever bir dilde cevap ver.
            """
            
            try:
                response = model.generate_content(prompt)
                recommendation = response.text
                ai_type = "real_gemini_specific"
            except Exception as e:
                if "quota" in str(e).lower():
                    bmi = request.user_weight / ((request.user_height/100)**2)
                    
                    # Basit beden uygunluk mantığı
                    if bmi < 18.5:
                        if request.product_size in ['XS', 'S']:
                            fit_result = "✅ EVET, bu beden size uyar"
                        else:
                            fit_result = "⚠️ Daha küçük beden deneyin (XS-S)"
                    elif bmi < 25:
                        if request.product_size in ['S', 'M']:
                            fit_result = "✅ EVET, bu beden size uyar"
                        else:
                            fit_result = "⚠️ S-M bedenleri daha uygun olabilir"
                    elif bmi < 30:
                        if request.product_size in ['M', 'L']:
                            fit_result = "✅ EVET, bu beden size uyar"
                        else:
                            fit_result = "⚠️ M-L bedenleri daha uygun olabilir"
                    else:
                        if request.product_size in ['L', 'XL', 'XXL']:
                            fit_result = "✅ EVET, bu beden size uyar"
                        else:
                            fit_result = "⚠️ Daha büyük beden deneyin (L-XL)"
                    
                    recommendation = f"""📊 BMI Hesabı: {bmi:.1f}

🎯 {request.brand} {request.product_name} - {request.product_size} Beden Analizi:

{fit_result}

👤 {gender_text.title()} vücut yapısı için:
{gender_advice.strip()}

💡 Bu analiz genel bir rehberdir. Deneme yapmanız en doğru sonucu verir."""
                    ai_type = "quota_limited_specific"
                else:
                    raise e
        else:
            # Fallback AI cevabı
            bmi = request.user_weight / ((request.user_height/100)**2)
            recommendation = f"""📊 BMI: {bmi:.1f}
🎯 {request.brand} {request.product_name} için {request.product_size} bedeni
👤 {gender_text.title()} vücut yapısına göre değerlendirme yapıldı.
💡 Genel olarak uygun görünüyor, deneme yapabilirsiniz."""
            ai_type = "fallback_specific"
            
        return {
            "success": True,
            "recommendation": recommendation,
            "ai_type": ai_type,
            "bmi": request.user_weight / ((request.user_height/100)**2),
            "gender": request.gender,
            "analysis_type": "specific_product_fit",
            "queried_product": f"{request.brand} {request.product_name} ({request.product_size})"
        }
        
    except Exception as e:
        print(f"Size analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-photo")
async def analyze_photo(file: UploadFile = File(...)):
    """AI fotoğraf analizi endpoint'i"""
    try:
        # Dosya kontrolleri
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Geçerli bir resim dosyası yükleyin")
        
        # Resmi oku ve işle
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Trend tracking ekle
        track_product_search(
            product_name="Photo Analysis",
            brand="AURA",
            category="photo_analysis",
            body_type="analysis_request"
        )
        
        if GEMINI_AVAILABLE:
            prompt = """
            Bu fotoğrafı analiz et ve şunları belirle:

            1. 👤 Cinsiyet (Erkek/Kadın)
            2. 🔹 Vücut tipi (Rectangle, Pear, Apple, Hourglass, Athletic)
            3. 📏 Genel vücut yapısı
            4. 🎯 Bu vücut tipi için en uygun kıyafet önerileri

            Format:
            👤 **Cinsiyet:** [Kadın/Erkek]
            🔹 **Vücut Tipi:** [Tip]
            📝 **Açıklama:** Bu vücut tipi [detaylı açıklama]
            🎯 **Öneriler:** [Cinsiyete özel kıyafet önerileri]

            Türkçe, profesyonel ama samimi bir dille yaz.
            Cinsiyet tespitine özel dikkat et çünkü beden önerileri cinsiyete göre değişir.
            """
            
            try:
                response = vision_model.generate_content([prompt, image])
                analysis = response.text
                ai_type = "real_gemini_vision"
            except Exception as e:
                if "quota" in str(e).lower():
                    analysis = """👤 **Cinsiyet:** Kadın
🔹 **Vücut Tipi:** Rectangle
📝 **Açıklama:** Bu vücut tipi dengeli omuz ve kalça ölçülerine sahip, bel çizgisi belirgin olmayan klasik bir yapıdır.
🎯 **Öneriler:** A-line elbiseler, yüksek bel pantolonlar, bel vurgulu kıyafetler, fit & flare kesimler, katmanlı giysiler önerilir."""
                    ai_type = "quota_limited_vision"
                else:
                    raise e
        else:
            # Fallback analiz
            analysis = """👤 **Cinsiyet:** Kadın
🔹 **Vücut Tipi:** Rectangle
📝 **Açıklama:** Klasik vücut yapısı analizi
🎯 **Öneriler:** Çeşitli kıyafet stilleri yakışır."""
            ai_type = "fallback_vision"
        
        return {
            "success": True,
            "analysis": analysis,
            "ai_type": ai_type
        }
        
    except Exception as e:
        print(f"Photo analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get-products")
def get_products(request: ProductRequest):
    """Dinamik ürün önerileri - SADECE 4 MARKA"""
    try:
        print(f"\n🛍️ === {request.brand} İSTEĞİ ===")
        print(f"Body type: {request.body_type}")
        print(f"Category: {request.category}")
        
        # SADECE 4 MARKA KONTROLÜ
        allowed_brands = ['Zara', 'Trendyol', 'H&M', 'Bershka']
        if request.brand not in allowed_brands:
            print(f"❌ {request.brand} desteklenmiyor. Sadece şu markalar var: {allowed_brands}")
            return {
                "success": False,
                "products": [],
                "ai_recommendation": f"{request.brand} şu anda desteklenmiyor. Mevcut markalar: {', '.join(allowed_brands)}",
                "brand": request.brand,
                "product_count": 0
            }
        
        # TREND TRACKING EKLE
        track_product_search(
            product_name=f"{request.brand} products", 
            brand=request.brand,
            category=request.category,
            body_type=request.body_type
        )
        
        # Dinamik ürün çekme
        products = scraper.get_products_by_brand(
            brand=request.brand,
            category=request.category,
            analysis_text=request.body_type,
            limit=6
        )
        
        print(f"✅ Döndürülen ürün sayısı: {len(products)}")
        
        if not products:
            print(f"❌ {request.brand} için ürün bulunamadı")
            return {
                "success": False,
                "products": [],
                "ai_recommendation": f"{request.brand} ürünleri şu anda yüklenemiyor.",
                "brand": request.brand,
                "product_count": 0
            }
        
        # AI recommendation
        recommendation = f"🎯 {request.brand} markasından vücut tipinize uygun özel seçim!"
        
        return {
            "success": True,
            "products": products,
            "ai_recommendation": recommendation,
            "brand": request.brand,
            "product_count": len(products),
            "is_dynamic": True,
            "available_brands": allowed_brands
        }
        
    except Exception as e:
        print(f"❌ HATA: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "products": [],
            "ai_recommendation": f"Hata: {str(e)}",
            "brand": request.brand,
            "product_count": 0
        }

# YENİ: Trend Analizi Endpoint
@app.post("/get-trends")
def get_trends(request: TrendRequest):
    """Trend analizi endpoint'i - SADECE 4 MARKA"""
    try:
        # Bu haftanın trendlerini getir
        weekly_trends = get_weekly_trends(
            category=request.category,
            body_type=request.body_type,
            limit=8
        )
        
        # Eğer gerçek veri yoksa mock data döndür - SADECE 4 MARKA
        if not weekly_trends:
            mock_trends = [
                {
                    "product_name": "Oversized Basic Tişört",
                    "brand": "Zara",
                    "category": "tişört",
                    "search_count": 45,
                    "trend_score": 85,
                    "price_range": "89-159 TL"
                },
                {
                    "product_name": "Wide Leg Jean",
                    "brand": "Trendyol", 
                    "category": "pantolon",
                    "search_count": 38,
                    "trend_score": 76,
                    "price_range": "139-199 TL"
                },
                {
                    "product_name": "Basic Cotton Tee",
                    "brand": "H&M",
                    "category": "tişört", 
                    "search_count": 32,
                    "trend_score": 68,
                    "price_range": "79-149 TL"
                },
                {
                    "product_name": "Streetwear Hoodie",
                    "brand": "Bershka",
                    "category": "hoodie",
                    "search_count": 29,
                    "trend_score": 65,
                    "price_range": "159-229 TL"
                },
                {
                    "product_name": "High Waist Jean",
                    "brand": "Zara",
                    "category": "pantolon",
                    "search_count": 24,
                    "trend_score": 58,
                    "price_range": "259-399 TL"
                }
            ]
            weekly_trends = mock_trends
        
        # Trend insights oluştur
        if GEMINI_AVAILABLE:
            try:
                insights_prompt = f"""
                Bu hafta en çok aranan ürünler (Sadece Zara, Trendyol, H&M, Bershka):
                {json.dumps(weekly_trends, ensure_ascii=False, indent=2)}
                
                Bu trend verilerine dayanarak:
                1. En popüler kategoriler
                2. Fiyat aralığı trendleri  
                3. Stil önerileri
                4. Bu trendlerin nedenleri
                
                Kısa ve akılda kalır şekilde özetle. Türkçe yaz.
                """
                
                insights_response = model.generate_content(insights_prompt)
                trend_insights = insights_response.text
            except:
                trend_insights = "📈 Bu hafta oversized ve rahat kesimli ürünler trend! Özellikle basic renkler ve minimal tasarımlar öne çıkıyor."
        else:
            trend_insights = "📈 Bu hafta oversized ve rahat kesimli ürünler trend! Özellikle basic renkler ve minimal tasarımlar öne çıkıyor."
        
        return {
            "success": True,
            "trends": weekly_trends,
            "insights": trend_insights,
            "week_number": datetime.now().isocalendar()[1],
            "total_products": len(weekly_trends),
            "supported_brands": ["Zara", "Trendyol", "H&M", "Bershka"]
        }
        
    except Exception as e:
        print(f"Trends API error: {e}")
        return {
            "success": False,
            "trends": [],
            "insights": "Trend verileri şu anda yüklenemiyor.",
            "error": str(e)
        }

@app.post("/chat-product-search")
def chat_product_search(request: ChatRequest):
    """GELIŞMIŞ AI STİL DANIŞMANI - Trend + Kişisel Analiz - SADECE 4 MARKA"""
    try:
        print(f"🤖 AI Stil Danışmanı isteği: {request.message}")
        
        # Trend tracking ekle
        track_product_search(
            product_name="AI Style Consultant",
            brand="AURA_AI",
            category="style_consultation",
            body_type=request.message[:50]  # İlk 50 karakter
        )
        
        # Conversation ID oluştur veya mevcut olanı kullan
        conv_id = request.conversation_id or str(uuid.uuid4())[:8]
        
        # Conversation history'yi al
        if conv_id not in conversation_memory:
            conversation_memory[conv_id] = {
                "messages": [],
                "user_preferences": {},
                "searched_products": [],
                "detected_gender": None,
                "detected_style": None,
                "body_type": None,
                "budget_range": None
            }
        
        conversation = conversation_memory[conv_id]
        
        # Kullanıcı mesajını kaydet
        conversation["messages"].append({
            "role": "user",
            "content": request.message,
            "timestamp": time.time()
        })
        
        # Güncel trend verilerini al
        current_trends = get_weekly_trends(limit=10)
        
        if GEMINI_AVAILABLE:
            # ADIM 1: Gelişmiş kullanıcı analizi
            analysis_prompt = f"""
Sen AURA AI Stil Danışmanısın. Kullanıcının mesajını analiz et: "{request.message}"

Conversation history:
{chr(10).join([f"{msg['role']}: {msg['content']}" for msg in conversation["messages"][-5:]])}

Güncel trend verileri (Sadece Zara, Trendyol, H&M, Bershka):
{json.dumps(current_trends[:5], ensure_ascii=False) if current_trends else "Henüz trend verisi yok"}

Şunları belirle ve JSON formatında döndür:
{{
    "gender": "kadın" veya "erkek",
    "body_type": "rectangle", "pear", "apple", "hourglass", "athletic" veya "unknown",
    "product_type": "tişört", "pantolon", "elbise", "mont", "ayakkabı" vs,
    "style_preferences": ["minimalist", "casual", "elegant", "sporty", "vintage", "trendy"],
    "color_preferences": ["neutral", "bold", "pastel", "dark", "specific_colors"],
    "budget_range": "ekonomik", "orta", "premium" veya rakam varsa o,
    "occasion": "günlük", "iş", "özel", "spor", "gece" vs,
    "season": "kış", "yaz", "sonbahar", "ilkbahar" veya "all",
    "search_intent": "product_search", "style_advice", "trend_info", "size_help",
    "search_keywords": "en uygun arama terimleri"
}}

Sadece JSON döndür.
"""
            
            try:
                analysis_response = model.generate_content(analysis_prompt)
                analysis_text = analysis_response.text.strip()
                
                # JSON parse et
                json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
                if json_match:
                    analysis_data = json.loads(json_match.group())
                else:
                    raise ValueError("JSON parse hatası")
                
                # Tespit edilen bilgileri kaydet
                conversation["detected_gender"] = analysis_data.get("gender", "kadın")
                conversation["detected_style"] = analysis_data.get("style_preferences", [])
                conversation["body_type"] = analysis_data.get("body_type", "unknown")
                conversation["budget_range"] = analysis_data.get("budget_range", "orta")
                
                print(f"🎯 AI Analiz: {analysis_data}")
                
            except Exception as e:
                print(f"⚠️ Analiz hatası: {e}")
                # Fallback analiz
                analysis_data = {
                    "gender": "kadın",
                    "product_type": "kıyafet",
                    "style_preferences": ["casual"],
                    "budget_range": "orta",
                    "search_intent": "product_search",
                    "search_keywords": request.message
                }
                conversation["detected_gender"] = "kadın"
            
            # ADIM 2: AI Stil Danışmanı Cevabı
            style_prompt = f"""
Sen AURA'nın AI Stil Danışmanısın. Profesyonel moda uzmanı gibi davran.

KULLANICI PROFİLİ:
- Cinsiyet: {conversation['detected_gender']}
- Vücut Tipi: {conversation.get('body_type', 'bilinmiyor')}
- Stil Tercihi: {conversation.get('detected_style', [])}
- Bütçe: {conversation.get('budget_range', 'belirtilmedi')}
- Son İstek: {request.message}

GÜNCEL TRENDLER (Bu hafta - Sadece Zara, Trendyol, H&M, Bershka):
{chr(10).join([f"• {t['product_name']} ({t['brand']}) - %{t['trend_score']} trend" for t in current_trends[:3]]) if current_trends else "Trend verileri yükleniyor"}

KULLANICI SORGUSU ANALİZİ:
- Aranan Ürün: {analysis_data.get('product_type', 'genel')}
- Stil Tercihi: {analysis_data.get('style_preferences', [])}
- Renk Tercihi: {analysis_data.get('color_preferences', [])}
- Durum: {analysis_data.get('occasion', 'günlük')}
- Sezon: {analysis_data.get('season', 'mevcut')}

GÖREVİN:
1. Kullanıcının isteğini anlayıp onaylama
2. Vücut tipine uygun önerilerde bulunma
3. Güncel trendleri dahil etme
4. Spesifik marka/renk/stil önerileri (Sadece Zara, Trendyol, H&M, Bershka)
5. Bütçeye uygun seçenekler sunma
6. Kısa ama değerli tavsiyeler verme

CEVAP STILI:
- Samimi ama profesyonel
- 3-4 cümle
- Emoji kullan ama abartma
- Spesifik önerilerde bulun

Conversation history:
{chr(10).join([f"{msg['role']}: {msg['content']}" for msg in conversation["messages"][-3:]])}

Türkçe cevap ver:
"""
            
            try:
                ai_response = model.generate_content(style_prompt)
                ai_message = ai_response.text
                
                # AI cevabını kaydet
                conversation["messages"].append({
                    "role": "assistant", 
                    "content": ai_message,
                    "timestamp": time.time()
                })
                
                print(f"✅ AI Stil Danışmanı cevabı oluşturuldu")
                
            except Exception as e:
                if "quota" in str(e).lower():
                    # Quota limited durumunda akıllı fallback
                    budget_text = f"bütçeniz ({conversation.get('budget_range', 'orta')})" if conversation.get('budget_range') != 'orta' else "bütçenize"
                    trend_text = f"Bu hafta {current_trends[0]['product_name']} çok trend!" if current_trends else "Bu sezon oversized ürünler popüler!"
                    
                    ai_message = f"""🎯 {conversation['detected_gender'].title()} stilinde {analysis_data.get('product_type', 'ürün')} önerisi hazırlıyorum! 
                    
{trend_text} {budget_text} uygun seçenekleri Zara, Trendyol, H&M ve Bershka'dan bulup size sunacağım. 

Hem trendleri hem de {conversation.get('body_type', 'vücut tipinizi')} dikkate alarak en uygun kombinleri öneriyorum! ✨"""
                else:
                    ai_message = f"🤖 {conversation['detected_gender'].title()} için {analysis_data.get('product_type', 'ürün')} önerisi hazırlıyorum!"
        else:
            # Gemini mevcut değilse basit cevap
            ai_message = "🤖 Stil danışmanınız olarak size Zara, Trendyol, H&M ve Bershka'dan en uygun ürünleri buluyorum!"
            analysis_data = {
                "gender": "kadın",
                "product_type": "kıyafet",
                "search_keywords": request.message
            }
            conversation["detected_gender"] = "kadın"
        
        # ADIM 3: AKILLI ÜRÜN ARAMA - SADECE 4 MARKA
        search_query = analysis_data.get("search_keywords", request.message)
        gender = conversation.get("detected_gender", "kadın")
        
        print(f"🔍 AI Stil Araması (Sadece 4 marka): {search_query}")
        
        # Gelişmiş ürün arama (trend + kişisel tercihler) - SADECE 4 MARKA
        all_products = scraper.search_real_products_web(
            search_query=search_query,
            gender=gender, 
            limit=8
        )

        # Ürünleri conversation'a kaydet
        conversation["searched_products"].extend(all_products)
        
        print(f"🛍️ AI Stil Danışmanı {len(all_products)} ürün önerisi buldu (4 markadan)")
        
        return {
            "ai_response": ai_message,
            "products": all_products,
            "conversation_id": conv_id,
            "success": True,
            "style_analysis": {
                "detected_gender": conversation.get("detected_gender"),
                "body_type": conversation.get("body_type"),
                "style_preferences": conversation.get("detected_style"),
                "budget_range": conversation.get("budget_range")
            },
            "current_trends": current_trends[:3] if current_trends else [],
            "search_query": search_query,
            "ai_type": "style_consultant",
            "supported_brands": ["Zara", "Trendyol", "H&M", "Bershka"]
        }
        
    except Exception as e:
        print(f"❌ AI Stil Danışmanı hatası: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "ai_response": f"Üzgünüm, stil danışmanlığında bir sorun oluştu. Lütfen tekrar deneyin.",
            "products": [],
            "conversation_id": request.conversation_id or "error",
            "success": False
        }

@app.get("/")
def read_root():
    return {
        "message": "AURA AI Backend - 4 Marka ile Güçlendirildi! 🎯📈", 
        "status": "running",
        "supported_brands": ["Zara", "Trendyol", "H&M", "Bershka"],
        "total_brands": 4
    }

@app.get("/brands")
def get_supported_brands():
    """Desteklenen markaları döndür"""
    return {
        "success": True,
        "brands": ["Zara", "Trendyol", "H&M", "Bershka"],
        "total": 4,
        "gender_support": {
            "Zara": ["kadın", "erkek"],
            "Trendyol": ["kadın", "erkek"], 
            "H&M": ["kadın", "erkek"],
            "Bershka": ["kadın", "erkek"]
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
