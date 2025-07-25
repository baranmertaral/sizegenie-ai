import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key: {api_key[:10]}..." if api_key else "API Key bulunamadı!")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')  # ← Bu satırı değiştir

test_prompt = """
Kullanıcı: Boy 175cm, Kilo 70kg, Normal vücut yapısı
Ürün: Zara Erkek Basic T-shirt - M Beden
Bu ürün kullanıcıya uygun mu? Uyumluluk yüzdesi ver.
"""

try:
    response = model.generate_content(test_prompt)
    print("✅ Gemini Test Başarılı!")
    print("Cevap:", response.text)
except Exception as e:
    print("❌ Hata:", e)
