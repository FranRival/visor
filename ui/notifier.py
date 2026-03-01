class Notifier:

    def __init__(self, canvas):
        self.canvas = canvas
        self.notificacion_id = None
        self.rect_id = None

    def mostrar(self, texto, color="green"):
        if self.notificacion_id:
            self.canvas.delete(self.notificacion_id)
            self.canvas.delete(self.rect_id)

        self.notificacion_id = self.canvas.create_text(
            400,
            40,
            text=texto,
            fill=color,
            font=("Arial", 24, "bold")
        )

        bbox = self.canvas.bbox(self.notificacion_id)

        self.rect_id = self.canvas.create_rectangle(
            bbox[0] - 20,
            bbox[1] - 10,
            bbox[2] + 20,
            bbox[3] + 10,
            fill="black",
            outline=""
        )

        self.canvas.tag_lower(self.rect_id, self.notificacion_id)

        self.canvas.after(1500, self.limpiar)

    def limpiar(self):
        if self.notificacion_id:
            self.canvas.delete(self.notificacion_id)
            self.canvas.delete(self.rect_id)