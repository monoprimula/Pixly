def histogram_hesapla(img):
    """
    Görüntünün histogramını hesaplar.
    
    Parametreler:
    img: Giriş görüntüsü (gri tonlamalı veya RGB)
    
    Dönüş:
    histogram: 256 elemanlı liste, her eleman o yoğunluk değerinin görüntüde kaç kez geçtiğini gösterir
    """
    h = len(img)
    w = len(img[0])
    
    # Histogram dizisi oluştur (0-255 arası)
    histogram = [0] * 256
    
    # Histogramı hesapla
    for y in range(h):
        for x in range(w):
            if isinstance(img[y][x], list):  # RGB görüntü
                deger = sum(img[y][x]) // 3  # Ortalama değer
            else:  # Gri tonlamalı görüntü
                deger = img[y][x]
            histogram[deger] += 1
    
    return histogram

def histogram_germe(img):
    """
    Görüntünün histogramını germe/genişletme işlemi yapar.
    Görüntünün minimum ve maksimum değerlerini kullanarak histogramı 0-255 aralığına yayar.
    Renkli görüntülerde TÜM KANALLAR için ORTAK min ve max ile uygular.
    
    Parametreler:
    img: Giriş görüntüsü (gri tonlamalı veya RGB)
    
    Dönüş:
    sonuc: Histogramı gerilmiş görüntü
    """
    h = len(img)
    w = len(img[0])
    is_rgb = isinstance(img[0][0], list)
    
    if is_rgb:
        # Tüm kanallar için ortak min ve max değerleri hesapla
        min_val = 255
        max_val = 0
        for y in range(h):
            for x in range(w):
                for kanal in range(3):
                    deger = img[y][x][kanal]
                    if deger < min_val:
                        min_val = deger
                    if deger > max_val:
                        max_val = deger
        if min_val == max_val:
            return img
        # Sonra germe işlemini uygula
        sonuc = []
        for y in range(h):
            satir = []
            for x in range(w):
                piksel = img[y][x]
                yeni_piksel = []
                for kanal in range(3):
                    deger = piksel[kanal]
                    yeni_deger = int((deger - min_val) * (255 / (max_val - min_val)))
                    yeni_piksel.append(yeni_deger)
                satir.append(yeni_piksel)
            sonuc.append(satir)
        return sonuc
    else:
        # Gri tonlamalı için min ve max değerleri hesapla
        min_val = 255
        max_val = 0
        for y in range(h):
            for x in range(w):
                deger = img[y][x]
                if deger < min_val:
                    min_val = deger
                if deger > max_val:
                    max_val = deger
        if min_val == max_val:
            return img
        # Sonra germe işlemini uygula
        sonuc = []
        for y in range(h):
            satir = []
            for x in range(w):
                deger = img[y][x]
                yeni_deger = int((deger - min_val) * (255 / (max_val - min_val)))
                satir.append(yeni_deger)
            sonuc.append(satir)
        return sonuc

def histogram_esitleme(img):
    """
    Görüntünün histogramını eşitler.
    Renkli görüntülerde her kanal için ayrı ayrı uygular.
    
    Parametreler:
    img: Giriş görüntüsü (gri tonlamalı veya RGB)
    
    Dönüş:
    sonuc: Histogramı eşitlenmiş görüntü
    """
    h = len(img)
    w = len(img[0])
    is_rgb = isinstance(img[0][0], list)
    
    if is_rgb:
        # Her kanal için histogram ve kümülatif histogram hesapla
        histograms = [[0]*256 for _ in range(3)]
        for y in range(h):
            for x in range(w):
                for kanal in range(3):
                    histograms[kanal][img[y][x][kanal]] += 1
        
        # Kümülatif histogramları hesapla
        kumulatif = [[0]*256 for _ in range(3)]
        for kanal in range(3):
            kumulatif[kanal][0] = histograms[kanal][0]
            for i in range(1, 256):
                kumulatif[kanal][i] = kumulatif[kanal][i-1] + histograms[kanal][i]
        
        toplam_piksel = h * w
        sonuc = []
        for y in range(h):
            satir = []
            for x in range(w):
                piksel = img[y][x]
                yeni_piksel = []
                for kanal in range(3):
                    deger = piksel[kanal]
                    yeni_deger = int((kumulatif[kanal][deger] / toplam_piksel) * 255)
                    yeni_piksel.append(yeni_deger)
                satir.append(yeni_piksel)
            sonuc.append(satir)
        return sonuc
    else:
        # Gri tonlamalı için histogram ve kümülatif histogram hesapla
        histogram = histogram_hesapla(img)
        kumulatif = [0] * 256
        kumulatif[0] = histogram[0]
        for i in range(1, 256):
            kumulatif[i] = kumulatif[i-1] + histogram[i]
        
        toplam_piksel = h * w
        esitlenmis = []
        for y in range(h):
            satir = []
            for x in range(w):
                deger = img[y][x]
                yeni_deger = int((kumulatif[deger] / toplam_piksel) * 255)
                satir.append(yeni_deger)
            esitlenmis.append(satir)
        return esitlenmis