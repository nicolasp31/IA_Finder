import sys
import subprocess
import json
import shutil
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QFileDialog, QVBoxLayout, QHBoxLayout,
    QTextEdit, QTableWidget, QTableWidgetItem, QTabWidget, QMenuBar, QMenu, QProgressBar
)
from PyQt6.QtGui import QFont, QAction, QPalette, QColor
from PyQt6.QtCore import Qt

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

    result = subprocess.run(
        ["exiftool", "-json", image_path],
        capture_output=True, text=True, check=True
    )
    metadata = json.loads(result.stdout)[0]
    return metadata

class IAImageChecker(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Detector de Imágenes con IA")
        self.setFixedSize(800, 480)

        # Layout principal horizontal
        main_layout = QHBoxLayout()

        # Menú superior
        self.menu_bar = QMenuBar()
        self.init_menu()
        # Para mostrar menu_bar encima, usar layout vertical principal
        main_vertical = QVBoxLayout()
        main_vertical.setMenuBar(self.menu_bar)
        main_vertical.addLayout(main_layout)
        self.setLayout(main_vertical)
        
        # Panel izquierdo
        self.tabs = QTabWidget()
        self.tabs.setFixedWidth(300)
        main_layout.addWidget(self.tabs)

        # Añadimos pestañas a tabs
        self.init_left_tabs()

        # Panel derecho (análisis IA)
        self.right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(15, 15, 15, 15)
        right_layout.setSpacing(15)
        self.right_panel.setLayout(right_layout)
        main_layout.addWidget(self.right_panel)

        # Título IA analysis
        self.analysis_title = QLabel("IA analysis")
        self.analysis_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        right_layout.addWidget(self.analysis_title, alignment=Qt.AlignmentFlag.AlignLeft)

        # Barra de progreso determinada
        self.progress = QProgressBar()
        self.progress.setMinimum(0)
        self.progress.setMaximum(100)
        self.progress.hide()  # Oculto inicialmente
        right_layout.addWidget(self.progress)

        self.analysis_status = QLabel("Selecciona un archivo para iniciar el análisis")
        self.analysis_status.setFont(QFont("Arial", 11))
        right_layout.addWidget(self.analysis_status)

        # Icono resultado (check verde o cruz rojo)
        self.result_icon = QLabel()
        self.result_icon.setFixedSize(64, 64)
        right_layout.addWidget(self.result_icon, alignment=Qt.AlignmentFlag.AlignLeft)

        # Texto resultado final
        self.result_text = QLabel("")
        self.result_text.setFont(QFont("Arial", 12))
        self.result_text.setWordWrap(True)
        right_layout.addWidget(self.result_text)

        # Botón ver metadata completa
        self.view_metadata_button = QPushButton("< View complete metadata")
        self.view_metadata_button.setEnabled(False)
        self.view_metadata_button.clicked.connect(self.show_full_metadata)
        right_layout.addWidget(self.view_metadata_button, alignment=Qt.AlignmentFlag.AlignLeft)

        self.full_metadata = None  # Para almacenar metadata completa

    def init_menu(self):
        # Menú Archive
        menu_archive = self.menu_bar.addMenu("Archive")

        open_action = QAction("Open", self)
        open_action.triggered.connect(self.select_image)
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(QApplication.instance().quit)

        menu_archive.addAction(open_action)
        menu_archive.addSeparator()
        menu_archive.addAction(exit_action)

        # Menú Scanning
        menu_scanning = self.menu_bar.addMenu("Scanning")
        menu_scanning.addAction("Quick scanning")
        menu_scanning.addAction("Deep scanning")
        menu_scanning.addSeparator()
        menu_scanning.addAction("Scan multiple files")
        menu_scanning.addAction("View recent results")

    def init_left_tabs(self):
        # Pestaña IA Finder
        ia_finder_widget = QWidget()
        ia_layout = QVBoxLayout()
        ia_layout.setContentsMargins(10, 10, 10, 10)
        ia_layout.setSpacing(10)
        ia_finder_widget.setLayout(ia_layout)

        # Botón seleccionar archivo
        self.select_file_button = QPushButton("Select archive")
        self.select_file_button.clicked.connect(self.select_image)
        ia_layout.addWidget(self.select_file_button)

        # Etiqueta pequeña extra: Extracted metadata
        self.label_metadata_header = QLabel("Extracted metadata")
        self.label_metadata_header.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        ia_layout.addWidget(self.label_metadata_header)

        # Tabla con metadatos extraídos
        self.metadata_table = QTableWidget(0, 2)
        self.metadata_table.setHorizontalHeaderLabels(["Field", "Value"])
        self.metadata_table.verticalHeader().setVisible(False)
        self.metadata_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.metadata_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.metadata_table.setFixedHeight(150)
        self.metadata_table.horizontalHeader().setStretchLastSection(True)
        ia_layout.addWidget(self.metadata_table)

        # Añadir tabs
        self.tabs.addTab(ia_finder_widget, "IA Finder")
        self.tabs.addTab(QWidget(), "Archive")
        self.tabs.addTab(QWidget(), "Escaneo")
        self.tabs.addTab(QWidget(), "About")

    def select_image(self):
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Selecciona una imagen",
            "",
            "Archivos de imagen (*.png *.jpg *.jpeg *.webp *.gif)"
        )
        if file_path:
            self.analysis_status.setText("Analyzing metadata...")
            self.progress.setValue(10)
            self.progress.show()
            self.result_icon.clear()
            self.result_text.clear()
            self.view_metadata_button.setEnabled(False)
            QApplication.processEvents()

            try:
                metadata = get_metadata_with_exiftool(file_path)
                self.full_metadata = metadata
                self.fill_metadata_table(metadata)
                self.progress.setValue(60)

                is_ai, message = check_ai_generated(metadata)
                self.progress.setValue(100)
                self.analysis_status.setText("")

                # Mostrar icono y texto resultado
                self.result_icon.setText("❌" if is_ai else "✅")

                # Mostrar texto resumen
                if is_ai:
                    status_text = "<b>Archive status:</b> Suspected AI generated"
                else:
                    status_text = "<b>Archive status:</b> Genuine archive"
                self.result_text.setText(
                    f"{status_text}<br>{message}<br><br><b>0% IA</b>" if not is_ai else f"{status_text}<br>{message}"
                )
                self.view_metadata_button.setEnabled(True)
            except FileNotFoundError as fnf_error:
                self.progress.hide()
                self.analysis_status.setText(f"⚠️ {fnf_error}")
            except Exception as err:
                self.progress.hide()
                self.analysis_status.setText(f"Error al leer metadata: {err}")

    def fill_metadata_table(self, metadata):
        self.metadata_table.setRowCount(0)
        import os
        filename = os.path.basename(metadata.get("SourceFile", "Unknown"))
        file_type = metadata.get("FileType", metadata.get("MIMEType", "Unknown"))
        file_size = metadata.get("FileSize", "Unknown")
        date_modified = metadata.get("ModifyDate", metadata.get("DateTimeOriginal", "Unknown"))

        items = [
            ("Name", filename),
            ("Type", file_type),
            ("Size", str(file_size)),
            ("Modified date", date_modified)
        ]
        for field, value in items:
            row = self.metadata_table.rowCount()
            self.metadata_table.insertRow(row)
            self.metadata_table.setItem(row, 0, QTableWidgetItem(field))
            self.metadata_table.setItem(row, 1, QTableWidgetItem(str(value)))

    def show_full_metadata(self):
        if self.full_metadata:
            import pprint
            metadata_str = pprint.pformat(self.full_metadata, indent=2, width=80)
            dlg = QWidget()
            dlg.setWindowTitle("Complete metadata")
            dlg.setFixedSize(600, 400)
            layout = QVBoxLayout()
            txt = QTextEdit()
            txt.setPlainText(metadata_str)
            txt.setReadOnly(True)
            layout.addWidget(txt)
            dlg.setLayout(layout)
            dlg.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            dlg.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 🌙 Activar modo oscuro
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
    dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(142, 45, 197))
    dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)

    app.setPalette(dark_palette)
    app.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: none; }")

    window = IAImageChecker()
    window.show()
    sys.exit(app.exec())
