from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk
import os

bg_color = "#1B2430"
image_list = []
current_image_index = 0


def update_lightbox(index):
    global current_image_index
    if 0 <= index < len(image_list):
        img_path = image_list[index]
        img = Image.open(img_path)
        img.thumbnail((600, 400), Image.Resampling.LANCZOS)
        tk_img = ImageTk.PhotoImage(img)

        img_label.config(image=tk_img)
        img_label.image = tk_img
        current_image_index = index


def show_next_image(event=None):
    update_lightbox(current_image_index + 1)


def show_previous_image(event=None):
    update_lightbox(current_image_index - 1)


def open_lightbox(image_path):
    global img_label
    lightbox_window = Toplevel()
    lightbox_window.title("Image View")
    lightbox_window.geometry("600x400")
    lightbox_window.configure(bg=bg_color)

    # prev and next buttons
    btn_prev = Button(lightbox_window, text="<", command=show_previous_image)
    btn_prev.pack(side=LEFT, padx=10)

    btn_next = Button(lightbox_window, text=">", command=show_next_image)
    btn_next.pack(side=RIGHT, padx=10)

    # bind arrow keys to show next and previous images
    lightbox_window.bind("<Left>", show_previous_image)
    lightbox_window.bind("<Right>", show_next_image)

    img_label = Label(lightbox_window, bg=bg_color)
    img_label.pack(expand=True)

    update_lightbox(image_list.index(image_path))


def select_folder():
    global image_list, current_image_index

    # clear the frame
    for widget in frame_inside_canvas.winfo_children():
        widget.destroy()

    # open folder dialog
    folder_path = filedialog.askdirectory()
    if folder_path:
        image_list = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if f.endswith((".png", ".jpg", ".jpeg"))
        ]
        row, col = 0, 0
        for img_path in image_list:
            img = Image.open(img_path)
            img.thumbnail((100, 100), Image.Resampling.LANCZOS)
            tk_img = ImageTk.PhotoImage(img)

            img_label = Label(frame_inside_canvas, image=tk_img, bg=bg_color)
            img_label.image = tk_img
            img_label.grid(row=row, column=col, padx=10, pady=10)
            # open image in lightbox on button click
            img_label.bind("<Button-1>", lambda e, path=img_path: open_lightbox(path))

            col += 1
            # show 5 images per row
            if col >= 5:
                col = 0
                row += 1
        current_image_index = 0


root = Tk()
root.title("Photo Viewer")
root.geometry("950x500")
root.configure(bg=bg_color)

# "open folder" button
open_folder_btn = Button(
    root, text="Open Folder", command=select_folder, bg=bg_color, fg="white"
)
open_folder_btn.pack(side=TOP, pady=10)

# frame to hold images
frame = Frame(root, bg=bg_color)
frame.pack(fill=BOTH, expand=True)

canvas = Canvas(frame, bg=bg_color)
canvas.pack(side=LEFT, fill=BOTH, expand=True)

scrollbar = Scrollbar(frame, orient=VERTICAL, command=canvas.yview)
scrollbar.pack(side=RIGHT, fill=Y)

canvas.configure(yscrollcommand=scrollbar.set)
canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

frame_inside_canvas = Frame(canvas, bg=bg_color)
canvas.create_window((0, 0), window=frame_inside_canvas, anchor="nw")

# button to exit
exit_button = Button(root, text="Exit", command=root.quit, bg=bg_color, fg="white")
exit_button.pack(side=BOTTOM, pady=10)


root.mainloop()
