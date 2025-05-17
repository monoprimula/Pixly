import numpy as np

def rgb_to_hsv(img):
    # RGB görüntü değilse hata ver
    if len(img.shape) != 3 or img.shape[2] != 3:
        raise ValueError("Görüntü 3 kanallı RGB olmalıdır")
    
    # 0-1 aralığına normalize et
    img_norm = img.astype(np.float32) / 255.0
    
    # R, G, B kanallarını ayır
    r, g, b = img_norm[:,:,0], img_norm[:,:,1], img_norm[:,:,2]
    
    # V (value): maksimum kanal değeri
    v = np.max(img_norm, axis=2)
    
    # Minimum değer
    min_val = np.min(img_norm, axis=2)
    
    # Renk aralığı
    delta = v - min_val
    
    # S (saturation): parlaklığa göre normalleştirilmiş fark
    s = np.zeros_like(v)
    mask = v > 0
    s[mask] = delta[mask] / v[mask]
    
    # H (hue): renk tonu, kanal farklarına göre hesaplanır
    h = np.zeros_like(v)
    mask_r = (v == r) & (delta != 0)
    h[mask_r] = ((g[mask_r] - b[mask_r]) / delta[mask_r]) % 6

    mask_g = (v == g) & (delta != 0)
    h[mask_g] = ((b[mask_g] - r[mask_g]) / delta[mask_g]) + 2

    mask_b = (v == b) & (delta != 0)
    h[mask_b] = ((r[mask_b] - g[mask_b]) / delta[mask_b]) + 4

    # H değeri 0-1 aralığına getirilir
    h = h / 6.0

    # HSV kanalları birleştirilir
    hsv = np.stack([h, s, v], axis=2)

    # 8-bit'e dönüştür
    hsv_8bit = np.clip(hsv * 255.0, 0, 255).astype(np.uint8)
    
    return hsv_8bit

def rgb_to_lab(img):
    if len(img.shape) != 3 or img.shape[2] != 3:
        raise ValueError("Görüntü 3 kanallı RGB olmalıdır")
    
    # 0-1 aralığına normalize et
    img_norm = img.astype(np.float32) / 255.0

    # Gamma düzeltmesi yapılır
    mask = img_norm > 0.04045
    img_norm[mask] = ((img_norm[mask] + 0.055) / 1.055) ** 2.4
    img_norm[~mask] = img_norm[~mask] / 12.92

    # RGB -> XYZ dönüşüm matrisi
    M = np.array([
        [0.4124, 0.3576, 0.1805],
        [0.2126, 0.7152, 0.0722],
        [0.0193, 0.1192, 0.9505]
    ])

    # Her piksel için matris çarpımı uygulanır
    xyz = np.zeros_like(img_norm)
    for i in range(img_norm.shape[0]):
        for j in range(img_norm.shape[1]):
            xyz[i, j, :] = np.dot(M, img_norm[i, j, :])

    # XYZ değerleri referans beyaz noktasına göre normalize edilir
    xyz_ref = np.array([0.95047, 1.0, 1.08883])
    xyz_norm = xyz / xyz_ref

    # f(x) fonksiyonu uygulanır
    mask = xyz_norm > 0.008856
    xyz_norm[mask] = np.power(xyz_norm[mask], 1/3)
    xyz_norm[~mask] = 7.787 * xyz_norm[~mask] + 16/116

    # L, a, b değerleri hesaplanır
    L = 116 * xyz_norm[:,:,1] - 16
    a = 500 * (xyz_norm[:,:,0] - xyz_norm[:,:,1])
    b = 200 * (xyz_norm[:,:,1] - xyz_norm[:,:,2])

    # Lab birleştirilir
    lab = np.stack([L, a, b], axis=2)

    # 8-bit'e uygun şekilde dönüştürülür
    L_scaled = L * 255 / 100
    a_scaled = a + 128
    b_scaled = b + 128

    lab_8bit = np.stack([L_scaled, a_scaled, b_scaled], axis=2)
    lab_8bit = np.clip(lab_8bit, 0, 255).astype(np.uint8)
    
    return lab_8bit

def rgb_to_ycbcr(img):
    if len(img.shape) != 3 or img.shape[2] != 3:
        raise ValueError("Görüntü 3 kanallı RGB olmalıdır")

    img_float = img.astype(np.float32)

    # Y: parlaklık (ağırlık ortalamaya göre hesaplanıyor), Cb ve Cr: renk farkı bileşenleri
    y = 0.299 * img_float[:,:,0] + 0.587 * img_float[:,:,1] + 0.114 * img_float[:,:,2]
    cb = 128 - 0.168736 * img_float[:,:,0] - 0.331264 * img_float[:,:,1] + 0.5 * img_float[:,:,2]
    cr = 128 + 0.5 * img_float[:,:,0] - 0.418688 * img_float[:,:,1] - 0.081312 * img_float[:,:,2]

    # Y, Cb, Cr kanallarını birleştir
    ycbcr = np.stack([y, cb, cr], axis=2)

    # 8-bit'e dönüştür
    ycbcr = np.clip(ycbcr, 0, 255).astype(np.uint8)
    
    return ycbcr
