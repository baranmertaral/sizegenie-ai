import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin
import random

class ProductScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def extract_body_info_from_analysis(self, analysis_text):
        """AI analizinden akıllıca bilgi çıkar"""
        analysis_lower = analysis_text.lower()
        
        # Cinsiyet tespiti
        if any(word in analysis_lower for word in ['👩', 'kadın', 'bayan', 'hanım', 'female', 'woman']):
            gender = 'kadın'
        elif any(word in analysis_lower for word in ['👨', 'erkek', 'adam', 'bay', 'male', 'man']):
            gender = 'erkek'
        else:
            gender = 'kadın'  # default
        
        # Vücut tipi tespiti
        if any(word in analysis_lower for word in ['dikdörtgen', 'rectangle']):
            body_type = 'Rectangle'
        elif any(word in analysis_lower for word in ['pear', 'armut']):
            body_type = 'Pear'
        elif any(word in analysis_lower for word in ['apple', 'elma']):
            body_type = 'Apple'
        elif any(word in analysis_lower for word in ['hourglass', 'kum saati']):
            body_type = 'Hourglass'
        elif any(word in analysis_lower for word in ['athletic', 'atletik']):
            body_type = 'Athletic'
        else:
            body_type = 'Rectangle'  # default
        
        print(f"🔍 Tespit edilen: {gender} {body_type}")
        return gender, body_type
    
    def get_recommended_categories(self, gender, body_type):
        """Vücut tipine göre önerilen kategoriler"""
        recommendations = {
            'kadın': {
                'Rectangle': ['bel_vurgulu', 'wrap_elbise', 'yuksek_bel', 'kemer_detayli', 'peplum'],
                'Pear': ['omuz_detayli', 'boat_neck', 'blazer', 'acik_ust_renk', 'structured_top'],
                'Apple': ['empire_waist', 'v_neck', 'flowy_top', 'straight_leg', 'uzun_cardigan'],
                'Hourglass': ['fitted_elbise', 'bodycon', 'wrap_dress', 'high_waist', 'belted'],
                'Athletic': ['feminen_detay', 'soft_lines', 'curves', 'ruffles', 'flowing']
            },
            'erkek': {
                'Rectangle': ['layered', 'textured', 'regular_fit', 'horizontal_stripes'],
                'Athletic': ['fitted', 'slim_fit', 'tailored', 'structured'],
                'Apple': ['v_neck', 'vertical_lines', 'dark_colors', 'single_breasted']
            }
        }
        
        return recommendations.get(gender, {}).get(body_type, ['basic'])
    
    def get_all_products_by_brand(self, brand):
        """Tüm ürün havuzu - kategorilere göre ayrılmış"""
        product_pools = {
            'Zara': {
                'bel_vurgulu': [
                    {'name': 'Bel Vurgulu Midi Elbise', 'price': '399.95 TL', 'image': 'https://dummyimage.com/300x400/e74c3c/ffffff?text=Bel+Vurgulu+Elbise', 'url': 'https://www.zara.com/tr/tr/kadin-elbise-l1066.html'},
                    {'name': 'Kemer Detaylı Elbise', 'price': '349.95 TL', 'image': 'https://dummyimage.com/300x400/c0392b/ffffff?text=Kemer+Detayli', 'url': 'https://www.zara.com/tr/tr/kadin-elbise-l1066.html'},
                ],
                'wrap_elbise': [
                    {'name': 'Çiçekli Wrap Elbise', 'price': '449.95 TL', 'image': 'https://dummyimage.com/300x400/f39c12/ffffff?text=Wrap+Elbise', 'url': 'https://www.zara.com/tr/tr/kadin-elbise-l1066.html'},
                    {'name': 'Saten Wrap Dress', 'price': '499.95 TL', 'image': 'https://dummyimage.com/300x400/d35400/ffffff?text=Saten+Wrap', 'url': 'https://www.zara.com/tr/tr/kadin-elbise-l1066.html'},
                ],
                'yuksek_bel': [
                    {'name': 'Yüksek Bel Wide Leg', 'price': '349.95 TL', 'image': 'https://dummyimage.com/300x400/3498db/ffffff?text=Yuksek+Bel', 'url': 'https://www.zara.com/tr/tr/kadin-pantolon-l1335.html'},
                    {'name': 'High Waist Straight', 'price': '289.95 TL', 'image': 'https://dummyimage.com/300x400/2980b9/ffffff?text=High+Waist', 'url': 'https://www.zara.com/tr/tr/kadin-pantolon-l1335.html'},
                ],
                'omuz_detayli': [
                    {'name': 'Omuz Detaylı Bluz', 'price': '199.95 TL', 'image': 'https://dummyimage.com/300x400/1abc9c/ffffff?text=Omuz+Detayli', 'url': 'https://www.zara.com/tr/tr/kadin-tishertler-l1362.html'},
                    {'name': 'Statement Shoulder', 'price': '249.95 TL', 'image': 'https://dummyimage.com/300x400/16a085/ffffff?text=Statement+Shoulder', 'url': 'https://www.zara.com/tr/tr/kadin-tishertler-l1362.html'},
                ],
                'blazer': [
                    {'name': 'Structured Blazer', 'price': '699.95 TL', 'image': 'https://dummyimage.com/300x400/8e44ad/ffffff?text=Structured+Blazer', 'url': 'https://www.zara.com/tr/tr/kadin-blazer-l1309.html'},
                    {'name': 'Oversize Blazer', 'price': '599.95 TL', 'image': 'https://dummyimage.com/300x400/9b59b6/ffffff?text=Oversize+Blazer', 'url': 'https://www.zara.com/tr/tr/kadin-blazer-l1309.html'},
                ],
                'fitted_elbise': [
                    {'name': 'Bodycon Midi', 'price': '299.95 TL', 'image': 'https://dummyimage.com/300x400/e67e22/ffffff?text=Bodycon+Midi', 'url': 'https://www.zara.com/tr/tr/kadin-elbise-l1066.html'},
                    {'name': 'Fitted Pencil Dress', 'price': '349.95 TL', 'image': 'https://dummyimage.com/300x400/f39c12/ffffff?text=Fitted+Pencil', 'url': 'https://www.zara.com/tr/tr/kadin-elbise-l1066.html'},
                ],
                'v_neck': [
                    {'name': 'V Neck Sweater', 'price': '199.95 TL', 'image': 'https://dummyimage.com/300x400/27ae60/ffffff?text=V+Neck+Sweater', 'url': 'https://www.zara.com/tr/tr/kadin-tishertler-l1362.html'},
                ],
                'fitted': [
                    {'name': 'Slim Fit Gömlek', 'price': '299.95 TL', 'image': 'https://dummyimage.com/300x400/34495e/ffffff?text=Slim+Fit', 'url': 'https://www.zara.com/tr/tr/erkek-gomlek-l669.html'},
                    {'name': 'Tailored Shirt', 'price': '349.95 TL', 'image': 'https://dummyimage.com/300x400/2c3e50/ffffff?text=Tailored', 'url': 'https://www.zara.com/tr/tr/erkek-gomlek-l669.html'},
                ],
                'basic': [
                    {'name': 'Basic Tişört', 'price': '99.95 TL', 'image': 'https://dummyimage.com/300x400/95a5a6/ffffff?text=Basic', 'url': 'https://www.zara.com/tr/tr/kadin-tishertler-l1362.html'},
                ]
            },
            'Pull & Bear': {
                'bel_vurgulu': [
                    {'name': 'Bel Detaylı Elbise', 'price': '159.99 TL', 'image': 'https://dummyimage.com/300x400/ff6b6b/ffffff?text=Bel+Detayli', 'url': 'https://www.pullandbear.com/tr/kadin-n6417'},
                ],
                'yuksek_bel': [
                    {'name': 'High Waist Mom Jean', 'price': '199.99 TL', 'image': 'https://dummyimage.com/300x400/4ecdc4/ffffff?text=Mom+Jean', 'url': 'https://www.pullandbear.com/tr/kadin/giyim/jean-n6581'},
                ],
                'omuz_detayli': [
                    {'name': 'Off-Shoulder Top', 'price': '89.99 TL', 'image': 'https://dummyimage.com/300x400/45b7d1/ffffff?text=Off+Shoulder', 'url': 'https://www.pullandbear.com/tr/kadin-n6417'},
                ],
                'fitted': [
                    {'name': 'Regular Fit Hoodie', 'price': '149.99 TL', 'image': 'https://dummyimage.com/300x400/786fa6/ffffff?text=Regular+Hoodie', 'url': 'https://www.pullandbear.com/tr/erkek-n6228'},
                ],
                'basic': [
                    {'name': 'Basic Tee', 'price': '69.99 TL', 'image': 'https://dummyimage.com/300x400/96ceb4/ffffff?text=Basic', 'url': 'https://www.pullandbear.com/tr/kadin-n6417'},
                ]
            },
            'Stradivarius': {
                'fitted_elbise': [
                    {'name': 'Bodycon Elbise', 'price': '179.95 TL', 'image': 'https://dummyimage.com/300x400/f8b500/ffffff?text=Bodycon', 'url': 'https://www.stradivarius.com/tr/kadin/giyim/elbise-n1995'},
                    {'name': 'Fitted Mini', 'price': '149.95 TL', 'image': 'https://dummyimage.com/300x400/f0932b/ffffff?text=Fitted+Mini', 'url': 'https://www.stradivarius.com/tr/kadin/giyim/elbise/mini-n1999'},
                ],
                'bel_vurgulu': [
                    {'name': 'Cinched Waist Dress', 'price': '199.95 TL', 'image': 'https://dummyimage.com/300x400/eb4d4b/ffffff?text=Cinched+Waist', 'url': 'https://www.stradivarius.com/tr/kadin/giyim/elbise-n1995'},
                ],
                'omuz_detayli': [
                    {'name': 'Shoulder Detail Top', 'price': '119.95 TL', 'image': 'https://dummyimage.com/300x400/a29bfe/ffffff?text=Shoulder+Detail', 'url': 'https://www.stradivarius.com/tr/kadin-n1906'},
                ],
                'basic': [
                    {'name': 'Trendy Tee', 'price': '79.95 TL', 'image': 'https://dummyimage.com/300x400/74b9ff/ffffff?text=Trendy', 'url': 'https://www.stradivarius.com/tr/kadin-n1906'},
                ]
            }
        }
        
        return product_pools.get(brand, {})
    
    def get_dynamic_products_by_analysis(self, brand, analysis_text, limit=6):
        """DİNAMİK ürün seçimi - Her seferinde farklı!"""
        
        # Vücut tipi ve cinsiyet çıkar
        gender, body_type = self.extract_body_info_from_analysis(analysis_text)
        
        # Önerilen kategorileri al
        recommended_categories = self.get_recommended_categories(gender, body_type)
        
        print(f"🎯 {gender} {body_type} için kategoriler: {recommended_categories}")
        
        # Markadan tüm ürünleri al
        all_brand_products = self.get_all_products_by_brand(brand)
        
        selected_products = []
        
        # Önerilen kategorilerden ürün seç
        for category in recommended_categories:
            if category in all_brand_products:
                category_products = all_brand_products[category].copy()
                random.shuffle(category_products)  # HER SEFERINDE FARKLI SIRALAMA
                selected_products.extend(category_products[:2])  # Her kategoriden max 2 ürün
        
        # Yeterli ürün yoksa basic'lerle doldur
        if len(selected_products) < limit and 'basic' in all_brand_products:
            basic_products = all_brand_products['basic'].copy()
            random.shuffle(basic_products)
            selected_products.extend(basic_products)
        
        # Listeyi karıştır ve sınırla
        random.shuffle(selected_products)  # FINAL KARIŞTIRMA
        final_products = selected_products[:limit]
        
        # Brand bilgisi ekle
        for product in final_products:
            product['brand'] = brand
            product['recommended_for'] = f"{gender} {body_type}"
        
        print(f"✅ {len(final_products)} dinamik ürün seçildi")
        
        return final_products
    
    def get_products_by_brand(self, brand, category="woman", body_type="Rectangle", analysis_text="", limit=6):
        """ANA METOD - Her çağrıda farklı ürünler!"""
        
        if analysis_text and len(analysis_text) > 10:
            return self.get_dynamic_products_by_analysis(brand, analysis_text, limit)
        else:
            # Fallback - basit sistem
            return self.get_dynamic_products_by_analysis(brand, f"kadın {body_type}", limit)

# Test için
if __name__ == "__main__":
    scraper = ProductScraper()
    
    test_analysis = "👩 Cinsiyet: Kadın 🔹 Vücut Tipi: Rectangle"
    
    print("=== TEST 1 ===")
    products1 = scraper.get_dynamic_products_by_analysis('Zara', test_analysis)
    for p in products1:
        print(f"- {p['name']}")
    
    print("\n=== TEST 2 (Aynı analiz, farklı sonuç olmalı) ===")
    products2 = scraper.get_dynamic_products_by_analysis('Zara', test_analysis)
    for p in products2:
        print(f"- {p['name']}")
