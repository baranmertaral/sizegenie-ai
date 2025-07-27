from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import google.generativeai as genai
from photo_analysis import analyze_body_photo
from product_scraper import ProductScraper
import base64

load_dotenv()

app = FastAPI(title="SizeGenie AI", description="Real AI-powered clothing size recommendation with Gemini Vision")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gemini yapılandırması
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash')
    GEMINI_AVAILABLE = True
    print("✅ Gemini Vision AI aktif - Gerçek analiz hazır!")
except Exception as e:
    GEMINI_AVAILABLE = False
    print(f"❌ Gemini yapılandırma hatası: {e}")

# Product scraper instance
scraper = ProductScraper()

class SizeRequest(BaseModel):
    user_height: int
    user_weight: int
    product_name: str
    product_size: str
    brand: str

class ProductRequest(BaseModel):
    brand: str
    body_type: str
    category: str = "woman"

@app.get("/")
def root():
    return {
        "message": "SizeGenie AI - Premium Gemini Vision Analysis", 
        "status": "active", 
        "gemini_status": GEMINI_AVAILABLE,
        "ai_mode": "premium_real_ai",
        "features": ["Real Photo Analysis", "AI Size Recommendations", "Product Suggestions"]
    }

@app.post("/analyze-size")
def analyze_size(request: SizeRequest):
    """Gerçek AI ile beden uyumluluğu analizi"""
    try:
        if not GEMINI_AVAILABLE:
            raise HTTPException(
                status_code=503, 
                detail="AI servisi şu anda kullanılamıyor. Lütfen daha sonra tekrar deneyin."
            )
        
        prompt = f"""
        Sen dünyanın en deneyimli giyim uzmanı ve fit specialistısın. Aşağıdaki bilgileri profesyonel seviyede analiz et:

        👤 Kullanıcı Profili:
        - Boy: {request.user_height}cm
        - Kilo: {request.user_weight}kg
        
        👕 Ürün Bilgileri:
        - Marka: {request.brand}
        - Ürün: {request.product_name}
        - Seçilen Beden: {request.product_size}
        
        🎯 Analiz Görevlerin:
        1. Bu ürünün kullanıcıya fit uygunluğunu hesapla
        2. {request.brand} markasının kalıp özelliklerini değerlendir
        3. BMI ve vücut oranlarını göz önünde bulundur
        4. Alternative beden önerileri sun
        5. Styling tavsiyeleri ver
        
        📊 Yanıt Formatı:
        - Uyumluluk yüzdesi: X% (hesaplanmış)
        - Önerilen beden: [birincil öneri + alternatifler]
        - Fit analizi: [nasıl oturacağı, hangi bölgelerde rahat/dar olacağı]
        - Marka özellikleri: [{request.brand}'nın kalıp karakteristikleri]
        - Styling ipuçları: [nasıl kombinlemeli, hangi aksesuarlarla]
        
        Türkçe, profesyonel ve detaylı cevap ver. Emoji kullanarak organize et.
        Marka deneyimini ve fitting expertise'ini yansıt.
        """
        
        try:
            response = model.generate_content(prompt)
            ai_response = response.text
            print(f"✅ Gerçek AI beden analizi: {request.brand} {request.product_name}")
            
            return {
                "success": True,
                "recommendation": ai_response,
                "user_data": request.dict(),
                "ai_type": "real_gemini_pro",
                "analysis_timestamp": "live"
            }
            
        except Exception as e:
            if "quota" in str(e).lower() or "limit" in str(e).lower():
                raise HTTPException(
                    status_code=429,
                    detail="AI analiz limiti aşıldı. Lütfen birkaç saat sonra tekrar deneyin."
                )
            else:
                raise HTTPException(status_code=500, detail=f"AI analiz hatası: {str(e)}")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-photo")
async def analyze_photo(file: UploadFile = File(...)):
    """Gerçek Gemini Vision ile fotoğraf analizi"""
    try:
        if not GEMINI_AVAILABLE:
            raise HTTPException(
                status_code=503,
                detail="AI Vision servisi şu anda kullanılamıyor. Lütfen daha sonra tekrar deneyin."
            )
        
        # Fotoğrafı oku ve validate et
        image_data = await file.read()
        
        if len(image_data) == 0:
            raise HTTPException(status_code=400, detail="Geçersiz fotoğraf dosyası")
        
        # Profesyonel Vision AI prompt
        prompt = """
        Sen dünyanın en deneyimli moda danışmanı ve vücut analisti olarak bu fotoğraftaki kişinin profesyonel seviyede vücut analizini yap:
        
        🔍 DETAYLI ANALİZ KRİTERLERİ:
        
        1. 👤 Temel Bilgiler:
           - Cinsiyet tespiti (Erkek/Kadın)
           - Yaş grubu tahmini (20-30, 30-40, vs.)
           
        2. 📐 Vücut Tipi Analizi:
           - Ana tip: Rectangle/Pear/Apple/Hourglass/Athletic/Stocky
           - Alt kategoriler ve nüanslar
           
        3. 📏 Ölçü Değerlendirmesi:
           - Omuz genişliği: Dar/Orta/Geniş (cm tahmini)
           - Bel kalça oranı: Sayısal değer (0.6-1.0)
           - Genel yapı: İnce/Orta/Dolgun/Atletik/Güçlü
           
        4. 🎯 Proporsiyonel Analiz:
           - Üst-alt vücut dengesi
           - Bel tanımı seviyesi
           - Genel simetri değerlendirmesi
           
        5. 👗 DETAYLI GİYSİ ÖNERİLERİ:
           
           ✨ Mükemmel Uyacak Kıyafetler:
           - Spesifik kesim önerileri
           - Hangi markalardan ne almalı
           - Hangi renkler yakışır
           
           ⚠️ Kaçınılması Gerekenler:
           - Hangi kesimler yakışmaz
           - Hangi renklerden uzak durmalı
           
           🌟 Pro Styling İpuçları:
           - Hangi vücut bölgeleri vurgulanmalı
           - Görsel aldatmaca teknikleri
           - Aksesuar önerileri
           
        6. 🛍️ MARKA ÖNERİLERİ:
           - Zara: Bu vücut tipi için hangi koleksiyonlar
           - H&M: Önerilen ürün kategorileri
           - Pull&Bear: Uygun stil tipleri
           - Stradivarius: Yakışacak kesimler
           
        7. 🎨 RENK VE DESEN TAVSİYELERİ:
           - Ten rengi uyumlu palet
           - Vücut tipine göre desen seçimi
           - Kontrast ve ton tavsiyeleri
           
        YANIT FORMATI:
        Emoji'ler kullanarak organize et, professional ama sıcak bir dil kullan.
        Pozitif ve motive edici olsun ama gerçekçi kalsin.
        Her öneriyi açıkla - neden bu öneriyi veriyorsun?
        
        Türkçe olarak en detaylı ve profesyonel analizi yap!
        """
        
        try:
            response = model.generate_content([
                prompt, 
                {"mime_type": "image/jpeg", "data": image_data}
            ])
            
            real_analysis = response.text
            print(f"✅ Gerçek Gemini Vision analizi tamamlandı - {file.filename}")
            
            return {
                "success": True,
                "analysis": real_analysis,
                "filename": file.filename,
                "ai_type": "real_gemini_vision",
                "analysis_timestamp": "live",
                "file_size_kb": len(image_data) // 1024
            }
            
        except Exception as e:
            if "quota" in str(e).lower() or "limit" in str(e).lower():
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "AI Vision analiz limiti aşıldı",
                        "message": "Günlük analiz limitine ulaşıldı. Lütfen 24 saat sonra tekrar deneyin.",
                        "retry_after": "24 hours"
                    }
                )
            else:
                raise HTTPException(status_code=500, detail=f"Vision AI hatası: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get-products")
def get_products(request: ProductRequest):
    """Dinamik ürün önerileri"""
    try:
        print(f"\n🛍️ === {request.brand} İSTEĞİ ===")
        print(f"Body type: {request.body_type}")
        print(f"Category: {request.category}")
        
        # Dinamik ürün çekme
        products = scraper.get_products_by_brand(
            brand=request.brand,
            category=request.category,
            analysis_text=request.body_type,  # Bu analiz metni
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
            "is_dynamic": True
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

@app.get("/brands")
def get_available_brands():
    """Desteklenen markalar"""
    return {
        "brands": [
            {
                "name": "Zara",
                "category": "Fast Fashion Premium",
                "specialties": ["Trendy", "European Fit", "Quality Basics"]
            },
            {
                "name": "Pull & Bear", 
                "category": "Casual Streetwear",
                "specialties": ["Urban", "Relaxed Fit", "Youth Culture"]
            },
            {
                "name": "Stradivarius",
                "category": "Feminine Fashion", 
                "specialties": ["Elegant", "Feminine Cuts", "Seasonal Trends"]
            }
        ],
        "success": True,
        "total_brands": 3
    }

@app.get("/status")
def get_ai_status():
    """AI servisi durumu"""
    return {
        "service_status": "active",
        "gemini_vision_available": GEMINI_AVAILABLE,
        "ai_mode": "premium_real_time" if GEMINI_AVAILABLE else "service_unavailable",
        "features": {
            "photo_analysis": GEMINI_AVAILABLE,
            "size_recommendations": GEMINI_AVAILABLE,
            "product_styling": GEMINI_AVAILABLE
        },
        "message": "Gerçek AI servisleri aktif 🚀" if GEMINI_AVAILABLE else "AI servisleri geçici olarak kullanılamıyor ⚠️"
    }

@app.get("/health")
def health_check():
    """Sistem sağlık kontrolü"""
    return {
        "status": "healthy",
        "timestamp": "live",
        "version": "2.0.0-premium",
        "ai_engine": "gemini-1.5-flash",
        "services": {
            "api": True,
            "ai_vision": GEMINI_AVAILABLE,
            "product_scraper": True
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
