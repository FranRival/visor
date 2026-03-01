import os


class Controller:

    def __init__(self, state, layout, file_manager,
                 image_manager, crop_engine,
                 matcher, preview_panel,
                 notifier):

        self.state = state
        self.layout = layout
        self.file_manager = file_manager
        self.image_manager = image_manager
        self.crop_engine = crop_engine
        self.matcher = matcher
        self.preview_panel = preview_panel
        self.notifier = notifier

        self.bind()

    # ==========================
    # BINDS
    # ==========================

    def bind(self):
        self.layout.btn_select.config(command=self.seleccionar_carpeta)
        self.layout.list_sub.bind("<<ListboxSelect>>", self.cargar_subcarpeta)

        self.layout.canvas.bind("<ButtonPress-1>", self.iniciar_arrastre)
        self.layout.canvas.bind("<ButtonRelease-1>", self.detener_arrastre)
        self.layout.canvas.bind("<B1-Motion>", self.arrastrar)

        self.layout.root.bind("s", self.guardar)

    # ==========================
    # CARPETA
    # ==========================

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

    # ==========================
    # SUBCARPETA
    # ==========================

    def cargar_subcarpeta(self, event):
        if not self.layout.list_sub.curselection():
            return

        indice = self.layout.list_sub.curselection()[0]
        ruta = self.state.subcarpetas[indice]

        self.preview_panel.cargar_subcarpeta(
            ruta,
            self.cargar_imagen
        )

    # ==========================
    # CARGAR IMAGEN
    # ==========================

    def cargar_imagen(self, ruta):
        self.state.imagen_original = self.image_manager.cargar_imagen(ruta)

        cx, cy, cw, ch = self.crop_engine.calcular_crop_inicial(
            self.state.imagen_original
        )

        self.state.crop_x = cx
        self.state.crop_y = cy
        self.state.crop_w = cw
        self.state.crop_h = ch

        self.renderizar()

    # ==========================
    # RENDER
    # ==========================

    def renderizar(self):
        if self.state.imagen_original is None:
            return

        img = self.image_manager.renderizar(
            self.state.imagen_original,
            self.state.crop_x,
            self.state.crop_y,
            self.state.crop_w,
            self.state.crop_h
        )

        self.state.imagen_actual = img

        self.layout.canvas.delete("all")
        self.layout.canvas.create_image(
            400,
            250,
            anchor="center",
            image=img
        )

    # ==========================
    # DRAG
    # ==========================

    def iniciar_arrastre(self, event):
        self.state.dragging = True

    def detener_arrastre(self, event):
        self.state.dragging = False

    def arrastrar(self, event):
        if not self.state.dragging:
            return

        if self.state.imagen_original is None:
            return

        alto_canvas = self.layout.canvas.winfo_height()
        escala_y = self.state.imagen_original.height / alto_canvas

        nuevo_y = int(event.y * escala_y - self.state.crop_h / 2)

        nuevo_y = max(
            0,
            min(
                nuevo_y,
                self.state.imagen_original.height - self.state.crop_h
            )
        )

        self.state.crop_y = nuevo_y

        self.renderizar()

    # ==========================
    # GUARDAR
    # ==========================

    def guardar(self, event=None):

        if self.state.imagen_original is None:
            self.notifier.mostrar("No hay imagen cargada", "red")
            return

        carpeta = os.path.join(self.state.carpeta_madre, "AAA")
        self.file_manager.crear_carpeta(carpeta)

        ruta_guardado = os.path.join(
            carpeta,
            f"{self.state.contador_guardado}.jpg"
        )

        self.image_manager.guardar_recorte(
            self.state.imagen_original,
            ruta_guardado,
            self.state.crop_x,
            self.state.crop_y,
            self.state.crop_w,
            self.state.crop_h
        )

        indice = self.layout.list_sub.curselection()[0]

        if self.matcher.validar(self.state.contador_guardado, indice):
            self.layout.match_label.config(text="MATCH", fg="lime")
        else:
            self.layout.match_label.config(text="NO MATCH", fg="red")

        self.notifier.mostrar(
            f"{self.state.contador_guardado}.jpg guardada",
            "cyan"
        )

        self.state.contador_guardado += 1