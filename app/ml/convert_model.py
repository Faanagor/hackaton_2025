"""
Script para descargar, convertir y preparar MobileFaceNet para Android.

EJECUTAR UNA SOLA VEZ antes de empezar con Android.
"""

import tensorflow as tf
import numpy as np
import urllib.request
import os

# ============================================
# PASO 1: Descargar modelo pre-entrenado
# ============================================

print("📥 Descargando MobileFaceNet pre-entrenado...")

# Modelo pre-entrenado de GitHub
MODEL_URL = "https://github.com/sirius-ai/MobileFaceNet_TF/raw/master/output/MobileFaceNet_9925_9680.pb"
MODEL_PATH = "mobilefacenet.pb"

if not os.path.exists(MODEL_PATH):
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    print(f"✅ Modelo descargado: {MODEL_PATH}")
else:
    print(f"✅ Modelo ya existe: {MODEL_PATH}")

# ============================================
# PASO 2: Cargar modelo
# ============================================

print("\n📂 Cargando modelo...")


def load_graph(frozen_graph_filename):
    """Carga un grafo de TensorFlow desde archivo .pb"""
    with tf.io.gfile.GFile(frozen_graph_filename, "rb") as f:
        graph_def = tf.compat.v1.GraphDef()
        graph_def.ParseFromString(f.read())

    with tf.Graph().as_default() as graph:
        tf.import_graph_def(graph_def, name="")

    return graph


graph = load_graph(MODEL_PATH)

# Obtener tensores de entrada y salida
input_tensor = graph.get_tensor_by_name("input:0")
output_tensor = graph.get_tensor_by_name("embeddings:0")

print("✅ Modelo cargado")
print(f"   Input shape: {input_tensor.shape}")  # (None, 112, 112, 3)
print(f"   Output shape: {output_tensor.shape}")  # (None, 128)

# ============================================
# PASO 3: Convertir a TensorFlow Lite
# ============================================

print("\n🔧 Convirtiendo a TensorFlow Lite...")

# Convertir usando TF 1.x compatibility
converter = tf.compat.v1.lite.TFLiteConverter.from_frozen_graph(
    graph_def_file=MODEL_PATH,
    input_arrays=["input"],
    output_arrays=["embeddings"],
    input_shapes={"input": [1, 112, 112, 3]},
)

# Optimizaciones para reducir tamaño y aumentar velocidad
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.target_spec.supported_types = [tf.float16]  # Usar float16

# Convertir
tflite_model = converter.convert()

# Guardar modelo .tflite
TFLITE_PATH = "mobilefacenet.tflite"
with open(TFLITE_PATH, "wb") as f:
    f.write(tflite_model)

print(f"✅ Modelo TFLite guardado: {TFLITE_PATH}")
print(f"   Tamaño: {len(tflite_model) / 1024 / 1024:.2f} MB")

# ============================================
# PASO 4: Probar el modelo TFLite
# ============================================

print("\n🧪 Probando modelo TFLite...")

# Crear intérprete
interpreter = tf.lite.Interpreter(model_path=TFLITE_PATH)
interpreter.allocate_tensors()

# Obtener detalles de entrada/salida
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

print("✅ Detalles del modelo:")
print(f"   Input shape: {input_details[0]['shape']}")
print(f"   Output shape: {output_details[0]['shape']}")

# Crear imagen de prueba (rostro ficticio)
test_image = np.random.rand(1, 112, 112, 3).astype(np.float32)

# Normalizar (igual que en producción)
test_image = (test_image - 127.5) / 127.5

# Ejecutar inferencia
interpreter.set_tensor(input_details[0]["index"], test_image)
interpreter.invoke()
embedding = interpreter.get_tensor(output_details[0]["index"])

print("✅ Inferencia exitosa!")
print(f"   Embedding shape: {embedding.shape}")  # (1, 128)
print(f"   Primeros 5 valores: {embedding[0][:5]}")

# ============================================
# PASO 5: Crear script de prueba
# ============================================

print("\n📝 Creando script de prueba...")

TEST_SCRIPT = """
import tensorflow as tf
import numpy as np

# Cargar modelo
interpreter = tf.lite.Interpreter(model_path="mobilefacenet.tflite")
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

def extract_embedding(image_array):
    '''
    Extrae embedding de una imagen.
    
    Args:
        image_array: numpy array (112, 112, 3) con valores 0-255
    
    Returns:
        embedding: numpy array (128,) con el vector facial
    '''
    # Normalizar
    image_normalized = (image_array - 127.5) / 127.5
    image_normalized = np.expand_dims(image_normalized, axis=0).astype(np.float32)
    
    # Inferencia
    interpreter.set_tensor(input_details[0]['index'], image_normalized)
    interpreter.invoke()
    embedding = interpreter.get_tensor(output_details[0]['index'])
    
    return embedding[0]

# Ejemplo de uso
if __name__ == "__main__":
    # Crear imagen de prueba
    test_img = np.random.randint(0, 255, (112, 112, 3), dtype=np.uint8)
    
    # Extraer embedding
    emb = extract_embedding(test_img)
    
    print(f"Embedding shape: {emb.shape}")
    print(f"Embedding (primeros 10): {emb[:10]}")
"""

with open("test_model.py", "w") as f:
    f.write(TEST_SCRIPT)

print("✅ Script de prueba creado: test_model.py")

print("\n" + "=" * 50)
print("✨ ¡CONVERSIÓN COMPLETA!")
print("=" * 50)
print(f"\n📱 Copia el archivo '{TFLITE_PATH}' a tu proyecto Android:")
print(f"   Android/app/src/main/assets/{TFLITE_PATH}")
print("\n🎯 Ahora puedes usar el modelo en Android con TFLite Interpreter")
