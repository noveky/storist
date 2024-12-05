from . import file_system_watcher

from backend.models.models import *
from backend.preprocessing import preprocessing_handler
from backend.repositories import file_repository, watch_directory_repository

import asyncio, threading, os


watcher = None


def gather_unpreprocessed_files():
    print("Gathering unpreprocessed files...")
    for file in file_repository.query_all_files():
        if not file.metadata.get("preprocessing_done", False):
            preprocess_file(file.path)


def preprocess_file(path):
    async def run_preprocessing():
        result = await preprocessing_handler.preprocess_file(path)
        file_repository.save_file_metadata(path, result)

    thread = threading.Thread(target=lambda: asyncio.run(run_preprocessing()))
    thread.start()


def create_event_handler(path):
    print(f"File created: {path}")
    file_repository.get_or_create_file(file_path=path)
    preprocess_file(path)


def delete_event_handler(path):
    print(f"File deleted: {path}")
    file_repository.delete_file(file_path=path)


def modify_event_handler(path):
    print(f"File modified: {path}")
    file_repository.get_or_create_file(file_path=path)
    preprocess_file(path)


def move_event_handler(src_path, dest_path):
    print(f"File moved: {src_path} -> {dest_path}")
    file_repository.move_file(src_path=src_path, dest_path=dest_path)


def start_watcher():
    global watcher

    watch_directories = watch_directory_repository.query_all_watch_directories()
    watcher = file_system_watcher.FileSystemWatcher(
        paths=[watch_directory.path for watch_directory in watch_directories],
        create_event_handler=create_event_handler,
        delete_event_handler=delete_event_handler,
        modify_event_handler=modify_event_handler,
        move_event_handler=move_event_handler,
    )
    watcher.start()


def stop_watcher():
    watcher.stop()


def on_watch_directories_change():
    watch_directories = watch_directory_repository.query_all_watch_directories()

    for path in list(watcher.paths):
        if path not in watch_directories:
            watcher.remove_path(path)

    for path in list(watch_directories):
        if path not in watcher.paths:
            watcher.add_path(path)


watch_directory_repository.watch_directories_change_handlers.append(
    on_watch_directories_change
)
