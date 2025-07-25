import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

def analyze_body_photo(image_data):
    """Fotoğraftan vücut analizi yap"""
    
    prompt = """
    Bu fotoğraftaki kişinin vücut analizini yap:
    
    1. Vücut Tipi: (Apple/Pear/Rectangle/Hourglass)
    2. Omuz Genişliği: (Dar/Orta/Geniş) 
    3. Bel Kalça Oranı: (Tahmini)
    4. Genel Yapı: (İnce/Orta/Dolgun)
    5. Giysi Önerileri: Bu vücut tipine uygun kesimler
    
    Analizi Türkçe yap ve net şekilde formatla.
    """
    
    try:
        response = model.generate_content([
            prompt, 
            {"mime_type": "image/jpeg", "data": image_data}
        ])
        return response.text
    except Exception as e:
        return f"Hata: {e}"

if __name__ == "__main__":
    print("📸 Fotoğraf analizi modülü hazır!")
