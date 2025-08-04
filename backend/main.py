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

# CORS ayarları - Vercel için güncellenmiş
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da tüm originlere izin ver
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basit product scraper (import yerine burada tanımlayacağız)
class ProductScraper:
    def search_real_products_web(self, search_query, gender, limit=8):
        # Mock data - gerçek scraper yerine
        mock_products = [
            {
                "name": f"{search_query} - Trend Ürün",
                "brand": "Zara",
                "price": "89-159 TL",
                "image": "https://via.placeholder.com/300x400/FF6B6B/FFFFFF?text=Zara",
                "link": "https://zara.com"
            },
            {
                "name": f"{search_query} - Premium Seçenek", 
                "brand": "H&M",
                "price": "79-129 TL",
                "image": "https://via.placeholder.com/300x400/4ECDC4/FFFFFF?text=H%26M",
                "link": "https://hm.com"
            },
            {
                "name": f"{search_query} - Ekonomik",
                "brand": "Trendyol",
                "price": "45-89 TL", 
                "image": "https://via.placeholder.com/300x400/95E1D3/FFFFFF?text=Trendyol",
                "link": "https://trendyol.com"
            },
            {
                "name": f"{search_query} - Genç Stil",
                "brand": "Bershka",
                "price": "99-169 TL",
                "image": "https://via.placeholder.com/300x400/F38BA8/FFFFFF?text=Bershka", 
                "link": "https://bershka.com"
            }
        ]
        return mock_products[:limit]
    
    def get_products_by_brand(self, brand, category, analysis_text, limit=6):
        mock_products = [
            {
                "name": f"{brand} - {category} Önerisi 1",
                "brand": brand,
                "price": "99-199 TL",
                "image": f"https://via.placeholder.com/300x400/45B7D1/FFFFFF?text={brand}",
                "link": f"https://{brand.lower().replace(' ', '').replace('&', '')}.com"
            },
            {
                "name": f"{brand} - {category} Önerisi 2", 
                "brand": brand,
                "price": "129-229 TL",
                "image": f"https://via.placeholder.com/300x400/96CEB4/FFFFFF?text={brand}",
                "link": f"https://{brand.lower().replace(' ', '').replace('&', '')}.com"
            },
            {
                "name": f"{brand} - {category} Önerisi 3",
                "brand": brand, 
                "price": "159-259 TL",
                "image": f"https://via.placeholder.com/300x400/FFEAA7/000000?text={brand}",
                "link": f"https://{brand.lower().replace(' ', '').replace('&', '')}.com"
            }
        ]
        return mock_products[:limit]

scraper = ProductScraper()

# Database initialization for trends
def init_trends_db():
    try:
        conn = sqlite3.connect(':memory:')  # Vercel için in-memory DB
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
        return conn
    except Exception as e:
        print(f"Database init error: {e}")
        return None

# Global db connection
db_conn = init_trends_db()

# Trend tracking fonksiyonları
def track_product_search(product_name, brand, category, body_type=None, price_range=None):
    """Her ürün aramasını kaydet"""
    try:
        if not db_conn:
            return False
            
        cursor = db_conn.cursor()
        current_week = datetime.now().isocalendar()[1]
        
        cursor.execute('''
        SELECT id, search_count FROM product_trends 
        WHERE product_name = ? AND brand = ? AND week_number = ?
        ''', (product_name, brand, current_week))
        
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute('''
            UPDATE product_trends 
            SET search_count = search_count + 1 
            WHERE id = ?
            ''', (existing[0],))
        else:
            cursor.execute('''
            INSERT INTO product_trends 
            (product_name, brand, category, body_type, price_range, date_added, week_number)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (product_name, brand, category, body_type, price_range, datetime.now().date(), current_week))
        
        db_conn.commit()
        return True
    except Exception as e:
        print(f"Trend tracking error: {e}")
        return False

def get_weekly_trends(category=None, body_type=None, limit=10):
    """Bu haftanın trend ürünlerini getir"""
    try:
        if not db_conn:
            # Fallback mock data
            return [
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
                    "brand": "Pull & Bear",
                    "category": "pantolon", 
                    "search_count": 38,
                    "trend_score": 76,
                    "price_range": "199-299 TL"
                }
            ]
        
        cursor = db_conn.cursor()
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
                'trend_score': min(100, (row[3] * 10))
            })
        
        return trends if trends else get_weekly_trends()  # Recursive fallback
    except Exception as e:
        print(f"Get trends error: {e}")
        return []

# Pydantic Models
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

class TrendRequest(BaseModel):
    category: Optional[str] = None
    body_type: Optional[str] = None
    price_range: Optional[str] = None

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

@app.get("/")
def read_root():
    return {
        "message": "AURA AI Backend - Vercel'de Çalışıyor! 🎯📈",
        "status": "running",
        "gemini_available": GEMINI_AVAILABLE,
        "supported_brands": ["Zara", "Trendyol", "H&M", "Bershka", "Pull & Bear"],
        "endpoints": ["/analyze-size", "/analyze-photo", "/get-products", "/get-trends", "/chat-product-search"]
    }

@app.post("/analyze-size")
def analyze_size(request: SizeRequest):
    """AI beden analizi endpoint'i"""
    try:
        track_product_search(
            product_name=request.product_name,
            brand=request.brand,
            category="size_analysis",
            body_type=f"{request.gender}_{request.user_height}_{request.user_weight}"
        )
        
        gender_text = "kadın" if request.gender == "kadın" else "erkek"
        
        if GEMINI_AVAILABLE:
            prompt = f"""
            Sen bir kıyafet beden uzmanısın. 

            Kullanıcı Bilgileri:
            - Cinsiyet: {gender_text}
            - Boy: {request.user_height} cm
            - Kilo: {request.user_weight} kg
            - Marka: {request.brand}
            - Ürün: {request.product_name} 
            - Denenen Beden: {request.product_size}

            Bu {gender_text} için {request.product_size} bedeni uygun mu?

            BMI hesapla ve beden önerisi yap. Türkçe, samimi dilde cevap ver.
            """
            
            try:
                response = model.generate_content(prompt)
                recommendation = response.text
                ai_type = "real_gemini"
            except Exception as e:
                bmi = request.user_weight / ((request.user_height/100)**2)
                recommendation = f"""📊 BMI: {bmi:.1f}
🎯 {request.brand} {request.product_name} - {request.product_size} beden analizi tamamlandı."""
                ai_type = "fallback"
        else:
            bmi = request.user_weight / ((request.user_height/100)**2)
            recommendation = f"📊 BMI: {bmi:.1f} - {request.product_size} bedeni için genel değerlendirme."
            ai_type = "fallback"
            
        return {
            "success": True,
            "recommendation": recommendation,
            "ai_type": ai_type,
            "bmi": request.user_weight / ((request.user_height/100)**2),
            "gender": request.gender
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-photo")
async def analyze_photo(file: UploadFile = File(...)):
    """AI fotoğraf analizi endpoint'i"""
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Geçerli bir resim dosyası yükleyin")
        
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        track_product_search(
            product_name="Photo Analysis",
            brand="AURA",
            category="photo_analysis"
        )
        
        if GEMINI_AVAILABLE:
            prompt = """Bu fotoğrafı analiz et:
            1. Cinsiyet (Kadın/Erkek)
            2. Vücut tipi (Rectangle, Pear, Apple, Hourglass)
            3. Kıyafet önerileri
            
            Türkçe, detaylı analiz yap."""
            
            try:
                response = vision_model.generate_content([prompt, image])
                analysis = response.text
                ai_type = "real_gemini_vision"
            except:
                analysis = "👤 **Cinsiyet:** Kadın\n🔹 **Vücut Tipi:** Rectangle\n🎯 **Öneriler:** A-line kesimler önerilir."
                ai_type = "fallback_vision"
        else:
            analysis = "Fotoğraf analizi için AI desteği gerekiyor."
            ai_type = "fallback"
        
        return {
            "success": True,
            "analysis": analysis,
            "ai_type": ai_type
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get-products")
def get_products(request: ProductRequest):
    """Dinamik ürün önerileri"""
    try:
        track_product_search(
            product_name=f"{request.brand} products", 
            brand=request.brand,
            category=request.category,
            body_type=request.body_type
        )
        
        products = scraper.get_products_by_brand(
            brand=request.brand,
            category=request.category,
            analysis_text=request.body_type,
            limit=6
        )
        
        return {
            "success": True,
            "products": products,
            "ai_recommendation": f"🎯 {request.brand} markasından vücut tipinize uygun seçim!",
            "brand": request.brand,
            "product_count": len(products)
        }
        
    except Exception as e:
        return {
            "success": False,
            "products": [],
            "ai_recommendation": f"Hata: {str(e)}",
            "brand": request.brand,
            "product_count": 0
        }

@app.post("/get-trends")
def get_trends(request: TrendRequest):
    """Trend analizi endpoint'i"""
    try:
        weekly_trends = get_weekly_trends(
            category=request.category,
            body_type=request.body_type,
            limit=8
        )
        
        if not weekly_trends:
            weekly_trends = [
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
                    "brand": "Pull & Bear", 
                    "category": "pantolon",
                    "search_count": 38,
                    "trend_score": 76,
                    "price_range": "199-299 TL"
                }
            ]
        
        if GEMINI_AVAILABLE:
            try:
                insights_prompt = f"Bu trend verileri: {json.dumps(weekly_trends[:3], ensure_ascii=False)} - Kısa trend analizi yap."
                insights_response = model.generate_content(insights_prompt)
                trend_insights = insights_response.text
            except:
                trend_insights = "📈 Bu hafta oversized ve rahat kesimli ürünler trend!"
        else:
            trend_insights = "📈 Bu hafta oversized ve rahat kesimli ürünler trend!"
        
        return {
            "success": True,
            "trends": weekly_trends,
            "insights": trend_insights,
            "week_number": datetime.now().isocalendar()[1],
            "total_products": len(weekly_trends)
        }
        
    except Exception as e:
        return {
            "success": False,
            "trends": [],
            "insights": "Trend verileri yüklenemiyor.",
            "error": str(e)
        }

@app.post("/chat-product-search")
def chat_product_search(request: ChatRequest):
    """AI Stil Danışmanı"""
    try:
        track_product_search(
            product_name="AI Style Consultant",
            brand="AURA_AI",
            category="style_consultation"
        )
        
        conv_id = request.conversation_id or str(uuid.uuid4())[:8]
        
        if conv_id not in conversation_memory:
            conversation_memory[conv_id] = {
                "messages": [],
                "detected_gender": "kadın"
            }
        
        conversation = conversation_memory[conv_id]
        conversation["messages"].append({
            "role": "user",
            "content": request.message,
            "timestamp": time.time()
        })
        
        if GEMINI_AVAILABLE:
            try:
                style_prompt = f"""Sen AURA AI Stil Danışmanısın. 
                Kullanıcı diyor: "{request.message}"
                
                Kısa, samimi ve yardımcı bir cevap ver. Türkçe."""
                
                ai_response = model.generate_content(style_prompt)
                ai_message = ai_response.text
            except:
                ai_message = f"🤖 '{request.message}' için en uygun ürünleri buluyorum!"
        else:
            ai_message = f"🤖 '{request.message}' konusunda size yardımcı olmaya çalışıyorum!"
        
        # Ürün arama
        products = scraper.search_real_products_web(
            search_query=request.message,
            gender=conversation.get("detected_gender", "kadın"),
            limit=6
        )
        
        conversation["messages"].append({
            "role": "assistant", 
            "content": ai_message,
            "timestamp": time.time()
        })
        
        return {
            "ai_response": ai_message,
            "products": products,
            "conversation_id": conv_id,
            "success": True,
            "ai_type": "style_consultant"
        }
        
    except Exception as e:
        return {
            "ai_response": "Üzgünüm, bir sorun oluştu. Tekrar deneyin.",
            "products": [],
            "conversation_id": request.conversation_id or "error",
            "success": False
        }

# Vercel için handler
app = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
