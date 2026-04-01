from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QLabel, QPushButton,
                             QCheckBox, QSizePolicy)
from PyQt5.QtGui import QIcon, QFont, QPixmap, QPainter, QColor
from PyQt5.QtCore import Qt, pyqtSignal, QSize


class CustomSidebar(QFrame):
    dashboard_clicked = pyqtSignal()
    registration_clicked = pyqtSignal()
    users_list_clicked = pyqtSignal()
    asistencia_list_clicked = pyqtSignal()
    dashboard_clicked = pyqtSignal()
    logout_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setup_sidebar()

    def setup_sidebar(self):
        self.setFixedWidth(250)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
            }
            QPushButton {
                background-color: transparent;
                color: #9197B3;
                text-align: left;
                padding: 10px 18px;
                font-family: 'Poppins Medium';
                font-size: 13px;
                border: none;
                margin-left: 15px;
                margin-right: 15px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #0F7E8D;
                color: white;
            }
            QPushButton:hover QLabel {
                color: white;
            }
            QLabel {
                font-family: 'Poppins Medium';
            }
            QCheckBox {
                font-family: 'Poppins Medium';
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(14)

        self.setup_logo(layout)
        self.setup_navigation_buttons(layout)
        self.setup_logout_button(layout)

    def setup_logo(self, layout):
        # Crear QLabel para la imagen
        logo = QLabel()

        # Cargar la imagen desde la ruta especificada
        pixmap = QPixmap("icons/LOGO CFBD_CFBD_LOGO ORIGINAL_PNG.png")

        # Escalar la imagen manteniendo la relación de aspecto (ajusta el tamaño según necesites)
        scaled_pixmap = pixmap.scaled(200, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Establecer la imagen en el QLabel
        logo.setPixmap(scaled_pixmap)

        # Estilo para el QLabel (centrado, márgenes, etc.)
        logo.setStyleSheet("""
            QLabel {
                margin-top: 11px;
                qproperty-alignment: AlignCenter;
                margin-bottom: 10px;
                
            }
        """)

        # Asegurar que el QLabel se expanda correctamente
        logo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Añadir el logo al layout
        layout.addWidget(logo)

    def setup_navigation_buttons(self, layout):
        buttons = [
            ("Dashboard", "icons/casa (1).png", self.dashboard_clicked),
            ("Registro de Usuarios", "icons/agregar-usuario (1).png", self.registration_clicked),
            ("Lista de Usuarios", "icons/usuarios (2).png", self.users_list_clicked),
            ("Control de Asistencia", "icons/reloj-con-flecha-circular.png", self.asistencia_list_clicked),
        ]

        for text, icon_path, signal in buttons:
            btn = QPushButton(text)
            self.setup_button_icon(btn, icon_path)

            if signal:
                btn.clicked.connect(signal)

            layout.addWidget(btn)

    def set_active_button(self, button_name):
        """Resalta el botón de la página actual"""
        # Buscar todos los botones en la barra lateral
        for btn in self.findChildren(QPushButton):
            # Comparar el texto del botón (eliminando espacios extra)
            if btn.text().strip() == button_name:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #0F7E8D;
                        color: white;
                    }
                    QPushButton:hover {
                        background-color: #0d6e7b;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        color: #9197B3;
                    }
                    QPushButton:hover {
                        background-color: #0F7E8D;
                        color: white;
                    }
                """)

    def setup_button_icon(self, button, icon_path):
        # Configurar el icono
        icon = QIcon(icon_path)
        pixmap = icon.pixmap(16, 16)
        colored_pixmap = self.colorize_pixmap(pixmap, QColor("#9197B3"))
        button.setIcon(QIcon(colored_pixmap))
        button.setIconSize(QSize(18, 18))  # Aumentar ligeramente el tamaño del icono

        # Configurar el texto con espacios no separables
        button.setText("   " + button.text())  # Añade 3 espacios antes del texto

        # Estilo CSS completo para el botón
        button.setStyleSheet("""
            QPushButton {
                spacing: 2px;
                padding-left: 22px;
                text-align: left;
            }
            QPushButton::icon {
                padding-left: 25px;
            }
        """)

    def setup_logout_button(self, layout):
        layout.addStretch()
        self.btn_logout = QPushButton("Cerrar sesión")  # Cambiado a atributo de clase
        self.setup_button_icon(self.btn_logout, "icons/logout_icon.png")
        self.btn_logout.setStyleSheet("""
            QPushButton {
                color: #e53935;
                margin-top: 20px;
                spacing: 12px;
            }
            QPushButton:hover {
                background-color: #fce4ec;
                color: #d32f2f;
            }
        """)
        self.btn_logout.clicked.connect(self.logout_clicked.emit)  # Conectar señal
        layout.addWidget(self.btn_logout)

    def colorize_pixmap(self, pixmap, color):
        colored_pixmap = QPixmap(pixmap.size())
        colored_pixmap.fill(Qt.transparent)

        painter = QPainter(colored_pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.drawPixmap(0, 0, pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(colored_pixmap.rect(), color)
        painter.end()

        return colored_pixmap