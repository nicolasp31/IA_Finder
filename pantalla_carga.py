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

        # Nombre aplicacion
        bienvenida = QLabel("DETECTOR DE IA")
        bienvenida.setFont(QFont("Arial", 72, QFont.Weight.Bold))
        bienvenida.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bienvenida.setStyleSheet("""
            color: #60FF9F;
            letter-spacing: 1px;
        """)
        sombra1 = QGraphicsDropShadowEffect()
        sombra1.setColor(QColor(30,30,30))
        sombra1.setOffset(0, 3)
        sombra1.setBlurRadius(12)
        bienvenida.setGraphicsEffect(sombra1)
        layout.addWidget(bienvenida)

        layout.addSpacing(50)

        # HBox para logo + mensaje
        sub_layout = QHBoxLayout()
        sub_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Mensaje reconocimiento exifftool
        powered = QLabel("Desarrolado con EXIFTOOL by Phil Harvey")
        powered.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        powered.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        powered.setStyleSheet("color: #fff; letter-spacing: 1px;")

        sombra2 = QGraphicsDropShadowEffect()
        sombra2.setColor(QColor(50,50,50))
        sombra2.setOffset(0, 2)
        sombra2.setBlurRadius(7)
        powered.setGraphicsEffect(sombra2)

        # Logo exiftool
        logo = QLabel()
        logo.setFixedSize(40, 40)
        logo.setStyleSheet("background-color: white; border-radius: 4px;") 
        pixmap = QPixmap("exiftool.png")
        pixmap = pixmap.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        logo.setPixmap(pixmap)


        sub_layout.addWidget(powered)
        sub_layout.addSpacing(15)
        sub_layout.addWidget(logo)
        layout.addLayout(sub_layout)

#funcion para mostrar la pantalla de carga
def mostrar_pantallaCarga(app, tiempo=2000):
    splash = pantallaCarga()
    splash.show()
    splash.showMaximized()
    app.processEvents()
    QTimer.singleShot(tiempo, splash.close)
    return splash
