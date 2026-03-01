class EventController:
    def __init__(self, state, layout, file_manager, image_manager, crop_engine):
        self.state = state
        self.layout = layout
        self.file_manager = file_manager
        self.image_manager = image_manager
        self.crop_engine = crop_engine

        self.bind_events()

    def bind_events(self):
        self.layout.root.bind("s", self.guardar)