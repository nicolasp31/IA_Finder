import os
import sys
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget, QHBoxLayout, QGraphicsDropShadowEffect
from PyQt6.QtGui import QPixmap, QFont, QColor
from PyQt6.QtCore import Qt, QTimer

class pantallaCarga(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(900, 680)
        self.setStyleSheet("background-color: #222222;")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Título principal
        bienvenida = QLabel("DETECTOR DE IA")
        bienvenida.setFont(QFont("Arial", 72, QFont.Weight.Bold))
        bienvenida.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bienvenida.setStyleSheet("""
            color: #60FF9F;
            letter-spacing: 1px;
        """)
        sombra1 = QGraphicsDropShadowEffect()
        sombra1.setColor(QColor(30, 30, 30))
        sombra1.setOffset(0, 3)
        sombra1.setBlurRadius(12)
        bienvenida.setGraphicsEffect(sombra1)
        layout.addWidget(bienvenida)

        layout.addSpacing(50)

        # Sub-layout para el texto de crédito y el logo
        sub_layout = QHBoxLayout()
        sub_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Mensaje de reconocimiento a ExifTool
        powered = QLabel("Desarrollado con EXIFTOOL by Phil Harvey")
        powered.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        powered.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        powered.setStyleSheet("color: #fff; letter-spacing: 1px;")

        sombra2 = QGraphicsDropShadowEffect()
        sombra2.setColor(QColor(50, 50, 50))
        sombra2.setOffset(0, 2)
        sombra2.setBlurRadius(7)
        powered.setGraphicsEffect(sombra2)

        # Logo de ExifTool
        logo = QLabel()
        logo.setFixedSize(40, 40)
        logo.setStyleSheet("background-color: white; border-radius: 4px;")

        # --- Detectar ruta real del icono ---
        if hasattr(sys, "_MEIPASS"):
            base_path = sys._MEIPASS  # Carpeta temporal cuando está empaquetado
        else:
            base_path = os.path.abspath(".")

        icon_path = os.path.join(base_path, "exiftool.ico")

        # Cargar icono si existe
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            pixmap = pixmap.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo.setPixmap(pixmap)
        else:
            print(f"No se encontró el icono en: {icon_path}")

        # Agregar al layout
        sub_layout.addWidget(powered)
        sub_layout.addSpacing(15)
        sub_layout.addWidget(logo)
        layout.addLayout(sub_layout)

# --- Función para mostrar pantalla de carga ---
def mostrar_pantallaCarga(app, tiempo=2000):
    splash = pantallaCarga()
    splash.show()
    splash.showMaximized()
    app.processEvents()
    QTimer.singleShot(tiempo, splash.close)
    return splash
