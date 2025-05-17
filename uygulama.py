from flask import Flask, request, jsonify, render_template
import base64
import io
import json
import numpy as np
from PIL import Image
from goruntu_isleme import morfolojik_islemler
from goruntu_isleme.kenar_tespiti import prewitt_kenar_tespiti
from goruntu_isleme.filtreler import unsharp_mask
from goruntu_isleme.filtreler import mean_konvolusyon
from goruntu_isleme.goruntu_araclar import (
    goruntu_oku, goruntu_kaydet, goruntuyu_yeniden_boyutlandir,
    gri_tonlamaya_cevir, goruntuyu_kirp, goruntuyu_dondur,
    kontrast_arttir, tek_esikleme  
)
from goruntu_isleme.morfolojik_islemler import (morfolojik_islem_uygula, yapi_elemani_olustur)
from goruntu_isleme.filtreler import (
    unsharp_mask, tuz_biber_gurultusu_ekle, 
    ortalama_filtresi, medyan_filtresi
)
from goruntu_isleme.renk_uzayi_donusumleri import (
    rgb_to_hsv, rgb_to_lab, rgb_to_ycbcr
)
from goruntu_isleme.goruntu_aritmetigi import (
    goruntu_toplama, goruntu_bolme, agirlikli_toplama
)
from goruntu_isleme.histogram_islemleri import (
    histogram_hesapla, histogram_germe, histogram_esitleme
)

uygulama = Flask(__name__)

def convert_list_to_numpy(img_list):
    """Python listesi formatındaki görüntüyü NumPy dizisine dönüştürür"""
    if not img_list:
        return None
    
    # Listeden NumPy dizisine dönüştür
    np_array = np.array(img_list, dtype=np.uint8)
    return np_array

# dtype=np.uint8 görüntü verileri genellikle 0–255 arası değer içerdiği için bu tip kullanılır

def convert_numpy_to_list(np_array):
    """NumPy dizisini Python listesine dönüştürür. Flask JSON yanıtlarında NumPy doğrudan kullanılmadığı için bu dönüşüm gereklidir."""
    if np_array is None:
        return None
    
    # NumPy dizisinden listeye dönüştür
    return np_array.tolist()

@uygulama.route('/')
def ana_sayfa():
    return render_template('index.html')

@uygulama.route('/islem', methods=['POST'])
def islem_yap():
    try:
        # Görüntüyü al
        dosya = request.files['file']
        img = goruntu_oku(dosya)
        if img is None:
            return jsonify({'success': False, 'error': 'Görüntü okunamadı'})
        
        # İşlem tipini al
        islem = request.form.get('operation')
        
        # İşlemi uygula
        if islem == 'histogram_germe':
            sonuc = histogram_germe(img)
        #histogram_germe(img) fonksiyonu görüntüyü geliştirir (parlaklık/kontrast artırılır).

            # Sonucu base64 formatına çevir
            tampon = io.BytesIO()
            h = len(sonuc)
            w = len(sonuc[0])
            flat = [tuple(p) if isinstance(p, list) else (p, p, p) for row in sonuc for p in row]
            im = Image.new('RGB', (w, h))
            im.putdata(flat) #piksel verileri girilir.
            im.save(tampon, format='JPEG', quality=95)
            # Histogram bilgilerini de döndür
            hist_original = histogram_hesapla(img)
            hist_sonuc = histogram_hesapla(sonuc)
            return jsonify({
                'success': True,
                'image': base64.b64encode(tampon.getvalue()).decode('utf-8'),
                'histogram_original': json.dumps(hist_original),
                'histogram_sonuc': json.dumps(hist_sonuc)
            })
         # Hem orijinal görüntü hem de işlenmiş görüntü için histogram bilgisi alınır (histogram_hesapla() fonksiyonu).

        elif islem == 'histogram_esitleme':
            sonuc = histogram_esitleme(img)
        # histogram_esitleme(img) fonksiyonu görüntünün kontrastını artırmak için histogram eşitleme uygular.

            # Sonucu base64 formatına çevir
            tampon = io.BytesIO()
            h = len(sonuc)
            w = len(sonuc[0])
            flat = [tuple(p) if isinstance(p, list) else (p, p, p) for row in sonuc for p in row]
            im = Image.new('RGB', (w, h))
            im.putdata(flat)
            im.save(tampon, format='JPEG', quality=95)
            # Histogram bilgilerini de döndür
            hist_original = histogram_hesapla(img)
            hist_sonuc = histogram_hesapla(sonuc)
            return jsonify({
                'success': True,
                'image': base64.b64encode(tampon.getvalue()).decode('utf-8'),
                'histogram_original': json.dumps(hist_original),
                'histogram_sonuc': json.dumps(hist_sonuc)
            })
       #Gri tonlamaya çevirme
        elif islem == 'grayscale':
            sonuc = gri_tonlamaya_cevir(img)
        
        #Eşik değeri giriyoruz. Girilen değere göre pikselleri s-b rengine dönüştürür.
        elif islem == 'binary':
            gri = gri_tonlamaya_cevir(img)
            esik = int(request.form.get('binaryThreshold', 128))
            sonuc = []
            for y in range(len(gri)):
                satir = []
                for x in range(len(gri[0])):
                    deger = gri[y][x]
                    if isinstance(deger, list):
                        deger = sum(deger) // len(deger)
                    satir.append(255 if deger > esik else 0)
                sonuc.append(satir)

        #Döndürme
        elif islem == 'rotate':
            sonuc = goruntuyu_dondur(img, float(request.form.get('rotateAngle', 45)))

        #Kırpma
        elif islem == 'crop':
            try:
                # Parametreleri al ve int'e dönüştür
                x = int(request.form.get('cropX1', 0))
                y = int(request.form.get('cropY1', 0))
                x2 = int(request.form.get('cropX2', len(img[0])))
                y2 = int(request.form.get('cropY2', len(img)))
                
                # Genişlik ve yüksekliği hesapla
                genislik = x2 - x
                yukseklik = y2 - y
                
                # Negatif değerleri kontrol et
                if genislik <= 0 or yukseklik <= 0:
                    return jsonify({'success': False, 'error': 'Geçersiz kırpma boyutları'})
                
                # Görüntü sınırlarını kontrol et
                if x < 0 or y < 0 or x2 > len(img[0]) or y2 > len(img):
                    return jsonify({'success': False, 'error': 'Kırpma alanı görüntü sınırları dışında'})
                
                # Hata ayıklama bilgileri
                print(f"Kırpma parametreleri: x={x}, y={y}, genislik={genislik}, yukseklik={yukseklik}")
                print(f"Görüntü boyutları: genislik={len(img[0])}, yukseklik={len(img)}")
                
                # Kırpma işlemini uygula
                sonuc = goruntuyu_kirp(img, x, y, genislik, yukseklik)
                
                if sonuc is None:
                    return jsonify({'success': False, 'error': 'Kırpma işlemi başarısız oldu'})
                    
            except ValueError as e:
                print(f"Değer dönüştürme hatası: {str(e)}")
                return jsonify({'success': False, 'error': f'Geçersiz kırpma parametreleri: {str(e)}'})
            except Exception as e:
                print(f"Kırpma hatası: {str(e)}")
                return jsonify({'success': False, 'error': f'Kırpma hatası: {str(e)}'})

       #Yeniden Boyutlandırma
        elif islem == 'resize':
            olcek = float(request.form.get('resizeScale', 0.5))
            yeni_boyut = (max(1, int(len(img[0]) * olcek)), max(1, int(len(img) * olcek)))
            sonuc = goruntuyu_yeniden_boyutlandir(img, yeni_boyut[0], yeni_boyut[1])

       #Kontrast Arttırma
        elif islem == 'contrast':
            sonuc = kontrast_arttir(img, float(request.form.get('contrastFactor', 1.5)))

        #Kenar Tespiti(Prewitt Operatörü)
        elif islem == 'edge_detection':
            sonuc = prewitt_kenar_tespiti(img)

        # Filtreleme – Unsharp Mask (Keskinleştirme)
        elif islem == 'filter':
            sonuc = unsharp_mask(
                img,
                float(request.form.get('unsharpAmount', 1.0)), #etki miktarı
                float(request.form.get('unsharpRadius', 1.0)), #bulanıklaştırma yarıçapı
                int(request.form.get('unsharpThreshold', 0))   #değişim eşiği
            )

       #Tek eşikleme
        elif islem == 'threshold':
                esik_degeri = int(request.form.get('thresholdValue', 128))
                sonuc = tek_esikleme(img, esik_degeri)

       #Mean Konvolüsyon
        elif islem == 'mean_convolution_manual':
            kernel_boyutu = int(request.form.get('kernelSize', 3))
            if kernel_boyutu % 2 == 0:  # Çift sayı ise tek sayıya çevir
                kernel_boyutu += 1
            sonuc = mean_konvolusyon(img, kernel_boyutu)

        #Morfolojik işlemler
        elif islem == 'morphology':
            # Morfolojik işlem parametrelerini al
            morph_tip = request.form.get('morphology_type', 'genisletme')
            yapi_sekil = request.form.get('structuring_element', 'kare')
            yapi_boyut = int(request.form.get('element_size', 3))
            iterasyon = int(request.form.get('iterations', 1))
            
            # Yapı elemanını oluştur
            yapi_elemani = yapi_elemani_olustur(yapi_sekil, yapi_boyut)
            
            # Morfolojik işlemi uygula
            sonuc = morfolojik_islem_uygula(
                img,
                islem_tipi=morph_tip,
                sekil=yapi_sekil,
                boyut=yapi_boyut,
                iterasyon=iterasyon
            )

        #Gürültü Ekleme(tuz-biber)
        elif islem == 'add_noise':
            yogunluk = float(request.form.get('noiseIntensity', 0.05))
            sonuc = tuz_biber_gurultusu_ekle(img, yogunluk)

       #Mean Filtresi. Ortalama filtresi tüm değerlerin ortalamasını alır.
        elif islem == 'mean_filter':
            kernel_boyutu = int(request.form.get('meanKernelSize', 3))
            sonuc = ortalama_filtresi(img, kernel_boyutu)

       # Medyan Filtresi. Medyan filtresi, orta değeri seçerek kenar koruyucu bir filtre sağlar.
        elif islem == 'median_filter':
            kernel_boyutu = int(request.form.get('medianKernelSize', 3))
            sonuc = medyan_filtresi(img, kernel_boyutu)

        #RGB dönüşümleri
        elif islem == 'color_space':
            donusum_tipi = request.form.get('colorSpaceType', 'rgb_to_hsv')
            
            # Python listesini NumPy dizisine dönüştür
            np_img = convert_list_to_numpy(img)
            
            # Doğru boyut kontrolü
            if len(np_img.shape) == 2:  # Gri tonlamalı görüntü
                # RGB'ye dönüştür (3 kanalı tekrarlayarak)
                np_img = np.stack([np_img, np_img, np_img], axis=2)
            elif len(np_img.shape) == 3 and np_img.shape[2] == 1:
                # 1 kanallı görüntüyü 3 kanala genişlet
                np_img = np.concatenate([np_img, np_img, np_img], axis=2)
            
            if donusum_tipi == 'rgb_to_hsv':
                np_sonuc = rgb_to_hsv(np_img)
            elif donusum_tipi == 'rgb_to_lab':
                np_sonuc = rgb_to_lab(np_img)
            elif donusum_tipi == 'rgb_to_ycbcr':
                np_sonuc = rgb_to_ycbcr(np_img)
            else:
                return jsonify({'success': False, 'error': 'Geçersiz renk uzayı dönüşüm tipi'})
            
            # NumPy dizisini Python listesine dönüştür
            sonuc = convert_numpy_to_list(np_sonuc)

       #Görüntü Aritmetiği     
        elif islem == 'image_arithmetic':
            # İkinci görüntüyü al
            second_file = request.files['secondImage']
            if not second_file:
                return jsonify({'success': False, 'error': 'İkinci görüntü gerekli'})
            
            img2 = goruntu_oku(second_file)
            if img2 is None:
                return jsonify({'success': False, 'error': 'İkinci görüntü okunamadı'})
            
            # Aritmetik işlem tipini al
            arithmetic_operation = request.form.get('arithmeticOperation')
            
            if arithmetic_operation == 'toplama':
                sonuc = goruntu_toplama(img, img2)
            elif arithmetic_operation == 'bolme':
                sonuc = goruntu_bolme(img, img2)
            elif arithmetic_operation == 'agirlikli_toplama':
                alpha = float(request.form.get('alpha', 0.5))
                beta = float(request.form.get('beta', 0.5))
                sonuc = agirlikli_toplama(img, img2, alpha, beta)
            else:
                return jsonify({'success': False, 'error': 'Geçersiz aritmetik işlem tipi'})
        else:
            return jsonify({'success': False, 'error': 'Geçersiz işlem tipi'})
        
        # Sonucu base64 formatına çevir
        tampon = io.BytesIO()
        h = len(sonuc)
        w = len(sonuc[0])
        flat = [tuple(p) if isinstance(p, list) else (p, p, p) for row in sonuc for p in row]
        im = Image.new('RGB', (w, h))
        im.putdata(flat)
        im.save(tampon, format='JPEG', quality=95)
        
        return jsonify({
            'success': True,
            'image': base64.b64encode(tampon.getvalue()).decode('utf-8')
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()  # Konsola detaylı hata mesajını bas
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    uygulama.run(debug=True)

