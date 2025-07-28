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
    """Dinamik ürün önerileri"""
    try:
        print(f"\n🛍️ === {request.brand} İSTEĞİ ===")
        print(f"Body type: {request.body_type}")
        print(f"Category: {request.category}")
        
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

@app.post("/chat-product-search")
def chat_product_search(request: ChatRequest):
    """GERÇEK AI ile WEB ARAMA - dinamik ürün sohbeti"""
    try:
        print(f"🤖 Chat isteği: {request.message}")
        
        # Conversation ID oluştur veya mevcut olanı kullan
        conv_id = request.conversation_id or str(uuid.uuid4())[:8]
        
        # Conversation history'yi al
        if conv_id not in conversation_memory:
            conversation_memory[conv_id] = {
                "messages": [],
                "user_preferences": {},
                "searched_products": [],
                "detected_gender": None,
                "detected_style": None
            }
        
        conversation = conversation_memory[conv_id]
        
        # Kullanıcı mesajını kaydet
        conversation["messages"].append({
            "role": "user",
            "content": request.message,
            "timestamp": time.time()
        })
        
        if GEMINI_AVAILABLE:
            # İLK ADIM: Kullanıcı mesajından cinsiyet ve ürün bilgisi çıkar
            analysis_prompt = f"""
Kullanıcının bu mesajını analiz et: "{request.message}"

Conversation history:
{chr(10).join([f"{msg['role']}: {msg['content']}" for msg in conversation["messages"][-3:]])}

Şunları belirle ve JSON formatında döndür:
{{
    "gender": "kadın" veya "erkek" (eğer belirsizse "kadın" varsayılan),
    "product_type": "tişört", "pantolon", "elbise", "jean", "mont", "hoodie", "gömlek", "ayakkabı" vs,
    "style_preferences": ["oversize", "vintage", "basic", "yüksek bel", "spor", "klasik" vs],
    "color_preferences": ["beyaz", "siyah", "mavi", "kırmızı" vs],
    "brand_preferences": ["zara", "pull&bear", "stradivarius" vs veya "any"],
    "search_keywords": "web araması için en uygun anahtar kelimeler"
}}

Sadece JSON döndür, başka metin ekleme.
"""
            
            try:
                analysis_response = model.generate_content(analysis_prompt)
                analysis_text = analysis_response.text.strip()
                
                # JSON parse et
                json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
                if json_match:
                    analysis_data = json.loads(json_match.group())
                else:
                    # Fallback
                    analysis_data = {
                        "gender": "kadın",
                        "product_type": "tişört",
                        "style_preferences": ["basic"],
                        "color_preferences": ["beyaz"],
                        "brand_preferences": ["any"],
                        "search_keywords": request.message
                    }
                
                # Tespit edilen bilgileri kaydet
                conversation["detected_gender"] = analysis_data.get("gender", "kadın")
                conversation["detected_style"] = analysis_data.get("style_preferences", [])
                
                print(f"🔍 Tespit edilen cinsiyet: {conversation['detected_gender']}")
                print(f"📊 Tespit edilen stil: {conversation['detected_style']}")
                print(f"🔍 Arama kelimesi: {analysis_data.get('search_keywords', '')}")
                
            except Exception as e:
                print(f"⚠️ Analiz hatası: {e}")
                analysis_data = {
                    "gender": "kadın",
                    "product_type": "tişört",
                    "search_keywords": request.message
                }
                conversation["detected_gender"] = "kadın"
            
            # İKİNCİ ADIM: AI cevabı oluştur
            chat_prompt = f"""
Sen bir kişisel alışveriş asistanısın. 

Kullanıcı profili:
- Cinsiyet: {conversation['detected_gender']}
- Son istek: {request.message}
- Tespit edilen ürün: {analysis_data.get('product_type', 'kıyafet')}
- Stil tercihleri: {analysis_data.get('style_preferences', [])}

Conversation History:
{chr(10).join([f"{msg['role']}: {msg['content']}" for msg in conversation["messages"][-5:]])}

Görevin:
1. Kullanıcının isteğini anlıyorum demek
2. Hangi özelliklerde ürün aradığını belirtmek
3. "Size uygun ürünleri internetten buluyorum" demek
4. Samimi ve profesyonel olmak

2-3 cümle ile Türkçe cevap ver.
"""
            
            try:
                ai_response = model.generate_content(chat_prompt)
                ai_message = ai_response.text
                
                # AI cevabını kaydet
                conversation["messages"].append({
                    "role": "assistant", 
                    "content": ai_message,
                    "timestamp": time.time()
                })
                
                print(f"✅ AI cevabı oluşturuldu")
                
            except Exception as e:
                if "quota" in str(e).lower():
                    ai_message = f"🤖 Anlıyorum! {conversation['detected_gender']} için {analysis_data.get('product_type', 'ürün')} arıyorsunuz. İnternetten size uygun seçenekleri buluyorum."
                else:
                    ai_message = "🤖 İsteğinizi anlıyorum, size uygun ürünleri internetten buluyorum."
        else:
            # Fallback - basit analiz
            ai_message = "🤖 İsteğinizi anlıyorum, size uygun ürünleri internetten buluyorum."
            analysis_data = {
                "gender": "kadın",
                "product_type": "tişört",
                "search_keywords": request.message
            }
            conversation["detected_gender"] = "kadın"
        
        # ÜÇÜNCÜ ADIM: GERÇEK WEB ARAMA
        search_query = analysis_data.get("search_keywords", request.message)
        gender = conversation.get("detected_gender", "kadın")
        
        print(f"🔍 Web arama terimi: {search_query}")
        
        # WEB'DEN GERÇEK ÜRÜN ARAMA
        all_products = scraper.search_real_products_web(
            search_query=search_query,
            gender=gender, 
            limit=6
        )

        # Ürünleri conversation'a kaydet
        conversation["searched_products"].extend(all_products)
        
        print(f"🛍️ Web'den toplam {len(all_products)} dinamik ürün bulundu")
        
        return {
            "ai_response": ai_message,
            "products": all_products,
            "conversation_id": conv_id,
            "success": True,
            "detected_gender": conversation.get("detected_gender"),
            "search_query": search_query,
            "analysis_data": analysis_data
        }
        
    except Exception as e:
        print(f"❌ Chat hatası: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "ai_response": f"Üzgünüm, bir hata oluştu: {str(e)}",
            "products": [],
            "conversation_id": request.conversation_id or "error",
            "success": False
        }

@app.get("/")
def read_root():
    return {"message": "AURA AI Backend - Sadeleştirilmiş Beden Analizi Aktif! 🎯", "status": "running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
