from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt

class ErrorDialog(QDialog):
    def __init__(self):
        super().__init__()

        # Configuración de la ventana
        self.setWindowTitle(" ")
        self.setFixedSize(300, 300)
        self.setWindowFlags(Qt.FramelessWindowHint)

        # Estilo CSS con borde rojo personalizado
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                font-family: Arial;
                border: 7px solid #d32f2f;  
            }
            QLabel#error_title {
                font-size: 40px;
                font-weight: bold;
                color: black;
            }
            QLabel#message {
                font-size: 15px;
                color: black;
            }
            QPushButton {
                background-color: #d32f2f;
                border-radius: 5px;
                color: white;
                border: none;
                padding: 14px 28px;
                font-size: 20px;
                min-width: 50px;
            }
            QPushButton:hover {
                background-color: #b71c1c;
            }
            QPushButton:pressed {
                background-color: #8e0000;
            }
        """)

        # Widgets
        self.label_error = QLabel("ERROR")
        self.label_error.setObjectName("error_title")
        self.label_error.setAlignment(Qt.AlignCenter)

        self.label_message = QLabel("Complete todos los campos obligatorios")
        self.label_message.setObjectName("message")
        self.label_message.setAlignment(Qt.AlignCenter)

        self.button_accept = QPushButton("Aceptar")
        self.button_accept.clicked.connect(self.close)

        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(0)
        layout.addWidget(self.label_error)
        layout.addWidget(self.label_message)
        layout.addWidget(self.button_accept, alignment=Qt.AlignCenter)

        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication([])
    dialog = ErrorDialog()
    dialog.exec_()