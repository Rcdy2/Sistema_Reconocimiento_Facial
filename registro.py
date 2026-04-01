from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame, QLineEdit,
                             QComboBox, QHBoxLayout, QPushButton, QStackedWidget,
                             QStyledItemDelegate, QApplication, QMessageBox, QFileDialog)
from PyQt5.QtGui import QFont, QIntValidator, QRegExpValidator, QPixmap, QIcon
from PyQt5.QtCore import Qt, QRegExp, QSize, QPoint
import pyodbc
import os
from PIL import Image
import sys
from database_connection import get_db_connection

class UserRegistrationPage(QWidget):
    class UserRegistrationPage(QWidget):
        def darken_color(self, hex_color, percent):
            hex_color = hex_color.lstrip('#')
            rgb = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
            darkened = tuple(max(0, int(c * (100 - percent) / 100)) for c in rgb)
            return '#%02x%02x%02x' % darkened



    def __init__(self):
        super().__init__()
        self.archivo_biometrico = None  # Variable para almacenar la ruta del archivo biométrico
        self.setup_ui()

    def setup_ui(self):
        page_layout = QVBoxLayout(self)
        page_layout.setAlignment(Qt.AlignCenter)
        page_layout.setContentsMargins(0, 0, 0, 0)

        form_container = QFrame()
        form_container.setFixedWidth(900)
        form_container.setFixedHeight(600)
        form_container.setStyleSheet("QFrame { background-color: white; padding: 20px; }")

        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(10)

        self.setup_form_fields(form_layout)
        self.setup_form_buttons(form_layout)

        page_layout.addWidget(form_container)

    def setup_form_fields(self, layout):
        columns_container = QWidget()
        columns_container.setStyleSheet("background-color: white;")
        columns_layout = QHBoxLayout(columns_container)
        columns_layout.setContentsMargins(20, 20, 20, 20)
        columns_layout.setSpacing(50)

        left_column = self.create_form_column([
            ("Nombre", "Ingrese el nombre del usuario", None, False),
            ("DNI", "DNI debe tener 8 dígitos", QIntValidator(10000000, 99999999), False),
            ("Cargo", "Seleccione el cargo del usuario", None, True)
        ])

        right_column = self.create_form_column([
            ("Apellidos", "Ingrese los apellidos del usuario", None, False),
            ("Celular", "Celular debe tener 9 dígitos", QIntValidator(100000000, 999999999), False),
            ("Correo Electrónico", "usuario@dominio.com",
             QRegExpValidator(QRegExp("[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}")), False)
        ])

        columns_layout.addWidget(left_column)
        columns_layout.addWidget(right_column)
        layout.addWidget(columns_container)

    def create_form_column(self, fields):
        column = QWidget()
        column.setStyleSheet("background-color: white;")
        layout = QVBoxLayout(column)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(44)

        for label_text, placeholder, validator, is_combo in fields:
            container = QWidget()

            field_layout = QVBoxLayout(container)
            field_layout.setContentsMargins(0, 0, 0, 0)
            field_layout.setSpacing(6)

            label = QLabel(label_text)
            label.setStyleSheet("""
                font-family: 'Poppins Medium';
                font-size: 10px;
                color: #333333;
                background-color: transparent;
                padding: 0 0 1px 0;
            """)
            field_layout.addWidget(label)

            if is_combo:
                field = self.create_combobox()
            else:
                field = self.create_lineedit(placeholder, validator)

            if not hasattr(self, 'form_fields'):
                self.form_fields = {}
            self.form_fields[label_text.lower()] = field

            field_layout.addWidget(field)
            layout.addWidget(container)

        return column

    def create_lineedit(self, placeholder, validator):
        field = QLineEdit()
        field.setPlaceholderText(placeholder)
        field.setStyleSheet("""
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
        if validator:
            field.setValidator(validator)
        return field

    def create_combobox(self):
        field = QComboBox()
        field.addItems(["Seleccione un cargo", "Personal de Seguridad", "Administrativo", "Ejecutivo"])

        class ComboBoxDelegate(QStyledItemDelegate):
            def sizeHint(self, option, index):
                size = super().sizeHint(option, index)
                size.setHeight(40)
                return size

            def paint(self, painter, option, index):
                option.rect.adjust(0, 5, 0, -5)
                super().paint(painter, option, index)

        field.setItemDelegate(ComboBoxDelegate())
        field.setStyleSheet("""
            QComboBox {
                font-family: 'Poppins';
                font-size: 11px;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                padding: 8px;
                min-height: 28px;
                background: white;
            }
            QComboBox::drop-down {
                width: 25px;
                border: none;
                background: transparent;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background: white;
                outline: none;
                min-width: 200px;
                padding: 5px 0;
                margin: 2px 0;
            }
            QComboBox QAbstractItemView::item {
                min-height: 40px;
                height: 40px;
                padding: 10px 15px;
                margin: 0 5px;
                background: white;
                color: #333333;
                border-radius: 5px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #0F7E8D;
                color: white;
                height: 40px;
                margin: 0;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #0F7E8D;
                color: white;
                height: 40px;
                margin: 0;
            }
        """)
        return field

    def setup_form_buttons(self, layout):
        buttons_container = QWidget()
        buttons_container.setStyleSheet("background-color: white;")
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 20, 0, 0)
        buttons_layout.setSpacing(15)

        btn_biometrico = QPushButton("Registro Biométrico")
        btn_borrar = QPushButton("Borrar Datos")
        btn_registrar = QPushButton("Registrar")

        for btn in [btn_biometrico, btn_borrar, btn_registrar]:
            btn.setFixedSize(180, 45)

        btn_biometrico.setStyleSheet("""
            QPushButton {
                font-family: 'Poppins Medium';
                font-size: 11px;
                color: #0F7E8D;
                background-color: white;
                border: 1px solid #0F7E8D;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #f0f9fa;
            }
        """)
        btn_biometrico.clicked.connect(self.seleccionar_archivo_biometrico)

        btn_borrar.setStyleSheet("""
            QPushButton {
                font-family: 'Poppins Medium';
                font-size: 11px;
                color: #0F7E8D;
                background-color: white;
                border: 1px solid #0F7E8D;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #f0f9fa;
            }
        """)
        btn_borrar.clicked.connect(self.borrar_datos)

        btn_registrar.setStyleSheet("""
            QPushButton {
                font-family: 'Poppins Medium';
                font-size: 11px;
                color: white;
                background-color: #0F7E8D;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0d6e7b;
            }
        """)
        btn_registrar.clicked.connect(self.guardar_datos)

        buttons_layout.addStretch()
        buttons_layout.addWidget(btn_biometrico)
        buttons_layout.addWidget(btn_borrar)
        buttons_layout.addWidget(btn_registrar)
        layout.addWidget(buttons_container)

    def seleccionar_archivo_biometrico(self):
        """Abre el diálogo para seleccionar archivo biométrico"""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo biométrico", "",
            "Imágenes (*.jpg *.png *.bmp *.tiff);;Todos los archivos (*.*)",
            options=options
        )

        if file_name:
            self.archivo_biometrico = file_name
            self.mostrar_ventana_archivo(file_name)

    def mostrar_ventana_archivo(self, ruta_archivo):
        """Muestra una ventana con los detalles del archivo seleccionado"""
        self.ventana_archivo = QWidget()
        self.ventana_archivo.setWindowTitle("Archivo Biométrico Cargado")
        self.ventana_archivo.setFixedSize(400, 400)

        layout = QVBoxLayout(self.ventana_archivo)

        # Nombre del archivo
        nombre = os.path.basename(ruta_archivo)
        label_nombre = QLabel(f"Archivo: {nombre}")
        label_nombre.setStyleSheet("font: 14px 'Arial';")
        layout.addWidget(label_nombre, alignment=Qt.AlignCenter)

        # Vista previa de la imagen
        try:
            imagen = Image.open(ruta_archivo)
            imagen.thumbnail((300, 300))
            imagen.save("temp_preview.png")

            label_imagen = QLabel()
            pixmap = QPixmap("temp_preview.png")
            label_imagen.setPixmap(pixmap)
            layout.addWidget(label_imagen, alignment=Qt.AlignCenter)

            os.remove("temp_preview.png")
        except Exception as e:
            label_error = QLabel("Vista previa no disponible")
            label_error.setStyleSheet("color: red;")
            layout.addWidget(label_error, alignment=Qt.AlignCenter)

        # Botón para eliminar archivo
        btn_eliminar = QPushButton("Eliminar archivo")
        btn_eliminar.setStyleSheet("""
            QPushButton {
                color: #FF5050;
                background-color: transparent;
                border: 2px solid #FF5050;
                border-radius: 5px;
                font: bold 12px 'Arial';
                min-width: 120px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        btn_eliminar.clicked.connect(lambda: self.eliminar_archivo(ruta_archivo))
        layout.addWidget(btn_eliminar, alignment=Qt.AlignCenter)

        self.ventana_archivo.show()

    def eliminar_archivo(self, ruta_archivo):
        """Elimina el archivo seleccionado"""
        try:
            if os.path.exists(ruta_archivo):
                os.remove(ruta_archivo)
            self.ventana_archivo.close()
            self.archivo_biometrico = None
            self.mostrar_mensaje_estilizado("Éxito", "Archivo eliminado correctamente.", QMessageBox.Information)
        except Exception as e:
            self.mostrar_mensaje_estilizado("Error", f"No se pudo eliminar el archivo:\n{str(e)}", QMessageBox.Critical)

    def conectar_db(self):
        try:
            conn = get_db_connection()
            if conn:
                self.logger.debug("¡Conexión exitosa!")
                return conn
            else:
                self.show_message("Error", "Servidor no encontrado", QMessageBox.Critical)
                return None
        except Exception as e:
            self.logger.error(f"Error: {str(e)}")
            return None

    def guardar_datos(self):
        """Guarda los datos del formulario en la base de datos"""
        nombre = self.form_fields['nombre'].text().strip()
        apellidos = self.form_fields['apellidos'].text().strip()
        dni = self.form_fields['dni'].text().strip()
        cargo = self.form_fields['cargo'].currentText()

        # Validar campos obligatorios
        if cargo == "Seleccione un cargo":
            cargo = ""

        if not all([nombre, apellidos, dni, cargo]):
            self.show_message("Advertencia", "Por favor complete todos los campos obligatorios.", QMessageBox.Warning)

            return

        try:
            conn = self.conectar_db()
            if conn is None:
                return

            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO personal 
                   (nombre, apellido, dni, cargo, fecha_registro) 
                   VALUES (?, ?, ?, ?, GETDATE())""",
                (nombre, apellidos, dni, cargo)
            )

            conn.commit()
            conn.close()

            self.mostrar_mensaje_estilizado("Éxito", "Usuario registrado correctamente.", QMessageBox.Information)
            self.borrar_datos()

        except Exception as e:
            self.mostrar_mensaje_estilizado("Error", f"No se pudo guardar el registro:\n{str(e)}", QMessageBox.Critical)

    def borrar_datos(self):
        """Limpia todos los campos del formulario"""
        for field in self.form_fields.values():
            if isinstance(field, QLineEdit):
                field.clear()
            elif isinstance(field, QComboBox):
                field.setCurrentIndex(0)

        if hasattr(self, 'ventana_archivo') and self.ventana_archivo:
            self.ventana_archivo.close()

        self.archivo_biometrico = None

    def mostrar_mensaje_estilizado(self, titulo, mensaje, tipo=QMessageBox.Information):
        """Muestra un mensaje con estilos personalizados sin barra de título y bordes redondeados"""
        msg = QMessageBox(self)

        # Configuración de la ventana sin barra de título y con bordes redondeados
        msg.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)  # Elimina toda la decoración de la ventana
        msg.setWindowModality(Qt.WindowModal)
        msg.setWindowFlags(msg.windowFlags() | Qt.WindowStaysOnTopHint)
        msg.setWindowTitle(titulo)
        msg.setText(mensaje)

        # Definir paletas de colores para cada tipo
        paletas = {
            QMessageBox.Information: {
                "bg": "#4CAF50",  # Verde
                "button_bg": "#388E3C",  # Verde oscuro
                "button_hover": "#0D7037",  # Verde más oscuro
                "separator": "#81C784",  # Verde claro
                "text": "white"
            },
            QMessageBox.Warning: {
                "bg": "#FF9800",  # Naranja
                "button_bg": "#F57C00",  # Naranja oscuro
                "button_hover": "#E65100",  # Naranja más oscuro
                "separator": "#FFCC80",  # Naranja claro
                "text": "white"
            },
            QMessageBox.Critical: {
                "bg": "#F44336",  # Rojo
                "button_bg": "#D32F2F",  # Rojo oscuro
                "button_hover": "#B71C1C",  # Rojo más oscuro
                "separator": "#EF9A9A",  # Rojo claro
                "text": "white"
            }
        }

        # Seleccionar paleta según el tipo
        paleta = paletas.get(tipo, paletas[QMessageBox.Information])

        # Aplicar estilos con bordes redondeados
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {paleta['bg']};
                font: bold 9pt "Arial";
                border-radius: 12px;
                border: 5px solid {paleta['button_bg']};
            }}
            QMessageBox QLabel {{
                padding: -20px 0px 10px 0px;
                color: #333333;
                font-size: 25px;
                min-width: 250px;
                min-height: 100px;
                border-radius: 10px;
                text-align: center;
            }}
            QMessageBox QPushButton {{
                font: bold 9pt "Arial";
                color: {paleta['text']};
                background-color: {paleta['button_bg']};
                border: none;
                padding: 8px 20px;
                border-radius: 8px;
                min-width: 80px;
                margin: 0 auto;
            }}
            QMessageBox QPushButton:hover {{
                background-color: {paleta['button_hover']};
            }}
            QMessageBox QFrame {{
                background-color: transparent;
                border: none;
            }}
        """)



        # Asegurar que el diseño se actualice correctamente
        def adjust_layout():
            # Ajustar el tamaño del mensaje para que se vean los bordes redondeados
            msg.layout().setContentsMargins(15, 15, 15, 15)

        msg.resizeEvent = lambda event: adjust_layout()
        adjust_layout()

        msg.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UserRegistrationPage()
    window.show()
    sys.exit(app.exec_())


    def show_message(self, title, message, icon):
        msg = QMessageBox(self)
        msg.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)

        if icon == QMessageBox.Information:
            icon_color = "#0F7E8D"
            icon_text = "INFO"
        elif icon == QMessageBox.Warning:
            icon_color = "#ffb347"
            icon_text = "ADVERTENCIA"
        elif icon == QMessageBox.Critical:
            icon_color = "#d32f2f"
            icon_text = "ERROR"
        else:
            icon_color = "#0F7E8D"
            icon_text = "MENSAJE"

        msg.setStyleSheet(f"""
            QMessageBox, QLabel, QPushButton{{
                background-color:white;
            }}
            QMessageBox {{
                background-color: white;
                border: 5px solid {icon_color};
                border-radius: 8px;
                font-family: 'Poppins';
            }}
            QMessageBox QLabel {{
                color: #333333;
                min-width: 250px;
                min-height: 100px;
            }}
            QMessageBox QLabel#qt_msgbox_label {{
                qproperty-alignment: AlignCenter;
                font-size: 25px;
                font-weight: bold;
                color: {icon_color};
                padding: 0;
            }}
            QMessageBox QLabel#qt_msgbox_informativelabel {{
                qproperty-alignment: AlignCenter;
                font-size: 14px;
                padding: 0 20px;
            }}
            QMessageBox QPushButton {{
                font-family: 'Poppins Medium';
                background-color: {icon_color};
                color: white;
                border-radius: 5px;
                padding: 8px 20px;
                font-size: 12px;
                min-width: 80px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: {self.darken_color(icon_color, 20)};
            }}
            QMessageBox QDialogButtonBox {{
                qproperty-centerButtons: true;
            }}
        """)

        msg.setWindowTitle(title)
        msg.setText(f"<b>{icon_text}</b>")
        msg.setInformativeText(message)

        ok_button = msg.addButton("Aceptar", QMessageBox.AcceptRole)
        ok_button.setCursor(Qt.PointingHandCursor)

        return msg.exec_()
