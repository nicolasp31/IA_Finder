# gui.py


import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QFileDialog, QVBoxLayout, QHBoxLayout,
    QTextEdit, QTableWidget, QTableWidgetItem, QTabWidget, QMenuBar, QProgressBar, QDialog
)
from PyQt6.QtGui import QFont, QAction
from PyQt6.QtCore import Qt
from Worker import HiloMetadata

class DetectorImagenIA(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Detector de archivos generados por IA")
        self.setFixedSize(1000, 680)
        # Layout principal horizontal
        layout_principal = QHBoxLayout()
        # Menú superior
        self.barra_menu = QMenuBar()
        self.inicializar_menu()
        # Layout vertical que contiene menú + contenido
        layout_vertical = QVBoxLayout()
        layout_vertical.setMenuBar(self.barra_menu)
        layout_vertical.addLayout(layout_principal)
        self.setLayout(layout_vertical)
        # Panel izquierdo con pestañas
        self.pestanas = QTabWidget()
        self.pestanas.setFixedWidth(300)
        layout_principal.addWidget(self.pestanas)
        self.inicializar_pestanas()
        # Panel derecho (análisis IA)
        self.panel_derecho = QWidget()
        layout_derecho = QVBoxLayout()
        layout_derecho.setContentsMargins(15, 15, 15, 15)
        layout_derecho.setSpacing(15)
        self.panel_derecho.setLayout(layout_derecho)
        layout_principal.addWidget(self.panel_derecho)
        # Título de análisis
        self.titulo_analisis = QLabel("Análisis de Archivo")
        self.titulo_analisis.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout_derecho.addWidget(self.titulo_analisis, alignment=Qt.AlignmentFlag.AlignLeft)
        # Barra de progreso
        self.barra_progreso = QProgressBar()
        self.barra_progreso.setMinimum(0)
        self.barra_progreso.setMaximum(100)
        self.barra_progreso.hide()
        layout_derecho.addWidget(self.barra_progreso)
        # Estado de análisis
        self.estado_analisis = QLabel("Selecciona un archivo para iniciar el análisis")
        self.estado_analisis.setFont(QFont("Arial", 11))
        layout_derecho.addWidget(self.estado_analisis)
        # Icono resultado
        self.icono_resultado = QLabel()
        self.icono_resultado.setFixedSize(64, 64)
        layout_derecho.addWidget(self.icono_resultado, alignment=Qt.AlignmentFlag.AlignLeft)
        # Texto resultado
        self.texto_resultado = QLabel("")
        self.texto_resultado.setFont(QFont("Arial", 12))
        self.texto_resultado.setWordWrap(True)
        layout_derecho.addWidget(self.texto_resultado)
        # Botón ver metadata completa
        self.boton_ver_metadata = QPushButton("< Ver metadata completa")
        self.boton_ver_metadata.setEnabled(False)
        self.boton_ver_metadata.clicked.connect(self.mostrar_metadata_completa)
        layout_derecho.addWidget(self.boton_ver_metadata, alignment=Qt.AlignmentFlag.AlignLeft)
        # Variables de control
        self.metadata_completa = None
        self._ventana_metadata = None  # Para mantener referencia de QDialog
        self.hilo = None  # Hilo de análisis en curso

    def inicializar_menu(self):
        menu_archivo = self.barra_menu.addMenu("Archivo")
        accion_abrir = QAction("Abrir", self)
        accion_abrir.triggered.connect(self.seleccionar_archivo)
        accion_salir = QAction("Salir", self)
        accion_salir.setShortcut("Ctrl+Q")
        accion_salir.triggered.connect(QApplication.instance().quit)
        menu_archivo.addAction(accion_abrir)
        menu_archivo.addSeparator()
        menu_archivo.addAction(accion_salir)

        menu_escaneo = self.barra_menu.addMenu("Escaneo")
        menu_escaneo.addAction("Escaneo rápido")
        menu_escaneo.addAction("Escaneo profundo")
        menu_escaneo.addSeparator()
        menu_escaneo.addAction("Escanear múltiples archivos")
        menu_escaneo.addAction("Ver resultados recientes")

    def inicializar_pestanas(self):
        widget_ia = QWidget()
        layout_ia = QVBoxLayout()
        layout_ia.setContentsMargins(10, 10, 10, 10)
        layout_ia.setSpacing(10)
        widget_ia.setLayout(layout_ia)
        self.boton_seleccionar = QPushButton("Seleccionar archivo")
        self.boton_seleccionar.clicked.connect(self.seleccionar_archivo)
        layout_ia.addWidget(self.boton_seleccionar)
        etiqueta_metadata = QLabel("Metadata extraída")
        etiqueta_metadata.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout_ia.addWidget(etiqueta_metadata)
        self.tabla_metadata = QTableWidget(0, 2)
        self.tabla_metadata.setHorizontalHeaderLabels(["Campo", "Valor"])
        self.tabla_metadata.verticalHeader().setVisible(False)
        self.tabla_metadata.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_metadata.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.tabla_metadata.setFixedHeight(150)
        self.tabla_metadata.horizontalHeader().setStretchLastSection(True)
        layout_ia.addWidget(self.tabla_metadata)
        self.pestanas.addTab(widget_ia, "Detector de IA")
        self.pestanas.addTab(QWidget(), "Archivos")
        self.pestanas.addTab(QWidget(), "Escaneo")
        self.pestanas.addTab(QWidget(), "Acerca de")

    def seleccionar_archivo(self):
        ruta_archivo, _ = QFileDialog.getOpenFileName(
            self,
            "Selecciona un archivo",
            "",
            "Archivos soportados (*.png *.jpg *.jpeg *.mp4 *.docx *.pdf *.xlsx *.pptx)"
        )
        if ruta_archivo:
            self.estado_analisis.setText("Analizando metadata...")
            self.barra_progreso.setValue(0)
            self.barra_progreso.show()
            self.icono_resultado.clear()
            self.texto_resultado.clear()
            self.boton_ver_metadata.setEnabled(False)
            self.hilo = HiloMetadata(ruta_archivo)
            self.hilo.progreso.connect(self.barra_progreso.setValue)
            self.hilo.terminado.connect(self.finalizar_analisis)
            self.hilo.error.connect(self.manejar_error)
            self.hilo.start()

    def finalizar_analisis(self, metadata, es_ia, mensaje, aplicacion, modelo):
        self.metadata_completa = metadata
        self.llenar_tabla_metadata(metadata)
        self.estado_analisis.setText("")
    
        if es_ia is True:
            self.icono_resultado.setText("❌")
            texto = f"<b>Resultado de análisis:</b> Archivo generado por IA<br>"
            texto += f"La aplicación con la que fue generado el archivo fue: {', '.join(aplicacion) if isinstance(aplicacion, list) else aplicacion}<br>"
            texto += f"El modelo de IA usado fue: {modelo if modelo != 'Desconocido' else 'No se pudo determinar el modelo exacto'}<br>"
        
        elif es_ia is None:
            self.icono_resultado.setText("⚠️")
            texto = f"<b>Resultado de análisis:</b> Posible generación por IA (no confirmado)<br>"
            texto += f"Se cree que el archivo pudo ser generado por: {', '.join(aplicacion) if isinstance(aplicacion, list) else aplicacion}<br>"
            texto += f"Se cree que el modelo de IA usado fue: {modelo if modelo != 'Desconocido' else 'No se pudo determinar el modelo'}<br>"
        
        else:  # es_ia False
            self.icono_resultado.setText("✅")
            texto = "<b>Resultado de análisis:</b> Archivo genuino<br><b>0% IA detectada</b><br>"
            texto += "No se detectó la aplicación con la que fue generado el archivo<br>"
            texto += "No se encontró modelo de IA generativa<br>"

         # clave para interpretar <br> como salto de línea
        self.texto_resultado.setText(f"{texto}<br>{mensaje}")
        self.boton_ver_metadata.setEnabled(True)


    def manejar_error(self, error):
        self.barra_progreso.hide()
        self.estado_analisis.setText(f"⚠️ Error: {error}")

    def llenar_tabla_metadata(self, metadata):
        self.tabla_metadata.setRowCount(0)
        nombre = os.path.basename(metadata.get("SourceFile", "Desconocido"))
        tipo = metadata.get("FileType", metadata.get("MIMEType", "Desconocido"))
        tamano = metadata.get("FileSize", "Desconocido")
        fecha = metadata.get("ModifyDate", metadata.get("DateTimeOriginal", "Desconocida"))
        items = [("Nombre", nombre), ("Tipo", tipo), ("Tamaño", str(tamano)), ("Fecha modificado", fecha)]
        for campo, valor in items:
            fila = self.tabla_metadata.rowCount()
            self.tabla_metadata.insertRow(fila)
            self.tabla_metadata.setItem(fila, 0, QTableWidgetItem(campo))
            self.tabla_metadata.setItem(fila, 1, QTableWidgetItem(str(valor)))

    def mostrar_metadata_completa(self):
        if self.metadata_completa:
            from pprint import pformat
            metadata_str = pformat(self.metadata_completa, indent=2, width=80)
            self._ventana_metadata = QDialog(self)
            self._ventana_metadata.setWindowTitle("Metadata completa")
            self._ventana_metadata.setFixedSize(600, 400)
            layout = QVBoxLayout()
            txt = QTextEdit()
            txt.setPlainText(metadata_str)
            txt.setReadOnly(True)
            layout.addWidget(txt)
            self._ventana_metadata.setLayout(layout)
            self._ventana_metadata.exec()
