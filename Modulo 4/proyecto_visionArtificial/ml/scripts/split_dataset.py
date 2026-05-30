import json, random, shutil
from pathlib import Path

SEED = 42
SRC_DIR = Path("data/faces_raw")
OUT_DIR = Path("data/processed")
TRAIN_RATIO = 0.70
VAL_RATIO   = 0.15
EXTS = {".jpg", ".jpeg", ".png"}

random.seed(SEED)

def list_images(folder: Path):
    return [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in EXTS]

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

# 1) Detectar clases (carpetas)
class_folders = sorted([p for p in SRC_DIR.iterdir() if p.is_dir()])
if not class_folders:
    raise SystemExit(f"No se encontraron carpetas de alumnos en: {SRC_DIR.resolve()}")

# 2) Map label -> id
labels = {cls.name: idx for idx, cls in enumerate(class_folders)}

# 3) Crear estructura salida
for split in ["train", "val", "test"]:
    for cls in class_folders:
        ensure_dir(OUT_DIR / split / cls.name)

# 4) Split por clase
for cls in class_folders:
    imgs = list_images(cls)
    n = len(imgs)
    if n < 6:
        print(f"[WARNING] {cls.name} tiene solo {n} imágenes (recomendado 8–10).")

    random.shuffle(imgs)

    n_train = max(1, int(n * TRAIN_RATIO))
    n_val   = max(1, int(n * VAL_RATIO))
    n_test  = n - n_train - n_val

    # asegurar test>=1 si es posible
    if n_test == 0 and n >= 3:
        n_test = 1
        n_train = max(1, n_train - 1)

    train_imgs = imgs[:n_train]
    val_imgs   = imgs[n_train:n_train + n_val]
    test_imgs  = imgs[n_train + n_val:]

    for p in train_imgs:
        shutil.copy2(p, OUT_DIR / "train" / cls.name / p.name)
    for p in val_imgs:
        shutil.copy2(p, OUT_DIR / "val" / cls.name / p.name)
    for p in test_imgs:
        shutil.copy2(p, OUT_DIR / "test" / cls.name / p.name)

    print(f"{cls.name}: train={len(train_imgs)} val={len(val_imgs)} test={len(test_imgs)}")

# 5) Guardar labels.json
with open(OUT_DIR / "labels.json", "w", encoding="utf-8") as f:
    json.dump(labels, f, ensure_ascii=False, indent=2)

print("\nSplit listo.")
print("labels.json:", (OUT_DIR / "labels.json").resolve())
print("processed:", OUT_DIR.resolve())