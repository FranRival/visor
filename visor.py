import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw

# ==============================
# VARIABLES GLOBALES
# ==============================

root = tk.Tk()
root.title("Visor Crop MVP")

imagen_original = None
imagen_actual = None

imagenes = []
subcarpetas = []

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
            subcarpetas.append(ruta)     # guardamos ruta real
            list_sub.insert(tk.END, item)  # mostramos solo nombre


# ==============================
# CARGAR IMÁGENES
# ==============================

def cargar_subcarpeta(event):
    global imagenes

    if not list_sub.curselection():
        return

    indice = list_sub.curselection()[0]
    subcarpeta = subcarpetas[indice]

    list_img.delete(0, tk.END)
    imagenes.clear()

    for archivo in os.listdir(subcarpeta):
        if archivo.lower().endswith((".jpg", ".jpeg", ".png")):
            imagenes.append(os.path.join(subcarpeta, archivo))  # ruta real
            list_img.insert(tk.END, archivo)  # SOLO nombre


# ==============================
# MOSTRAR IMAGEN
# ==============================

def cargar_imagen(event):
    global imagen_original
    global crop_x, crop_y, crop_w, crop_h

    if not list_img.curselection():
        return

    ruta = imagenes[list_img.curselection()[0]]
    imagen_original = Image.open(ruta)

    ancho, alto = imagen_original.size

    # Rectángulo 16:9 al 80% del ancho
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

    # Oscurecer
    overlay = Image.new("RGBA", img_display.size, (0, 0, 0, 120))
    img_display = img_display.convert("RGBA")
    img_display = Image.alpha_composite(img_display, overlay)

    # Restaurar zona visible
    zona = img_display.crop((
        crop_x_disp,
        crop_y_disp,
        crop_x_disp + crop_w_disp,
        crop_y_disp + crop_h_disp
    ))
    img_display.paste(zona, (crop_x_disp, crop_y_disp))

    # Borde rojo
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
# DRAG VERTICAL
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

frame_izq = tk.Frame(root)
frame_izq.pack(side=tk.LEFT, fill=tk.Y)

btn = tk.Button(frame_izq, text="Seleccionar Carpeta", command=seleccionar_carpeta)
btn.pack(pady=5)

list_sub = tk.Listbox(frame_izq, width=35)
list_sub.pack(padx=5, pady=5)
list_sub.bind("<<ListboxSelect>>", cargar_subcarpeta)

list_img = tk.Listbox(frame_izq, width=35)
list_img.pack(padx=5, pady=5)
list_img.bind("<<ListboxSelect>>", cargar_imagen)

canvas = tk.Canvas(root, width=800, height=500, bg="gray")
canvas.pack(side=tk.RIGHT)

canvas.bind("<ButtonPress-1>", iniciar_arrastre)
canvas.bind("<ButtonRelease-1>", detener_arrastre)
canvas.bind("<B1-Motion>", arrastrar)

root.mainloop()
