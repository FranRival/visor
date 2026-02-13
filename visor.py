import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw

# VARIABLES GLOBALES
root = tk.Tk()
root.title("Visor Crop MVP")

carpeta_madre = ""
subcarpetas = []
imagenes = []
imagen_actual = None
imagen_original = None

contador = 1
destino_path = ""

crop_x = 0
crop_y = 0
crop_w = 0
crop_h = 0

dragging = False

# ------------------------
# SELECCIONAR CARPETA MADRE
# ------------------------
def seleccionar_carpeta():
    global carpeta_madre, subcarpetas
    carpeta_madre = filedialog.askdirectory()
    if not carpeta_madre:
        return
    cargar_subcarpetas()

def cargar_subcarpetas():
    global subcarpetas
    list_cm.delete(0, tk.END)
    subcarpetas = [
        f for f in os.listdir(carpeta_madre)
        if os.path.isdir(os.path.join(carpeta_madre, f)) and not f.startswith("[AAA")
    ]
    for s in subcarpetas:
        list_cm.insert(tk.END, s)

# ------------------------
# CARGAR IMÁGENES
# ------------------------
def cargar_imagenes(event):
    global imagenes, contador, destino_path
    seleccion = list_cm.curselection()
    if not seleccion:
        return

    contador = 1  # reinicia contador por carpeta madre

    sub = subcarpetas[seleccion[0]]
    ruta = os.path.join(carpeta_madre, sub)

    imagenes = [
        f for f in os.listdir(ruta)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    list_img.delete(0, tk.END)
    for img in imagenes:
        list_img.insert(tk.END, img)

    # Crear carpeta destino
    destino_path = os.path.join(carpeta_madre, "[AAA")
    os.makedirs(destino_path, exist_ok=True)

# ------------------------
# MOSTRAR IMAGEN
# ------------------------
def mostrar_imagen(event):
    global imagen_original, imagen_actual
    global crop_x, crop_y, crop_w, crop_h

    seleccion = list_img.curselection()
    if not seleccion:
        return

    sub_index = list_cm.curselection()[0]
    sub = subcarpetas[sub_index]
    ruta = os.path.join(carpeta_madre, sub, imagenes[seleccion[0]])

    imagen_original = Image.open(ruta).convert("RGB")

    ancho, alto = imagen_original.size

    # Rectángulo 16:9 al 80% del ancho
    crop_w = int(ancho * 0.8)
    crop_h = int(crop_w * 9 / 16)

    crop_x = (ancho - crop_w) // 2
    crop_y = (alto - crop_h) // 2

    renderizar()

def renderizar():
    global imagen_actual

    img = imagen_original.copy()

    # Oscurecer imagen
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 120))
    img = img.convert("RGBA")
    img = Image.alpha_composite(img, overlay)

    # Restaurar zona del crop
    zona = imagen_original.crop((crop_x, crop_y, crop_x + crop_w, crop_y + crop_h))
    img.paste(zona, (crop_x, crop_y))

    # Dibujar borde
    draw = ImageDraw.Draw(img)
    draw.rectangle(
        (crop_x, crop_y, crop_x + crop_w, crop_y + crop_h),
        outline="red",
        width=3
    )

    imagen_actual = ImageTk.PhotoImage(img.resize((800, 500)))
    canvas.create_image(0, 0, anchor=tk.NW, image=imagen_actual)

# ------------------------
# DRAG CON MOUSE
# ------------------------
def iniciar_drag(event):
    global dragging
    dragging = True

def arrastrar(event):
    global crop_y
    if not dragging:
        return

    escala_y = imagen_original.size[1] / 500
    nuevo_y = int(event.y * escala_y - crop_h / 2)

    crop_y = max(0, min(nuevo_y, imagen_original.size[1] - crop_h))
    renderizar()

def finalizar_drag(event):
    global dragging
    dragging = False

# ------------------------
# GUARDAR CON S
# ------------------------
def guardar(event):
    global contador

    if imagen_original is None:
        return

    box = (crop_x, crop_y, crop_x + crop_w, crop_y + crop_h)
    recorte = imagen_original.crop(box)

    nombre = os.path.join(destino_path, f"{contador}.jpg")
    recorte.save(nombre, "JPEG", quality=95)

    contador += 1

    # avanzar automáticamente
    actual = list_img.curselection()
    if actual:
        siguiente = actual[0] + 1
        if siguiente < list_img.size():
            list_img.selection_clear(0, tk.END)
            list_img.selection_set(siguiente)
            list_img.event_generate("<<ListboxSelect>>")

# ------------------------
# INTERFAZ
# ------------------------
frame_top = tk.Frame(root)
frame_top.pack()

canvas = tk.Canvas(frame_top, width=800, height=500)
canvas.pack()

frame_bottom = tk.Frame(root)
frame_bottom.pack(fill=tk.BOTH, expand=True)

list_cm = tk.Listbox(frame_bottom, width=30)
list_cm.pack(side=tk.LEFT, fill=tk.BOTH)
list_cm.bind("<<ListboxSelect>>", cargar_imagenes)

list_img = tk.Listbox(frame_bottom)
list_img.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
list_img.bind("<<ListboxSelect>>", mostrar_imagen)

canvas.bind("<ButtonPress-1>", iniciar_drag)
canvas.bind("<B1-Motion>", arrastrar)
canvas.bind("<ButtonRelease-1>", finalizar_drag)

root.bind("s", guardar)

menu = tk.Menu(root)
menu.add_command(label="Seleccionar Carpeta Madre", command=seleccionar_carpeta)
root.config(menu=menu)

root.mainloop()
