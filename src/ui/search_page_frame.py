from .page_frame import PageFrame
from .document_card import DocumentCard
from backend.models.models import *
from backend.query import query_handler

import customtkinter as ctk
from PIL import Image
import datetime, threading, asyncio


class SearchPageFrame(PageFrame):
    content_types: list[tuple[str, ContentType]] = [
        ("不限", None),
        ("文本", "text"),
        ("图片", "image"),
    ]

    def __init__(self, master):
        super().__init__(master)

        self.content_type_var = ctk.StringVar(value=SearchPageFrame.content_types[0][0])
        self.content_type_index_var = ctk.IntVar(value=0)
        self.title_var = ctk.StringVar()
        self.description_var = ctk.StringVar()
        self.date_from_var = ctk.StringVar()
        self.date_to_var = ctk.StringVar()

        self.search_bar = ctk.CTkTabview(self, corner_radius=12, fg_color="#f9f9fa")
        self.search_bar.pack(fill="x", padx=24, pady=16)
        self.search_bar.add("条件检索")
        self.search_bar.add("自然语言检索")

        self.result_frame = ctk.CTkScrollableFrame(
            self, corner_radius=0, fg_color="transparent", orientation="vertical"
        )
        self.result_frame.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        self.nl_search_label = ctk.CTkLabel(
            self.search_bar.tab("自然语言检索"),
            text="请用自然语言描述目标文档的特征：",
            anchor="w",
        )
        self.nl_search_label.pack(fill="x", padx=16, pady=(20, 8))
        self.nl_search_textbox = ctk.CTkTextbox(
            self.search_bar.tab("自然语言检索"), height=100, fg_color="#eaeaeb"
        )
        self.nl_search_textbox.pack(fill="both", padx=16, pady=(0, 28))

        self.nl_search_button = ctk.CTkButton(
            self.search_bar.tab("自然语言检索"),
            text="检索",
            command=self.perform_nl_search,
            height=32,
        )
        self.nl_search_button.pack(fill="x", padx=16, pady=(0, 24))

        self.search_bar_inner = ctk.CTkFrame(
            self.search_bar.tab("条件检索"), fg_color="transparent"
        )
        self.search_bar_inner.pack(fill="both", padx=12, pady=20)
        self.search_bar_inner.grid_columnconfigure(0, weight=0)
        self.search_bar_inner.grid_columnconfigure(1, weight=1)

        self.search_in_label = ctk.CTkLabel(self.search_bar_inner, text="按类型")
        self.search_in_label.grid(row=0, column=0, sticky="w", padx=(16, 12), pady=8)

        self.search_in_combobox = ctk.CTkComboBox(
            self.search_bar_inner,
            values=["不限", "文本", "图片"],
            width=160,
            variable=self.content_type_var,
            command=self.update_search_in_index,
        )
        self.search_in_combobox.grid(row=0, column=1, sticky="w", padx=(8, 16), pady=8)

        self.title_label = ctk.CTkLabel(self.search_bar_inner, text="按标题")
        self.title_label.grid(row=1, column=0, sticky="w", padx=(16, 12), pady=8)

        self.title_entry = ctk.CTkEntry(
            self.search_bar_inner, textvariable=self.title_var
        )
        self.title_entry.grid(row=1, column=1, sticky="ew", padx=(8, 16), pady=8)

        self.description_label = ctk.CTkLabel(self.search_bar_inner, text="按描述")
        self.description_label.grid(row=2, column=0, sticky="w", padx=(16, 12), pady=8)

        self.description_entry = ctk.CTkEntry(
            self.search_bar_inner, textvariable=self.description_var
        )
        self.description_entry.grid(row=2, column=1, sticky="ew", padx=(8, 16), pady=8)

        self.date_label = ctk.CTkLabel(self.search_bar_inner, text="按日期")
        self.date_label.grid(row=3, column=0, sticky="w", padx=(16, 12), pady=8)

        self.date_frame = ctk.CTkFrame(self.search_bar_inner, fg_color="transparent")
        self.date_frame.grid(row=3, column=1, sticky="w", padx=(8, 0), pady=8)

        self.date_from_entry = ctk.CTkEntry(
            self.date_frame, width=140, textvariable=self.date_from_var
        )
        self.date_from_entry.pack(side="left")

        self.date_to_label = ctk.CTkLabel(self.date_frame, text="至")
        self.date_to_label.pack(side="left", padx=(12, 12))

        self.date_to_entry = ctk.CTkEntry(
            self.date_frame, width=140, textvariable=self.date_to_var
        )
        self.date_to_entry.pack(side="left")

        self.button_frame = ctk.CTkFrame(self.search_bar_inner, fg_color="transparent")
        self.button_frame.grid(
            row=8,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=(16, 16),
            pady=(20, 8),
        )
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)

        self.search_button = ctk.CTkButton(
            self.button_frame,
            text="检索",
            command=self.perform_conditional_search,
            height=32,
        )
        self.search_button.grid(row=0, column=0, sticky="e", padx=(0, 8))

        self.clear_button = ctk.CTkButton(
            self.button_frame, text="清空条件", command=self.clear_filters, height=32
        )
        self.clear_button.grid(row=0, column=1, sticky="w", padx=(8, 0))

    def update_search_in_index(self, *args):
        current_value = self.content_type_var.get()
        values = self.search_in_combobox.cget("values")
        self.content_type_index_var.set(values.index(current_value))

    def perform_nl_search(self):
        specification = self.nl_search_textbox.get("1.0", "end-1c")

        async def run_query():
            # Clear previous search results
            for widget in self.result_frame.winfo_children():
                widget.destroy()

            # Retrieve search results
            result_docs = await query_handler.handle_nl_query(specification)

            # Display search results
            self.display_search_results(result_docs)

        thread = threading.Thread(target=lambda: asyncio.run(run_query()))
        thread.start()

    def perform_conditional_search(self):
        # Fetching filter criteria from the input fields
        content_type_filter = SearchPageFrame.content_types[
            self.content_type_index_var.get()
        ][1]
        title_filter = self.title_var.get().lower()
        description_filter = self.description_var.get().lower()
        date_from_filter_str = self.date_from_var.get()
        date_to_filter_str = self.date_to_var.get()

        # Convert date strings to date objects for comparison
        date_from_filter = (
            datetime.datetime.strptime(date_from_filter_str, r"%Y-%m-%d")
            if date_from_filter_str
            else None
        )
        date_to_filter = (
            datetime.datetime.strptime(date_to_filter_str, r"%Y-%m-%d")
            if date_to_filter_str
            else None
        )

        async def run_query():
            self.clear_result_frame()

            # Retrieve search results
            result_docs = await query_handler.handle_conditional_query(
                query_content_type=content_type_filter,
                query_title=title_filter,
                query_description=description_filter,
                query_date_from=date_from_filter,
                query_date_to=date_to_filter,
            )

            # Display search results
            self.display_search_results(result_docs)

        thread = threading.Thread(target=lambda: asyncio.run(run_query()))
        thread.start()

    def clear_filters(self):
        self.content_type_var.set(SearchPageFrame.content_types[0][0])
        self.content_type_index_var.set(0)
        self.title_var.set("")
        self.description_var.set("")
        self.date_from_var.set("")
        self.date_to_var.set("")

    def clear_result_frame(self):
        for widget in self.result_frame.winfo_children():
            widget.destroy()

    def display_search_results(self, result_docs: list[Document]):
        self.clear_result_frame()
        for i, doc in enumerate(result_docs):
            DocumentCard(self.result_frame, document=doc, click_handler=None).pack(
                fill="x",
                expand=True,
                padx=16,
                pady=(16, 16 if i == len(result_docs) - 1 else 0),
            )
