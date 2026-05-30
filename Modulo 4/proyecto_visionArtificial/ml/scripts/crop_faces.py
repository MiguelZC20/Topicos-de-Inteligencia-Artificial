from pathlib import Path
import cv2

SRC_DIR = Path("data/raw")
OUT_DIR = Path("data/faces_raw")

IMG_SIZE = (160, 160)
MARGIN = 0.45
EXTS = {".jpg", ".jpeg", ".png"}

OUT_DIR.mkdir(parents=True, exist_ok=True)

cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(cascade_path)

if face_cascade.empty():
    raise RuntimeError("No se pudo cargar Haar Cascade de OpenCV.")

def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def clamp(value, min_value, max_value):
    return max(min_value, min(max_value, value))

total = 0
ok = 0
fail = 0

class_folders = sorted([p for p in SRC_DIR.iterdir() if p.is_dir()])

if not class_folders:
    raise SystemExit(f"No se encontraron carpetas en {SRC_DIR.resolve()}")

for cls in class_folders:
    out_cls = OUT_DIR / cls.name
    ensure_dir(out_cls)

    for img_path in cls.iterdir():
        if img_path.suffix.lower() not in EXTS:
            continue

        total += 1

        img = cv2.imread(str(img_path))
        if img is None:
            fail += 1
            print(f"[WARN] No pude leer: {img_path}")
            continue

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(60, 60)
        )

        if len(faces) == 0:
            fail += 1
            print(f"[NO FACE] {img_path}")
            continue

        # Tomar el rostro más grande
        x, y, w, h = max(faces, key=lambda box: box[2] * box[3])

        mx = int(w * MARGIN)
        my = int(h * MARGIN)

        img_h, img_w = img.shape[:2]

        x1 = clamp(x - mx, 0, img_w - 1)
        y1 = clamp(y - my, 0, img_h - 1)
        x2 = clamp(x + w + mx, 0, img_w)
        y2 = clamp(y + h + my, 0, img_h)

        face = img[y1:y2, x1:x2]

        if face.size == 0:
            fail += 1
            print(f"[BAD CROP] {img_path}")
            continue

        face_resized = cv2.resize(face, IMG_SIZE, interpolation=cv2.INTER_AREA)

        out_path = out_cls / img_path.name
        cv2.imwrite(str(out_path), face_resized)

        ok += 1

print("\nRecorte terminado")
print(f"Total: {total} | OK: {ok} | Fallidas: {fail}")
print("Salida:", OUT_DIR.resolve())