import tkinter as tk

from state import AppState
from core.file_manager import FileManager
from core.image_manager import ImageManager
from core.crop_engine import CropEngine
from core.matcher import Matcher

from ui.layout import Layout
from ui.preview_panel import PreviewPanel
from ui.notifier import Notifier
from ui.controller import Controller

from config import THUMB_SIZE


def main():
    root = tk.Tk()

    state = AppState()
    file_manager = FileManager()
    image_manager = ImageManager()
    crop_engine = CropEngine()
    matcher = Matcher()

    layout = Layout(root)

    preview_panel = PreviewPanel(
        layout.frame_preview,
        layout.canvas_preview,
        state,
        THUMB_SIZE
    )

    notifier = Notifier(layout.canvas)

    Controller(
        state,
        layout,
        file_manager,
        image_manager,
        crop_engine,
        matcher,
        preview_panel,
        notifier
    )

    root.mainloop()


if __name__ == "__main__":
    main()