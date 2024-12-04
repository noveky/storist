from .page_frame import PageFrame
from .document_card import DocumentCard
from backend.models.models import *
from backend.repositories import file_repository, tag_repository

import customtkinter as ctk
from PIL import Image
import datetime, threading, asyncio


class AllDocsPageFrame(PageFrame):
    def __init__(self, master):
        super().__init__(master)

        self.display_frame = ctk.CTkScrollableFrame(
            self, corner_radius=0, fg_color="transparent", orientation="vertical"
        )
        self.display_frame.pack(fill="both", expand=True, padx=24, pady=(16, 16))

    def fetch_documents(self):
        self.clear_display_frame()
        files = file_repository.query_all_files()
        tags = {
            file.id: [tag_repository.get_tag_by_id(tag_id) for tag_id in file.tag_ids]
            for file in files
        }
        docs = [Document.from_file(file, tags[file.id]) for file in files]
        docs = [doc for doc in docs if doc is not None]
        docs.sort(key=lambda x: x.created_at, reverse=True)
        self.display_documents(docs)

    def clear_display_frame(self):
        for widget in self.display_frame.winfo_children():
            widget.destroy()

    def display_documents(self, docs: list[Document]):
        self.clear_display_frame()
        for i, doc in enumerate(docs):
            if doc is None:
                continue
            DocumentCard(self.display_frame, document=doc, click_handler=None).pack(
                fill="x",
                expand=True,
                padx=16,
                pady=(16, 16 if i == len(docs) - 1 else 0),
            )
