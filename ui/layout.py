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

        self.canvas = tk.Canvas(
            self.frame_derecho,
            width=800,
            height=500,
            bg="gray"
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.match_label = tk.Label(
            self.frame_derecho,
            text="Esperando...",
            font=("Arial", 18)
        )
        self.match_label.pack(pady=10)