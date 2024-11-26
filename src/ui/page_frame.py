import customtkinter as ctk


class PageFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color="#eeeeef")

    def pack(self):
        super().pack(fill="both", expand=True)
        self.update()
