import tkinter as tk
from state import AppState
from core.file_manager import FileManager
from core.image_manager import ImageManager
from core.crop_engine import CropEngine
from ui.layout import Layout
from ui.events import EventController

def main():
    root = tk.Tk()

    state = AppState()
    file_manager = FileManager()
    image_manager = ImageManager()
    crop_engine = CropEngine()

    layout = Layout(root)

    EventController(
        state,
        layout,
        file_manager,
        image_manager,
        crop_engine
    )

    root.mainloop()

if __name__ == "__main__":
    main()