from .tag_widget import TagWidget
from backend.models.models import *

import customtkinter as ctk
from PIL import Image
import datetime

TEXTS_LINE_MAX_DISPLAY_LENGTH = 100
TEXTS_MAX_DISPLAY_LINES = 5


class DocumentCard(ctk.CTkFrame):
    def __init__(
        self,
        master,
        document: Document,
        click_handler,
    ):
        super().__init__(master, corner_radius=12, fg_color="#f9f9fa")
        self.grid_columnconfigure(0, weight=1)

        self.document = document

        # Thumbnail
        image = (
            Image.open(document.file_path) if document.content_type == "image" else None
        )
        if image is not None:
            thumbnail_size = image.size
            if thumbnail_size[0] > (MAX_THUMBNAIL_WIDTH := 120):
                thumbnail_size = (
                    MAX_THUMBNAIL_WIDTH,
                    int(thumbnail_size[1] * MAX_THUMBNAIL_WIDTH / thumbnail_size[0]),
                )
            if thumbnail_size[1] > (MAX_THUMBNAIL_HEIGHT := 90):
                thumbnail_size = (
                    int(thumbnail_size[0] * MAX_THUMBNAIL_HEIGHT / thumbnail_size[1]),
                    MAX_THUMBNAIL_HEIGHT,
                )
            self.thumbnail = ctk.CTkImage(image, size=thumbnail_size)
            self.image_label = ctk.CTkLabel(
                self, image=self.thumbnail, corner_radius=12, text=""
            )
            self.image_label.grid(
                row=0, column=1, rowspan=2, sticky="ne", padx=(0, 12), pady=(24, 0)
            )

        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text=document.title,
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="nw",
            justify="left",
        )
        self.title_label.grid(row=0, column=0, sticky="ew", padx=(24, 0), pady=(16, 0))
        self.title_label.bind(
            "<Configure>",
            lambda e: self.title_label.configure(
                wraplength=self.title_label.winfo_width()
                * 0.65  # FIXME I have no idea why it should multiply this (approximate) number
            ),
        )

        # Description
        self.description_label = ctk.CTkLabel(
            self,
            text=document.description,
            font=ctk.CTkFont(size=14),
            anchor="nw",
            justify="left",
        )
        self.description_label.grid(
            row=1, column=0, sticky="new", padx=(24, 0), pady=(0, 12)
        )
        self.description_label.bind(
            "<Configure>",
            lambda e: self.description_label.configure(
                wraplength=self.description_label.winfo_width()
                * 0.65  # FIXME I have no idea why it should multiply this (approximate) number
            ),
        )

        # Texts
        if document.content_type == "image" and document.texts:
            texts = [
                (
                    text[: TEXTS_LINE_MAX_DISPLAY_LENGTH - 3] + "..."
                    if len(text) > TEXTS_LINE_MAX_DISPLAY_LENGTH
                    else text
                )
                for text in document.texts[:TEXTS_MAX_DISPLAY_LINES]
            ]
            if len(document.texts) > TEXTS_MAX_DISPLAY_LINES:
                texts.append(
                    f"... and {len(document.texts) - TEXTS_MAX_DISPLAY_LINES} more"
                )
            texts_str = "\n".join(texts)

            self.texts_frame = ctk.CTkFrame(
                self, corner_radius=0, fg_color="transparent", height=0
            )
            self.texts_frame.grid(
                row=2, column=0, columnspan=2, sticky="ew", padx=(0, 0), pady=(0, 12)
            )
            self.texts_frame.grid_columnconfigure(0, weight=0)
            self.texts_frame.grid_columnconfigure(1, weight=1)
            self.texts_label = ctk.CTkLabel(
                self.texts_frame,
                text="包含文本：",
                font=ctk.CTkFont(size=14, weight="bold"),
                anchor="nw",
                justify="left",
            )
            self.texts_label.grid(
                row=0, column=0, sticky="nw", padx=(24, 0), pady=(0, 0)
            )
            self.texts_content_label = ctk.CTkLabel(
                self.texts_frame,
                text=texts_str,
                font=ctk.CTkFont(size=14),
                anchor="nw",
                justify="left",
            )
            self.texts_content_label.grid(
                row=0, column=1, sticky="new", padx=(12, 12), pady=(0, 0)
            )

        # Bottom frame
        self.bottom_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.bottom_frame.grid(
            row=3, column=0, columnspan=2, sticky="ew", padx=(0, 0), pady=(12, 8)
        )
        self.bottom_frame.grid_columnconfigure(0, weight=1)

        # Tags
        self.tags_frame = ctk.CTkFrame(
            self.bottom_frame, corner_radius=0, fg_color="transparent", height=0
        )
        self.tags_frame.grid(row=0, column=0, sticky="ew", padx=(16, 0), pady=(0, 16))
        for tag in document.tags:
            tag_widget = TagWidget(self.tags_frame, tag_name=tag.name)
            tag_widget.pack(side="left", padx=6, pady=0)

        # Date
        if document.created_at is not None:
            self.date_label = ctk.CTkLabel(
                self.bottom_frame,
                text=document.created_at.strftime(r"%Y-%m-%d %H:%M:%S"),
                text_color="#777777",
            )
            self.date_label.grid(row=0, column=1, sticky="e", padx=(0, 24), pady=0)

        # Click event
        def bind_click_event(widget):
            widget.bind("<Button-1>", lambda *args: click_handler(self))
            for child in widget.winfo_children():
                bind_click_event(child)

        if click_handler:
            bind_click_event(self)


if __name__ == "__main__":  # TODO Remove this
    app = ctk.CTk()
    app.geometry("400x300")

    sample_image = Image.new("RGB", (1920, 1080), color="red")

    document_card = DocumentCard(
        app,
        Document(
            file=File(id="1", path="path/to/file.jpg", tag_ids=[], metadata={}),
            file_path="../test/2/handwritten.bmp",
            content_type="image",
            created_at=datetime.datetime.now(),
            title="Sample Document",
            description="This is a sample document.",
            tags=[Tag(id="1", name="tag1"), Tag(id="2", name="tag2")],
            texts=["This is a sample text.", "This is another sample text."],
        ),
        click_handler=lambda card: print("Clicked on card"),
    )
    document_card.pack(padx=12, pady=12, fill="x", expand=True)

    app.mainloop()
