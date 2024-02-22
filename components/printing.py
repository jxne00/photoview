import os
import win32api
import win32print

from tkinter import Toplevel, Button, Label, filedialog, OptionMenu, StringVar
from PIL import Image, ImageTk


class Printing:
    def __init__(self, master, image_path, bg_color):
        self.master = master
        self.image_path = image_path
        self.bg_color = bg_color
        self.overlay_image_path = None
        self.printer_name = StringVar(self.master)
        self.init_ui()

    def init_ui(self):
        self.print_window = Toplevel(self.master)
        self.print_window.title("Print Preview")
        self.print_window.configure(bg=self.bg_color)
        self.print_window.geometry("800x600")

        self.preview_label = Label(self.print_window, bg=self.bg_color)
        self.preview_label.pack(expand=True)

        Button(
            self.print_window, text="Upload Overlay", command=self.upload_overlay
        ).pack(side="top")

        # dropdown to select printer
        printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)
        printer_names = [printer[2] for printer in printers]
        self.printer_name.set(win32print.GetDefaultPrinter())
        OptionMenu(self.print_window, self.printer_name, *printer_names).pack(
            side="top"
        )

        # button to toggle overlay on/off
        Button(
            self.print_window,
            text="Toggle Overlay",
            command=self.toggle_overlay,
            relief="flat",
        ).pack(side="top")

        # print button
        Button(self.print_window, text="Print Image", command=self.print_image).pack(
            side="bottom"
        )

        self.update_preview()

    def upload_overlay(self):
        self.overlay_image_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg")]
        )
        if self.overlay_image_path:
            self.update_preview(with_overlay=True)
            self.print_window.focus_force()

    def toggle_overlay(self):
        if self.overlay_image_path:
            # toggle with/without overlay
            self.update_preview(toggle=True)

    def update_preview(self, with_overlay=False, toggle=False):
        img = Image.open(self.image_path)
        if self.overlay_image_path and (with_overlay or toggle):
            overlay = Image.open(self.overlay_image_path).resize(
                img.size, Image.Resampling.LANCZOS
            )
            img.paste(overlay, (0, 0), overlay)

        # resize image to fit the window
        max_size = (800, 600)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        tk_img = ImageTk.PhotoImage(img)
        self.preview_label.config(image=tk_img)
        self.preview_label.image = tk_img
        self.print_window.focus_force()

    def print_image(self):
        selected_printer = self.printer_name.get()
        self.do_print(self.image_path, selected_printer, with_overlay=True)

    def do_print(self, image_path, printer_name, with_overlay=False):
        if with_overlay and self.overlay_image_path:
            img = Image.open(self.image_path)
            overlay = Image.open(self.overlay_image_path).resize(
                img.size, Image.Resampling.LANCZOS
            )
            img.paste(overlay, (0, 0), overlay)
            temp_path = "temp_print_image_with_overlay.png"
            img.save(temp_path)
            image_path = temp_path

        win32print.SetDefaultPrinter(printer_name)
        win32api.ShellExecute(0, "print", image_path, '/d:"%s"' % printer_name, ".", 0)

        if with_overlay:
            os.remove(temp_path)
