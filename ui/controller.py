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
    # REFRESH SUBCARPETAS
    # ==========================

    def refresh_subcarpetas(self):

        if not self.state.carpeta_madre:
            return

        carpeta = self.state.carpeta_madre

        self.state.subcarpetas = self.file_manager.listar_subcarpetas(carpeta)

        self.layout.list_sub.delete(0, "end")

        for i, ruta in enumerate(self.state.subcarpetas):
            nombre = os.path.basename(ruta)
            self.layout.list_sub.insert("end", f"{i+1}. {nombre}")

        self.notifier.mostrar("Lista actualizada", "green")
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


        #cambios
        #1. En el panel del explorador necesitamos un modo de edicion. un check. ese check va a seleccionar varias carpetas y luego eliminar
        #2. en el boton de refresh, al dar click me reiniciar y me borra la ubicacion
        #3. necesitamos poder hacer mas grande el panel del explorador. con un triangulo en la extrema derecha. 
        #4. poder eliminar imagenes 
        #5. desaparecio el nombre de la carpeta y la cantidad de carpetas porque estaban los nombres donde esta el boton de refresh 