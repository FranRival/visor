import os
import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog, messagebox
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
notificacion_id = None

nombre_carpeta_var = tk.StringVar(value="")
total_recortes_var = tk.StringVar(value="Recortes: 0")
match_var = tk.StringVar(value="Esperando...")

# ==============================
# SELECCIONAR CARPETA MADRE
# ==============================

def seleccionar_carpeta():
    global carpeta_madre, subcarpetas, contador_guardado, carpeta_destino_actual

    carpeta_madre = filedialog.askdirectory()
    if not carpeta_madre:
        return

    contador_guardado = 1
    total_recortes_var.set("Recortes: 0")
    carpeta_destino_actual = os.path.join(carpeta_madre, "AAA")
    nombre_carpeta_var.set(os.path.basename(carpeta_madre))


    status_var.set("")

    list_sub.delete(0, tk.END)
    subcarpetas.clear()

    for item in os.listdir(carpeta_madre):
        ruta = os.path.join(carpeta_madre, item)
        if os.path.isdir(ruta):
            subcarpetas.append(ruta)

            numero = len(subcarpetas)
            list_sub.insert(tk.END, f"{numero}. {item}")

            contador_carpetas_var.set(f"Carpetas: {len(subcarpetas)}")


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
# COPIAR RUTA AAA
# ==============================

def copiar_ruta_aaa(event=None):
    global carpeta_destino_actual

    if not carpeta_destino_actual:
        mostrar_notificacion("No hay carpeta seleccionada", "red")
        return

    os.makedirs(carpeta_destino_actual, exist_ok=True)

    root.clipboard_clear()
    root.clipboard_append(carpeta_destino_actual)
    root.update()

    mostrar_notificacion("Ruta copiada", "cyan")


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
# RENOMBRAR CARPETA (CLICK DERECHO)
# ==============================

def menu_click_derecho(event):
    try:
        index = list_sub.nearest(event.y)
        list_sub.selection_clear(0, tk.END)
        list_sub.selection_set(index)
        list_sub.activate(index)
        menu_carpetas.post(event.x_root, event.y_root)
    except:
        pass


def cambiar_nombre_carpeta():
    if not list_sub.curselection():
        return

    index = list_sub.curselection()[0]
    ruta_actual = subcarpetas[index]
    nombre_actual = os.path.basename(ruta_actual)

    nuevo_nombre = simpledialog.askstring(
        "Cambiar nombre",
        "Nuevo nombre de carpeta:",
        initialvalue=nombre_actual
    )

    if nuevo_nombre is None:
        return  # Cancelado

    nuevo_nombre = nuevo_nombre.strip()

    # Validaciones
    if not nuevo_nombre:
        messagebox.showerror("Error", "El nombre no puede estar vacío.")
        return

    caracteres_invalidos = r'\/:*?"<>|'
    if any(c in nuevo_nombre for c in caracteres_invalidos):
        messagebox.showerror("Error", "El nombre contiene caracteres inválidos.")
        return

    nueva_ruta = os.path.join(carpeta_madre, nuevo_nombre)

    if os.path.exists(nueva_ruta):
        messagebox.showerror("Error", "Ya existe una carpeta con ese nombre.")
        return

    try:
        os.rename(ruta_actual, nueva_ruta)

        # Actualizar lista interna
        subcarpetas[index] = nueva_ruta

        # Actualizar Listbox
        list_sub.delete(index)
        list_sub.insert(index, f"{index+1}. {nuevo_nombre}")

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo renombrar.\n{e}")

# ==============================
# ABRIR CARPETA
# ==============================

def abrir_carpeta_seleccionada():
    if not list_sub.curselection():
        return

    index = list_sub.curselection()[0]
    ruta = subcarpetas[index]

    if os.path.exists(ruta):
        os.startfile(ruta)

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
# NOTIFICACIÓN EN VISOR
# ==============================

def mostrar_notificacion(texto, color="green"):
    global notificacion_id

    # Borrar anterior si existe
    if notificacion_id:
        canvas.delete(notificacion_id)

    # Crear texto centrado
    notificacion_id = canvas.create_text(
        400,
        40,
        text=texto,
        fill=color,
        font=("Arial", 24, "bold")
    )

    # Fondo semitransparente simulado
    bbox = canvas.bbox(notificacion_id)
    rect = canvas.create_rectangle(
        bbox[0] - 20,
        bbox[1] - 10,
        bbox[2] + 20,
        bbox[3] + 10,
        fill="black",
        outline=""
    )

    canvas.tag_lower(rect, notificacion_id)

    # Auto eliminar después de 1.5 segundos
    def borrar():
        canvas.delete(notificacion_id)
        canvas.delete(rect)

    root.after(1500, borrar)


# ==============================
# GUARDAR RECORTE
# ==============================


def guardar_recorte(event=None):
    global contador_guardado

    if imagen_original is None:
        mostrar_notificacion("No hay imagen cargada", "red")
        return

    if not carpeta_destino_actual:
        mostrar_notificacion("No hay carpeta seleccionada", "red")
        return

    os.makedirs(carpeta_destino_actual, exist_ok=True)

    ruta_guardado = os.path.join(carpeta_destino_actual, f"{contador_guardado}.jpg")

    recorte = imagen_original.crop(
        (crop_x, crop_y, crop_x + crop_w, crop_y + crop_h)
    )

    recorte.save(ruta_guardado, quality=95)

    status_var.set(f"{contador_guardado}.jpg - guardada")

    mostrar_notificacion(f"{contador_guardado}.jpg guardada", "lime")

    validar_match(contador_guardado)

    contador_guardado += 1

    total_actual = int(total_recortes_var.get().split(": ")[1])
    total_actual += 1
    total_recortes_var.set(f"Recortes: {total_actual}")


    

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
# VALIDAR MATCH
# ==============================

def validar_match(numero_guardado):
    if not list_sub.curselection():
        match_var.set("NO MATCH")
        match_label.config(fg="red")
        return

    indice = list_sub.curselection()[0]
    numero_carpeta = indice + 1

    if numero_guardado == numero_carpeta:
        match_var.set("MATCH")
        match_label.config(fg="lime")
    else:
        match_var.set("NO MATCH")
        match_label.config(fg="red")
# ==============================
# INTERFAZ
# ==============================

frame_izq = tk.Frame(root, width=350)
frame_izq.pack(side=tk.LEFT, fill=tk.Y)
frame_izq.pack_propagate(False)


# Contenedor botón + contador
top_container = tk.Frame(frame_izq)
top_container.pack(pady=5, fill=tk.X)

btn = tk.Button(top_container, text="Seleccionar Carpeta", command=seleccionar_carpeta)
btn.pack(side=tk.LEFT)

contador_carpetas_var = tk.StringVar(value="Carpetas: 0")
label_contador = tk.Label(top_container, textvariable=contador_carpetas_var)
label_contador.pack(side=tk.LEFT, padx=10)

label_nombre_carpeta = tk.Label(
    top_container,
    textvariable=nombre_carpeta_var,
    fg="black",
    font=("Arial", 10, "bold")
)
label_nombre_carpeta.pack(side=tk.LEFT, padx=10)





# Contenedor para lista + scrollbar
list_container = tk.Frame(frame_izq)
list_container.pack(padx=5, pady=5, fill=tk.X)

list_sub = tk.Listbox(list_container, width=30, height=8)
scroll_sub = tk.Scrollbar(list_container, orient="vertical", command=list_sub.yview)

list_sub.configure(yscrollcommand=scroll_sub.set)

list_sub.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scroll_sub.pack(side=tk.RIGHT, fill=tk.Y)

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


# ==============================
# SCROLL SUAVE PARA LISTBOX
# ==============================

def _on_mousewheel_listbox(event):
    # desplazamiento más suave (mitad de velocidad normal)
    list_sub.yview_scroll(int(-1 * (event.delta / 240)), "units")

def bind_scroll_listbox(event):
    list_sub.bind_all("<MouseWheel>", _on_mousewheel_listbox)

def unbind_scroll_listbox(event):
    list_sub.unbind_all("<MouseWheel>")

canvas_preview.bind("<Enter>", bind_scroll)
canvas_preview.bind("<Leave>", unbind_scroll)

canvas = tk.Canvas(root, width=800, height=500, bg="gray")
canvas.pack(side=tk.RIGHT, expand=True)

# ==============================
# MINI PANEL MATCH (lado derecho del visor)
# ==============================

match_frame = tk.Frame(root, bg="black", width=180, height=80)
match_frame.place(x=1030, y=120)  # ajusta si quieres moverlo

match_label = tk.Label(
    match_frame,
    textvariable=match_var,
    font=("Arial", 18, "bold"),
    bg="black",
    fg="yellow"
)

match_label.place(relx=0.5, rely=0.5, anchor="center")


# ==============================
# MENU CONTEXTUAL LISTBOX
# ==============================

menu_carpetas = tk.Menu(root, tearoff=0)

menu_carpetas.add_command(
    label="Abrir carpeta",
    command=abrir_carpeta_seleccionada
)

menu_carpetas.add_separator()

menu_carpetas.add_command(
    label="Cambiar nombre",
    command=cambiar_nombre_carpeta
)

list_sub.bind("<Button-3>", menu_click_derecho)


# ==============================
# CONTADOR CENTRADO SOBRE VISOR
# ==============================

label_total_canvas = tk.Label(
    canvas,
    textvariable=total_recortes_var,
    font=("Arial", 14),
    bg="lightgray",
    fg="black"
)

label_total_canvas.place(relx=0.66, y=5, anchor="n")


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

bottom_row = tk.Frame(right_panel)
bottom_row.pack(anchor="e")

# Texto estilo link
link_copiar = tk.Label(
    bottom_row,
    text="Copiar ruta",
    fg="black",
    cursor="hand2"
)
link_copiar.pack(side=tk.LEFT, padx=(0, 15))
link_copiar.bind("<Button-1>", copiar_ruta_aaa)

btn_abrir = tk.Button(
    bottom_row,
    text="Abrir carpeta AAA",
    command=abrir_carpeta_aaa
)
btn_abrir.pack(side=tk.LEFT)


root.bind("s", guardar_recorte)
root.bind("S", guardar_recorte)

root.mainloop()
