import copy  
#Görüntü işleme alanında şekil ve yapı üzerinde yapılan işlenmerdir. Genellikle sb resimler
# Yapı elemanını oluşturur: kare ya da daire şeklinde, işlem yapılacak bölgeyi tanımlar.
def yapi_elemani_olustur(sekil='kare', boyut=3):
    boyut = int(boyut)
    if boyut % 2 == 0:
        boyut += 1 
    
    if sekil == 'kare':
        # Kare yapı elemanı: tüm hücreler 1 (aktif)
        return [[1 for _ in range(boyut)] for _ in range(boyut)]
    
    elif sekil == 'daire':
        # Daire yapı elemanı: merkezden uzaklığa göre belirlenir
        yapi_elemani = [[0 for _ in range(boyut)] for _ in range(boyut)]
        merkez = boyut // 2
        for i in range(boyut):
            for j in range(boyut):
                # Eğer piksel merkezden yarıçap içinde ise 1 yapılır
                if (i - merkez)**2 + (j - merkez)**2 <= merkez**2:
                    yapi_elemani[i][j] = 1
        return yapi_elemani
    
    else:
        # Geçersiz şekil verilirse varsayılan kare döner
        return [[1 for _ in range(boyut)] for _ in range(boyut)]

# Görüntüyü ikili (binary) forma çevirir: piksel > eşik ise 255, değilse 0
def cv2_benzeri_esikleme(goruntu, esik_degerleri=[64, 128, 192]):
    if not esik_degerleri:
        raise ValueError("Eşik değerleri listesi boş olamaz!")
    
    # Grup sayısı = len(esik_degerleri) + 1
    binary = [[0 for _ in range(len(goruntu[0]))] for _ in range(len(goruntu))]
    
    for i in range(len(goruntu)):
        for j in range(len(goruntu[0])):
            piksel = goruntu[i][j]
            if isinstance(piksel, list):  # RGB ise ortalama al
                piksel = sum(piksel) // len(piksel)
            
            # Pikseli uygun gruba ata
            for k, esik in enumerate(esik_degerleri):
                if piksel <= esik:
                    binary[i][j] = k * (255 // len(esik_degerleri))  # Grup değeri
                    break
            else:
                binary[i][j] = 255  # Son grup (en yüksek değerler)
    
    return esik_degerleri, binary

# Görüntüyü kenarlardan sıfırlarla genişletir (padding)
def goruntu_doldur(goruntu, pad_size, deger=0):
    yukseklik = len(goruntu)
    genislik = len(goruntu[0])
    
    # Yeni sıfırlarla dolu görüntü oluştur
    # Orijinal görüntüyü ortasına kopyala
    padded = [[deger for _ in range(genislik + 2 * pad_size)] for _ in range(yukseklik + 2 * pad_size)]
    
    for i in range(yukseklik):
        for j in range(genislik):
            padded[i + pad_size][j + pad_size] = goruntu[i][j]
    
    return padded

# Beyaz bölgeleri genişletir (dilate): kenarlara doğru yayar
def genisletme(goruntu, yapi_elemani, iterasyon=1):
    _, binary = cv2_benzeri_esikleme(goruntu)  # Binary formata çevir
    sonuc = copy.deepcopy(binary)
    
    se_yukseklik = len(yapi_elemani)
    se_genislik = len(yapi_elemani[0])
    pad = se_yukseklik // 2  # Yapı elemanının yarıçapı kadar padding

    for _ in range(iterasyon):
        padded = goruntu_doldur(sonuc, pad, 0)  # Görüntüyü kenarlardan sıfırla genişlet
        temp = [[0 for _ in range(len(sonuc[0]))] for _ in range(len(sonuc))]  # Yeni boş çıktı
        
        for i in range(len(sonuc)):
            for j in range(len(sonuc[0])):
                dilate = False
                for se_i in range(se_yukseklik):
                    for se_j in range(se_genislik):
                        if yapi_elemani[se_i][se_j] == 1:
                            # Yapı elemanının altındaki alanda en az bir beyaz varsa genişlet
                            if padded[i + se_i][j + se_j] == 255:
                                dilate = True
                                break
                    if dilate:
                        break
                if dilate:
                    temp[i][j] = 255  # Pikseli beyaz yap
        sonuc = copy.deepcopy(temp)
    
    return sonuc

# Beyaz bölgeleri küçültür (erode): sadece yapı elemanı tam oturursa beyaz kalır
def asinma(goruntu, yapi_elemani, iterasyon=1):
    _, binary = cv2_benzeri_esikleme(goruntu)
    sonuc = copy.deepcopy(binary)
    
    se_yukseklik = len(yapi_elemani)
    se_genislik = len(yapi_elemani[0])
    pad = se_yukseklik // 2

    for _ in range(iterasyon):
        padded = goruntu_doldur(sonuc, pad, 0)
        temp = [[0 for _ in range(len(sonuc[0]))] for _ in range(len(sonuc))]

        for i in range(len(sonuc)):
            for j in range(len(sonuc[0])):
                erode = True
                for se_i in range(se_yukseklik):
                    for se_j in range(se_genislik):
                        if yapi_elemani[se_i][se_j] == 1:
                            # Yapı elemanının altındaki her nokta beyaz olmalı
                            if padded[i + se_i][j + se_j] != 255:
                                erode = False
                                break
                    if not erode:
                        break
                if erode:
                    temp[i][j] = 255  # Pikseli beyaz bırak
        sonuc = copy.deepcopy(temp)

    return sonuc

# Açma işlemi: önce aşındırma, sonra genişletme (gürültü temizliği için)
def acma(goruntu, yapi_elemani, iterasyon=1):
    sonuc = copy.deepcopy(goruntu)
    for _ in range(iterasyon):
        sonuc = asinma(sonuc, yapi_elemani, 1)       # Küçük gürültüleri temizle
        sonuc = genisletme(sonuc, yapi_elemani, 1)   # Yapıyı tekrar büyüt
    return sonuc

# Kapama işlemi: önce genişletme, sonra aşındırma (boşluk doldurma için)
def kapama(goruntu, yapi_elemani, iterasyon=1):
    sonuc = copy.deepcopy(goruntu)
    for _ in range(iterasyon):
        sonuc = genisletme(sonuc, yapi_elemani, 1)   # Beyaz alanları büyüt
        sonuc = asinma(sonuc, yapi_elemani, 1)       # Orijinal şekli geri kazandır
    return sonuc

def morfolojik_islem_uygula(goruntu, islem_tipi, sekil='kare', boyut=3, iterasyon=1):
    se = yapi_elemani_olustur(sekil, boyut)  # Yapı elemanını oluştur
    if islem_tipi == 'genisletme':
        return genisletme(goruntu, se, iterasyon)
    elif islem_tipi == 'asinma':
        return asinma(goruntu, se, iterasyon)
    elif islem_tipi == 'acma':
        return acma(goruntu, se, iterasyon)
    elif islem_tipi == 'kapama':
        return kapama(goruntu, se, iterasyon)
    else:
        raise ValueError(f"Geçersiz işlem tipi: {islem_tipi}")
