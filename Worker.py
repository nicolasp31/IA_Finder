# worker.py

from PyQt6.QtCore import QThread, pyqtSignal
from metadata_analisis import analizar_metadata_por_tipo, detectar_aplicacion, detectar_modelo

class HiloMetadata(QThread):
    progreso = pyqtSignal(int)
    terminado = pyqtSignal(dict, object, str, object, object)  # metadata, es_ia, mensaje, aplicacion, modelo
    error = pyqtSignal(Exception)

    def __init__(self, ruta_archivo):
        super().__init__()
        self.ruta_archivo = ruta_archivo

    def run(self):
        try:
            self.progreso.emit(10)
            metadata, es_ia, mensaje = analizar_metadata_por_tipo(self.ruta_archivo)
            aplicacion = detectar_aplicacion(metadata)
            modelo = detectar_modelo(metadata)
            self.progreso.emit(100)
            self.terminado.emit(metadata, es_ia, mensaje, aplicacion, modelo)
        except Exception as e:
            self.error.emit(e)
