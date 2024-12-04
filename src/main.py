from utils import utils
from config import config
from ui.app import App
from backend.fs import file_manager

import os


if __name__ == "__main__":
    try:
        os.makedirs(config.DATA_DIR, exist_ok=True)
        file_manager.start_watcher()
        file_manager.gather_unpreprocessed_files()

        app = App()
        app.mainloop()
    finally:
        file_manager.stop_watcher()
