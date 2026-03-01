import os

class EventController:

    def __init__(self, state, layout, file_manager, image_manager, crop_engine):
        self.state = state
        self.layout = layout
        self.file_manager = file_manager
        self.image_manager = image_manager
        self.crop_engine = crop_engine

        self.bind_events()

    def bind_events(self):
        self.layout.btn_select.config(command=self.seleccionar_carpeta)
        self.layout.list_sub.bind("<<ListboxSelect>>", self.cargar_subcarpeta)
        self.layout.root.bind("s", self.guardar_recorte)

    def seleccionar_carpeta(self):
        carpeta = self.file_manager.seleccionar_carpeta()
        if not carpeta:
            return

        self.state.carpeta_madre = carpeta
        self.state.subcarpetas = self.file_manager.listar_subcarpetas(carpeta)

        self.layout.list_sub.delete(0, "end")

        for i, ruta in enumerate(self.state.subcarpetas):
            nombre = os.path.basename(ruta)
            self.layout.list_sub.insert("end", f"{i+1}. {nombre}")

    def cargar_subcarpeta(self, event):
        if not self.layout.list_sub.curselection():
            return

        indice = self.layout.list_sub.curselection()[0]
        ruta = self.state.subcarpetas[indice]

        archivos = [
            f for f in os.listdir(ruta)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ]

        if not archivos:
            return

        imagen_path = os.path.join(ruta, archivos[0])
        self.state.imagen_original = self.image_manager.cargar_imagen(imagen_path)

        cx, cy, cw, ch = self.crop_engine.calcular_crop_inicial(self.state.imagen_original)

        self.state.crop_x = cx
        self.state.crop_y = cy
        self.state.crop_w = cw
        self.state.crop_h = ch

        self.renderizar()

    def renderizar(self):
        img = self.image_manager.renderizar(
            self.state.imagen_original,
            self.state.crop_x,
            self.state.crop_y,
            self.state.crop_w,
            self.state.crop_h
        )

        self.state.imagen_actual = img
        self.layout.canvas.delete("all")
        self.layout.canvas.create_image(400, 250, anchor="center", image=img)

    def guardar_recorte(self, event=None):
        if self.state.imagen_original is None:
            return

        carpeta = os.path.join(self.state.carpeta_madre, "AAA")
        self.file_manager.crear_carpeta(carpeta)

        ruta_guardado = os.path.join(carpeta, f"{self.state.contador_guardado}.jpg")

        self.image_manager.guardar_recorte(
            self.state.imagen_original,
            ruta_guardado,
            self.state.crop_x,
            self.state.crop_y,
            self.state.crop_w,
            self.state.crop_h
        )

        indice = self.layout.list_sub.curselection()[0]

        if self.crop_engine.validar_match(self.state.contador_guardado, indice):
            self.layout.match_label.config(text="MATCH", fg="lime")
        else:
            self.layout.match_label.config(text="NO MATCH", fg="red")

        self.state.contador_guardado += 1