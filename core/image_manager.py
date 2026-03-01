from PIL import Image, ImageTk, ImageDraw
from config import THUMB_SIZE

class ImageManager:

    def cargar_imagen(self, ruta):
        return Image.open(ruta)

    def crear_miniatura(self, ruta):
        with Image.open(ruta) as img:
            img.thumbnail((THUMB_SIZE, THUMB_SIZE))
            return ImageTk.PhotoImage(img)

    def renderizar(self, imagen_original, crop_x, crop_y, crop_w, crop_h):
        img_display = imagen_original.copy()
        img_display.thumbnail((800, 500))

        escala_x = imagen_original.width / img_display.width
        escala_y = imagen_original.height / img_display.height

        crop_x_disp = int(crop_x / escala_x)
        crop_y_disp = int(crop_y / escala_y)
        crop_w_disp = int(crop_w / escala_x)
        crop_h_disp = int(crop_h / escala_y)

        draw = ImageDraw.Draw(img_display)
        draw.rectangle(
            (
                crop_x_disp,
                crop_y_disp,
                crop_x_disp + crop_w_disp,
                crop_y_disp + crop_h_disp
            ),
            outline="red",
            width=3
        )

        return ImageTk.PhotoImage(img_display)

    def guardar_recorte(self, imagen_original, ruta_guardado, crop_x, crop_y, crop_w, crop_h):
        recorte = imagen_original.crop(
            (crop_x, crop_y, crop_x + crop_w, crop_y + crop_h)
        )
        recorte.save(ruta_guardado, quality=95)