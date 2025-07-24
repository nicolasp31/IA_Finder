import sys
import subprocess
import json
import shutil
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QFileDialog, QVBoxLayout, QTextEdit
)
from PyQt6.QtGui import QFont

# Palabras clave típicas de imágenes generadas con IA
IA_KEYWORDS = [
    "DALL·E", "Midjourney", "Stable Diffusion", "Wombo",
    "Generative", "AI", "Photoshop Beta", "Dream", "Runway",
    "CreatorTool=AI", "Generated"
]

# Rutas clave para rastros de IA generativa
IA_TRACE_URL = "http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia"

# Detección de modelos conocidos
MODEL_TAGS = {
    "GPT-4o": "GPT 4o (OPENIA)",
    "OpenAI API": "GPT 4o (OPENIA)",
    "Made with Google AI": "Google IA"
}

# Descripción por modelo
DESCRIPTION_TAGS = {
    "GPT-4o": "contenido generado mediante ChatGPT",
    "OpenAI API": "contenido generado mediante ChatGPT",
    "Made with Google AI": "contenido generado mediante Gemini"
}

def check_ai_generated(metadata):
    for key, value in metadata.items():
        value_str = str(value).lower()
        for keyword in IA_KEYWORDS:
            if keyword.lower() in value_str:
                return True, f"Patrón detectado en '{key}': {value}"
    return False, "No se encontraron patrones típicos de IA."

def analyze_metadata(metadata, file_path):
    result_lines = []

    # 1. EXTENSIÓN DEL ARCHIVO
    extension = os.path.splitext(file_path)[1].lower()
    result_lines.append(f"Extensión: {extension}")

    # 2. RASTRO DE IA GENERATIVA POR URL IPTC
    found_iptc = any(IA_TRACE_URL in str(value) for value in metadata.values())
    if found_iptc:
        result_lines.append("Generado por IA: ✅ Sí (rastro IPTC encontrado)")
    else:
        result_lines.append("Generado por IA: ❌ No se encontró rastro de IA generativa")

    # 3. MODELO GENERATIVO
    detected_model = None
    for key, value in metadata.items():
        value_str = str(value)
        for tag, label in MODEL_TAGS.items():
            if tag in value_str:
                detected_model = label
                break
        if detected_model:
            break

    if detected_model:
        result_lines.append(f"Modelo generativo: {detected_model}")
    else:
        result_lines.append("Modelo generativo: No se pudo encontrar el modelo en los metadatos")

    # 4. DESCRIPCIÓN
    description = None
    for key, value in metadata.items():
        value_str = str(value)
        for tag, desc in DESCRIPTION_TAGS.items():
            if tag in value_str:
                description = desc
                break
        if description:
            break

    if description:
        result_lines.append(f"Descripción: {description}")
    else:
        result_lines.append("Descripción: No se pudo determinar el origen del contenido")

    return "\n".join(result_lines)

def get_metadata_with_exiftool(image_path):
    if shutil.which("exiftool") is None:
        raise FileNotFoundError("ExifTool no está instalado o no se encuentra en el PATH del sistema.")

    try:
        result = subprocess.run(
            ["exiftool", "-json", image_path],
            capture_output=True, text=True, check=True
        )
        metadata = json.loads(result.stdout)[0]
        return metadata
    except subprocess.CalledProcessError as e:
        raise Exception(f"Error al ejecutar exiftool: {e}")

class IAImageChecker(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Detector de Imágenes con IA")
        self.setFixedSize(600, 450)

        layout = QVBoxLayout()

        self.title_label = QLabel("Sube una imagen para analizar si fue creada con IA")
        self.title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(self.title_label)

        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        layout.addWidget(self.result_box)

        self.upload_button = QPushButton("Seleccionar Imagen")
        self.upload_button.clicked.connect(self.select_image)
        layout.addWidget(self.upload_button)

        self.setLayout(layout)

    def select_image(self):
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Selecciona una imagen",
            "",
            "Archivos de imagen (*.png *.jpg *.jpeg *.webp)"
        )

        if file_path:
            self.result_box.setText("Analizando metadata...")
            QApplication.processEvents()

            try:
                metadata = get_metadata_with_exiftool(file_path)
                is_ai, ai_message = check_ai_generated(metadata)
                analysis_summary = analyze_metadata(metadata, file_path)

                final_output = f"¿Imagen generada con IA? {'✅ Sí' if is_ai else '❌ No'}\n{ai_message}\n\n{analysis_summary}"
                self.result_box.setText(final_output)

            except FileNotFoundError as fnf_error:
                self.result_box.setText(f"⚠️ {fnf_error}")
            except Exception as err:
                self.result_box.setText(f"Error al leer metadata: {err}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IAImageChecker()
    window.show()
    sys.exit(app.exec())