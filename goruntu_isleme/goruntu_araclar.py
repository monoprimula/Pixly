from PIL import Image

def goruntu_oku(dosya_yolu):
    """
    Görüntüyü okuma (JPEG, PNG, BMP vb. formatları destekler)
    Pillow kütüphanesi kullanılarak görüntü okunur ve saf python listesine dönüştürülür
    """
    try:
        img = Image.open(dosya_yolu)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img_list = list(img.getdata())
        w, h = img.size
        # Görüntüyü 2D liste olarak düzenle
        img_2d = []
        for i in range(h):
            satir = []
            for j in range(w):
                piksel = img_list[i * w + j]
                satir.append(list(piksel))  # Tuple'ı liste'ye çevir
            img_2d.append(satir)
        return img_2d
    except Exception as e:
        print(f"Görüntü okuma hatası: {e}")
        return None

def goruntu_kaydet(img, dosya_yolu):
    """
    Saf python listesi olan görüntüyü kaydetme
    """
    try:
        h = len(img)
        w = len(img[0])
        flat = [tuple(p) if isinstance(p, list) else (p, p, p) for row in img for p in row]
        im = Image.new('RGB', (w, h))
        im.putdata(flat)
        im.save(dosya_yolu)
    except Exception as e:
        print(f"Görüntü kaydetme hatası: {e}")



def gri_tonlamaya_cevir(img):
    h = len(img)
    w = len(img[0])
    if isinstance(img[0][0], int):
        return img
    gri = [] # Görüntüdeki her piksel için gri tonlama hesaplaması yapılır

    for y in range(h):
        satir = []
        for x in range(w):
            r, g, b = img[y][x]
            deger = int(0.299 * r + 0.587 * g + 0.114 * b) 
            satir.append(deger)
        gri.append(satir)
    return gri

def goruntuyu_yeniden_boyutlandir(img, genislik=None, yukseklik=None):
    """
    Görüntüyü yeniden boyutlandırır
    """
    h = len(img)
    w = len(img[0])
    c = len(img[0][0]) if isinstance(img[0][0], list) else 1
    
    if genislik is None and yukseklik is None:
        return img
    if genislik is None:
        oran = yukseklik / h
        yeni_genislik = int(w * oran)
        yeni_yukseklik = yukseklik
    else:
        oran = genislik / w
        yeni_genislik = genislik
        yeni_yukseklik = int(h * oran)
    
    
    if c == 1:
        yeniden = [[0 for _ in range(yeni_genislik)] for _ in range(yeni_yukseklik)]
    else:
        yeniden = [[[0]*c for _ in range(yeni_genislik)] for _ in range(yeni_yukseklik)]
    
    for y in range(yeni_yukseklik):
        for x in range(yeni_genislik):
            orijinal_x = x / oran
            orijinal_y = y / oran
            x0 = int(orijinal_x)
            x1 = min(x0 + 1, w - 1)
            y0 = int(orijinal_y)
            y1 = min(y0 + 1, h - 1)
            wx = orijinal_x - x0
            wy = orijinal_y - y0
            
            if c == 1:
                f00 = img[y0][x0]
                f10 = img[y1][x0]
                f01 = img[y0][x1]
                f11 = img[y1][x1]
                piksel = int((1 - wx) * (1 - wy) * f00 + wx * (1 - wy) * f01 + (1 - wx) * wy * f10 + wx * wy * f11)
                yeniden[y][x] = piksel
            else:
                piksel = []
                for kanal in range(c):
                    f00 = img[y0][x0][kanal]
                    f10 = img[y1][x0][kanal]
                    f01 = img[y0][x1][kanal]
                    f11 = img[y1][x1][kanal]
                    deger = int((1 - wx) * (1 - wy) * f00 + wx * (1 - wy) * f01 + (1 - wx) * wy * f10 + wx * wy * f11)
                    piksel.append(deger)
                yeniden[y][x] = piksel
    return yeniden



def kontrast_arttir(img, faktor):
    """
    Görüntünün kontrastını artırır
    """
    h = len(img)
    w = len(img[0])
    c = len(img[0][0]) if isinstance(img[0][0], list) else 1
    
    # Ortalama pixel değeri hesapla(gri tonlama ise doğrudan, renki ise ortalama kanal değeri kullanılır
    toplam = 0
    sayi = 0
    for y in range(h):
        for x in range(w):
            if c == 1:
                toplam += img[y][x]
            else:
                toplam += sum(img[y][x]) // c
            sayi += 1
    ortalama = toplam / sayi
    
    sonuc = []
    for y in range(h):
        satir = []
        for x in range(w):
            if c == 1: # piksel değeri ortalamanın üstündeyse daha parlak, altındaysa daha koyu yapılır.
                deger = int((img[y][x] - ortalama) * faktor + ortalama)
                satir.append(min(255, max(0, deger)))
            else:
                piksel = []
                for kanal in range(c):
                    deger = int((img[y][x][kanal] - ortalama) * faktor + ortalama)
                    piksel.append(min(255, max(0, deger)))
                satir.append(piksel)
        sonuc.append(satir)
    return sonuc

def goruntuyu_kirp(img, x, y, genislik, yukseklik):
    """
    Görüntüyü belirtilen koordinatlardan kırpar
    """
    try:
        # Parametre tiplerini kontrol et
        print(f"Gelen parametre tipleri: x={type(x)}, y={type(y)}, genislik={type(genislik)}, yukseklik={type(yukseklik)}")
        
        # Parametreleri int'e dönüştür
        x = int(x)
        y = int(y)
        genislik = int(genislik)
        yukseklik = int(yukseklik)
        
        print(f"Dönüştürülmüş parametreler: x={x}, y={y}, genislik={genislik}, yukseklik={yukseklik}")
        
        # Görüntü boyutlarını al
        h = len(img)
        w = len(img[0])
        print(f"Görüntü boyutları: w={w}, h={h}")
        
        # görüntü dışına taşmasın diye boyutları sınırlandır
        x = max(0, min(x, w-1))
        y = max(0, min(y, h-1))
        genislik = max(1, min(genislik, w - x))
        yukseklik = max(1, min(yukseklik, h - y))
        
        print(f"Düzeltilmiş parametreler: x={x}, y={y}, genislik={genislik}, yukseklik={yukseklik}")
        
        # Yeni görüntü için boş liste oluştur
        kirpilmis = []
        
        # Kırpma işlemini gerçekleştir - 
        for i in range(y, y + yukseklik):
            yeni_satir = []
            for j in range(x, x + genislik):
                try:
                    piksel = img[i][j] # belirlenen yeni yükseklik ve genişlik alınır
                    if isinstance(piksel, tuple):
                        yeni_satir.append(list(piksel))
                    elif isinstance(piksel, list):
                        yeni_satir.append(piksel.copy())
                    else:
                        yeni_satir.append(piksel)
                except IndexError as e:
                    print(f"İndeks hatası: i={i}, j={j}, img boyutu={len(img)}x{len(img[0])}")
                    raise
            kirpilmis.append(yeni_satir)
            
        return kirpilmis
        
    except Exception as e:
        print(f"Kırpma fonksiyonu hatası: {str(e)}")
        print(f"Hata detayı: {type(e).__name__}")
        raise

def goruntuyu_dondur(img, aci):
    import math
    h = len(img)
    w = len(img[0])
    c = len(img[0][0]) if isinstance(img[0][0], (list, tuple)) else 1
    aci_rad = math.radians(aci)
    cos_theta = math.cos(aci_rad) # açı dönüşümleri
    sin_theta = math.sin(aci_rad)# derce cinsinden radyana sin/cos radyanda çalışır
    merkez_x = w // 2  # görüntünün ortasını bul ve döndürme noktası olarak belirle
    merkez_y = h // 2
    yeni_w = int(abs(w * cos_theta) + abs(h * sin_theta)) # yeni geişlik ve yüksekliği belirle
    yeni_h = int(abs(h * cos_theta) + abs(w * sin_theta))
    if c == 1:
        dondurulmus = [[0 for _ in range(yeni_w)] for _ in range(yeni_h)]
    else:
        dondurulmus = [[[0, 0, 0] for _ in range(yeni_w)] for _ in range(yeni_h)]
    for y in range(yeni_h):
        for x in range(yeni_w):
            # yeni kordinattan, orjinal görüntüdeki karşılık gelen nokta hesaplanır 
            # matamtiksel döndürme formülü uygulanır
            orijinal_x = (x - yeni_w//2) * cos_theta + (y - yeni_h//2) * sin_theta + merkez_x
            orijinal_y = -(x - yeni_w//2) * sin_theta + (y - yeni_h//2) * cos_theta + merkez_y
            en_yakin_x = int(orijinal_x)
            en_yakin_y = int(orijinal_y)
            #hesaplanan nokta görüntünün dışına çıkmıyor ise
            if 0 <= en_yakin_x < w and 0 <= en_yakin_y < h:
                if c == 1:
                    dondurulmus[y][x] = img[en_yakin_y][en_yakin_x]
                else:
                    dondurulmus[y][x] = list(img[en_yakin_y][en_yakin_x])
    return dondurulmus

def tek_esikleme(img, esik_degeri):
    # görüntü kili binary hale getirlir. 
    #eşik değerinin altında olan pixeller eşik değerinden büyükse beyaz küçükse siyah değerini alır 
    h = len(img)
    w = len(img[0])
    sonuc = []
    for y in range(h):
        satir = []
        for x in range(w):
            deger = img[y][x] if isinstance(img[y][x], int) else sum(img[y][x])//3
            satir.append(255 if deger > esik_degeri else 0)
        sonuc.append(satir)
    return sonuc