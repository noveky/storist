from utils import utils
from config import config
from ui.app import App
from backend.fs import file_manager

import os
from sklearn.metrics.pairwise import cosine_similarity


if __name__ == "__main__":
    os.makedirs(config.DATA_DIR, exist_ok=True)
    file_manager.start_watcher()

    app = App()
    app.mainloop()
