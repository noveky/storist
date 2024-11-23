from . import file_system_watcher
from backend.preprocessing import image_preprocessor

watcher = None


def preprocess_file(path: str):
    if path.endswith(".png") or path.endswith(".jpg") or path.endswith(".jpeg"):
        image_preprocessor.preprocess_image(path)
    elif path.endswith(".txt") or path.endswith(".md"):
        pass  # TODO Text preprocessing
    else:
        pass  # Not supported, ignore


def create_event_handler(path):
    preprocess_file(path)


def delete_event_handler(path):
    pass


def modify_event_handler(path):
    preprocess_file(path)


def move_event_handler(src_path, dest_path):
    pass


def start_watcher(paths_to_watch):
    global watcher

    watcher = file_system_watcher.FileSystemWatcher(
        paths_to_watch,
        create_event_handler=create_event_handler,
        delete_event_handler=delete_event_handler,
        modify_event_handler=modify_event_handler,
        move_event_handler=move_event_handler,
    )
    watcher.start()


def change_paths_to_watch(paths_to_watch):
    for path in watcher.paths:
        if path not in set(paths_to_watch):
            watcher.remove_path(path)

    for path in paths_to_watch:
        if path not in watcher.paths:
            watcher.add_path(path)
