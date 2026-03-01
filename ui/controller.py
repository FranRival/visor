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

    def bind(self):
        self.layout.btn_select.config(command=self.seleccionar_carpeta)
        self.layout.list_sub.bind("<<ListboxSelect>>", self.cargar_subcarpeta)
        self.layout.root.bind("s", self.guardar)

    def seleccionar_carpeta(self):
        carpeta = self.file_manager.seleccionar_carpeta()
        if not carpeta:
            return

        self.state.carpeta_madre = carpeta
        self.state.subcarpetas = self.file_manager.listar_subcarpetas(carpeta)

        self.layout.list_sub.delete(0, "end")

        for i, ruta in enumerate(self.state.subcarpetas):
            import os
            nombre = os.path.basename(ruta)
            self.layout.list_sub.insert("end", f"{i+1}. {nombre}")

    def cargar_subcarpeta(self, event):
        if not self.layout.list_sub.curselection():
            return

        indice = self.layout.list_sub.curselection()[0]
        ruta = self.state.subcarpetas[indice]

        self.preview_panel.cargar_subcarpeta(
            ruta,
            self.cargar_imagen
        )

    def cargar_imagen(self, ruta):
        self.state.imagen_original = self.image_manager.cargar_imagen(ruta)

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

    def guardar(self, event=None):
        if self.state.imagen_original is None:
            self.notifier.mostrar("No hay imagen cargada", "red")
            return

        import os
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

        if self.matcher.validar(self.state.contador_guardado, indice):
            self.layout.match_label.config(text="MATCH", fg="lime")
        else:
            self.layout.match_label.config(text="NO MATCH", fg="red")

        self.notifier.mostrar(f"{self.state.contador_guardado}.jpg guardada", "cyan")

        self.state.contador_guardado += 1