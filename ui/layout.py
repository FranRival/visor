import tkinter as tk
from config import WINDOW_WIDTH, WINDOW_HEIGHT

class Layout:

    def __init__(self, root):
        self.root = root
        self.root.title("Visor Crop MVP")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        self.build()

    def build(self):
        self.frame_izq = tk.Frame(self.root, width=350)
        self.frame_izq.pack(side=tk.LEFT, fill=tk.Y)
        self.frame_izq.pack_propagate(False)

        self.btn_select = tk.Button(self.frame_izq, text="Seleccionar Carpeta")
        self.btn_select.pack(pady=10)

        self.list_sub = tk.Listbox(self.frame_izq)
        self.list_sub.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.frame_derecho = tk.Frame(self.root)
        self.frame_derecho.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.frame_derecho, width=800, height=500, bg="gray")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.match_label = tk.Label(self.frame_derecho, text="Esperando...", font=("Arial", 18))
        self.match_label.pack(pady=10)