from .page_frame import PageFrame
from .document_card import DocumentCard
from .tag_widget import TagWidget
from backend.models.models import *
from backend.repositories import file_repository, tag_repository

import customtkinter as ctk, tkinter as tk
from PIL import Image
import datetime, threading, asyncio


class TagManagerPageFrame(PageFrame):
    def __init__(self, master):
        super().__init__(master)

        self.add_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.add_frame.pack(fill="x", expand=True, padx=24, pady=(16, 0))

        self.add_input = tk.StringVar()

        def add_tag():
            tag_repository.create_tag(self.add_input.get())
            self.fetch_tags()

        self.add_entry = ctk.CTkEntry(self.add_frame, textvariable=self.add_input)
        self.add_entry.pack(fill="x", expand=True, padx=24, pady=(16, 0))

        self.add_button = ctk.CTkButton(self.add_frame, text="添加", command=add_tag)
        self.add_button.pack(fill="x", expand=True, padx=24, pady=(16, 16))

        self.display_frame = ctk.CTkScrollableFrame(
            self, corner_radius=0, fg_color="transparent", orientation="vertical"
        )
        self.display_frame.pack(fill="both", expand=True, padx=24, pady=(16, 16))

    def fetch_tags(self):
        self.clear_display_frame()
        tags = tag_repository.query_all_tags()
        self.display_tags(tags)

    def clear_display_frame(self):
        for widget in self.display_frame.winfo_children():
            widget.destroy()

    def display_tags(self, tags: list[Tag]):
        self.clear_display_frame()
        for i, tag in enumerate(tags):

            def delete_tag():
                tag_repository.delete_tag(tag.id)
                self.fetch_tags()

            TagWidget(self.display_frame, tag_name=tag.name).pack(
                fill="x",
                padx=(16, 0),
                pady=(8, 0),
            )
            ctk.CTkButton(
                self.display_frame,
                fg_color="#ff4444",
                hover_color="#ff6666",
                text="删除",
                command=delete_tag,
            ).pack(fill="x", padx=(16, 0), pady=(8, 8))
