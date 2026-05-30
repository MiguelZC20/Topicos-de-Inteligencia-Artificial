import json
from pathlib import Path

import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.metrics import confusion_matrix, classification_report


# Configuración general para el entrenamiento
DATA_DIR = Path("data/processed")
TRAIN_DIR = DATA_DIR / "train"
VAL_DIR = DATA_DIR / "val"
TEST_DIR = DATA_DIR / "test"
LABELS_PATH = DATA_DIR / "labels.json"

IMG_SIZE = (160, 160)
BATCH_SIZE = 8
EPOCHS_HEAD = 15
EPOCHS_FINE = 10
SEED = 42

MODELS_DIR = Path("models")
REPORTS_DIR = Path("reports")
MODELS_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

BEST_MODEL_PATH = MODELS_DIR / "best_model.keras"
FINAL_MODEL_PATH = MODELS_DIR / "final_model.keras"


# Carga de las etiquetas
# alumno_01 --> 0
# alumno_02 --> 1
with open(LABELS_PATH, "r", encoding="utf-8") as f:
    labels = json.load(f)

class_names = sorted(labels.keys(), key=lambda x: labels[x])
num_classes = len(class_names)

print(f"Clases detectadas: {num_classes}")
print(class_names)


"""
    Creación de datasets
        - TensorFlow carga automaticamente las imagenes desde las carpetas train, val y test.
        - Se generan tres conjuntos (entrenamiento, validación y pruebas).
        - Se redimensionan las imagenes y las etiquetas se representan como enteros.
"""
train_ds = tf.keras.utils.image_dataset_from_directory(
    TRAIN_DIR,
    labels="inferred",
    label_mode="int",
    class_names=class_names,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=True,
    seed=SEED
)

val_ds = tf.keras.utils.image_dataset_from_directory(
    VAL_DIR,
    labels="inferred",
    label_mode="int",
    class_names=class_names,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=False
)

test_ds = tf.keras.utils.image_dataset_from_directory(
    TEST_DIR,
    labels="inferred",
    label_mode="int",
    class_names=class_names,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=False
)

# Optimizacion para reducir tiempos de entrenamiento
# Preparar las siguientes imagenes mientras se procesan las actuales
AUTOTUNE = tf.data.AUTOTUNE
train_ds = train_ds.cache().prefetch(AUTOTUNE)
val_ds = val_ds.cache().prefetch(AUTOTUNE)
test_ds = test_ds.cache().prefetch(AUTOTUNE)


"""
    DATA AUGMENTATION
        - Se generan transformaciones aleatorias durante el entrenamiento.
        - RandomFlip: cambios de orientacion en el rostro.
        - RandomRotation: rotaciones para simular inclinaciones.
        - RandomZoom: acercamientos y alejamientos.
        - RandomContrast: cambios de iluminacion.
"""
data_augmentation = tf.keras.Sequential([
    tf.keras.layers.RandomFlip("horizontal"),
    tf.keras.layers.RandomRotation(0.05),
    tf.keras.layers.RandomZoom(0.10),
    tf.keras.layers.RandomContrast(0.10),
], name="data_augmentation")


"""
    Modelo base (Transfer Learning)
        - MobileNetV2 preentrenada sobre ImageNet.
            - menor tiempo de entrenamiento.
            - menor cantidad de datos requeridos.
"""
base_model = tf.keras.applications.MobileNetV2(
    input_shape=IMG_SIZE + (3,),
    include_top=False,
    weights="imagenet"
)

# Congelar capas convolucionales de MobileNetV2
# para entrenar el clasificador final
base_model.trainable = False


# Construcción del modelo
inputs = tf.keras.Input(shape=IMG_SIZE + (3,))
x = data_augmentation(inputs)
x = tf.keras.applications.mobilenet_v2.preprocess_input(x)
x = base_model(x, training=False)
x = tf.keras.layers.GlobalAveragePooling2D()(x)
x = tf.keras.layers.Dropout(0.35)(x)
outputs = tf.keras.layers.Dense(num_classes, activation="softmax")(x)

model = tf.keras.Model(inputs, outputs)

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

model.summary()


callbacks = [
    tf.keras.callbacks.EarlyStopping(   # Detener si la validacion deja de mejorar
        monitor="val_accuracy",
        patience=5,
        restore_best_weights=True
    ),
    tf.keras.callbacks.ModelCheckpoint( # Guardar el mejor modelo encontrado
        filepath=BEST_MODEL_PATH,
        monitor="val_accuracy",
        save_best_only=True
    )
]


"""
    Fase 1: Entrenamiento inicial
        - MobileNetV2 permanece congelada.
        - Se adapta el clasificador a los alumnos del dataset
"""
print("\nEntrenamiento inicial: base congelada ")
history_head = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=EPOCHS_HEAD,
    callbacks=callbacks
)


"""
    Fase 2: Fine-tuning: 
        - Se descongelan las ultimas capas de MobileNetV2 
        - para especializar en caracteristicas faciales
"""
print("\nFine-tuning: últimas capas de MobileNetV2 ")

base_model.trainable = True

fine_tune_at = len(base_model.layers) - 40

for layer in base_model.layers[:fine_tune_at]:
    layer.trainable = False

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

history_fine = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=EPOCHS_FINE,
    callbacks=callbacks
)

# Guardar el modelo final
model.save(FINAL_MODEL_PATH)
print(f"\nModelo final guardado en: {FINAL_MODEL_PATH}")

# Evaluacion final con el conjunto de pruebas
print("\nEvaluación en conjunto TEST ")
test_loss, test_acc = model.evaluate(test_ds)
print(f"Test loss: {test_loss:.4f}")
print(f"Test accuracy: {test_acc:.4f}")


# Generar predicciones sobre cada imagen del conjunto de pruebas
y_true = []
y_pred = []

for images, labels_batch in test_ds:
    predictions = model.predict(images, verbose=0)
    y_true.extend(labels_batch.numpy())
    y_pred.extend(np.argmax(predictions, axis=1))

y_true = np.array(y_true)
y_pred = np.array(y_pred)


# Reporte de clasificacion
report = classification_report(
    y_true,
    y_pred,
    target_names=class_names,
    zero_division=0
)

print("\n=== Reporte de clasificacion ===")
print(report)

with open(REPORTS_DIR / "classification_report.txt", "w", encoding="utf-8") as f:
    f.write(report)


# Matriz de confusion
# Permite visualizar clasificaciones correctas y confusiones entre alumnos
cm = confusion_matrix(y_true, y_pred)

plt.figure(figsize=(12, 10))
sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=class_names,
    yticklabels=class_names
)
plt.xlabel("Prediccion")
plt.ylabel("Clase real")
plt.title("Matriz de confusion")
plt.tight_layout()
plt.savefig(REPORTS_DIR / "confusion_matrix.png")
plt.close()

print(f"Matriz de confusion guardada en: {REPORTS_DIR / 'confusion_matrix.png'}")


# Curvas de entrenamiento
# Visualizar la evolucion de accuracy y loss durante todo el proceso
acc = history_head.history["accuracy"] + history_fine.history["accuracy"]
val_acc = history_head.history["val_accuracy"] + history_fine.history["val_accuracy"]
loss = history_head.history["loss"] + history_fine.history["loss"]
val_loss = history_head.history["val_loss"] + history_fine.history["val_loss"]

plt.figure(figsize=(10, 6))
plt.plot(acc, label="Train accuracy")
plt.plot(val_acc, label="Validation accuracy")
plt.xlabel("Epoca")
plt.ylabel("Accuracy")
plt.title("Accuracy durante entrenamiento")
plt.legend()
plt.tight_layout()
plt.savefig(REPORTS_DIR / "accuracy_curve.png")
plt.close()

plt.figure(figsize=(10, 6))
plt.plot(loss, label="Train loss")
plt.plot(val_loss, label="Validation loss")
plt.xlabel("Epoca")
plt.ylabel("Loss")
plt.title("Loss durante entrenamiento")
plt.legend()
plt.tight_layout()
plt.savefig(REPORTS_DIR / "loss_curve.png")
plt.close()

print(f"Graficas guardadas en: {REPORTS_DIR.resolve()}")
print("\nEntrenamiento terminado")