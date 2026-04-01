from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer
import cv2


class VentanaAcceso(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Acceso Concedido")
        self.setFixedSize(400, 200)
        self.setStyleSheet("background-color: #4CAF50;")



        layout = QVBoxLayout()
        label = QLabel("Acceso Permitido")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("""
            QLabel {
               
                font: bold 11pt "Arial";
                color: white;
            
                border: none;
               
                border-radius: 5px;
                min-width: 100px;
            }
        """)
        layout.addWidget(label)
        self.setLayout(layout)


class ReconocimientoFacialIngreso(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Verificación Facial - Ingreso")
        self.setFixedSize(800, 900)

        # Configuración de la ventana
        self.layout = QVBoxLayout()
        self.label_video = QLabel()
        self.layout.addWidget(self.label_video)
        self.setLayout(self.layout)

        # Configuración de OpenCV
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')   # noqa
        self.cap = cv2.VideoCapture(0)
        self.rostro_detectado = False

        # Timer para actualizar el frame
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_frame)  # noqa
        self.timer.start(50)  # Actualizar cada 50ms

    def actualizar_frame(self):
        ret, frame = self.cap.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

            if len(faces) > 0 and not self.rostro_detectado:
                self.rostro_detectado = True
                self.timer.stop()
                self.mostrar_acceso_concedido()
                return

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Convertir el frame de OpenCV a formato Qt
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w
            convert_to_qt_format = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            p = convert_to_qt_format.scaled(self.label_video.width(), self.label_video.height(), Qt.KeepAspectRatio)
            self.label_video.setPixmap(QPixmap.fromImage(p))

    def mostrar_acceso_concedido(self):
        self.cap.release()
        ventana_acceso = VentanaAcceso(self.parent())
        ventana_acceso.exec_()
        self.close()

    def closeEvent(self, event):
        # Liberar recursos al cerrar la ventana
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()
        event.accept()


def abrir_reconocimiento_para_ingreso(pantalla):
    ventana_facial = ReconocimientoFacialIngreso(pantalla)
    ventana_facial.exec_()