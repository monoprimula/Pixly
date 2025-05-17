def goruntu_toplama(img1, img2):
    """
    İki görüntüyü toplar
    :param img1: İlk görüntü (2D veya 3D liste)
    :param img2: İkinci görüntü (2D veya 3D liste)
    :return: Toplanmış görüntü
    """
    # Görüntüleri aynı boyuta getir
    img1, img2 = goruntuleri_ayni_boyuta_getir(img1, img2)
    
    # Toplama işlemi
    sonuc = []
    for y in range(len(img1)):
        satir = []
        for x in range(len(img1[0])):
            if isinstance(img1[0][0], list):  # RGB görüntü
                piksel = []
                for kanal in range(3):
                    deger = img1[y][x][kanal] + img2[y][x][kanal]
                    piksel.append(min(255, max(0, deger)))
                satir.append(piksel)
            else:  # Gri tonlamalı görüntü
                deger = img1[y][x] + img2[y][x]
                satir.append(min(255, max(0, deger)))
        sonuc.append(satir)
    
    return sonuc

def goruntu_bolme(img1, img2):
    """
    İki görüntüyü böler (img1 / img2)
    :param img1: İlk görüntü (2D veya 3D liste)
    :param img2: İkinci görüntü (2D veya 3D liste)
    :return: Bölünmüş görüntü
    """
    # Görüntüleri aynı boyuta getir
    img1, img2 = goruntuleri_ayni_boyuta_getir(img1, img2)
    
    # Bölme işlemi
    sonuc = []
    for y in range(len(img1)):
        satir = []
        for x in range(len(img1[0])):
            if isinstance(img1[0][0], list):  # RGB görüntü
                piksel = []
                for kanal in range(3):
                    payda = img2[y][x][kanal] if img2[y][x][kanal] != 0 else 1
                    deger = (img1[y][x][kanal] / payda) * 255
                    piksel.append(min(255, max(0, int(deger))))
                satir.append(piksel)
            else:  # Gri tonlamalı görüntü
                payda = img2[y][x] if img2[y][x] != 0 else 1
                deger = (img1[y][x] / payda) * 255
                satir.append(min(255, max(0, int(deger))))
        sonuc.append(satir)
    
    return sonuc

def agirlikli_toplama(img1, img2, alpha=0.5, beta=0.5):
    """
    İki görüntüyü ağırlıklı olarak toplar
    :param img1: İlk görüntü (2D veya 3D liste)
    :param img2: İkinci görüntü (2D veya 3D liste)
    :param alpha: İlk görüntünün ağırlığı (0-1 arası)
    :param beta: İkinci görüntünün ağırlığı (0-1 arası)
    :return: Ağırlıklı toplanmış görüntü
    """
    # Görüntüleri aynı boyuta getir
    img1, img2 = goruntuleri_ayni_boyuta_getir(img1, img2)
    
    # Ağırlıklı toplama işlemi
    sonuc = []
    for y in range(len(img1)):
        satir = []
        for x in range(len(img1[0])):
            if isinstance(img1[0][0], list):  # RGB görüntü
                piksel = []
                for kanal in range(3):
                    deger = alpha * img1[y][x][kanal] + beta * img2[y][x][kanal]
                    piksel.append(min(255, max(0, int(deger))))
                satir.append(piksel)
            else:  # Gri tonlamalı görüntü
                deger = alpha * img1[y][x] + beta * img2[y][x]
                satir.append(min(255, max(0, int(deger))))
        sonuc.append(satir)
    
    return sonuc 

def goruntuleri_ayni_boyuta_getir(img1, img2):
    """
    İki görüntüyü aynı boyuta getirir. İkinci görüntüyü ilk görüntünün boyutuna yeniden boyutlandırır.
    
    Parametreler:
    img1: İlk görüntü (2D veya 3D liste)
    img2: İkinci görüntü (2D veya 3D liste)
    
    Dönüş:
    img1, img2: Aynı boyuta getirilmiş görüntüler
    """
    h1, w1 = len(img1), len(img1[0])
    h2, w2 = len(img2), len(img2[0])
    
    if h1 != h2 or w1 != w2:
        # İkinci görüntüyü yeniden boyutlandır
        yeni_img2 = []
        for y in range(h1):
            satir = []
            for x in range(w1):
                # En yakın komşu interpolasyonu
                orj_y = int(y * h2 / h1)
                orj_x = int(x * w2 / w1)
                satir.append(img2[orj_y][orj_x])
            yeni_img2.append(satir)
        img2 = yeni_img2
    
    return img1, img2