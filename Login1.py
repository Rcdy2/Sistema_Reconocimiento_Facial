from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame, QLineEdit,
                             QPushButton, QHBoxLayout, QApplication, QMessageBox,
                             QSizePolicy, QGridLayout)
from PyQt5.QtGui import QFont, QPixmap, QPalette, QBrush, QPainter, QIcon
from PyQt5.QtCore import Qt, QSize
from database_connection import get_db_connection
import sys
import pyodbc
import logging

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)


class LoginPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Inicio de Sesión - Sistema de Seguridad Facial')
        self.setFixedSize(800, 500)
        self.usuario_autenticado = None
        self.logger = logging.getLogger(__name__)
        self.main_window = None

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)  # fondo transparente

        self.setup_ui()
        self.setup_window_controls()
        self.setup_back_button()  # Nuevo botón de regreso

    def setup_back_button(self):
        """Configura el botón de flecha para regresar al menú principal"""
        self.back_button = QPushButton(self)
        self.back_button.setObjectName("BackButton")
        self.back_button.setFixedSize(30, 30)
        self.back_button.setIcon(QIcon("icons/arrow.png"))
        self.back_button.setIconSize(QSize(12, 12))
        self.back_button.setCursor(Qt.PointingHandCursor)
        self.back_button.setStyleSheet("""
            QPushButton#BackButton {
                background-color: rgba(255, 255, 255, 0.1);
                border: none;
                border-radius: 5px;
            }
            QPushButton#BackButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        self.back_button.move(3, 3)
        self.back_button.clicked.connect(self.go_back_to_main)
        self.back_button.raise_()

    def go_back_to_main(self):
        """Regresa a la ventana principal"""
        from Principal import CleanLoginSystemBlackControls
        self.main_window = CleanLoginSystemBlackControls()
        self.main_window.show()
        self.close()

    def setup_ui(self):
        # Contenedor principal con transparencia
        main_container = QWidget(self)
        main_container.setGeometry(0, 0, 800, 550)
        main_container.setStyleSheet("""
               background-color: rgba(0, 0, 0, 0); 
               border-radius: 15px;
           """)

        # Cargar imagen con transparencia
        try:
            pixmap = QPixmap("SetUp/Fondo.jpg")
            if not pixmap.isNull():
                # Crear versión transparente de la imagen
                transparent_pixmap = QPixmap(pixmap.size())
                transparent_pixmap.fill(Qt.transparent)

                painter = QPainter(transparent_pixmap)
                painter.setCompositionMode(QPainter.CompositionMode_Source)
                painter.setOpacity(0.92)  # Ajusta la transparencia
                painter.drawPixmap(0, 0, pixmap)
                painter.end()

                # Crear label para la imagen de fondo
                bg_label = QLabel(main_container)
                bg_label.setGeometry(0, 0, 800, 550)
                bg_label.setPixmap(transparent_pixmap.scaled(
                    800, 550, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
                bg_label.setAlignment(Qt.AlignCenter)
        except Exception as e:
            self.logger.error(f"Error cargando imagen: {str(e)}")

        # centrá el contenido verticalmente
        main_layout = QGridLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setRowStretch(0, 1)  # Espacio flexible arriba
        main_layout.setRowStretch(2, 1)  # Espacio flexible abajo

        # Contenedor central para dos paneles (izquierdo y derecho)
        center_container = QWidget()
        center_container.setStyleSheet("background-color: transparent;")
        center_layout = QHBoxLayout(center_container)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)

        # Contenedor izquierdo para el formulario
        left_container = QWidget()
        left_container.setStyleSheet("""
            background-color: transparent;
            border-radius: 0 10px 10px 0;
        """)
        left_container.setFixedWidth(400)
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(40, 40, 40, 40)  # Reducido margen vertical
        left_layout.setSpacing(20)  # Espaciado reducido

        # Logo o título del sistema
        titulo = QLabel("Bienvenido")
        titulo.setStyleSheet("""
            QLabel {
                font-family: 'Poppins Medium';
                font-size: 30px;
                color: white;
                padding-bottom: 10px;
                margin-bottom: 10px;
            }
        """)
        titulo.setAlignment(Qt.AlignLeft)
        left_layout.addWidget(titulo, alignment=Qt.AlignTop)

        # Formulario
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 18px;
                min-width: 300px;
            }
        """)
        form_frame.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(10, 10, 10, 10)
        form_layout.setSpacing(13)

        def create_input_field(label_text, placeholder, is_password=False):
            container = QWidget()
            container.setStyleSheet("background-color: white;")
            field_layout = QVBoxLayout(container)
            field_layout.setContentsMargins(0, 0, 0, 0)
            field_layout.setSpacing(6)  # Espacio entre label y campo

            label = QLabel(label_text)
            label.setStyleSheet("""
                font-family: 'Poppins Medium';
                font-size: 10px;
                color: #333333;
                background-color: transparent;
                padding: 0 0 1px 0;
            """)
            field_layout.addWidget(label)

            input_field = QLineEdit()
            input_field.setPlaceholderText(placeholder)
            if is_password:
                input_field.setEchoMode(QLineEdit.Password)
                input_field.returnPressed.connect(self.authenticate)

            input_field.setStyleSheet("""
                QLineEdit {
                    font-family: 'Poppins';
                    font-size: 11px;
                    border: 1px solid #e0e0e0;
                    border-radius: 5px;
                    padding: 5px 10px;
                    min-height: 35px;
                }
                QLineEdit:focus {
                    border: 1px solid #0F7E8D;
                }
            """)
            field_layout.addWidget(input_field)

            return container, input_field

        user_container, self.user_input = create_input_field("Usuario", "Ingrese su nombre de usuario")
        form_layout.addWidget(user_container)

        pass_container, self.password_input = create_input_field("Contraseña", "Ingrese su contraseña", True)
        form_layout.addWidget(pass_container)

        # Botón para mostrar/ocultar contraseña
        self.toggle_password_btn = QPushButton("Mostrar contraseña")
        self.toggle_password_btn.setStyleSheet("""
            QPushButton {
                font-family: 'Poppins';
                font-size: 11px;
                color: #0F7E8D;
                background-color: transparent;
                border: none;
                text-align: left;
                padding: 5px 0;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
        """)
        self.toggle_password_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_password_btn.clicked.connect(self.toggle_password_visibility)
        form_layout.addWidget(self.toggle_password_btn)

        # Botón de inicio de sesión (estilo similar al de registro.py)
        login_btn = QPushButton("Iniciar Sesión")
        login_btn.setStyleSheet("""
            QPushButton {
                font-family: 'Poppins Medium';
                font-size: 11px;
                color: white;
                background-color: #0F7E8D;
                border: none;
                border-radius: 5px;
                padding: 12px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #0d6e7b;
            }
            QPushButton:pressed {
                background-color: #0b5d68;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        login_btn.clicked.connect(self.authenticate)
        form_layout.addWidget(login_btn)

        left_layout.addWidget(form_frame)
        left_layout.addStretch()  # espacio flexible para centrar verticalmente

        # Contenedor derecho para el logo
        right_container = QWidget()
        right_container.setStyleSheet("background-color: transparent;")
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Cargar el logo
        try:
            logo_label = QLabel()
            pixmap = QPixmap("icons/LOGO CFBD_CFBD_LOGO BLANCO_PNG (1).png")
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(350, 350, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                logo_label.setPixmap(scaled_pixmap)
                logo_label.setAlignment(Qt.AlignCenter)
                logo_label.setStyleSheet("background-color: transparent;")
            else:
                raise FileNotFoundError
        except Exception as e:
            self.logger.error(f"No se pudo cargar el logo: {str(e)}")
            logo_label = QLabel("LOGO")
            logo_label.setStyleSheet("""
                font-family: 'Poppins Medium';
                font-size: 24px;
                color: white;
                background-color: transparent;
            """)
            logo_label.setAlignment(Qt.AlignCenter)

        right_layout.addStretch()
        right_layout.addWidget(logo_label, alignment=Qt.AlignCenter)
        right_layout.addStretch()

        center_layout.addWidget(left_container)
        center_layout.addWidget(right_container)

        main_layout.addWidget(center_container, 1, 0)

    def toggle_password_visibility(self):
        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_password_btn.setText("Ocultar contraseña")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_password_btn.setText("Mostrar contraseña")

    def conectar_db(self):
        """Llama a la conexión centralizada"""
        try:
            self.logger.debug("Intentando conectar a la base de datos...")
            # Asegúrate de tener: from database_connection import get_db_connection al inicio del archivo
            conn = get_db_connection()
            if conn:
                self.logger.debug("¡Conexión exitosa!")
                return conn
            else:
                self.show_message("Error", "No se pudo conectar al servidor SQL.", QMessageBox.Critical)
                return None
        except Exception as e:
            self.logger.error(f"Fallo en conectar_db: {str(e)}")
            return None

    def validar_usuario(self, usuario, contrasena):
        """Valida las credenciales contra la base de datos"""
        conn = self.conectar_db()  # Aquí es donde antes fallaba porque no encontraba la función
        if not conn:
            return None

        try:
            cursor = conn.cursor()
            self.logger.debug(f"Buscando usuario: {usuario}")

            # Consulta SQL
            cursor.execute("""
                SELECT id, nombre, usuario, rol
                FROM usuarios_sistema
                WHERE usuario = ? AND contrasena = ?
            """, (usuario, contrasena))

            resultado = cursor.fetchone()
            if resultado:
                return {
                    'id': resultado[0],
                    'nombre': resultado[1],
                    'usuario': resultado[2],
                    'rol': resultado[3]
                }
            return None

        except Exception as e:
            self.logger.error(f"Error en consulta SQL: {str(e)}")
            return None
        finally:
            conn.close()

    def authenticate(self):
        username = self.user_input.text().strip()
        password = self.password_input.text().strip()

        if not username:
            self.show_message("", "Ingrese su nombre de usuario", QMessageBox.Warning)
            self.user_input.setFocus()
            return

        if not password:
            self.show_message("", "Ingrese su contraseña", QMessageBox.Warning)
            self.password_input.setFocus()
            return

        # Mostrar algún indicador de carga (opcional)
        loading_msg = QMessageBox(self)
        loading_msg.setWindowFlags(Qt.FramelessWindowHint)
        loading_msg.setText("Autenticando...")
        loading_msg.setStandardButtons(QMessageBox.NoButton)
        loading_msg.show()

        QApplication.processEvents()  # Forzar actualización de la UI

        try:
            usuario = self.validar_usuario(username, password)
            loading_msg.close()  # Cerrar el mensaje de carga

            if usuario:
                self.usuario_autenticado = usuario
                self.hide()
                if not self.main_window:
                    from main import ModernAdminPanel
                    self.main_window = ModernAdminPanel()
                self.main_window.show()
            else:
                self.show_message("Error de autenticación",
                                  "Credenciales incorrectas. Por favor intente nuevamente.",
                                  QMessageBox.Critical)
                self.password_input.clear()
                self.password_input.setFocus()

        except Exception as e:
            loading_msg.close()
            self.logger.error(f"Error durante autenticación: {str(e)}")
            self.show_message("Error",
                              f"Ocurrió un error durante la autenticación: {str(e)}",
                              QMessageBox.Critical)
        finally:
            self.setEnabled(True)

    def show_message(self, title, message, icon):
        """Versión mejorada del messagebox"""
        msg = QMessageBox(self)
        msg.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)

        # Contenido del mensaje
        msg.setText(f"<b>{title}</b>")
        msg.setText("ERROR")
        msg.setInformativeText(message)

        msg.setStyleSheet("""
            QMessageBox {
                background-color: white;
                border: 5px solid #d32f2f;
                font-family: 'Poppins';

            }
            QMessageBox QLabel {
                padding: -20px 0px 10px 0px;
                color: #333333;
                font-size: 25px;
                min-width: 250px;
                min-height: 100px;
                border-radius: 10px;
                text-align: center;

            }

             QMessageBox QLabel#qt_msgbox_label {
                padding: -20px ;
                qproperty-alignment: AlignCenter;
                font-size: 40px;
                font-weight: bold;
                color: #d32f2f;
             }

              QMessageBox QLabel#qt_msgbox_informativelabel {
                qproperty-alignment: AlignCenter;
                font-size: 20px;
              }
            QMessageBox QPushButton {
                font-family: 'Poppins Medium';
                background-color: #d32f2f;
                color: white;
                border-radius: 5px;
                padding: 8px 20px;
                font-size: 12px;
                min-width: 80px;  
                margin: 0 auto;
            }
            QMessageBox QPushButton:hover {
                background-color: #b71c1c;  
            }

             QMessageBox QDialogButtonBox {
                qproperty-centerButtons: true;
            }
        """)

        # Botón OK
        ok_button = msg.addButton("Aceptar", QMessageBox.AcceptRole)
        ok_button.setCursor(Qt.PointingHandCursor)

        msg.exec_()

    def setup_window_controls(self):
        """Configura los botones de control de la ventana (minimizar y cerrar)"""
        # Crear un contenedor frame en lugar de QWidget
        self.control_buttons = QFrame(self)
        self.control_buttons.setObjectName("ControlButtons")
        self.control_buttons.setFixedSize(70, 30)

        # Posición absoluta en la esquina superior derecha
        self.control_buttons.move(self.width() - 70, round(4.5))

        # Configuración crítica para el manejo de eventos
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
        btn_minimize.setIcon(QIcon("icons/Recurso 14A_Blanco.png"))
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
        btn_close.setIcon(QIcon("icons/Recurso 3A_Blanco.png"))
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
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and hasattr(self, 'drag_position'):
            self.move(event.globalPos() - self.drag_position)
            event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("* { font-family: 'Poppins'; }")
    login_window = LoginPage()
    login_window.show()

    sys.exit(app.exec_())