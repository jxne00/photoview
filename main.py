import os
from tkinter import Tk, Button, Frame, Canvas, Scrollbar, Label, filedialog, messagebox
from PIL import Image, ImageTk

from components.lightbox import Lightbox
from components.printing import Printing


class PhotoViewerApp:
    def __init__(self, root):
        self.root = root
        self.selected_image_path = None
        self.bg_color = "#1B2430"
        self.button_color = "#2E3B4E"
        self.image_list = []
        self.current_image_index = 0
        self.init_ui()

    def init_ui(self):
        """UI setup for the main app window"""
        self.root.title("Photo Viewer")
        self.root.geometry("1080x600")
        self.root.configure(bg=self.bg_color)

        buttons_frame = Frame(self.root, bg=self.bg_color)
        buttons_frame.pack(side="top", pady=10, fill="x", padx=10)

        # "open folder" button
        open_folder_btn = Button(
            buttons_frame,
            text="Open Folder",
            command=self.select_folder,
            bg=self.button_color,
            fg="white",
            relief="flat",
            font=("Helvetica", 10, "bold"),
            padx=20,
            pady=5,
        )
        open_folder_btn.grid(row=0, column=0, padx=5)

        # "print" button
        print_button = Button(
            buttons_frame,
            text="Print",
            command=self.print_image,
            bg=self.button_color,
            fg="white",
            relief="flat",
            font=("Helvetica", 10, "bold"),
            padx=20,
            pady=5,
        )
        print_button.grid(row=0, column=1, padx=5)

        # frame to hold images
        frame = Frame(self.root, bg=self.bg_color)
        frame.pack(fill="both", expand=True)

        canvas = Canvas(frame, bg=self.bg_color)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        self.frame_inside_canvas = Frame(canvas, bg=self.bg_color)
        canvas.create_window((0, 0), window=self.frame_inside_canvas, anchor="nw")

        # button to exit
        exit_button = Button(
            self.root, text="Exit", command=self.root.quit, bg=self.bg_color, fg="white"
        )
        exit_button.pack(side="bottom", pady=10)

    def select_folder(self):
        # clear the frame
        for widget in self.frame_inside_canvas.winfo_children():
            widget.destroy()

        folder_path = filedialog.askdirectory()
        if folder_path:
            self.image_list = [
                os.path.join(folder_path, f)
                for f in os.listdir(folder_path)
                if f.endswith((".png", ".jpg", ".jpeg"))
            ]
            row, col = 0, 0
            for img_path in self.image_list:
                self.add_image_to_gallery(img_path, row, col)
                col += 1
                if col >= 5:  # show 5 images per row
                    col = 0
                    row += 1
            self.current_image_index = 0

    def add_image_to_gallery(self, img_path, row, col):
        # open image and add to gallery
        img = Image.open(img_path)
        img.thumbnail((100, 100), Image.Resampling.LANCZOS)
        tk_img = ImageTk.PhotoImage(img)

        img_label = Label(self.frame_inside_canvas, image=tk_img, bg=self.bg_color)
        img_label.image = tk_img
        img_label.grid(row=row, column=col, padx=10, pady=10)

        # open lightbox on double click
        img_label.bind("<Double-1>", lambda e, path=img_path: self.open_lightbox(path))
        # set selected image on single click
        # img_label.bind("<Button-1>", lambda e, path=img_path: self.select_image(path))
        img_label.bind(
            "<Button-1>",
            lambda e, path=img_path, label=img_label: self.select_image(path, label),
        )

    def select_image(self, path, label=None):
        # clear previous selection
        for widget in self.frame_inside_canvas.winfo_children():
            if isinstance(widget, Label):
                widget.configure(bg=self.bg_color)

        # highlight selected image
        label.configure(bg="blue")
        self.selected_image_path = path

    def open_lightbox(self, image_path):
        index = self.image_list.index(image_path)
        Lightbox(self.root, self.image_list, self.bg_color, start_index=index)

    def print_image(self):
        # print selected image
        if self.selected_image_path:
            Printing(self.root, self.selected_image_path, self.bg_color)
        else:
            # show error if no image selected
            self.show_error("Please select an image to print.")

    def show_error(self, message):
        messagebox.showerror("Error", message)


if __name__ == "__main__":
    root = Tk()
    app = PhotoViewerApp(root)
    root.mainloop()
