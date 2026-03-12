class AppState:
    def __init__(self):
        self.imagen_original = None
        self.imagen_actual = None

        self.imagenes = []
        self.subcarpetas = []
        self.miniaturas = []

        self.carpeta_madre = ""
        self.carpeta_destino_actual = ""

        self.contador_guardado = 1

        self.crop_x = 0
        self.crop_y = 0
        self.crop_w = 0
        self.crop_h = 0

        self.dragging = False
        self.notificacion_id = None

        self.modo_edicion = False
        self.checks_carpetas = set()

        self.zoom = 1.0