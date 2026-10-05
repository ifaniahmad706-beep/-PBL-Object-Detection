import cv2
import os
import time

SAVE_DIR = "dataset/train/images"
CAMERA_ID = 2

os.makedirs(SAVE_DIR, exist_ok=True)

camera = cv2.VideoCapture(CAMERA_ID, cv2.CAP_DSHOW)

if not camera.isOpened():
    print("ERROR: Webcam tidak dapat dibuka.")
    exit()

print("Webcam berhasil dibuka.")
print("Tekan SPACE untuk mengambil foto.")
print("Tekan Q untuk keluar.")

count = 0

while True:
    ret, frame = camera.read()

    if not ret:
        print("ERROR: Gagal membaca frame dari webcam.")
        break

    cv2.imshow("Dataset Capture", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == 32:  # SPACE
        filename = os.path.join(
            SAVE_DIR,
            f"box_{count:04d}.jpg"
        )

        cv2.imwrite(filename, frame)

        print(f"Foto tersimpan: {filename}")
        count += 1

        time.sleep(0.3)

    elif key == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()

print(f"\nSelesai. Total foto: {count}")