from pathlib import Path
import tensorflow as tf

MODEL_PATH = Path("models/final_model.keras")
TFLITE_PATH = Path("models/model.tflite")

print("Cargando modelo:", MODEL_PATH)
model = tf.keras.models.load_model(MODEL_PATH)

converter = tf.lite.TFLiteConverter.from_keras_model(model)

# Optimización básica para móvil
converter.optimizations = [tf.lite.Optimize.DEFAULT]

tflite_model = converter.convert()

with open(TFLITE_PATH, "wb") as f:
    f.write(tflite_model)

print("Modelo TFLite guardado en:", TFLITE_PATH.resolve())
print("Tamaño:", round(TFLITE_PATH.stat().st_size / (1024 * 1024), 2), "MB")