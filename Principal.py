import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QLabel, QPushButton, QHBoxLayout, QSpacerItem,
                             QSizePolicy, QFrame)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPixmap, QPalette, QBrush, QIcon

from Login1 import LoginPage
from validaracceso import ValidarAccesoPage


class CleanLoginSystemBlackControls(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Ingreso - CFBD")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFixedSize(800, 500)

        # Configurar fondo
        self.setup_background()

        # Widget principal
        main_widget = QWidget()
        main_widget.setAttribute(Qt.WA_TranslucentBackground)
        self.setCentralWidget(main_widget)

        # Layout principal (centrado vertical y horizontal)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Configurar controles de ventana (nuevo estilo)
        self.setup_window_controls()

        # 2. Contenedor central para el contenido
        center_container = QFrame()
        center_container.setFrameShape(QFrame.NoFrame)
        center_container.setAttribute(Qt.WA_TranslucentBackground)

        # Layout del contenedor central
        center_layout = QVBoxLayout(center_container)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)
        center_layout.setAlignment(Qt.AlignCenter)

        # 3. Widget de contenido (para centrado perfecto)
        content_widget = QWidget()
        content_widget.setFixedWidth(600)  # Ancho fijo para mejor alineación
        content_widget.setAttribute(Qt.WA_TranslucentBackground)

        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(30)
        content_layout.setAlignment(Qt.AlignCenter)

        # Logo (centrado)
        self.setup_logo(content_layout)

        # Texto "SISTEMA DE INGRESO" (centrado)
        title = QLabel("SISTEMA DE INGRESO")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            color: white;
            font: bold 40px 'Arial';
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            margin-top: 20px;
        """)
        content_layout.addWidget(title)

        # Botones (centrados)
        self.setup_buttons(content_layout)

        # Añadir contenido al centro
        center_layout.addWidget(content_widget)
        main_layout.addWidget(center_container, 1)

    def setup_background(self):
        background = QPixmap("fondo/Fondo.jpg")

        if background.isNull():
            print("Error: No se pudo cargar la imagen de fondo")
            # Fondo negro alternativo si la imagen no carga
            self.setStyleSheet("background-color: black;")
            return

        scaled_background = background.scaled(
            self.size(),
            Qt.IgnoreAspectRatio,
            Qt.SmoothTransformation
        )

        background_label = QLabel(self)
        background_label.setPixmap(scaled_background)
        background_label.setGeometry(0, 0, self.width(), self.height())

    def setup_logo(self, layout):
        logo = QPixmap("icons/LOGO CFBD_CFBD_LOGO BLANCO_PNG (1).png")
        if not logo.isNull():
            logo = logo.scaled(500, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label = QLabel()
            logo_label.setPixmap(logo)
            logo_label.setAlignment(Qt.AlignCenter)
            logo_label.setStyleSheet("margin-bottom: 10px;")
            layout.addWidget(logo_label)

    def setup_buttons(self, layout):
        # Estilo base para botones
        button_style = """
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                min-width: 180px;
                min-height: 50px;
                font: bold 16px 'Arial';
            }}
            QPushButton:hover {{
                background-color: {hover};
            }}
        """

        # Crear un layout horizontal para los botones
        botones_layout = QHBoxLayout()

        # Botón Ingreso
        btn_ingreso = QPushButton("CONTROL DE INGRESO")
        btn_ingreso.setStyleSheet(button_style.format(
            color="#4CAF50", hover="#45a049"
        ))
        btn_ingreso.clicked.connect(self.open_control)  # Conectar señal
        botones_layout.addWidget(btn_ingreso)

        # Botón Administrador
        btn_admin = QPushButton("ADMINISTRADOR")
        btn_admin.setStyleSheet(button_style.format(
            color="#2196F3", hover="#0b7dda"
        ))
        btn_admin.clicked.connect(self.open_admin_login)  # Conectar señal
        botones_layout.addWidget(btn_admin)

        # Centrar el layout horizontal dentro del layout principal
        layout.addLayout(botones_layout)

    def setup_window_controls(self):
        """Nuevos controles de ventana al estilo Login1.py"""
        # Crear un contenedor frame
        self.control_buttons = QFrame(self)
        self.control_buttons.setObjectName("ControlButtons")
        self.control_buttons.setFixedSize(70, 30)

        # Posición absoluta en la esquina superior derecha
        self.control_buttons.move(self.width() - 70, 4)

        # Configuración para el manejo de eventos
        self.control_buttons.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.control_buttons.setWindowFlags(Qt.FramelessWindowHint)
        self.control_buttons.setStyleSheet("""
            QFrame#ControlButtons {
                background-color: transparent;
                border: none;
            }
        """)

        # Layout horizontal
        buttons_layout = QHBoxLayout(self.control_buttons)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(5)

        # Botón Minimizar
        btn_minimize = QPushButton()
        btn_minimize.setObjectName("MinimizeButton")
        btn_minimize.setFixedSize(30, 30)
        btn_minimize.setIcon(QIcon("icons/Recurso 14A_Blanco.png"))  # Asegúrate de tener este icono
        btn_minimize.setIconSize(QSize(12, 12))
        btn_minimize.setCursor(Qt.PointingHandCursor)
        btn_minimize.setStyleSheet("""
            QPushButton#MinimizeButton {
                background-color: rgba(255, 255, 255, 0.1);
                border: none;
                border-radius: 5px;
            }
            QPushButton#MinimizeButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        btn_minimize.clicked.connect(self.showMinimized)

        # Botón Cerrar
        btn_close = QPushButton()
        btn_close.setObjectName("CloseButton")
        btn_close.setFixedSize(30, 30)
        btn_close.setIcon(QIcon("icons/Recurso 3A_Blanco.png"))  # Asegúrate de tener este icono
        btn_close.setIconSize(QSize(12, 12))
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton#CloseButton {
                background-color: rgba(255, 0, 0, 0.1);
                border: none;
                border-radius: 5px;
            }
            QPushButton#CloseButton:hover {
                background-color: rgba(255, 0, 0, 0.3);
            }
        """)
        btn_close.clicked.connect(self.close)

        # Añadir botones al layout
        buttons_layout.addWidget(btn_minimize)
        buttons_layout.addWidget(btn_close)

        # Asegurar que esté encima de todo
        self.control_buttons.raise_()
        self.control_buttons.setFocusPolicy(Qt.NoFocus)

    def mousePressEvent(self, event):
        """Permite arrastrar la ventana"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """Permite arrastrar la ventana"""
        if event.buttons() == Qt.LeftButton and hasattr(self, 'drag_position'):
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def open_admin_login(self):
        """Abre la ventana de login de administrador"""
        self.login_window = LoginPage()
        self.login_window.show()
        self.close()

    def open_control(self):
        """Abre la ventana de login de administrador"""
        self.login_window = ValidarAccesoPage()
        self.login_window.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    font = QFont("Arial", 10)
    app.setFont(font)

    window = CleanLoginSystemBlackControls()
    window.show()
    sys.exit(app.exec_())