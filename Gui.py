# gui.py


import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QFileDialog, QVBoxLayout, QHBoxLayout,
    QTextEdit, QTableWidget, QTableWidgetItem, QTabWidget, QMenuBar, QProgressBar, QDialog ,  QMessageBox
)
from PyQt6.QtGui import QFont, QAction
from PyQt6.QtCore import Qt
from Worker import HiloMetadata
from metadata_analisis import verificar_archivo_ia


class DetectorArchivoIA(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Detector de archivos generados por IA")
        self.setFixedSize(1000, 680)
        # Layout principal horizontal
        layout_principal = QHBoxLayout()
        # Menú superior
        self.barra_menu = QMenuBar()
        self.inicializar_menu()
        self.aplicar_estilos_menu()
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

        accion_abrir = QAction("Abrir archivo", self)
        accion_abrir.triggered.connect(self.seleccionar_archivo)

        accion_abrir_carpeta = QAction("Abrir carpeta", self)
        accion_abrir_carpeta.triggered.connect(self.seleccionar_carpeta)

        accion_exportar = QAction("Exportar reporte", self)
        accion_exportar.triggered.connect(self.exportar_reporte)

        accion_salir = QAction("Salir", self)
        accion_salir.setShortcut("Ctrl+Q")
        accion_salir.triggered.connect(QApplication.instance().quit)

        menu_archivo.addAction(accion_abrir)
        menu_archivo.addAction(accion_abrir_carpeta)
        menu_archivo.addSeparator()
        menu_archivo.addAction(accion_exportar)
        menu_archivo.addSeparator()
        menu_archivo.addAction(accion_salir)

        # Menú Escaneo original sin cambio
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
        
    def aplicar_estilos_menu(self):
        self.barra_menu.setStyleSheet("""
            QMenuBar {
                background-color: #232323;
                color: white;
            }
            QMenuBar::item {
                background-color: #232323;
                color: white;
            }
            QMenuBar::item:selected {
                background-color: #444444;
                color: #FFD700;
            }
            QMenu {
                background-color: #232323;
                color: white;
                border: 1px solid #888888;
            }
            QMenu::item {
                background-color: #232323;
                color: white;
                padding: 6px 40px 6px 24px;
            }
            QMenu::item:selected {
                background-color: #444444;
                color: #FFD700;
            }
        """)
        
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
        if not self.metadata_completa:
            return

        # Detectar patrones usando tu función
        es_ia, mensaje = verificar_archivo_ia(self.metadata_completa)

        # Extraer claves de patrones detectados (máx 3)
        claves_resaltadas = set()
        if mensaje and es_ia is not False:
            for linea in mensaje.split('\n'):
                # Extrae el nombre del campo entre comillas simples
                inicio = linea.find("'") + 1
                fin = linea.find("'", inicio)
                if inicio > 0 and fin > inicio:
                    clave = linea[inicio:fin]
                    claves_resaltadas.add(clave)
                if len(claves_resaltadas) >= 3:
                    break

        # Generar la metadata en HTML con numeración y resaltado
        rows = []
        for idx, (k, v) in enumerate(self.metadata_completa.items(), start=1):
            if k in claves_resaltadas:
                # Resaltado: negrita y color rojo
                fila = f"<tr><td><b style='color:red;'>{idx}. {k}</b></td><td><b style='color:red;'>{v}</b></td></tr>"
            else:
                fila = f"<tr><td>{idx}. {k}</td><td>{v}</td></tr>"
            rows.append(fila)

        metadata_html = (
            "<table border='1' cellpadding='4' cellspacing='0'>"
            + "".join(rows)
            + "</table>"
        )

        self._ventana_metadata = QDialog(self)
        self._ventana_metadata.setWindowTitle("Metadata completa")
        self._ventana_metadata.setFixedSize(800, 600)
        layout = QVBoxLayout()
        txt = QTextEdit()
        txt.setHtml(metadata_html)
        txt.setReadOnly(True)
        layout.addWidget(txt)
        self._ventana_metadata.setLayout(layout)
        self._ventana_metadata.exec()

    def seleccionar_carpeta(self):
        ruta_carpeta = QFileDialog.getExistingDirectory(self, "Selecciona una carpeta")
        if ruta_carpeta:
            # Aquí puedes implementar la lógica para buscar y analizar archivos dentro de la carpeta
            QMessageBox.information(self, "Carpeta seleccionada", f"Carpeta seleccionada:\n{ruta_carpeta}")
        # Ejemplo: recorrer archivos y analizar uno a uno o mostrar una lista

    def exportar_reporte(self):
        if not self.metadata_completa:
            QMessageBox.warning(self, "Atención", "No hay metadata para exportar.")
            return

        # Detectar patrones usando la función existente
        es_ia, mensaje = verificar_archivo_ia(self.metadata_completa)

        claves_resaltadas = set()
        if mensaje and es_ia is not False:
            for linea in mensaje.split('\n'):
                inicio = linea.find("'") + 1
                fin = linea.find("'", inicio)
                if inicio > 0 and fin > inicio:
                    clave = linea[inicio:fin]
                    claves_resaltadas.add(clave)
                if len(claves_resaltadas) >= 3:
                    break

        # Preguntar ruta y tipo de archivo para guardar
        ruta_guardar, filtro = QFileDialog.getSaveFileName(
            self,
            "Guardar reporte de metadata",
            "reporte_metadata.html",
            "Archivo HTML (*.html);;Archivo CSV (*.csv)"
        )
        if not ruta_guardar:
            return  # Canceló la acción

        if filtro == "Archivo CSV (*.csv)" or ruta_guardar.lower().endswith(".csv"):
            # Guardar como CSV
            import csv
            with open(ruta_guardar, mode='w', newline='', encoding='utf-8') as archivo_csv:
                escritor = csv.writer(archivo_csv)
                escritor.writerow(["#", "Campo", "Valor", "Patrón Detectado"])
                for idx, (k, v) in enumerate(self.metadata_completa.items(), start=1):
                    resaltado = "Sí" if k in claves_resaltadas else "No"
                    escritor.writerow([idx, k, v, resaltado])

        else:
            # Guardar como HTML con formato y resaltado
            rows = []
            for idx, (k, v) in enumerate(self.metadata_completa.items(), start=1):
                if k in claves_resaltadas:
                    fila = f"<tr><td><b style='color:red;'>{idx}. {k}</b></td><td><b style='color:red;'>{v}</b></td></tr>"
                else:
                    fila = f"<tr><td>{idx}. {k}</td><td>{v}</td></tr>"
                rows.append(fila)

            metadata_html = (
                "<html><head><meta charset='utf-8'><style>"
                "table {border-collapse: collapse; width: 100%;}"
                "td, th {border: 1px solid #999; padding: 8px;}"
                "</style></head><body>"
                "<h2>Metadata completa</h2>"
                "<table>" + "".join(rows) + "</table>"
                "</body></html>"
            )

            with open(ruta_guardar, "w", encoding="utf-8") as f:
                f.write(metadata_html)

        QMessageBox.information(self, "Éxito", f"Reporte guardado en:\n{ruta_guardar}")


""""

    def mostrar_metadata_completa(self):
        if self.metadata_completa:
            from pprint import pformat
            metadata_str = pformat(self.metadata_completa, indent=2, width=80)
            self._ventana_metadata = QDialog(self)
            self._ventana_metadata.setWindowTitle("Metadata completa")
            self._ventana_metadata.setFixedSize(800, 600)
            layout = QVBoxLayout()
            txt = QTextEdit()
            txt.setPlainText(metadata_str)
            txt.setReadOnly(True)
            layout.addWidget(txt)
            self._ventana_metadata.setLayout(layout)
            self._ventana_metadata.exec()
"""