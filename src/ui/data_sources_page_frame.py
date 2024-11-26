from .page_frame import PageFrame
from .tag_widget import TagWidget
from .data_source_edit_panel import EditDataSourcePanel
from backend.models.models import *
from backend.repositories import file_repository, tag_repository

import customtkinter as ctk
from PIL import Image
import datetime, threading, asyncio, os


class DataSourceCard(ctk.CTkFrame):
    def __init__(
        self,
        master,
        data_source: DataSource,
        click_command,
    ):
        super().__init__(master, corner_radius=12, fg_color="#f9f9fa", height=900)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.data_source = data_source

        # Path
        self.path_header = ctk.CTkLabel(
            self, text="路径", font=ctk.CTkFont(size=16, weight="bold"), anchor="w"
        )
        self.path_header.grid(row=0, column=0, sticky="nsw", padx=(24, 0), pady=(16, 0))
        self.path_label = ctk.CTkLabel(
            self,
            text=f"{data_source.watch_directory.path}",
            font=ctk.CTkFont(size=14),
            anchor="w",
            justify="left",
        )
        self.path_label.grid(row=0, column=1, sticky="nsew", padx=(24, 0), pady=(16, 0))
        self.path_label.bind(
            "<Configure>",
            lambda e: self.path_label.configure(
                wraplength=self.path_label.winfo_width()
                * 0.65  # FIXME I have no idea why it should multiply this (approximate) number
            ),
        )

        # Tags
        self.tags_header = ctk.CTkLabel(
            self,
            text="关联标签",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w",
        )
        self.tags_header.grid(
            row=1, column=0, sticky="nsw", padx=(24, 0), pady=(12, 16)
        )
        self.tags_frame = ctk.CTkFrame(
            self, corner_radius=0, fg_color="transparent", height=0
        )
        self.tags_frame.grid(
            row=1, column=1, sticky="nsew", padx=(16, 0), pady=(12, 16)
        )
        for tag in data_source.associated_tags:
            tag_widget = TagWidget(self.tags_frame, tag)
            tag_widget.pack(side="left", padx=6, pady=0)

        # Click event
        def bind_click_event(widget):
            widget.bind("<Button-1>", lambda *args: click_command(self))
            for child in widget.winfo_children():
                bind_click_event(child)

        bind_click_event(self)


class DataSourcesPageFrame(PageFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        self.display_frame = ctk.CTkScrollableFrame(
            self, corner_radius=0, fg_color="transparent", orientation="vertical"
        )
        self.display_frame.grid(row=1, column=0, sticky="nsew", padx=24, pady=16)

        self.add_button = ctk.CTkButton(
            self,
            text="添加数据源",
            width=140,
            command=self.on_add_button_click,
        )
        self.add_button.grid(row=0, column=0, sticky="w", padx=(24, 0), pady=(16, 16))

        self.edit_data_source_panel = None

    def fetch_data_sources(self):
        self.clear_display_frame()
        watch_directories = file_repository.query_all_watch_directories()
        data_sources = [
            DataSource.from_watch_directory(
                watch_directory,
                tag_repository.get_tags_by_ids(watch_directory.associated_tag_ids),
            )
            for watch_directory in watch_directories
        ]
        self.display_data_sources(data_sources)

    def clear_display_frame(self):
        for widget in self.display_frame.winfo_children():
            widget.destroy()
        if self.edit_data_source_panel:
            self.edit_data_source_panel.destroy()

    def display_data_sources(self, data_sources: list[DataSource]):
        for data_source in data_sources:
            data_source_card = DataSourceCard(
                self.display_frame,
                data_source=data_source,
                click_command=self.on_data_source_click,
            )
            data_source_card.pack(fill="x", padx=0, pady=(0, 16), expand=True)

    def on_add_button_click(self):
        self.edit_data_source_panel = EditDataSourcePanel(
            self, close_command=self.on_edit_panel_close, mode="add"
        )
        self.edit_data_source_panel.grid(row=0, rowspan=2, column=1, sticky="nsew")

    def on_data_source_click(self, data_source_card: DataSourceCard):
        self.edit_data_source_panel = EditDataSourcePanel(
            self,
            close_command=self.on_edit_panel_close,
            mode="edit",
            data_source=data_source_card.data_source,
        )
        self.edit_data_source_panel.grid(row=0, rowspan=2, column=1, sticky="nsew")

    def on_edit_panel_close(self):
        self.fetch_data_sources()
        self.edit_data_source_panel.destroy()
