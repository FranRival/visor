from PIL import Image, ImageTk, ImageDraw

class ImageManager:

    def cargar_imagen(self, ruta):
        return Image.open(ruta)

    def crear_miniatura(self, ruta, size):
        with Image.open(ruta) as img:
            img.thumbnail((size, size))
            return ImageTk.PhotoImage(img)