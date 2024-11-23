import customtkinter as ctk
import tkinter as tk

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")


class TabButton(ctk.CTkButton):
    def __init__(self, master, text):
        super().__init__(
            master, text=text, width=300
        )  # FIXME width=300 is supposed to be redundant
        self.grid(padx=5, pady=5, sticky="ew")

        self.is_selected = False

    def select(self):
        self.is_selected = True

    def deselect(self):
        self.is_selected = False


class DrawerFrame(ctk.CTkFrame):
    def __init__(self, master, width):
        super().__init__(master, width=width, corner_radius=0)
        self.pack(side="left", fill="y")
        self.grid_columnconfigure(0, weight=1)

        self.tab_buttons: list[TabButton] = []

    def add_tab(self, text, select_command):
        def command_wrapper(command, tab_button):
            def wrapper():
                nonlocal command, tab_button
                for tb in self.tab_buttons:
                    if tb is tab_button:
                        tb.select()
                    else:
                        tb.deselect()
                command()

            return wrapper

        tab_button = TabButton(self, text)
        tab_button.configure(command=command_wrapper(select_command, tab_button))
        self.tab_buttons.append(tab_button)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("收藏家")
        self.geometry("1280x720")
        self.resizable(True, True)

        self.items = []

        self.create_widgets()

    def create_widgets(self):
        # Main frame

        main_frame = tk.PanedWindow(self, orient="horizontal")
        main_frame.pack(fill="both", expand=True)

        # Left drawer

        left_drawer = DrawerFrame(main_frame, width=300)
        left_drawer.add_tab("添加", self.show_add_item)
        left_drawer.add_tab("搜索", self.show_search)
        left_drawer.add_tab("所有物品", self.show_all_items)

        # Main area

        self.main_area = ctk.CTkFrame(main_frame, corner_radius=0, fg_color="white")
        self.main_area.pack(side="left", fill="both", expand=True)

        # Right panel

        right_panel = ctk.CTkFrame(main_frame, width=300, corner_radius=0)
        right_panel.pack(side="right", fill="y")

    def show_add_item(self):
        pass

    def show_search(self):
        pass

    def show_all_items(self):
        pass


if __name__ == "__main__":
    app = App()
    app.mainloop()
