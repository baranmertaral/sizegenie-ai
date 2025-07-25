from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import google.generativeai as genai
from photo_analysis import analyze_body_photo
import base64

load_dotenv()

app = FastAPI(title="SizeGenie AI", description="AI-powered clothing size recommendation with photo analysis")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gemini yapılandırması
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

class SizeRequest(BaseModel):
    user_height: int
    user_weight: int
    product_name: str
    product_size: str
    brand: str

@app.get("/")
def root():
    return {"message": "SizeGenie AI API with Photo Analysis", "status": "active"}

@app.post("/analyze-size")
def analyze_size(request: SizeRequest):
    try:
        prompt = f"""
        Kullanıcı Profili:
        - Boy: {request.user_height}cm
        - Kilo: {request.user_weight}kg
        
        Ürün Bilgileri:
        - Marka: {request.brand}
        - Ürün: {request.product_name}
        - Seçilen Beden: {request.product_size}
        
        Bu ürün kullanıcıya uygun mu? 
        Yanıt formatı:
        - Uyumluluk yüzdesi: X%
        - Önerilen beden: [beden]
        - Açıklama: [kısa açıklama]
        """
        
        response = model.generate_content(prompt)
        return {
            "success": True,
            "recommendation": response.text,
            "user_data": request.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-photo")
async def analyze_photo(file: UploadFile = File(...)):
    try:
        # Fotoğrafı oku
        image_data = await file.read()
        
        # Fotoğraf analizi yap
        analysis_result = analyze_body_photo(image_data)
        
        return {
            "success": True,
            "analysis": analysis_result,
            "filename": file.filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
