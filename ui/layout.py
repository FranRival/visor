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
        # FRAME IZQUIERDO
        # ========================

        self.frame_izq = tk.Frame(self.root, width=350)
        self.frame_izq.pack(side=tk.LEFT, fill=tk.Y)
        self.frame_izq.pack_propagate(False)

        self.btn_select = tk.Button(self.frame_izq, text="Seleccionar Carpeta")
        self.btn_select.pack(pady=10)

        self.list_sub = tk.Listbox(self.frame_izq)
        self.list_sub.pack(fill=tk.X, padx=5)

        # ========================
        # PREVIEW SCROLL
        # ========================

        self.preview_container = tk.Frame(self.frame_izq)
        self.preview_container.pack(fill=tk.BOTH, expand=True)

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

        self.frame_derecho = tk.Frame(self.root)
        self.frame_derecho.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Dividimos horizontalmente
        self.canvas = tk.Canvas(
            self.frame_derecho,
            bg="gray"
        )
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
                
        