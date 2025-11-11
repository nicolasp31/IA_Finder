import os
import sys
import subprocess
import platform
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QFileDialog, QVBoxLayout, QHBoxLayout,
    QTextEdit, QTableWidget, QTableWidgetItem, QTabWidget, QMenuBar, QProgressBar, QDialog, QMessageBox
)
from PyQt6.QtGui import QFont, QAction
from PyQt6.QtCore import Qt
from Worker import HiloMetadata
from metadata_analisis import verificar_archivo_ia


class DetectorArchivoGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Detector de archivos generados por IA")
        self.setMinimumSize(900, 680)
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
        # Elementos iniciales del panel derecho
        self.titulo_analisis = QLabel("Análisis de Archivo")
        self.titulo_analisis.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout_derecho.addWidget(self.titulo_analisis, alignment=Qt.AlignmentFlag.AlignLeft)
        self.barra_progreso = QProgressBar()
        self.barra_progreso.setMinimum(0)
        self.barra_progreso.setMaximum(100)
        self.barra_progreso.hide()
        layout_derecho.addWidget(self.barra_progreso)
        self.estado_analisis = QLabel("Selecciona un archivo para iniciar el análisis")
        self.estado_analisis.setFont(QFont("Arial", 11))
        layout_derecho.addWidget(self.estado_analisis)
        self.icono_resultado = QLabel()
        self.icono_resultado.setFixedSize(64, 64)
        layout_derecho.addWidget(self.icono_resultado, alignment=Qt.AlignmentFlag.AlignLeft)
        self.texto_resultado = QLabel("")
        self.texto_resultado.setFont(QFont("Arial", 12))
        self.texto_resultado.setWordWrap(True)
        layout_derecho.addWidget(self.texto_resultado)
        self.boton_ver_metadata = QPushButton("< Ver metadata completa")
        self.boton_ver_metadata.setEnabled(False)
        self.boton_ver_metadata.clicked.connect(self.mostrar_metadata_completa)
        layout_derecho.addWidget(self.boton_ver_metadata, alignment=Qt.AlignmentFlag.AlignLeft)
        # Variables de control
        self.metadata_completa = None
        self._ventana_metadata = None  # Para mantener referencia de QDialog
        self.hilo = None  # Hilo de análisis en curso

        # Conectar cambio de pestaña para actualizar panel derecho
        self.pestanas.currentChanged.connect(self.actualizar_panel_derecho_por_pestana)

    def inicializar_menu(self):
        menu_archivo = self.barra_menu.addMenu("Archivo")


        accion_abrir = QAction("Abrir archivo", self)
        accion_abrir.triggered.connect(self.seleccionar_archivo)

        accion_abrir_reporte = QAction("Abrir reporte", self)  # nuevo
        accion_abrir_reporte.triggered.connect(self.abrir_reporte)

        accion_exportar = QAction("Exportar reporte", self)
        accion_exportar.triggered.connect(self.exportar_reporte)

        accion_salir = QAction("Salir", self)
        accion_salir.setShortcut("Ctrl+Q")
        accion_salir.triggered.connect(QApplication.instance().quit)

        menu_archivo.addAction(accion_abrir)
        menu_archivo.addSeparator()
        menu_archivo.addAction(accion_abrir_reporte) 
        menu_archivo.addSeparator()
        menu_archivo.addAction(accion_exportar)
        menu_archivo.addSeparator()
        menu_archivo.addAction(accion_salir)

        # Menú Acerca de Nosotros
        menu_acerca = self.barra_menu.addMenu("Acerca de Nosotros")

        accion_ayuda = QAction("Ayuda", self)
        accion_sobre = QAction("Sobre Detector de IA", self)
        accion_instalacion = QAction("Instalación", self)
        accion_como_usar = QAction("¿Cómo usar?", self)

        menu_acerca.addAction(accion_ayuda)
        menu_acerca.addAction(accion_sobre)
        menu_acerca.addAction(accion_instalacion)
        menu_acerca.addAction(accion_como_usar)

        # Conectar las acciones para actualizar panel derecho
        accion_ayuda.triggered.connect(lambda: self.mostrar_contenido_derecho("ayuda"))
        accion_sobre.triggered.connect(lambda: self.mostrar_contenido_derecho("sobre"))
        accion_instalacion.triggered.connect(lambda: self.mostrar_contenido_derecho("instalacion"))
        accion_como_usar.triggered.connect(lambda: self.mostrar_contenido_derecho("como_usar"))

    def inicializar_pestanas(self):
        widget_ia = QWidget()
        layout_ia = QVBoxLayout()
        layout_ia.setContentsMargins(10, 10, 10, 10)
        layout_ia.setSpacing(10)
        widget_ia.setLayout(layout_ia)
        self.boton_seleccionar = QPushButton("Seleccionar archivo")
        self.boton_seleccionar.clicked.connect(self.seleccionar_archivo)
        layout_ia.addWidget(self.boton_seleccionar)
        self.boton_exportar_reporte = QPushButton("Exportar reporte")
        self.boton_exportar_reporte.clicked.connect(self.exportar_reporte)
        layout_ia.addWidget(self.boton_exportar_reporte)
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

        widget_reporte = QWidget()
        layout_reporte = QVBoxLayout()
        widget_reporte.setLayout(layout_reporte)

        self.boton_abrir_reporte = QPushButton("Abrir reporte")
        self.boton_abrir_reporte.clicked.connect(self.abrir_reporte)
        layout_reporte.addWidget(self.boton_abrir_reporte)

        self.texto_reporte = QTextEdit()
        self.texto_reporte.setReadOnly(True)
        layout_reporte.addWidget(self.texto_reporte)
        self.pestanas.addTab(widget_reporte, "Abrir reporte")
        


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

    def mostrar_contenido_derecho(self, opcion):
        layout = self.panel_derecho.layout()
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        if opcion == "como_usar":
            try:
            # Detectar si se ejecuta empaquetado con PyInstaller
                if hasattr(sys, "_MEIPASS"):
                    base_path = sys._MEIPASS  # Carpeta temporal del ejecutable
                else:
                    base_path = os.path.abspath(".")

            # Construir ruta al manual PDF
                ruta_pdf = os.path.join(base_path, "Manual_Usuario.pdf")

            # Comprobar existencia
                if not os.path.exists(ruta_pdf):
                    print(f"No se encontró el manual en: {ruta_pdf}")
                    return

            # Abrir el PDF según el sistema operativo
                if platform.system() == "Windows":
                    os.startfile(ruta_pdf)
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", ruta_pdf])
                else:  # Linux y otros
                    subprocess.run(["xdg-open", ruta_pdf])

            except Exception as e:
                print(f"Error al abrir el manual: {e}")

        textos = {
            "ayuda": """
                <h2>Ayuda</h2>
                <p>Esta herramienta te permite analizar si un archivo ha sido generado por inteligencia artificial (IA) mediante el análisis de su metadata.</p>
                <ul>
                <li><b>Selecciona un archivo</b> compatible, como imágenes, documentos o videos, usando el botón "Seleccionar archivo".</li>
                <li>El sistema extraerá automáticamente la metadata y evaluará la probabilidad de generación por IA.</li>
                <li>En la sección de resultados, podrás ver un resumen claro con el resultado del análisis y detalles del modelo o aplicación detectada.</li>
                <li>Utiliza el botón <b>"Ver metadata completa"</b> para explorar todos los datos extraídos del archivo.</li>
                <li>Puedes exportar un reporte completo en formatos HTML o CSV para revisar o compartir los resultados.</li>
                <li>Para abrir reportes guardados, usa la pestaña "Abrir reporte".</li>
                <li>Si presentas problemas, accede a la sección "Cómo usar" para abrir el manual de usuario completo o "Instalación" si tienes problemas con el funcionamiento dle aplicativo en el menú "Acerca de Nosotros".</li>
                <li>Esta aplicación es ideal para educadores, investigadores y profesionales que necesitan verificar la autenticidad del contenido digital.</li>
                </ul>
                <li><b>Si tienes cualquier otra duda contactate con nuestros desarrolladores:<b></li>
                <li>dfelipevenegas@ucundinamarca.edu.co | nicolasprieto@ucundinamarca.edu.co</li>
            """,
            "sobre": """
                <h2>Sobre Detector de IA</h2>
                <p>La aplicación IA Finder es una herramienta desarrollada en Python utilizando las librerías Exiftool y PyQt6. Su propósito es analizar la metadata de diversos tipos de archivos digitales y determinar si estos fueron generados o manipulados por sistemas de Inteligencia Artificial (IA). Este software contribuye a la verificación de autenticidad de documentos y materiales digitales en entornos académicos e investigativos.</p>

                <p>Ha sido desarrollado en el semillero UPS de la Universidad de Cundinamarca por Daniel Felipe Venegas Vargas y Nicolas Prieto. El objetivo principal es detectar patrones de IA en archivos buscando evidencias de ser generados por IA, siendo útil en la verificación de autenticidad de archivos, así como trabajos de investigación en torno a metadatos.</p>
                <p>Además, es una herramienta de fácil mantenimiento, de uso libre y código abierto con el propósito de fortalecer la investigación de patrones de metadatos en archivos generados por IA y la democratización de herramientas de este tipo.</p>
            """,
            "instalacion": """
            <h2>Instalación</h2>
                <p>Para instalar IA Finder, sigue estos pasos:</p>
                <ol>
                <li>Descarga el archivo ejecutable de IA Finder desde la página oficial o proveedor confiable.</li>
                <li>Guárdalo en una carpeta de tu preferencia.</li>
                <li>Ejecuta el programa haciendo doble clic sobre el archivo .exe.</li>
                <li>Espera unos segundos mientras se inicia la interfaz de usuario.</li>
                <li>Se abrirá en una ventana con el título 'Detector de archivos generados por IA'.</li>
                </ol>
                <h3>Requisitos del sistema</h3>
                <ul>
                <li>Sistema operativo: Windows 10 o superior.</li>
                <li>IA Finder ejecutable (.exe).</li>
                <li>No requiere instalación de Docker Desktop ni dependencias externas adicionales.</li>
                <li>Permisos de lectura sobre los archivos a analizar.</li>
                </ul>
                <h3>¿No puedes usar IA Finder?</h3>
                <p>Existe una versión alternativa:</p>
                <ul>
                <li>Descarga <a href="https://example.com/DetectorDeIA_Libre" target="_blank">DetectorDeIA_Libre</a>.</li>
                <li>Descarga e instala correctamente Exiftool en tu sistema operativo, siguiendo las instrucciones en <a href="https://exiftool.org/install.html" target="_blank">https://exiftool.org/install.html</a>.</li>
                <li>Ejecuta el archivo con doble clic.</li>
                <li>Sigue las instrucciones del manual para aprender sobre todas las funciones.</li>
                </ul>
            """,
            
        }
        texto = textos.get(opcion, "<p>Seleccione una opción para mostrar información.</p>")

        contenido_html = QTextEdit()
        contenido_html.setReadOnly(True)
        contenido_html.setHtml(texto)
        layout.addWidget(contenido_html)


    def actualizar_panel_derecho_por_pestana(self, index):
        nombre_pestana = self.pestanas.tabText(index)
        layout = self.panel_derecho.layout()

        # Limpiar siempre el panel derecho
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        if nombre_pestana == "Detector de IA":
            layout.addWidget(self.titulo_analisis, alignment=Qt.AlignmentFlag.AlignLeft)
            layout.addWidget(self.barra_progreso)
            if self.barra_progreso.isHidden():
                self.barra_progreso.hide()
            else:
                self.barra_progreso.show()
            layout.addWidget(self.estado_analisis)
            layout.addWidget(self.icono_resultado, alignment=Qt.AlignmentFlag.AlignLeft)
            layout.addWidget(self.texto_resultado)
            layout.addWidget(self.boton_ver_metadata, alignment=Qt.AlignmentFlag.AlignLeft)

        elif nombre_pestana == "Abrir reporte":
            widget_reporte = QWidget()
            layout_reporte = QVBoxLayout()
            widget_reporte.setLayout(layout_reporte)

            btn_abrir = QPushButton("Abrir reporte")
            btn_abrir.clicked.connect(self.abrir_reporte)
            layout_reporte.addWidget(btn_abrir)

            self.texto_reporte = QTextEdit()
            self.texto_reporte.setReadOnly(True)
            layout_reporte.addWidget(self.texto_reporte)

            layout.addWidget(widget_reporte)

        else:
            self.mostrar_contenido_derecho(nombre_pestana.lower())

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
        
        lineas = mensaje.split('\n') if mensaje else []
        resumen_3 = "\n".join(lineas[:3]) if len(lineas) > 3 else mensaje

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
        else: 
            self.icono_resultado.setText("✅")
            texto = "<b>Resultado de análisis:</b> Archivo genuino<br><b>0% IA detectada</b><br>"
            texto += "No se detectó la aplicación con la que fue generado el archivo<br>"
            texto += "No se encontró modelo de IA generativa<br>"

        self.texto_resultado.setText(f"{texto}<br>{resumen_3}")
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

    def abrir_reporte(self):
        ruta_archivo, _ = QFileDialog.getOpenFileName(
            self,
            "Selecciona un archivo de reporte",
            "",
            "Archivos soportados (*.html *.csv)"
        )
        if not ruta_archivo:
            return

        layout = self.panel_derecho.layout()
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        try:
            with open(ruta_archivo, "r", encoding="utf-8") as f:
                contenido = f.read()

            if ruta_archivo.lower().endswith(".html"):
                texto_html = QTextEdit()
                texto_html.setReadOnly(True)
                texto_html.setHtml(contenido)
                layout.addWidget(texto_html)
            else:
                import csv
                from io import StringIO

                tabla = QTableWidget()
                csv_buffer = StringIO(contenido)
                lector = csv.reader(csv_buffer)
                filas = list(lector)

                if filas:
                    tabla.setRowCount(len(filas) - 1)
                    tabla.setColumnCount(len(filas[0]))
                    tabla.setHorizontalHeaderLabels(filas[0])
                    tabla.verticalHeader().setVisible(False)
                    tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
                    tabla.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
                    tabla.horizontalHeader().setStretchLastSection(True)

                    for row_idx, row in enumerate(filas[1:]):
                        for col_idx, valor in enumerate(row):
                            tabla.setItem(row_idx, col_idx, QTableWidgetItem(valor))
                layout.addWidget(tabla)

        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo abrir el archivo:\n{str(e)}")


    def mostrar_metadata_completa(self):
        if not self.metadata_completa:
            return

        # Detectar patrones usando la función
        es_ia, mensaje = verificar_archivo_ia(self.metadata_completa)

        # Extraer todas las claves detectadas dentro del mensaje (sin límite)
        claves_resaltadas = set()
        if mensaje and es_ia is not False:
            for linea in mensaje.split('\n'):
                inicio = linea.find("'") + 1
                fin = linea.find("'", inicio)
                if inicio > 0 and fin > inicio:
                    clave = linea[inicio:fin]
                    claves_resaltadas.add(clave)

        # Generar la metadata en HTML con numeración y resaltado
        rows = []
        for idx, (k, v) in enumerate(self.metadata_completa.items(), start=1):
            if k in claves_resaltadas:
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



    def exportar_reporte(self):
        if not self.metadata_completa:
            QMessageBox.warning(self, "Atención", "No hay metadata para exportar.")
            return

        # Usar función que busca todos los patrones sin límite
        es_ia, mensaje = verificar_archivo_ia(self.metadata_completa)

        claves_resaltadas = set()
        if mensaje and es_ia is not False:
            for linea in mensaje.split('\n'):
                inicio = linea.find("'") + 1
                fin = linea.find("'", inicio)
                if inicio > 0 and fin > inicio:
                    clave = linea[inicio:fin]
                    claves_resaltadas.add(clave)

        # Preguntar ruta y tipo de archivo para guardar
        ruta_guardar, filtro = QFileDialog.getSaveFileName(
            self,
            "Guardar reporte de metadata",
            "reporte_metadata.html",
            "Archivo HTML (*.html);;Archivo CSV (*.csv)"
        )
        if not ruta_guardar:
            return  

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
