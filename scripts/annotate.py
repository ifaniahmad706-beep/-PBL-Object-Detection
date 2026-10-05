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

index = 0
boxes = []

drawing = False
start_x = 0
start_y = 0

image = None
display = None

WINDOW = "Manual Annotation"


def redraw():
    global display

    display = image.copy()

    for i, (x1, y1, x2, y2) in enumerate(boxes):

        cv2.rectangle(
            display,
            (x1, y1),
            (x2, y2),
            (255, 0, 0),
            2
        )

        cv2.putText(
            display,
            f"BOX {i + 1}",
            (x1, max(y1 - 10, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 0, 0),
            2
        )


def mouse_callback(event, x, y, flags, param):

    global drawing
    global start_x
    global start_y
    global boxes

    # KLIK KIRI -> mulai menggambar
    if event == cv2.EVENT_LBUTTONDOWN:

        drawing = True

        start_x = x
        start_y = y

    # LEPAS KLIK KIRI -> selesai menggambar
    elif event == cv2.EVENT_LBUTTONUP:

        if not drawing:
            return

        drawing = False

        x1 = min(start_x, x)
        y1 = min(start_y, y)

        x2 = max(start_x, x)
        y2 = max(start_y, y)

        if x2 - x1 > 5 and y2 - y1 > 5:

            boxes.append(
                (x1, y1, x2, y2)
            )

            print(
                f"Box {len(boxes)} dibuat: "
                f"({x1},{y1}) -> ({x2},{y2})"
            )

            redraw()

    # KLIK KANAN -> SAVE
    elif event == cv2.EVENT_RBUTTONDOWN:

        if len(boxes) == 0:

            print("BELUM ADA BOX. Buat bounding box dulu.")

            return

        save_label()


def save_label():

    global index

    image_name = images[index]

    h, w = image.shape[:2]

    label_name = (
        os.path.splitext(image_name)[0]
        + ".txt"
    )

    label_path = os.path.join(
        LABEL_DIR,
        label_name
    )

    with open(label_path, "w") as f:

        for x1, y1, x2, y2 in boxes:

            x_center = ((x1 + x2) / 2) / w
            y_center = ((y1 + y2) / 2) / h

            box_width = (x2 - x1) / w
            box_height = (y2 - y1) / h

            f.write(
                f"{CLASS_ID} "
                f"{x_center:.6f} "
                f"{y_center:.6f} "
                f"{box_width:.6f} "
                f"{box_height:.6f}\n"
            )

    print()
    print("=" * 50)
    print("LABEL BERHASIL DISIMPAN")
    print(f"File: {label_path}")
    print(f"Jumlah box: {len(boxes)}")
    print("=" * 50)

    cv2.destroyWindow(WINDOW)

    index += 1


while index < len(images):

    image_name = images[index]

    image_path = os.path.join(
        IMAGE_DIR,
        image_name
    )

    image = cv2.imread(image_path)

    if image is None:

        print(
            f"Gagal membaca: {image_name}"
        )

        index += 1

        continue

    boxes = []

    redraw()

    cv2.namedWindow(
        WINDOW,
        cv2.WINDOW_NORMAL
    )

    cv2.setMouseCallback(
        WINDOW,
        mouse_callback
    )

    print()
    print("=" * 50)
    print(
        f"GAMBAR {index + 1}/{len(images)}"
    )
    print(f"File: {image_name}")
    print()
    print("KLIK KIRI + DRAG  = buat bounding box")
    print("KLIK KANAN         = SAVE")
    print("=" * 50)

    while True:

        cv2.imshow(
            WINDOW,
            display
        )

        key = cv2.waitKey(20) & 0xFF

        # Q sebagai emergency exit
        if key == ord("q"):

            cv2.destroyAllWindows()

            print()
            print("Annotation dihentikan.")

            exit()

        # ESC sebagai emergency exit
        if key == 27:

            cv2.destroyAllWindows()

            print()
            print("Annotation dihentikan.")

            exit()

        # Window ditutup
        if cv2.getWindowProperty(
            WINDOW,
            cv2.WND_PROP_VISIBLE
        ) < 1:

            exit()

        # Setelah klik kanan dan save,
        # index berubah.
        if index >= len(images):
            break

        # Jika window sebelumnya sudah ditutup
        try:

            visible = cv2.getWindowProperty(
                WINDOW,
                cv2.WND_PROP_VISIBLE
            )

            if visible < 1:
                break

        except:
            break

        # Save membuat window ditutup.
        # Cek apakah label untuk gambar ini sudah ada.
        label_name = (
            os.path.splitext(image_name)[0]
            + ".txt"
        )

        label_path = os.path.join(
            LABEL_DIR,
            label_name
        )

        if os.path.exists(label_path):

            cv2.destroyAllWindows()

            break

cv2.destroyAllWindows()

print()
print("=" * 50)
print("ANNOTATION SELESAI")
print("=" * 50)