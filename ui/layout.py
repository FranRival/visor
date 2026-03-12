import tkinter as tk
from config import WINDOW_WIDTH, WINDOW_HEIGHT


class Layout:

    def __init__(self, root):
        self.root = root
        self.root.title("Visor Crop MVP")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        self.build()

    def build(self):

        # ========================
        # SPLIT PRINCIPAL
        # ========================

        self.main_split = tk.PanedWindow(
            self.root,
            orient=tk.HORIZONTAL,
            sashwidth=6,
            bg="#444"
        )

        self.main_split.pack(fill=tk.BOTH, expand=True)

        # ========================
        # FRAME IZQUIERDO
        # ========================

        self.frame_izq = tk.Frame(self.main_split, width=350)
        self.frame_izq.pack_propagate(False)

        self.main_split.add(self.frame_izq)

        
        # CONTENEDOR BOTONES SUPERIORES
        # CONTENEDOR SUPERIOR
        self.top_buttons = tk.Frame(self.frame_izq)
        self.top_buttons.pack(fill=tk.X, pady=10)

        self.btn_select = tk.Button(
            self.top_buttons,
            text="Seleccionar Carpeta"
        )
        self.btn_select.pack(side=tk.LEFT, padx=5)

        self.btn_refresh = tk.Button(
            self.top_buttons,
            text="Refresh"
        )
        self.btn_refresh.pack(side=tk.LEFT, padx=5)

        self.btn_edit = tk.Button(
            self.top_buttons,
            text="Edición"
        )
        self.btn_edit.pack(side=tk.LEFT, padx=5)

        # etiqueta nombre carpeta
        self.label_carpeta = tk.Label(
            self.top_buttons,
            text="Carpeta: -",
            anchor="w"
        )
        self.label_carpeta.pack(side=tk.LEFT, padx=10)

        # contador carpetas
        self.label_total = tk.Label(
            self.top_buttons,
            text="(0)"
        )
        self.label_total.pack(side=tk.LEFT)

        # ========================
        # SPLIT VERTICAL IZQUIERDO
        # ========================

        self.left_split = tk.PanedWindow(
            self.frame_izq,
            orient=tk.VERTICAL,
            sashwidth=6
        )

        self.left_split.pack(fill=tk.BOTH, expand=True, padx=5)

        # ========================
        # CONTENEDOR EXPLORADOR
        # ========================

        self.list_container = tk.Frame(self.left_split)

        self.list_sub = tk.Listbox(
            self.list_container,
            selectmode=tk.EXTENDED
        )

        self.list_sub.pack(fill=tk.BOTH, expand=True)

        self.left_split.add(self.list_container, height=150)


        # ========================
        # PREVIEW SCROLL
        # ========================

        self.preview_container = tk.Frame(self.left_split)

        self.left_split.add(self.preview_container)

        self.canvas_preview = tk.Canvas(self.preview_container)
        self.scrollbar_preview = tk.Scrollbar(
            self.preview_container,
            orient="vertical",
            command=self.canvas_preview.yview
        )

        self.frame_preview = tk.Frame(self.canvas_preview)

        self.frame_preview.bind(
            "<Configure>",
            lambda e: self.canvas_preview.configure(
                scrollregion=self.canvas_preview.bbox("all")
            )
        )

        self.canvas_preview.create_window(
            (0, 0),
            window=self.frame_preview,
            anchor="nw"
        )

        self.canvas_preview.configure(
            yscrollcommand=self.scrollbar_preview.set
        )

        self.canvas_preview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar_preview.pack(side=tk.RIGHT, fill=tk.Y)

        
        # ========================
        # FRAME DERECHO
        # ========================

        self.frame_derecho = tk.Frame(self.main_split)
        self.main_split.add(self.frame_derecho)

        # Dividimos horizontalmente
        self.canvas = tk.Canvas(
            self.frame_derecho,
            bg="gray"
        )

        # ========================
        # ZOOM SLIDER
        # ========================

        self.zoom_slider = tk.Scale(
            self.frame_derecho,
            from_=50,
            to=200,
            orient="horizontal",
            label="Zoom %",
            length=200
        )

        self.zoom_slider.set(100)
        self.zoom_slider.pack(side=tk.BOTTOM, pady=5)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.match_frame = tk.Frame(
            self.frame_derecho,
            bg="black",
            width=180
        )
        self.match_frame.pack(side=tk.RIGHT, fill=tk.Y)
        self.match_frame.pack_propagate(False)

        self.match_label = tk.Label(
            self.match_frame,
            text="Esperando...",
            font=("Arial", 18, "bold"),
            bg="black",
            fg="yellow"
        )
        self.match_label.pack(pady=20)

        # Espaciador
        self.spacer = tk.Frame(self.match_frame, bg="black")
        self.spacer.pack(expand=True)

        # Botón copiar ruta
        self.btn_copy = tk.Button(
            self.match_frame,
            text="Copiar ruta"
        )
        self.btn_copy.pack(pady=5, padx=10, fill=tk.X)

        # Botón abrir carpeta AAA
        self.btn_open = tk.Button(
            self.match_frame,
            text="Abrir carpeta AAA"
        )
        self.btn_open.pack(pady=5, padx=10, fill=tk.X)


         #eliminar carpeta       
        self.menu_carpetas = tk.Menu(self.root, tearoff=0)

        self.menu_carpetas.add_command(
            label="Abrir carpeta"
        )

        self.menu_carpetas.add_command(
            label="Cambiar nombre"
        )

        self.menu_carpetas.add_separator()

        self.menu_carpetas.add_command(
            label="Eliminar carpeta"
        )