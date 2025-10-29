import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt, QTimer
from Gui import DetectorArchivoGUI
from pantalla_carga import pantallaCarga  # <-- Asumiendo que defines el splash en Splash.py, o pones aquí la clase

def main():
    app = QApplication(sys.argv)

    # Tema oscuro
    paleta_oscura = QPalette()
    paleta_oscura.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    paleta_oscura.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    paleta_oscura.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
    paleta_oscura.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    paleta_oscura.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    paleta_oscura.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    paleta_oscura.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    paleta_oscura.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    paleta_oscura.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    paleta_oscura.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    paleta_oscura.setColor(QPalette.ColorRole.Highlight, QColor(142, 45, 197))
    paleta_oscura.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    app.setPalette(paleta_oscura)
    app.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: none; }")

    # Mostrar pantalla de carga
    Carga = pantallaCarga()
    Carga.show()

    # Mostrar ventana principal después del splash
    def lanzar_principal():
        ventana = DetectorArchivoGUI()
        ventana.show()
        Carga.close()

    QTimer.singleShot(2200, lanzar_principal)  # Tiempo de splash en milisegundos

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
