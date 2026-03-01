import os
from tkinter import filedialog

class FileManager:

    def seleccionar_carpeta(self):
        return filedialog.askdirectory()

    def listar_subcarpetas(self, carpeta_madre):
        return [
            os.path.join(carpeta_madre, f)
            for f in os.listdir(carpeta_madre)
            if os.path.isdir(os.path.join(carpeta_madre, f))
        ]

    def crear_carpeta(self, ruta):
        os.makedirs(ruta, exist_ok=True)

    def abrir_en_explorador(self, ruta):
        if os.path.exists(ruta):
            os.startfile(ruta)

    def renombrar(self, origen, destino):
        os.rename(origen, destino)

    def existe(self, ruta):
        return os.path.exists(ruta)