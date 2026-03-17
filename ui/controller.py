import os
import tkinter as tk


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
        self.layout.btn_refresh.config(command=self.refresh_subcarpetas)
        self.layout.btn_select.config(command=self.seleccionar_carpeta)
        self.layout.list_sub.bind("<<ListboxSelect>>", self.cargar_subcarpeta)
        self.layout.list_sub.bind("<Double-Button-1>", self.renombrar_inline)
        self.layout.root.bind("<F2>", self.renombrar_inline)

        self.layout.btn_copy.config(command=self.copiar_ruta)
        self.layout.btn_open.config(command=self.abrir_carpeta_aaa)

        self.layout.canvas.bind("<ButtonPress-1>", self.iniciar_arrastre)
        self.layout.canvas.bind("<ButtonRelease-1>", self.detener_arrastre)
        self.layout.canvas.bind("<B1-Motion>", self.arrastrar)

        self.layout.root.bind("s", self.guardar)

        self.layout.btn_edit.config(command=self.toggle_modo_edicion)

        self.layout.btn_scissors.config(command=self.toggle_modo_tijeras)

        # MENU CONTEXTUAL
        self.layout.menu_carpetas.entryconfig(
            "Abrir carpeta",
            command=self.abrir_carpeta
        )

        self.layout.menu_carpetas.entryconfig(
            "Cambiar nombre",
            command=self.renombrar_carpeta
        )

        self.layout.menu_carpetas.entryconfig(
            "Eliminar carpeta",
            command=self.eliminar_carpeta
        )

        self.layout.list_sub.bind("<Button-3>", self.menu_click_derecho)

        self.layout.zoom_slider.config(command=self.cambiar_zoom)

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

        if self.state.subcarpetas:
            self.layout.list_sub.selection_set(0)
            self.layout.list_sub.activate(0)
            self.actualizar_info_carpeta()    


    # ==========================
    # MODO EDICION
    # ==========================

    def toggle_modo_edicion(self):

        self.state.modo_edicion = not self.state.modo_edicion

        if self.state.modo_edicion:
            self.layout.btn_edit.config(text="Salir edición")
            self.notifier.mostrar("Modo edición activado", "cyan")
        else:
            self.layout.btn_edit.config(text="Edición")
            self.state.checks_carpetas.clear()
            self.notifier.mostrar("Modo edición desactivado", "cyan")

        self.actualizar_lista_checks()



    # ==========================
    # mostrar checks
    # ==========================
    def actualizar_lista_checks(self):

        self.layout.list_sub.delete(0, "end")

        for i, ruta in enumerate(self.state.subcarpetas):

            nombre = os.path.basename(ruta)

            if self.state.modo_edicion:

                if ruta in self.state.checks_carpetas:
                    prefijo = "[✓]"
                else:
                    prefijo = "[ ]"

                texto = f"{prefijo} {i+1}. {nombre}"

            else:

                texto = f"{i+1}. {nombre}"

            self.layout.list_sub.insert("end", texto)
            self.actualizar_info_carpeta()
   
    # ==========================
    # REFRESH SUBCARPETAS
    # ==========================




    def refresh_subcarpetas(self):

        if not self.state.carpeta_madre:
            return

        # guardar nombre de carpeta seleccionada
        seleccion = self.layout.list_sub.curselection()

        nombre_actual = None
        if seleccion:
            indice = seleccion[0]
            ruta_actual = self.state.subcarpetas[indice]
            nombre_actual = os.path.basename(ruta_actual)

        carpeta = self.state.carpeta_madre

        # recargar subcarpetas
        self.state.subcarpetas = self.file_manager.listar_subcarpetas(carpeta)

        # limpiar lista
        self.layout.list_sub.delete(0, "end")

        nuevo_indice = None

        for i, ruta in enumerate(self.state.subcarpetas):

            nombre = os.path.basename(ruta)

            self.layout.list_sub.insert("end", f"{i+1}. {nombre}")

            if nombre_actual and nombre == nombre_actual:
                nuevo_indice = i

        # restaurar selección
        if nuevo_indice is not None:

            self.layout.list_sub.selection_set(nuevo_indice)
            self.layout.list_sub.activate(nuevo_indice)

            ruta = self.state.subcarpetas[nuevo_indice]

            self.preview_panel.cargar_subcarpeta(
                ruta,
                self.cargar_imagen
            )

        self.notifier.mostrar("Lista actualizada", "green")
        self.actualizar_info_carpeta()
    # ==========================
    # SUBCARPETA
    # ==========================

    def cargar_subcarpeta(self, event):

        if not self.layout.list_sub.curselection():
            return

        indice = self.layout.list_sub.curselection()[0]
        ruta = self.state.subcarpetas[indice]

        self.actualizar_info_carpeta()

        # ==========================
        # MODO EDICION (CHECKS)
        # ==========================

        if self.state.modo_edicion:

            if ruta in self.state.checks_carpetas:
                self.state.checks_carpetas.remove(ruta)
            else:
                self.state.checks_carpetas.add(ruta)

            self.actualizar_lista_checks()
            return

        # ==========================
        # MODO NORMAL
        # ==========================

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
            self.state.crop_h,
            zoom=self.state.zoom
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
        # NUMERO EN ESQUINA
        # ==========================

        numero = str(self.state.contador_guardado)

        ancho = self.layout.canvas.winfo_width()
        alto = self.layout.canvas.winfo_height()

        # texto
        text_id = self.layout.canvas.create_text(
            ancho - 20,
            alto - 20,
            text=numero,
            fill="white",
            font=("Arial", 28, "bold"),
            anchor="se"
        )

        # fondo negro detrás (mejor visibilidad)
        bbox = self.layout.canvas.bbox(text_id)

        rect_id = self.layout.canvas.create_rectangle(
            bbox[0] - 10,
            bbox[1] - 5,
            bbox[2] + 10,
            bbox[3] + 5,
            fill="black",
            outline=""
        )

        # poner fondo detrás del texto
        self.layout.canvas.tag_lower(rect_id, text_id)

    # ==========================
    # COPIAR RUTA
    # ==========================

    def copiar_ruta(self):

        if not self.state.carpeta_madre:
            self.notifier.mostrar("No hay carpeta seleccionada", "red")
            return

        carpeta = os.path.join(self.state.carpeta_madre, "AAA")

        self.layout.root.clipboard_clear()
        self.layout.root.clipboard_append(carpeta)
        self.layout.root.update()

        self.notifier.mostrar("Ruta copiada al portapapeles", "green")

    # ==========================
    # ABRIR CARPETA AAA
    # ==========================

    def abrir_carpeta_aaa(self):

        if not self.state.carpeta_madre:
            self.notifier.mostrar("No hay carpeta seleccionada", "red")
            return

        carpeta = os.path.join(self.state.carpeta_madre, "AAA")

        if not os.path.exists(carpeta):
            self.notifier.mostrar("La carpeta AAA no existe aún", "red")
            return

        os.startfile(carpeta)


    # ==========================
    # ZOOM
    # ==========================

    def cambiar_zoom(self, valor):

        zoom = int(valor) / 100
        self.state.zoom = zoom

        self.renderizar()


    # ==========================
    # ABRIR CARPETA
    # ==========================


    def abrir_carpeta(self):

        if not self.layout.list_sub.curselection():
            return

        indice = self.layout.list_sub.curselection()[0]
        ruta = self.state.subcarpetas[indice]

        os.startfile(ruta)

    # ==========================
    # RENOMBRAR CARPETA
    # ==========================

    def renombrar_carpeta(self):

        if not self.layout.list_sub.curselection():
            return

        indice = self.layout.list_sub.curselection()[0]
        ruta_actual = self.state.subcarpetas[indice]

        import tkinter.simpledialog as simpledialog
        import tkinter.messagebox as messagebox

        nombre_actual = os.path.basename(ruta_actual)

        nuevo_nombre = simpledialog.askstring(
            "Cambiar nombre",
            "Nuevo nombre de carpeta:",
            initialvalue=nombre_actual
        )

        if not nuevo_nombre:
            return

        nueva_ruta = os.path.join(
            os.path.dirname(ruta_actual),
            nuevo_nombre
        )

        try:

            os.rename(ruta_actual, nueva_ruta)

            self.state.subcarpetas[indice] = nueva_ruta

            self.layout.list_sub.delete(indice)
            self.layout.list_sub.insert(
                indice,
                f"{indice+1}. {nuevo_nombre}"
            )

        except Exception as e:

            messagebox.showerror(
                "Error",
                f"No se pudo renombrar.\n{e}"
            )

    # ==========================
    # DRAG
    # ==========================

    def iniciar_arrastre(self, event):
        if self.state.modo_tijeras:
            self.state.tijeras_inicio = (event.x, event.y)

            # borrar rectángulo anterior si existe
            if self.state.tijeras_rect:
                self.layout.canvas.delete(self.state.tijeras_rect)
                self.state.tijeras_rect = None

            return

        # modo normal
        self.state.dragging = True

    def detener_arrastre(self, event):
        if self.state.modo_tijeras:
            return

        self.state.dragging = False

    def arrastrar(self, event):
        if self.state.modo_tijeras:

            if not self.state.tijeras_inicio:
                return

            x0, y0 = self.state.tijeras_inicio
            x1, y1 = event.x, event.y

            # borrar anterior
            if self.state.tijeras_rect:
                self.layout.canvas.delete(self.state.tijeras_rect)

            # dibujar nuevo
            self.state.tijeras_rect = self.layout.canvas.create_rectangle(
                x0, y0, x1, y1,
                outline="red",
                width=2
            )

            return

        
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
    # MENU CLICK DERECHO
    # ==========================

    def menu_click_derecho(self, event):

        try:
            index = self.layout.list_sub.nearest(event.y)

            # Solo cambiar selección si el elemento no está ya seleccionado
            if index not in self.layout.list_sub.curselection():
                self.layout.list_sub.selection_clear(0, tk.END)
                self.layout.list_sub.selection_set(index)

            self.layout.menu_carpetas.post(event.x_root, event.y_root)

        except:
            pass


    # ==========================
    # RENOMBRAR INLINE
    # ==========================

    def renombrar_inline(self, event=None):

        if not self.layout.list_sub.curselection():
            return

        index = self.layout.list_sub.curselection()[0]
        ruta_actual = self.state.subcarpetas[index]

        nombre_actual = os.path.basename(ruta_actual)

        # posición del item en el listbox
        bbox = self.layout.list_sub.bbox(index)

        if not bbox:
            return

        x, y, w, h = bbox

        entry = tk.Entry(self.layout.list_sub)
        entry.insert(0, nombre_actual)
        entry.select_range(0, tk.END)

        entry.place(x=x, y=y, width=w, height=h)
        entry.focus()

        def confirmar(event=None):

            nuevo_nombre = entry.get().strip()

            if not nuevo_nombre:
                entry.destroy()
                return

            nueva_ruta = os.path.join(
                os.path.dirname(ruta_actual),
                nuevo_nombre
            )

            try:

                os.rename(ruta_actual, nueva_ruta)

                self.state.subcarpetas[index] = nueva_ruta

                self.layout.list_sub.delete(index)
                self.layout.list_sub.insert(index, f"{index+1}. {nuevo_nombre}")

                self.notifier.mostrar("Carpeta renombrada", "green")

            except Exception as e:

                self.notifier.mostrar("Error al renombrar", "red")

            entry.destroy()

        entry.bind("<Return>", confirmar)
        entry.bind("<FocusOut>", lambda e: entry.destroy())

    # ==========================
    # ELIMINAR CARPETAS
    # ==========================

    def eliminar_carpeta(self):

        indices = self.layout.list_sub.curselection()

        if not indices:
            return

        import tkinter.messagebox as messagebox

        confirmar = messagebox.askyesno(
            "Eliminar carpetas",
            f"¿Eliminar {len(indices)} carpeta(s)?"
        )

        if not confirmar:
            return

        import shutil

        eliminadas = 0

        try:

            # recorrer de atrás hacia adelante
            for indice in reversed(indices):

                ruta = self.state.subcarpetas[indice]

                shutil.rmtree(ruta)

                del self.state.subcarpetas[indice]
                self.layout.list_sub.delete(indice)

                eliminadas += 1

            self.notifier.mostrar(
                f"{eliminadas} carpeta(s) eliminadas",
                "green"
            )

        except Exception as e:

            self.notifier.mostrar(
                "Error al eliminar carpetas",
                "red"
            )

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

    # ==========================
    # 
    # ==========================



    def actualizar_info_carpeta(self):

        # 🔹 nombre carpeta madre
        if self.state.carpeta_madre:
            nombre_madre = os.path.basename(self.state.carpeta_madre)
            self.layout.label_carpeta.config(text=f"Carpeta: {nombre_madre}")
        else:
            self.layout.label_carpeta.config(text="Carpeta: -")

        # 🔹 contador subcarpetas
        seleccion = self.layout.list_sub.curselection()

        total = len(self.state.subcarpetas)

        if not seleccion:
            self.layout.label_total.config(text=f"(0/{total})")
            return

        indice = seleccion[0]

        self.layout.label_total.config(
            text=f"({indice+1}/{total})"
        )


    # ==========================
    # tijeras
    # ==========================



    def toggle_modo_tijeras(self):

        self.state.modo_tijeras = not self.state.modo_tijeras

        if self.state.modo_tijeras:
            self.layout.btn_scissors.config(text="Salir ✂️")
            self.notifier.mostrar("Modo tijeras activado", "cyan")
        else:
            self.layout.btn_scissors.config(text="✂️ Tijeras")
            self.notifier.mostrar("Modo tijeras desactivado", "cyan")

