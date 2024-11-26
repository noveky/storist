from utils import utils
from config import config

import os, time, threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

RECURSIVE_MONITORING = True


class ChangeHandler(FileSystemEventHandler):
    def __init__(
        self,
        current_state: dict,
        base_path: str,
        on_created,
        on_deleted,
        on_modified,
        on_moved,
    ):
        self.current_state = current_state
        self.base_path = base_path
        self.create_event_handler = on_created
        self.delete_event_handler = on_deleted
        self.modify_event_handler = on_modified
        self.move_event_handler = on_moved

    def on_created(self, event):
        if not event.is_directory:
            self.current_state[event.src_path] = os.path.getmtime(event.src_path)
            if self.create_event_handler:
                self.create_event_handler(event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            self.current_state.pop(event.src_path, None)
            if self.delete_event_handler:
                self.delete_event_handler(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self.current_state[event.src_path] = os.path.getmtime(event.src_path)
            if self.modify_event_handler:
                self.modify_event_handler(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self.current_state.pop(event.src_path, None)
            self.current_state[event.dest_path] = os.path.getmtime(event.dest_path)
            if self.move_event_handler:
                self.move_event_handler(event.src_path, event.dest_path)


def load_previous_states(paths) -> dict:
    states = {}
    if os.path.exists(config.FILE_STATES_FILE):
        with open(config.FILE_STATES_FILE, "r") as f:
            json_str = f.read()
        states = utils.load_json(json_str)
    for path in paths:
        if path not in states:
            states[path] = get_current_state(path)
    return states


def save_current_states(states):
    with open(config.FILE_STATES_FILE, "w") as f:
        f.write(utils.dump_json(states))


def get_current_state(path):
    state = {}
    for root, _, files in os.walk(path):
        for file in files:
            filepath = os.path.join(root, file)
            state[filepath] = os.path.getmtime(filepath)
    return state


class FileSystemWatcher:
    def __init__(
        self,
        paths,
        create_event_handler=None,
        delete_event_handler=None,
        modify_event_handler=None,
        move_event_handler=None,
    ):
        self.paths = {os.path.abspath(path) for path in paths}
        self.observers = {}
        self.lock = threading.Lock()
        self.current_states = load_previous_states(self.paths)

        # Callbacks
        self.create_event_handler = create_event_handler
        self.delete_event_handler = delete_event_handler
        self.modify_event_handler = modify_event_handler
        self.move_event_handler = move_event_handler

    def start(self):
        self.running = True
        self.monitor_thread = threading.Thread(target=self.monitor_directories)
        self.monitor_thread.start()

    def stop(self):
        self.running = False
        self.monitor_thread.join()
        save_current_states(self.current_states)

    def monitor_directories(self):
        for path in self.paths:
            self.start_observer(path)

        try:
            while self.running:
                time.sleep(1)
        finally:
            self.stop()

    def compare_states(self, previous_state: dict, current_state: dict, base_path: str):
        previous_files = set(previous_state.keys())
        current_files = set(current_state.keys())

        created_files = current_files - previous_files
        deleted_files = previous_files - current_files
        modified_files = {
            f
            for f in current_files & previous_files
            if previous_state[f] != current_state[f]
        }

        print(f"\nChanges in directory: {base_path}")
        for f in created_files:
            if self.create_event_handler:
                self.create_event_handler(f)
        for f in deleted_files:
            if self.delete_event_handler:
                self.delete_event_handler(f)
        for f in modified_files:
            if self.modify_event_handler:
                self.modify_event_handler(f)

    def start_observer(self, path):
        if path in self.observers:
            return

        if not os.path.isdir(path):
            return

        self.compare_states(self.current_states[path], get_current_state(path), path)
        event_handler = ChangeHandler(
            self.current_states[path],
            path,
            self.create_event_handler,
            self.delete_event_handler,
            self.modify_event_handler,
            self.move_event_handler,
        )
        observer = Observer()
        observer.schedule(event_handler, path, recursive=True)
        observer.start()
        self.observers[path] = observer

    def stop_observer(self, path):
        observer = self.observers.pop(path, None)
        if observer:
            observer.stop()
            observer.join()

    def add_path(self, path):
        with self.lock:
            if path not in self.paths:
                self.paths.add(path)
                self.current_states[path] = get_current_state(path)
                self.start_observer(path)

    def remove_path(self, path):
        with self.lock:
            if path in self.paths:
                self.paths.remove(path)
                self.stop_observer(path)
                self.current_states.pop(path, None)


if __name__ == "__main__":  # TODO Remove this

    def on_created(path):
        print(f"Custom handler: File created - {path}")

    def on_deleted(path):
        print(f"Custom handler: File deleted - {path}")

    def on_modified(path):
        print(f"Custom handler: File modified - {path}")

    def on_moved(src_path, dest_path):
        print(f"Custom handler: File moved from {src_path} to {dest_path}")

    watch_directories = [".."]

    monitor = FileSystemWatcher(
        watch_directories,
        create_event_handler=on_created,
        delete_event_handler=on_deleted,
        modify_event_handler=on_modified,
        move_event_handler=on_moved,
    )
    monitor.start()

    try:
        while True:
            time.sleep(1)
    finally:
        monitor.stop()
