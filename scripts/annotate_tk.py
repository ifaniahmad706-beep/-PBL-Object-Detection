import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import os


IMAGE_DIR = "dataset/train/images"
LABEL_DIR = "dataset/train/labels"

CLASS_ID = 0

os.makedirs(LABEL_DIR, exist_ok=True)


images = sorted([
    f for f in os.listdir(IMAGE_DIR)
    if f.lower().endswith((".jpg", ".jpeg", ".png"))
])


class AnnotationTool:

    def __init__(self, root):

        self.root = root
        self.root.title("Manual YOLO Annotation")

        self.index = 0

        self.image = None
        self.photo = None

        self.scale = 1.0

        self.boxes = []

        self.start_x = None
        self.start_y = None

        self.temp_rect = None

        # =========================
        # CANVAS
        # =========================

        self.canvas = tk.Canvas(
            root,
            width=1000,
            height=700,
            bg="black"
        )

        self.canvas.pack()

        # =========================
        # BUTTONS
        # =========================

        button_frame = tk.Frame(root)

        button_frame.pack(
            pady=10
        )

        tk.Button(
            button_frame,
            text="SAVE",
            width=12,
            height=2,
            command=self.save
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        tk.Button(
            button_frame,
            text="RESET",
            width=12,
            height=2,
            command=self.reset
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        tk.Button(
            button_frame,
            text="SKIP",
            width=12,
            height=2,
            command=self.skip
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        tk.Button(
            button_frame,
            text="QUIT",
            width=12,
            height=2,
            command=self.root.destroy
        ).pack(
            side=tk.LEFT,
            padx=5
        )

        # =========================
        # INFO
        # =========================

        self.info = tk.Label(
            root,
            text="",
            font=("Arial", 11)
        )

        self.info.pack(
            pady=5
        )

        # =========================
        # MOUSE
        # =========================

        self.canvas.bind(
            "<ButtonPress-1>",
            self.mouse_down
        )

        self.canvas.bind(
            "<B1-Motion>",
            self.mouse_move
        )

        self.canvas.bind(
            "<ButtonRelease-1>",
            self.mouse_up
        )

        # =========================
        # LOAD FIRST IMAGE
        # =========================

        self.load_image()


    def load_image(self):

        if self.index >= len(images):

            messagebox.showinfo(
                "Selesai",
                "Semua gambar sudah selesai di-annotate."
            )

            self.root.destroy()

            return

        image_name = images[self.index]

        image_path = os.path.join(
            IMAGE_DIR,
            image_name
        )

        self.image = cv2.imread(
            image_path
        )

        if self.image is None:

            self.index += 1

            self.load_image()

            return

        self.boxes = []

        self.display_image()

        self.update_info()


    def display_image(self):

        # OpenCV BGR -> RGB
        rgb = cv2.cvtColor(
            self.image,
            cv2.COLOR_BGR2RGB
        )

        pil_image = Image.fromarray(
            rgb
        )

        original_width, original_height = pil_image.size

        max_width = 1000
        max_height = 650

        self.scale = min(
            max_width / original_width,
            max_height / original_height,
            1.0
        )

        new_width = int(
            original_width * self.scale
        )

        new_height = int(
            original_height * self.scale
        )

        pil_image = pil_image.resize(
            (new_width, new_height)
        )

        self.photo = ImageTk.PhotoImage(
            pil_image
        )

        self.canvas.delete(
            "all"
        )

        self.canvas.config(
            width=new_width,
            height=new_height
        )

        self.canvas.create_image(
            0,
            0,
            anchor=tk.NW,
            image=self.photo
        )

        # gambar box yang sudah dibuat
        for box in self.boxes:

            x1, y1, x2, y2 = box

            self.canvas.create_rectangle(
                x1 * self.scale,
                y1 * self.scale,
                x2 * self.scale,
                y2 * self.scale,
                outline="red",
                width=3
            )


    def mouse_down(self, event):

        self.start_x = event.x
        self.start_y = event.y

        self.temp_rect = self.canvas.create_rectangle(
            self.start_x,
            self.start_y,
            self.start_x,
            self.start_y,
            outline="yellow",
            width=3
        )


    def mouse_move(self, event):

        if self.temp_rect is not None:

            self.canvas.coords(
                self.temp_rect,
                self.start_x,
                self.start_y,
                event.x,
                event.y
            )


    def mouse_up(self, event):

        if self.temp_rect is None:
            return

        x1 = min(
            self.start_x,
            event.x
        )

        y1 = min(
            self.start_y,
            event.y
        )

        x2 = max(
            self.start_x,
            event.x
        )

        y2 = max(
            self.start_y,
            event.y
        )

        self.canvas.delete(
            self.temp_rect
        )

        self.temp_rect = None

        if x2 - x1 < 5 or y2 - y1 < 5:
            return

        # convert dari ukuran tampilan
        # ke ukuran gambar asli
        real_x1 = int(
            x1 / self.scale
        )

        real_y1 = int(
            y1 / self.scale
        )

        real_x2 = int(
            x2 / self.scale
        )

        real_y2 = int(
            y2 / self.scale
        )

        self.boxes.append(
            (
                real_x1,
                real_y1,
                real_x2,
                real_y2
            )
        )

        print(
            f"Box {len(self.boxes)}: "
            f"({real_x1},{real_y1}) -> "
            f"({real_x2},{real_y2})"
        )

        self.display_image()


    def reset(self):

        self.boxes = []

        self.display_image()

        print("Semua bounding box dihapus.")


    def save(self):

        if len(self.boxes) == 0:

            messagebox.showwarning(
                "Belum ada box",
                "Buat bounding box terlebih dahulu."
            )

            return

        image_name = images[self.index]

        image_height, image_width = self.image.shape[:2]

        label_name = (
            os.path.splitext(image_name)[0]
            + ".txt"
        )

        label_path = os.path.join(
            LABEL_DIR,
            label_name
        )

        with open(
            label_path,
            "w"
        ) as f:

            for x1, y1, x2, y2 in self.boxes:

                x_center = (
                    (x1 + x2) / 2
                ) / image_width

                y_center = (
                    (y1 + y2) / 2
                ) / image_height

                width = (
                    x2 - x1
                ) / image_width

                height = (
                    y2 - y1
                ) / image_height

                f.write(
                    f"{CLASS_ID} "
                    f"{x_center:.6f} "
                    f"{y_center:.6f} "
                    f"{width:.6f} "
                    f"{height:.6f}\n"
                )

        print()
        print("=" * 50)
        print("LABEL BERHASIL DISIMPAN")
        print(f"File: {label_path}")
        print(f"Jumlah box: {len(self.boxes)}")
        print("=" * 50)

        self.index += 1

        self.load_image()


    def skip(self):

        self.index += 1

        self.load_image()


    def update_info(self):

        image_name = images[self.index]

        self.info.config(
            text=(
                f"Gambar {self.index + 1}/{len(images)}"
                f"    |    {image_name}"
                f"    |    Box: {len(self.boxes)}"
            )
        )


# =========================
# START PROGRAM
# =========================

root = tk.Tk()

app = AnnotationTool(
    root
)

root.mainloop()