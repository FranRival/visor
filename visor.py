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

crop_x = 0
crop_y = 0
crop_w = 0
crop_h = 0

dragging = False

# ==============================
# SELECCIONAR CARPETA MADRE
# ==============================

def seleccionar_carpeta():
    global carpeta_madre, subcarpetas

    carpeta_madre = filedialog.askdirectory()
    if not carpeta_madre:
        return

    list_sub.delete(0, tk.END)
    subcarpetas.clear()

    for item in os.listdir(carpeta_madre):
        ruta = os.path.join(carpeta_madre, item)
        if os.path.isdir(ruta):
            subcarpetas.append(ruta)
            list_sub.insert(tk.END, item)

# ==============================
# CARGAR SUBCARPETA (CARGA PROGRESIVA)
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

        if index >= len(imagenes):
            canvas_preview.configure(scrollregion=canvas_preview.bbox("all"))
            return

        ruta = imagenes[index]

        try:
            with Image.open(ruta) as img:
                img = img.convert("RGB")
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

        root.after(1, lambda: cargar_lote(index + 1))

    cargar_lote()

# ==============================
# CARGAR IMAGEN
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
# RENDERIZAR
# ==============================

def renderizar():
    global imagen_actual

    if imagen_original is None:
        return

    img_display = imagen_original.copy()
    img_display.thumbnail((800, 500), Image.LANCZOS)

    escala_x = imagen_original.width / img_display.width
    escala_y = imagen_original.height / img_display.height

    crop_x_disp = int(crop_x / escala_x)
    crop_y_disp = int(crop_y / escala_y)
    crop_w_disp = int(crop_w / escala_x)
    crop_h_disp = int(crop_h / escala_y)

    overlay = Image.new("RGBA", img_display.size, (0, 0, 0, 120))
    img_display = img_display.convert("RGBA")
    img_display = Image.alpha_composite(img_display, overlay)

    zona = img_display.crop((
        crop_x_disp,
        crop_y_disp,
        crop_x_disp + crop_w_disp,
        crop_y_disp + crop_h_disp
    ))
    img_display.paste(zona, (crop_x_disp, crop_y_disp))

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
    if imagen_original is None or not carpeta_madre:
        return

    carpeta_destino = os.path.join(carpeta_madre, "AAA")
    os.makedirs(carpeta_destino, exist_ok=True)

    existentes = [
        int(f.split(".")[0])
        for f in os.listdir(carpeta_destino)
        if f.split(".")[0].isdigit()
    ]

    siguiente = max(existentes) + 1 if existentes else 1

    recorte = imagen_original.crop(
        (crop_x, crop_y, crop_x + crop_w, crop_y + crop_h)
    )

    ruta_guardado = os.path.join(carpeta_destino, f"{siguiente}.jpg")
    recorte.save(ruta_guardado, quality=95)

    status_var.set(f"{siguiente}.jpg - guardada")

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

# ===== SCROLL CORRECTO Y ESTABLE =====

def _on_mousewheel(event):
    canvas_preview.yview_scroll(int(-1 * (event.delta / 120)), "units")

def _on_mousewheel_linux_up(event):
    canvas_preview.yview_scroll(-1, "units")

def _on_mousewheel_linux_down(event):
    canvas_preview.yview_scroll(1, "units")

def activar_scroll(event):
    canvas_preview.focus_set()


# ===== SCROLL WINDOWS CORREGIDO DEFINITIVO =====

def _on_mousewheel(event):
    canvas_preview.yview_scroll(int(-1 * (event.delta / 120)), "units")

def _on_mousewheel_linux_up(event):
    canvas_preview.yview_scroll(-1, "units")

def _on_mousewheel_linux_down(event):
    canvas_preview.yview_scroll(1, "units")

def bind_scroll(event):
    canvas_preview.bind_all("<MouseWheel>", _on_mousewheel)
    canvas_preview.bind_all("<Button-4>", _on_mousewheel_linux_up)
    canvas_preview.bind_all("<Button-5>", _on_mousewheel_linux_down)

def unbind_scroll(event):
    canvas_preview.unbind_all("<MouseWheel>")
    canvas_preview.unbind_all("<Button-4>")
    canvas_preview.unbind_all("<Button-5>")

canvas_preview.bind("<Enter>", bind_scroll)
canvas_preview.bind("<Leave>", unbind_scroll)



canvas = tk.Canvas(root, width=800, height=500, bg="gray")
canvas.pack(side=tk.RIGHT, expand=True)

canvas.bind("<ButtonPress-1>", iniciar_arrastre)
canvas.bind("<ButtonRelease-1>", detener_arrastre)
canvas.bind("<B1-Motion>", arrastrar)

status_var = tk.StringVar()
status_label = tk.Label(root, textvariable=status_var, anchor="e", fg="green")
status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

root.bind("s", guardar_recorte)
root.bind("S", guardar_recorte)

root.mainloop()
