from backend.models.models import *
from backend.repositories import watch_directory_repository, tag_repository

import customtkinter as ctk
from tkinter import StringVar, Listbox, messagebox, filedialog
import typing


class TagOption(ctk.CTkFrame):
    def __init__(self, master, tag: Tag, select_command=None, delete_command=None):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        self.tag = tag

        self.select_button = ctk.CTkButton(
            self,
            text=tag.name,
            anchor="w",
            fg_color="#f9f9fa",
            hover_color="#eaeaeb",
            corner_radius=0,
            height=30,
            command=select_command,
        )
        self.select_button.grid(row=0, column=0, sticky="ew")

        if delete_command:
            self.delete_button = ctk.CTkButton(
                self,
                text="×",
                anchor="center",
                fg_color="#ff4444",
                hover_color="#ff6666",
                corner_radius=0,
                width=30,
                height=30,
                command=delete_command,
            )
            self.delete_button.grid(row=0, column=1, sticky="e")

    def pack(self, **kwargs):
        super().pack(fill="x", **kwargs)
        self.update()


class TagListBox(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, corner_radius=0, fg_color="#f9f9fa", **kwargs)

    def add_tag_option(self, tag: Tag, select_command=None, delete_command=None):
        tag_option = TagOption(
            self, tag, select_command=select_command, delete_command=delete_command
        )
        tag_option.pack(fill="x", padx=16, pady=8)

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()


class EditDataSourcePanel(ctk.CTkFrame):
    def __init__(
        self,
        master,
        close_command,
        mode: typing.Literal["add", "edit"] = "edit",
        data_source: DataSource = None,
        **kwargs,
    ):
        super().__init__(master, corner_radius=0, width=400, **kwargs)
        self.close_command = close_command

        self.data_source = data_source

        self.path_var = StringVar()
        if data_source:
            self.path_var.set(data_source.watch_directory.path)

        # Path frame
        self.path_frame = ctk.CTkFrame(self)
        self.path_frame.pack(pady=(16, 0), fill="x", padx=16)

        # Path input
        self.path_label = ctk.CTkLabel(self.path_frame, text="目录")
        self.path_label.pack(pady=(8, 0))
        self.path_entry = ctk.CTkEntry(self.path_frame, textvariable=self.path_var)
        self.path_entry.pack(pady=8, fill="x", padx=16)

        # Browse button
        self.browse_button = ctk.CTkButton(
            self.path_frame, text="选择目录", command=self.browse_file
        )
        self.browse_button.pack(pady=(8, 16))

        # Tags frame
        self.tags_frame = ctk.CTkFrame(self)
        self.tags_frame.pack(fill="x", padx=16, pady=(16, 0))

        # Listbox for displaying current tags
        self.add_tag_label = ctk.CTkLabel(self.tags_frame, text="关联标签")
        self.add_tag_label.pack(pady=(8, 0))
        self.tags_listbox = TagListBox(self.tags_frame, height=100)
        self.tags_listbox.pack(pady=8, fill="x", padx=16)

        # Add tag frame
        self.add_tag_frame = ctk.CTkFrame(self)
        self.add_tag_frame.pack(pady=(16, 16), fill="x", padx=16)

        # Tags input with entry
        self.add_tag_label = ctk.CTkLabel(self.add_tag_frame, text="添加关联标签")
        self.add_tag_label.pack(pady=(8, 0))
        self.add_tag_input = StringVar()
        self.add_tag_entry = ctk.CTkEntry(
            self.add_tag_frame, textvariable=self.add_tag_input
        )
        self.add_tag_entry.pack(pady=8, fill="x", padx=16)
        self.add_tag_entry.bind("<KeyRelease>", self.update_tag_suggestions)

        # Listbox for displaying tag suggestions
        self.tag_suggestions = list[Tag]()
        self.tag_suggestions_listbox = TagListBox(self.add_tag_frame, height=100)
        self.tag_suggestions_listbox.pack(pady=(8, 16), fill="x", padx=16)

        self.save_button = ctk.CTkButton(self, text="完成", command=self.save_edits)
        self.save_button.pack(pady=8)

        if mode == "edit":
            self.delete_button = ctk.CTkButton(
                self,
                text="删除数据源",
                command=self.confirm_delete,
                fg_color="#ff4444",
                hover_color="#ff6666",
            )
            self.delete_button.pack(pady=8)

        self.selected_tags = list[Tag]()

    def browse_file(self):
        file_path = filedialog.askdirectory(title="选择目录")
        if file_path:
            self.path_entry.delete(0, "end")  # Clear current entry
            self.path_entry.insert(0, file_path)  # Insert selected file path

    def update_tag_suggestions(self, event):
        prefix = self.add_tag_input.get()
        self.tag_suggestions = tag_repository.query_tags_by_prefix(prefix)

        # Update the listbox with suggestions
        self.tag_suggestions_listbox.clear()
        for tag in self.tag_suggestions:
            self.tag_suggestions_listbox.add_tag_option(
                tag, select_command=lambda: self.add_tag_from_listbox(tag)
            )

    def add_tag_from_listbox(self, tag: Tag):
        self.selected_tags.append(tag)
        self.update_current_tags_listbox()
        self.add_tag_input.set("")  # Clear input after selection
        self.tag_suggestions_listbox.clear()  # Clear suggestions

    def update_current_tags_listbox(self):
        self.tags_listbox.clear()
        for tag in self.selected_tags:
            self.tags_listbox.add_tag_option(
                tag, delete_command=lambda: self.remove_tag(tag)
            )

    def remove_tag(self, tag: Tag):
        self.selected_tags.remove(tag)
        self.update_current_tags_listbox()

    def confirm_delete(self):
        if messagebox.askyesno("确认删除", "确定要删除此数据源吗？"):
            self.delete_data_source()

    def delete_data_source(self):
        watch_directory_repository.delete_watch_directory(
            self.data_source.watch_directory
        )
        self.close_command()

    def save_edits(self):
        path = self.path_entry.get()
        tags = self.selected_tags
        if self.data_source:
            watch_directory_repository.delete_watch_directory(
                self.data_source.watch_directory
            )
        watch_directory_repository.create_watch_directory(path, tags)
        self.close_command()

    def cancel_edits(self):
        # Close the panel without saving changes
        self.close_command()


if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("400x800")
    popup = EditDataSourcePanel(root)
    popup.pack(fill="both", expand=True)
    root.mainloop()
