import math
import random
from PIL import Image
import numpy as np

def resmi_listeden_donustur(img_list):
    """Liste yapısındaki görüntüyü PIL Image'a dönüştürür"""
    h = len(img_list)
    w = len(img_list[0])
    
    # Tek kanallı mı çok kanallı mı kontrol et
    if isinstance(img_list[0][0], list):
        c = len(img_list[0][0])
        arr = np.zeros((h, w, c), dtype=np.uint8)
        for y in range(h):
            for x in range(w):
                for k in range(c):
                    arr[y, x, k] = img_list[y][x][k]
        return Image.fromarray(arr)
    else:
        arr = np.zeros((h, w), dtype=np.uint8)
        for y in range(h):
            for x in range(w):
                arr[y, x] = img_list[y][x]
        return Image.fromarray(arr, mode='L')

def resmi_listeye_donustur(img):
    """PIL Image'ı liste yapısına dönüştürür"""
    img_array = np.array(img)
    h, w = img_array.shape[0], img_array.shape[1]

    # Gri tonlamalı mı renkli mi kontrol et
    if len(img_array.shape) == 2:
# Gri tonlamalı resimlerde dizi 2 boyutludur: (h, w)
        result = []
        for y in range(h):
            row = []
            for x in range(w):
                row.append(int(img_array[y, x]))
            result.append(row)
# Satır satır tüm pikseller gezilir. 


    else:
        c = img_array.shape[2]
# Renkli resimlerde dizi 3 boyutludur: (h, w, c)
        result = []
        for y in range(h):
            row = []
            for x in range(w):
                pixel = []
                for k in range(c):
                    pixel.append(int(img_array[y, x, k]))
                row.append(pixel)
            result.append(row)
    return result

#  Her pikseldeki kanal (kırmızı, yeşil, mavi, alfa) değerleri gezilir.


def gaussian_kernel_olustur(boyut, sigma=1.0):
#Gaussian kernel, görüntü işlemede genellikle bulanıklaştırma (blur), gürültü giderme ve kenar yumuşatma gibi işlemlerde kullanılır.

    """Gaussian kernel oluşturma """
    kernel = []
    merkez = boyut // 2
    toplam = 0.0
    for i in range(boyut):
        satir = []
        for j in range(boyut):
            x = i - merkez
            y = j - merkez 

# Gaussian formülünde mesafe hesaplamak için gerekir.
            deger = math.exp(-(x**2 + y**2) / (2 * sigma**2)) #2D Gaussian dağılımının değerini hesaplar.
            satir.append(deger)
            toplam += deger 
        kernel.append(satir)
    # Normalize et
    for i in range(boyut):
        for j in range(boyut):
            kernel[i][j] /= toplam

    return kernel
#  Bu adımda kernel normalize edilir. Yani tüm elemanlar, toplam değere bölünerek toplamları 1 olacak şekilde ayarlanır.


def padding_ekle(img, pad):
    """Kenarları pad kadar doldur"""
    h = len(img)
    w = len(img[0])
    c = len(img[0][0]) if isinstance(img[0][0], list) else 1
# Görüntü gri tonlamalı mı (c = 1) yoksa renkli mi (c = 3) olduğunu tespit eder. 
    if c == 1:
        yeni = [[0]*(w+2*pad) for _ in range(h+2*pad)]
# Yeni görüntü boyutu: (h + 2*pad) yüksekliğinde ve (w + 2*pad) genişliğinde sıfırlarla dolu bir matris oluşturulur.

        for y in range(h):
            for x in range(w):
                yeni[y+pad][x+pad] = img[y][x]
# Orijinal görüntüdeki pikselleri, yeni matrisin ortasına yerleştirir. Kenarlar padding nedeniyle boş kalır.

    else:
        yeni = [[[0]*c for _ in range(w+2*pad)] for _ in range(h+2*pad)]
        for y in range(h):
            for x in range(w): 
                yeni[y+pad][x+pad] = img[y][x][:] 

    return yeni

def gaussian_bulaniklastir(img, kernel_boyutu, sigma=1.0):  # sigma parametresi eklendi
    """Gaussian bulanıklaştırma"""
    kernel = gaussian_kernel_olustur(kernel_boyutu, sigma)  # sigma parametresi verildi
    pad = kernel_boyutu // 2
# Konvolüsyonun merkezli çalışması için gerekli padding miktarı hesaplanır.
    h = len(img)
    w = len(img[0])
    c = len(img[0][0]) if isinstance(img[0][0], list) else 1
# c == 1 ise gri tonlamalı, c > 1 ise renkli 
    padded = padding_ekle(img, pad)
    sonuc = []
    for y in range(h):
        satir = []
        for x in range(w):
            if c == 1:
                toplam = 0.0
                for ky in range(kernel_boyutu):
                    for kx in range(kernel_boyutu):
                        toplam += padded[y+ky][x+kx] * kernel[ky][kx]
                satir.append(int(min(255, max(0, toplam))))
            else:
                piksel = []
                for kanal in range(c):
                    toplam = 0.0
                    for ky in range(kernel_boyutu):
                        for kx in range(kernel_boyutu):
                            toplam += padded[y+ky][x+kx][kanal] * kernel[ky][kx]
                    piksel.append(int(min(255, max(0, toplam))))
                satir.append(piksel)
        sonuc.append(satir)
    return sonuc

def medyan_bulaniklastir(img, kernel_boyutu):
    """Medyan bulanıklaştırma """
    pad = kernel_boyutu // 2
    h = len(img)
    w = len(img[0])
    c = len(img[0][0]) if isinstance(img[0][0], list) else 1
    padded = padding_ekle(img, pad)
    sonuc = []
    for y in range(h):
        satir = []
        for x in range(w):
            if c == 1:
                degerler = []
                for ky in range(kernel_boyutu):
                    for kx in range(kernel_boyutu):
                        degerler.append(padded[y+ky][x+kx])
                degerler.sort()
                satir.append(degerler[len(degerler)//2])
#Ortanca değer (medyan) bulunur. Ortanca değer, yeni piksel olarak atanır.
            else:
                piksel = []
                for kanal in range(c):
                    degerler = []
                    for ky in range(kernel_boyutu):
                        for kx in range(kernel_boyutu):
                            degerler.append(padded[y+ky][x+kx][kanal])
                    degerler.sort()
                    piksel.append(degerler[len(degerler)//2])
                satir.append(piksel)
        sonuc.append(satir)
# Her kanal (R, G, B) için ayrı ayrı medyan alınır.
    return sonuc

def sobel(img, dx, dy, ksize=3):
    """Sobel operatörü"""
    # Sobel kernel'leri
    if dx == 1 and dy == 0:
        kernel = [[-1, 0, 1],
                 [-2, 0, 2],
                 [-1, 0, 1]]
    elif dx == 0 and dy == 1:
        kernel = [[-1, -2, -1],
                 [0, 0, 0],
                 [1, 2, 1]]
    else:
        kernel_x = [[-1, 0, 1],
                   [-2, 0, 2],
                   [-1, 0, 1]]
        kernel_y = [[-1, -2, -1],
                   [0, 0, 0],
                   [1, 2, 1]]
        kernel = [[kernel_x[i][j] * dx + kernel_y[i][j] * dy for j in range(3)] for i in range(3)]
    
    pad = ksize // 2
    h = len(img)
    w = len(img[0])
    c = len(img[0][0]) if isinstance(img[0][0], list) else 1
    padded = padding_ekle(img, pad)
    sonuc = []
    
    for y in range(h):
        satir = []
        for x in range(w):
            if c == 1:
                toplam = 0.0
                for ky in range(ksize):
                    for kx in range(ksize):
                        toplam += padded[y+ky][x+kx] * kernel[ky][kx]
                satir.append(int(min(255, max(0, toplam))))
            else:
                piksel = []
                for kanal in range(c):
                    toplam = 0.0
                    for ky in range(ksize):
                        for kx in range(ksize):
                            toplam += padded[y+ky][x+kx][kanal] * kernel[ky][kx]
                    piksel.append(int(min(255, max(0, toplam))))
                satir.append(piksel)
        sonuc.append(satir)
    return sonuc

def laplace(img, ksize=3):
    """Laplace operatörü """
#.Görüntüde ani geçişleri tespit etme.
    # Laplace kernel
    if ksize == 3:
        kernel = [[0, 1, 0],
                 [1, -4, 1],
                 [0, 1, 0]]
    else:
        kernel = [[1, 1, 1],
                 [1, -8, 1],
                 [1, 1, 1]]
# Ortadaki -4 veya -8 değeri, merkez pikselin ağırlığıdır.
    pad = ksize // 2
# Filtrenin kenar bölgelere düzgün uygulanması için görüntü etrafına padding (çerçeve) eklemek gerekir.
    h = len(img)
    w = len(img[0])
    c = len(img[0][0]) if isinstance(img[0][0], list) else 1
    padded = padding_ekle(img, pad)
    sonuc = []
    
    for y in range(h):
        satir = []
        for x in range(w):
            if c == 1:
                toplam = 0.0
                for ky in range(ksize):
                    for kx in range(ksize):
                        toplam += padded[y+ky][x+kx] * kernel[ky][kx]
                satir.append(int(min(255, max(0, toplam))))
            else:
                piksel = []
                for kanal in range(c):
                    toplam = 0.0
                    for ky in range(ksize):
                        for kx in range(ksize):
                            toplam += padded[y+ky][x+kx][kanal] * kernel[ky][kx]
                    piksel.append(int(min(255, max(0, toplam))))
                satir.append(piksel)
        sonuc.append(satir)
    return sonuc

def unsharp_mask(img, miktar=1.0, yaricap=1.0, esik=0):
# Görüntüyü bulanıklaştırdıktan sonra, orijinal görüntüden bulanık görüntüyü çıkartıp farkı (kenar bilgisi) güçlendirerek netleştirmektir.

    """
    Unsharp mask filtresi uygular 
    :param img: Giriş görüntüsü
    :param miktar: Keskinleştirme miktarı (0.0 - 5.0)
    :param yaricap: Bulanıklaştırma yarıçapı
    :param esik: Eşik değeri
    :return: Keskinleştirilmiş görüntü
    """
# Bu filtre, görüntüyü daha keskin (daha net, daha belirgin kenarlı) hale getirmek için kullanılır.

    # Gaussian blur uygula - Sigma parametresini açıkça ver
    kernel_size = int(yaricap * 2 + 1)
    blurred = gaussian_bulaniklastir(img, kernel_size, sigma=yaricap)
# Bulanıklaştırma, görüntüdeki yüksek frekans (kenar ve detayları) azaltır.
    
    h = len(img)
    w = len(img[0])
    c = len(img[0][0]) if isinstance(img[0][0], list) else 1
    sonuc = []
    
    for y in range(h):
        satir = []
        for x in range(w):
            if c == 1:
                # Fark görüntüsünü hesapla
                diff = img[y][x] - blurred[y][x]
                
                # Eşik değerini uygula
                if esik > 0 and abs(diff) < esik:
                    diff = 0
                # Eğer fark eşik değerinden küçükse, o fark önemsizdir diyerek 0 yapılır (gürültü bastırma).Yani sadece gerçekten belirgin farklar (kenarlar) korunur.
                
                # Keskinleştirilmiş görüntüyü hesapla
                deger = img[y][x] + miktar * diff 
               # Kenardan gelen fark miktar katsayısı ile orijinale eklenir. Böylece kenarlar güçlendirilmiş olur.
                satir.append(int(min(255, max(0, deger))))
            else:
                piksel = []
                for kanal in range(c):
                    # Fark görüntüsünü hesapla
                    diff = img[y][x][kanal] - blurred[y][x][kanal]
                    
                    # Eşik değerini uygula
                    if esik > 0 and abs(diff) < esik:
                        diff = 0
                    
                    # Keskinleştirilmiş görüntüyü hesapla
                    deger = img[y][x][kanal] + miktar * diff
                    piksel.append(int(min(255, max(0, deger))))
                satir.append(piksel)
        sonuc.append(satir)
    return sonuc

def tuz_biber_gurultusu_ekle(img, yogunluk=0.05):
# Rastgele piksellerin siyah (0) veya beyaz (255) yapılmasıyla oluşur. 

    """
    Görüntüye tuz ve biber gürültüsü ekler 
    :param img: Giriş görüntüsü
    :param yogunluk: Gürültü yoğunluğu (0.0 - 1.0)
    :return: Gürültülü görüntü
    """
    h = len(img)
    w = len(img[0])
    c = len(img[0][0]) if isinstance(img[0][0], list) else 1
    sonuc = []
    
    for y in range(h):
        satir = []
        for x in range(w):
            if c == 1:
                if random.random() < yogunluk:
                    # Tuz veya biber gürültüsü ekle
                    satir.append(255 if random.random() < 0.5 else 0)
# random.random() her çağrıldığında 0 ile 1 arasında rastgele bir sayı üretir. Piksel 0 yapılırsa (biber) siyah, 255 yapılırsa (tuz) beyaz olur.

                else:
                    satir.append(img[y][x])
            else:
                piksel = []
                for kanal in range(c):
                    if random.random() < yogunluk:
                        # Tuz veya biber gürültüsü ekle
                        piksel.append(255 if random.random() < 0.5 else 0)
                    else:
                        piksel.append(img[y][x][kanal])
                satir.append(piksel)
        sonuc.append(satir)
    return sonuc

def ortalama_filtresi(img, kernel_boyutu=3):
    """Ortalama filtresi """
# Ortalama filtresi, bir pikselin etrafındaki piksellerin ortalamasını alarak gürültüyü azaltmak ve görüntüyü yumuşatmak için kullanılan temel bir düşük geçiren filtre (low-pass filter) yöntemidir. 
    pad = kernel_boyutu // 2
    h = len(img)
    w = len(img[0])
    c = len(img[0][0]) if isinstance(img[0][0], list) else 1
    padded = padding_ekle(img, pad)
# Görüntü kenarlarına padding eklenerek kernel’in taşmaması sağlanır.
    sonuc = []
    
    for y in range(h):
        satir = []
        for x in range(w):
            if c == 1:
                toplam = 0
                for ky in range(kernel_boyutu):
                    for kx in range(kernel_boyutu):
                        toplam += padded[y+ky][x+kx]
                satir.append(int(toplam / (kernel_boyutu * kernel_boyutu)))
# y+ky ve x+kx ile, pikselin çevresindeki komşularına ulaşılır.Hepsi toplanır, sonra toplam komşu sayısına bölünerek ortalama hesaplanır.

            else:
                piksel = []
                for kanal in range(c):
                    toplam = 0
                    for ky in range(kernel_boyutu):
                        for kx in range(kernel_boyutu):
                            toplam += padded[y+ky][x+kx][kanal]
                    piksel.append(int(toplam / (kernel_boyutu * kernel_boyutu)))
                satir.append(piksel)
        sonuc.append(satir)
    return sonuc

def medyan_filtresi(img, kernel_boyutu=3):
    """Medyan filtresi """
# Her pikselin çevresindeki komşularının medyan değeri (ortanca değeri) ile değiştirilmesidir.

    pad = kernel_boyutu // 2
    h = len(img)
    w = len(img[0])
    c = len(img[0][0]) if isinstance(img[0][0], list) else 1
    padded = padding_ekle(img, pad)
    sonuc = []
    
    for y in range(h):
        satir = []
        for x in range(w):
            if c == 1:
                degerler = []
                for ky in range(kernel_boyutu):
                    for kx in range(kernel_boyutu):
                        degerler.append(padded[y+ky][x+kx])
                degerler.sort()
                satir.append(degerler[len(degerler)//2])
# Ortanca (medyan) değeri seçilerek o pikselin yeni değeri olarak atanır.
            else:
                piksel = []
                for kanal in range(c):
                    degerler = []
                    for ky in range(kernel_boyutu):
                        for kx in range(kernel_boyutu):
                            degerler.append(padded[y+ky][x+kx][kanal])
                    degerler.sort()
                    piksel.append(degerler[len(degerler)//2])
                satir.append(piksel)
        sonuc.append(satir)
    return sonuc

def mean_konvolusyon(img, kernel_boyutu):
    """Ortalama konvolüsyon """
# Görüntüyü bulanıklaştırmak için kullanılır. 
    pad = kernel_boyutu // 2
    h = len(img)
    w = len(img[0])
    c = len(img[0][0]) if isinstance(img[0][0], list) else 1
    padded = padding_ekle(img, pad)
    sonuc = []
    
    for y in range(h):
        satir = []
        for x in range(w):
            if c == 1:
                toplam = 0
                for ky in range(kernel_boyutu):
                    for kx in range(kernel_boyutu):
                        toplam += padded[y+ky][x+kx]
                satir.append(int(toplam / (kernel_boyutu * kernel_boyutu)))
# Ortalaması alınarak yeni değeri atanır.
            else:
                piksel = []
                for kanal in range(c):
                    toplam = 0
                    for ky in range(kernel_boyutu):
                        for kx in range(kernel_boyutu):
                            toplam += padded[y+ky][x+kx][kanal]
                    piksel.append(int(toplam / (kernel_boyutu * kernel_boyutu)))
                satir.append(piksel)
        sonuc.append(satir)
    return sonuc

