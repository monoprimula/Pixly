from .goruntu_araclar import gri_tonlamaya_cevir

def prewitt_kenar_tespiti(img):
    """Prewitt kenar tespiti"""
    # Görüntüyü gri tonlamaya çevir
    if isinstance(img[0][0], list):
        img = gri_tonlamaya_cevir(img)
    
    # Prewitt kernel'leri
    kernelx = [[-1, 0, 1],
               [-1, 0, 1],
               [-1, 0, 1]]
    kernely = [[-1, -1, -1],
               [0, 0, 0],
               [1, 1, 1]]
    
    h = len(img)
    w = len(img[0])
    
    # Kenar pikselleri kopyalayarak padding yap
    temp = [[0 for _ in range(w + 2)] for _ in range(h + 2)]
    for i in range(h):
        for j in range(w):
            temp[i+1][j+1] = img[i][j]
    
    # Kenar piksellerini kopyala
    for j in range(w):
        temp[0][j+1] = img[0][j]  # üst kenar
        temp[-1][j+1] = img[-1][j]  # alt kenar
    for i in range(h):
        temp[i+1][0] = img[i][0]  # sol kenar
        temp[i+1][-1] = img[i][-1]  # sağ kenar
    temp[0][0] = img[0][0]  # sol üst köşe
    temp[0][-1] = img[0][-1]  # sağ üst köşe
    temp[-1][0] = img[-1][0]  # sol alt köşe
    temp[-1][-1] = img[-1][-1]  # sağ alt köşe
    
    # Gradyan hesaplama
    grad_x = [[0 for _ in range(w)] for _ in range(h)]
    grad_y = [[0 for _ in range(w)] for _ in range(h)]
    
    for i in range(h):
        for j in range(w):
            # X gradyanı
            grad_x[i][j] = (
                temp[i][j+2] - temp[i][j] +
                temp[i+1][j+2] - temp[i+1][j] +
                temp[i+2][j+2] - temp[i+2][j]
            )
            
            # Y gradyanı
            grad_y[i][j] = (
                temp[i+2][j] + temp[i+2][j+1] + temp[i+2][j+2] -
                temp[i][j] - temp[i][j+1] - temp[i][j+2]
            )
    
    # Gradyan büyüklüğü
    grad_mag = [[0 for _ in range(w)] for _ in range(h)]
    max_mag = 0
    
    for i in range(h):
        for j in range(w):
            # sqrt(x^2 + y^2)
            mag = (grad_x[i][j]**2 + grad_y[i][j]**2)**0.5
    #Bu formül öklidyen normdur. Kenar gücünü belirler.
            grad_mag[i][j] = mag
            if mag > max_mag:
                max_mag = mag
    
    # Normalizasyon ve eşikleme
    sonuc = [[0 for _ in range(w)] for _ in range(h)]
    for i in range(h):
        for j in range(w):
            # Normalizasyon: 0-255 aralığına çek
            norm_deger = int((grad_mag[i][j] / max_mag) * 255)
            # Eşikleme
            sonuc[i][j] = 255 if norm_deger > 30 else 0
    
    return sonuc 

