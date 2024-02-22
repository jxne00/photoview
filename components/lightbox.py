from tkinter import Toplevel, Button, Label
from PIL import Image, ImageTk


class Lightbox:
    def __init__(self, master, image_list, bg_color, start_index=0):
        self.master = master
        self.image_list = image_list
        self.bg_color = bg_color
        self.current_image_index = start_index
        self.lightbox_window = Toplevel(self.master)
        self.lightbox_window.title("Image View")
        self.lightbox_window.geometry("600x400")
        self.lightbox_window.configure(bg=self.bg_color)
        self.img_label = Label(self.lightbox_window, bg=self.bg_color)
        self.init_ui()

    def init_ui(self):
        # prev and next buttons
        btn_prev = Button(
            self.lightbox_window, text="<", command=self.show_previous_image
        )
        btn_prev.pack(side="left", padx=10)

        btn_next = Button(self.lightbox_window, text=">", command=self.show_next_image)
        btn_next.pack(side="right", padx=10)

        # bind arrow keys
        self.lightbox_window.bind("<Left>", self.show_previous_image)
        self.lightbox_window.bind("<Right>", self.show_next_image)

        self.img_label.pack(expand=True)
        self.update_lightbox(self.current_image_index)

    def update_lightbox(self, index):
        if 0 <= index < len(self.image_list):
            img_path = self.image_list[index]
            img = Image.open(img_path)
            img.thumbnail((600, 400), Image.Resampling.LANCZOS)
            tk_img = ImageTk.PhotoImage(img)

            self.img_label.config(image=tk_img)
            self.img_label.image = tk_img
            self.current_image_index = index

    def show_next_image(self, event=None):
        self.update_lightbox(self.current_image_index + 1)

    def show_previous_image(self, event=None):
        self.update_lightbox(self.current_image_index - 1)
