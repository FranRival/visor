class CropEngine:

    def calcular_crop_inicial(self, imagen):
        ancho, alto = imagen.size

        crop_w = int(ancho * 0.8)
        crop_h = int(crop_w * 9 / 16)

        if crop_h > alto:
            crop_h = int(alto * 0.8)
            crop_w = int(crop_h * 16 / 9)

        crop_x = (ancho - crop_w) // 2
        crop_y = (alto - crop_h) // 2

        return crop_x, crop_y, crop_w, crop_h