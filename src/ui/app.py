from .search_page_frame import SearchPageFrame
from .all_docs_page_frame import AllDocsPageFrame
from .data_sources_page_frame import DataSourcesPageFrame

import customtkinter as ctk

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")


class TabButton(ctk.CTkButton):
    def __init__(self, master, text):
        super().__init__(
            master,
            text=f"  {text}",
            width=180,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        )
        self.pack(anchor="center", ipadx=10, ipady=8, padx=16, pady=(16, 0))

        self.is_selected = False

    def on_select(self):
        self.is_selected = True

    def on_deselect(self):
        self.is_selected = False


class DrawerFrame(ctk.CTkFrame):
    def __init__(self, master, width):
        super().__init__(master, width=width, corner_radius=0, fg_color="#2e81c3")
        self.pack(side="left", fill="y")

        self.tab_buttons: list[TabButton] = []

    def add_tab(self, text, select_command):
        def command_wrapper(command, tab_button):
            def wrapper():
                nonlocal command, tab_button
                for tb in self.tab_buttons:
                    if tb is tab_button:
                        tb.on_select()
                    else:
                        tb.on_deselect()
                command()

            return wrapper

        tab_button = TabButton(self, text)
        tab_button.configure(command=command_wrapper(select_command, tab_button))
        self.tab_buttons.append(tab_button)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("收藏家")
        self.geometry("1600x900")
        self.resizable(True, True)

        self.docs = []

        self.create_widgets()

    def create_widgets(self):
        # Window frame

        window_frame = ctk.CTkFrame(self)
        window_frame.pack(fill="both", expand=True)

        # Left drawer

        left_drawer = DrawerFrame(window_frame, width=180)
        left_drawer.add_tab("智能检索", self.show_search_page)
        left_drawer.add_tab("所有文档", self.show_all_docs_page)
        left_drawer.add_tab("数据源管理", self.show_data_sources_page)
        left_drawer.add_tab("标签管理", self.show_tag_manager_page)

        # Main area

        self.main_area = ctk.CTkFrame(window_frame, corner_radius=0)
        self.main_area.pack(side="left", fill="both", expand=True)

        # Page frames

        self.search_page_frame = SearchPageFrame(self.main_area)
        self.all_docs_page_frame = AllDocsPageFrame(self.main_area)
        self.data_sources_page_frame = DataSourcesPageFrame(self.main_area)

        # # Right panel

        # right_panel = ctk.CTkFrame(window_frame, width=300, corner_radius=0)
        # right_panel.pack(side="right", fill="y")

    def clear_main_area(self):
        for w in self.main_area.winfo_children():
            w.pack_forget()

    def show_search_page(self):
        self.clear_main_area()
        self.search_page_frame.pack()

    def show_all_docs_page(self):
        self.clear_main_area()
        self.all_docs_page_frame.pack()
        self.all_docs_page_frame.fetch_documents()

    def show_data_sources_page(self):
        self.clear_main_area()
        self.data_sources_page_frame.pack()
        self.data_sources_page_frame.fetch_data_sources()

    def show_tag_manager_page(self):
        self.clear_main_area()


if __name__ == "__main__":
    app = App()
    app.mainloop()
