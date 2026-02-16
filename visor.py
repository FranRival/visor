import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw

# ==============================
# CONFIGURACIÓN
# ==============================

THUMB_SIZE = 120

# ==============================
# VARIABLES GLOBALES
# ==============================

root = tk.Tk()
root.title("Visor Crop MVP")
root.geometry("1200x650")

imagen_original = None
imagen_actual = None

imagenes = []
subcarpetas = []
miniaturas = []

carpeta_madre = ""
carpeta_destino_actual = ""

contador_guardado = 1

crop_x = 0
crop_y = 0
crop_w = 0
crop_h = 0

dragging = False

# ==============================
# SELECCIONAR CARPETA MADRE
# ==============================

def seleccionar_carpeta():
    global carpeta_madre, subcarpetas, contador_guardado, carpeta_destino_actual

    carpeta_madre = filedialog.askdirectory()
    if not carpeta_madre:
        return

    contador_guardado = 1
    carpeta_destino_actual = os.path.join(carpeta_madre, "AAA")

    status_var.set("")

    list_sub.delete(0, tk.END)
    subcarpetas.clear()

    for item in os.listdir(carpeta_madre):
        ruta = os.path.join(carpeta_madre, item)
        if os.path.isdir(ruta):
            subcarpetas.append(ruta)
            list_sub.insert(tk.END, item)

# ==============================
# ABRIR CARPETA AAA
# ==============================

def abrir_carpeta_aaa():
    global carpeta_destino_actual

    if not carpeta_destino_actual:
        return

    os.makedirs(carpeta_destino_actual, exist_ok=True)
    os.startfile(carpeta_destino_actual)

# ==============================
# CARGAR SUBCARPETA
# ==============================

def cargar_subcarpeta(event):
    global imagenes, miniaturas

    if not list_sub.curselection():
        return

    indice = list_sub.curselection()[0]
    subcarpeta = subcarpetas[indice]

    imagenes.clear()
    miniaturas.clear()

    for widget in frame_preview.winfo_children():
        widget.destroy()

    archivos = [
        f for f in os.listdir(subcarpeta)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    imagenes.extend([os.path.join(subcarpeta, f) for f in archivos])

    fila = 0
    columna = 0

    def cargar_lote(index=0):
        nonlocal fila, columna

        LOTE = 8

        for _ in range(LOTE):

            if index >= len(imagenes):
                canvas_preview.configure(scrollregion=canvas_preview.bbox("all"))
                return

            ruta = imagenes[index]

            try:
                with Image.open(ruta) as img:
                    img.thumbnail((THUMB_SIZE, THUMB_SIZE), Image.BILINEAR)
                    mini = ImageTk.PhotoImage(img)
                    miniaturas.append(mini)

                    lbl = tk.Label(frame_preview, image=mini, cursor="hand2")
                    lbl.image = mini
                    lbl.grid(row=fila, column=columna, padx=5, pady=5)

                    lbl.bind("<Button-1>", lambda e, r=ruta: cargar_imagen_directa(r))

                    columna += 1
                    if columna == 3:
                        columna = 0
                        fila += 1

            except:
                pass

            index += 1

        root.after(10, lambda: cargar_lote(index))

    cargar_lote()

# ==============================
# CARGAR IMAGEN GRANDE
# ==============================

def cargar_imagen_directa(ruta):
    global imagen_original
    global crop_x, crop_y, crop_w, crop_h

    imagen_original = Image.open(ruta)

    ancho, alto = imagen_original.size

    crop_w = int(ancho * 0.8)
    crop_h = int(crop_w * 9 / 16)

    if crop_h > alto:
        crop_h = int(alto * 0.8)
        crop_w = int(crop_h * 16 / 9)

    crop_x = (ancho - crop_w) // 2
    crop_y = (alto - crop_h) // 2

    renderizar()

# ==============================
# RENDERIZAR (SIN OSCURECIMIENTO)
# ==============================

def renderizar():
    global imagen_actual

    if imagen_original is None:
        return

    img_display = imagen_original.copy()
    img_display.thumbnail((800, 500), Image.BILINEAR)

    escala_x = imagen_original.width / img_display.width
    escala_y = imagen_original.height / img_display.height

    crop_x_disp = int(crop_x / escala_x)
    crop_y_disp = int(crop_y / escala_y)
    crop_w_disp = int(crop_w / escala_x)
    crop_h_disp = int(crop_h / escala_y)

    draw = ImageDraw.Draw(img_display)
    draw.rectangle(
        (
            crop_x_disp,
            crop_y_disp,
            crop_x_disp + crop_w_disp,
            crop_y_disp + crop_h_disp
        ),
        outline="red",
        width=3
    )

    imagen_actual = ImageTk.PhotoImage(img_display)

    canvas.delete("all")
    canvas.create_image(400, 250, anchor=tk.CENTER, image=imagen_actual)

# ==============================
# GUARDAR RECORTE
# ==============================

def guardar_recorte(event=None):
    global contador_guardado

    if imagen_original is None or not carpeta_destino_actual:
        return

    os.makedirs(carpeta_destino_actual, exist_ok=True)

    ruta_guardado = os.path.join(carpeta_destino_actual, f"{contador_guardado}.jpg")

    recorte = imagen_original.crop(
        (crop_x, crop_y, crop_x + crop_w, crop_y + crop_h)
    )

    recorte.save(ruta_guardado, quality=95)

    status_var.set(f"{contador_guardado}.jpg - guardada")

    contador_guardado += 1

# ==============================
# DRAG
# ==============================

def iniciar_arrastre(event):
    global dragging
    dragging = True

def detener_arrastre(event):
    global dragging
    dragging = False

def arrastrar(event):
    global crop_y

    if not dragging or imagen_original is None:
        return

    escala_y = imagen_original.height / canvas.winfo_height()
    nuevo_y = int(event.y * escala_y - crop_h / 2)

    crop_y = max(0, min(nuevo_y, imagen_original.height - crop_h))
    renderizar()

# ==============================
# INTERFAZ
# ==============================

frame_izq = tk.Frame(root, width=350)
frame_izq.pack(side=tk.LEFT, fill=tk.Y)
frame_izq.pack_propagate(False)

btn = tk.Button(frame_izq, text="Seleccionar Carpeta", command=seleccionar_carpeta)
btn.pack(pady=5)

list_sub = tk.Listbox(frame_izq, width=30, height=8)
list_sub.pack(padx=5, pady=5, fill=tk.X)
list_sub.bind("<<ListboxSelect>>", cargar_subcarpeta)

preview_container = tk.Frame(frame_izq)
preview_container.pack(fill=tk.BOTH, expand=True)

canvas_preview = tk.Canvas(preview_container)
scrollbar = tk.Scrollbar(preview_container, orient="vertical", command=canvas_preview.yview)

frame_preview = tk.Frame(canvas_preview)

frame_preview.bind(
    "<Configure>",
    lambda e: canvas_preview.configure(scrollregion=canvas_preview.bbox("all"))
)

canvas_preview.create_window((0, 0), window=frame_preview, anchor="nw")
canvas_preview.configure(yscrollcommand=scrollbar.set)

canvas_preview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

def _on_mousewheel(event):
    canvas_preview.yview_scroll(int(-1 * (event.delta / 120)), "units")

def bind_scroll(event):
    canvas_preview.bind_all("<MouseWheel>", _on_mousewheel)

def unbind_scroll(event):
    canvas_preview.unbind_all("<MouseWheel>")

canvas_preview.bind("<Enter>", bind_scroll)
canvas_preview.bind("<Leave>", unbind_scroll)

canvas = tk.Canvas(root, width=800, height=500, bg="gray")
canvas.pack(side=tk.RIGHT, expand=True)

canvas.bind("<ButtonPress-1>", iniciar_arrastre)
canvas.bind("<ButtonRelease-1>", detener_arrastre)
canvas.bind("<B1-Motion>", arrastrar)

# ==============================
# PANEL INFERIOR DERECHO
# ==============================

right_panel = tk.Frame(root)
right_panel.place(relx=1.0, rely=1.0, anchor="se", x=-15, y=-15)

status_var = tk.StringVar()
status_label = tk.Label(right_panel, textvariable=status_var, fg="green")
status_label.pack(anchor="e")

btn_abrir = tk.Button(right_panel, text="Abrir carpeta AAA", command=abrir_carpeta_aaa)
btn_abrir.pack(anchor="e", pady=3)

root.bind("s", guardar_recorte)
root.bind("S", guardar_recorte)

root.mainloop()
