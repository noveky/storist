import customtkinter as ctk


class TagWidget(ctk.CTkFrame):
    def __init__(self, master, tag_name: str):
        super().__init__(
            master,
            height=28,
            corner_radius=14,
            border_width=2,
            border_color="#8a32a9",
            fg_color="#ece5f3",
        )

        self.hash_label = ctk.CTkLabel(
            self,
            height=20,
            text="#",
            text_color="#8a32a9",
            font=ctk.CTkFont(size=12),
        )
        self.hash_label.pack(side="left", padx=(12, 4), pady=3)

        self.text_label = ctk.CTkLabel(
            self,
            height=20,
            text=tag_name,
            text_color="#8a32a9",
            font=ctk.CTkFont(size=12),
        )
        self.text_label.pack(side="left", padx=(0, 12), pady=3)
