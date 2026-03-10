from PIL import Image, ImageTk
import os

class PreviewPanel:

    def __init__(self, frame_preview, canvas_preview, state, thumb_size):
        self.frame = frame_preview
        self.canvas = canvas_preview
        self.state = state
        self.thumb_size = thumb_size

        # ==========================
        # SCROLL CON RUEDA DEL MOUSE
        # ==========================

        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

    def _bind_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def limpiar(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.state.miniaturas.clear()

    def cargar_subcarpeta(self, ruta, callback_click):
        self.limpiar()

        archivos = [
            f for f in os.listdir(ruta)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ]

        self.state.imagenes = [os.path.join(ruta, f) for f in archivos]

        fila = 0
        columna = 0

        def cargar_lote(index=0):
            nonlocal fila, columna
            LOTE = 8

            for _ in range(LOTE):

                if index >= len(self.state.imagenes):
                    self.canvas.configure(scrollregion=self.canvas.bbox("all"))
                    return

                ruta_img = self.state.imagenes[index]

                try:
                    with Image.open(ruta_img) as img:
                        img.thumbnail((self.thumb_size, self.thumb_size))
                        mini = ImageTk.PhotoImage(img)
                        self.state.miniaturas.append(mini)

                        import tkinter as tk
                        lbl = tk.Label(self.frame, image=mini, cursor="hand2")
                        lbl.image = mini
                        lbl.grid(row=fila, column=columna, padx=5, pady=5)

                        lbl.bind(
                            "<Button-1>",
                            lambda e, r=ruta_img: callback_click(r)
                        )

                        columna += 1
                        if columna == 3:
                            columna = 0
                            fila += 1

                except:
                    pass

                index += 1

            self.canvas.after(10, lambda: cargar_lote(index))

        cargar_lote()