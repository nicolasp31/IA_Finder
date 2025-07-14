import sys
import subprocess
import json
import shutil  # Para verificar si exiftool está disponible
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

def check_ai_generated(metadata):
    for key, value in metadata.items():
        value_str = str(value).lower()
        for keyword in IA_KEYWORDS:
            if keyword.lower() in value_str:
                return True, f"Patrón detectado en '{key}': {value}"
    return False, "No se encontraron patrones típicos de IA."

def get_metadata_with_exiftool(image_path):
    if shutil.which("exiftool") is None:
        raise FileNotFoundError(
            "ExifTool no está instalado o no se encuentra en el PATH del sistema."
        )

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
        self.setFixedSize(600, 400)

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
                is_ai, message = check_ai_generated(metadata)
                result = f"¿Imagen generada con IA? {'✅ Sí' if is_ai else '❌ No'}\n\n{message}"
                self.result_box.setText(result)
            except FileNotFoundError as fnf_error:
                self.result_box.setText(f"⚠️ {fnf_error}")
            except Exception as err:
                self.result_box.setText(f"Error al leer metadata: {err}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IAImageChecker()
    window.show()
    sys.exit(app.exec())
