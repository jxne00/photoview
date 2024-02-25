import os
import configparser
from tkinter import Tk, Button, Frame, Canvas, Scrollbar, Label, filedialog, messagebox
from PIL import Image, ImageTk

from components.lightbox import Lightbox
from components.printing import Printing


class PhotoViewerApp:
    def __init__(self):
        self.root = Tk()
        self.selected_image_path = None
        self.bg_color = "#1B2430"
        self.image_list = []
        self.current_image_index = 0
        self.fullscreen = False
        self.fullscreen_button = None
        self.setup_UI()
        self.config_file = "config.ini"
        self.config = configparser.ConfigParser()
        self.load_config()
        self.check_last_opened()
        self.root.mainloop()

    def load_config(self):
        if os.path.exists(self.config_file):
            # set config file if exists
            self.config.read(self.config_file)
        else:
            # create config file with default values if not exist
            self.config["DEFAULT"] = {"last_opened_folder": ""}
            with open(self.config_file, "w") as configfile:
                self.config.write(configfile)

    def set_last_opened(self, folder_path):
        # save last opened folder path to config
        self.config["DEFAULT"]["last_opened_folder"] = folder_path
        with open(self.config_file, "w") as configfile:
            self.config.write(configfile)

    def get_last_opened(self):
        # get last opened folder path from config
        return self.config["DEFAULT"]["last_opened_folder"]

    def check_last_opened(self):
        # fill gallery with last opened folder if exists
        last_opened = self.get_last_opened()
        if last_opened and os.path.exists(last_opened):
            self.select_folder(folder_path=last_opened)

    def setup_UI(self):
        """UI setup for the main app window"""
        self.root.title("Photo Viewer")
        self.root.geometry("800x600")
        self.root.configure(bg=self.bg_color)

        # frame to hold buttons
        buttons_frame = Frame(self.root, bg=self.bg_color)
        buttons_frame.pack(side="top", pady=10, fill="x", padx=10)

        # "open folder" button
        open_folder_btn = Button(
            buttons_frame,
            text="Open Folder",
            command=self.select_folder,
            bg="#212c3d",
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
            bg="#212c3d",
            fg="white",
            relief="flat",
            font=("Helvetica", 10, "bold"),
            padx=20,
            pady=5,
        )
        print_button.grid(row=0, column=1, padx=5)

        # "fullscreen" button
        self.fullscreen_button = Button(
            buttons_frame,
            # add tick or cross to text based on current state
            text="Fullscreen" if not self.fullscreen else "Exit Fullscreen",
            command=self.toggle_fullscreen,
            bg="#212c3d",
            fg="white",
            relief="flat",
            font=("Helvetica", 10, "bold"),
            padx=20,
            pady=5,
        )
        self.fullscreen_button.grid(row=0, column=2, padx=5)

        # exit button
        exit_button = Button(
            buttons_frame,
            text="Exit",
            command=self.root.quit,
            bg="#212c3d",
            fg="white",
            relief="flat",
            font=("Helvetica", 10, "bold"),
            padx=20,
            pady=5,
        )
        exit_button.grid(row=0, column=3, padx=5)

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

    def select_folder(self, folder_path=None):
        """
        Open file dialog to select a folder and display images in the folder
        """
        if not folder_path:
            folder_path = filedialog.askdirectory()
            if not folder_path:
                return
            self.set_last_opened(folder_path)

        # clear any existing images
        for widget in self.frame_inside_canvas.winfo_children():
            widget.destroy()

        # get list of images within the folder
        self.image_list = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if f.endswith((".png", ".jpg", ".jpeg"))
        ]

        # add list of images to the gallery
        row, col = 0, 0
        for img_path in self.image_list:
            self.add_to_gallery(img_path, row, col)
            col += 1
            if col >= 5:  # show 5 images per row
                col = 0
                row += 1
        self.current_image_index = 0

    def add_to_gallery(self, img_path, row, col):
        """
        Open image from given path and add to the gallery
        """
        # open image and resize
        img = Image.open(img_path)
        img.thumbnail((200, 200), Image.LANCZOS)

        tk_img = ImageTk.PhotoImage(img)

        img_label = Label(self.frame_inside_canvas, image=tk_img, bg=self.bg_color)
        img_label.image = tk_img
        img_label.grid(row=row, column=col, padx=5, pady=5)

        # open lightbox on double click
        img_label.bind("<Double-1>", lambda e, path=img_path: self.open_lightbox(path))
        # set selected image on single click
        img_label.bind(
            "<Button-1>",
            lambda e, path=img_path, label=img_label: self.select_image(path, label),
        )

    def select_image(self, path, label=None):
        """
        Set selected image and highlight it
        """
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

    def toggle_fullscreen(self):
        """
        Toggle fullscreen mode
        """
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)

        # bind escape key to exit fullscreen
        if self.fullscreen:
            self.root.bind("<Escape>", self.toggle_fullscreen)
        self.root.bind("<F11>", self.toggle_fullscreen)

        self.fullscreen_button.configure(
            text="Fullscreen" if not self.fullscreen else "Exit Fullscreen"
        )


if __name__ == "__main__":
    PhotoViewerApp()
