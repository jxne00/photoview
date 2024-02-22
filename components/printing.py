import os
import win32api
import win32print

from tkinter import Toplevel, Button, Label, filedialog
from PIL import Image, ImageTk, ImageDraw


class Printing:
    def __init__(self, master, image_path, bg_color):
        self.master = master
        self.image_path = image_path
        self.bg_color = bg_color
        self.overlay_image_path = None
        self.init_ui()

    def init_ui(self):
        self.print_window = Toplevel(self.master)
        self.print_window.title("Print Preview")
        self.print_window.configure(bg=self.bg_color)

        self.preview_label = Label(self.print_window, bg=self.bg_color)
        self.preview_label.pack()

        Button(
            self.print_window, text="Upload Overlay", command=self.upload_overlay
        ).pack(side="top")
        Button(self.print_window, text="Print Image", command=self.print_image).pack(
            side="bottom"
        )

        self.update_preview()

    def upload_overlay(self):
        self.overlay_image_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg")]
        )
        if self.overlay_image_path:
            self.update_preview()

    def update_preview(self):
        img = Image.open(self.image_path)
        if self.overlay_image_path:
            overlay = Image.open(self.overlay_image_path).resize(
                img.size, Image.ANTIALIAS
            )
            img.paste(overlay, (0, 0), overlay)
        tk_img = ImageTk.PhotoImage(img)
        self.preview_label.config(image=tk_img)
        self.preview_label.image = tk_img

    def print_image(self):
        # print with overlay if available
        if self.overlay_image_path:
            img = Image.open(self.image_path)
            overlay = Image.open(self.overlay_image_path).resize(
                img.size, Image.ANTIALIAS
            )
            img.paste(overlay, (0, 0), overlay)
            temp_path = "temp_print_image.png"
            img.save(temp_path)
            self.do_print(temp_path)
            os.remove(temp_path)
        # print without overlay
        else:
            self.do_print(self.image_path)

    def do_print(self, image_path):
        printer_name = win32print.GetDefaultPrinter()
        win32api.ShellExecute(0, "print", image_path, None, ".", 0)
