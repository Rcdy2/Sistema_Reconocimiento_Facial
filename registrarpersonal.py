from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame, QLineEdit,
                             QComboBox, QHBoxLayout, QPushButton, QStyledItemDelegate,
                             QMessageBox, QApplication, QSpacerItem, QSizePolicy)
from PyQt5.QtGui import QFont, QIntValidator, QRegExpValidator, QPixmap, QImage, QRegularExpressionValidator
from PyQt5.QtCore import Qt, QRegExp, QTimer, QThread, pyqtSignal, QRegularExpression
import cv2
import face_recognition
import pyodbc
import os
import sys
import pickle
import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning
from database_connection import get_db_connection
from PIL import Image
import numpy as np

# Deshabilitar advertencias de SSL
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class ApiPeruWorker(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str, str)

    def __init__(self, dni):
        super().__init__()
        self.dni = dni
        self.token = "46fa0100748854bab3b4dada0becaab9d312f12bb05563db91228e0fc8b850cd"

    def run(self):
        url = "https://apiperu.dev/api/dni"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        data = {'dni': self.dni}

        try:
            response = requests.post(
                url,
                headers=headers,
                json=data,
                verify=False,
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('success', False):
                    self.finished.emit(result['data'])
                else:
                    self.error.emit("Error en la API", result.get('message', 'Error desconocido en la API'))
            else:
                self.error.emit("Error HTTP", f"Error {response.status_code}: {response.text}")

        except Exception as e:
            self.error.emit("Error de conexión", f"Error al conectar con la API: {str(e)}")


class PersonalRegistrationPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Registro de Personal - NovaMarket")
        self.setFixedSize(1000, 800)

        self.cam = None
        self.camera_active = False
        self.captured_images = []
        self.timer = None
        self.intentos_camara = 0

        self.db_conn = self.connect_db()

        self.setup_ui()
        self.init_camera()

    def connect_db(self):
        """Conectar a la base de datos usando get_db_connection o directamente."""
        try:
            # Usar la función centralizada (asumiendo que está definida en database_connection)
            conn = get_db_connection()
            if not conn:
                raise Exception("No se pudo conectar con get_db_connection")
            return conn
        except Exception:
            # Fallback: conexión directa por si la función falla
            try:
                return pyodbc.connect(
                    'DRIVER={ODBC Driver 17 for SQL Server};'
                    'SERVER=.;'
                    'DATABASE=UTP_SECURITYFACIAL;'
                    'Trusted_Connection=yes;'
                )
            except Exception as e:
                self.show_message("Error", f"No se pudo conectar a la base de datos:\n{str(e)}")
                return None

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 0, 20, 20)
        main_layout.setSpacing(20)

        # COLUMNA IZQUIERDA - FORMULARIO
        form_container = QFrame()
        form_container.setFixedSize(400, 700)
        form_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
            QLabel {
                font-family: 'Poppins Medium';
                font-size: 10px;
                color: #333333;
                padding: 0 0 1px 0;
            }
        """)

        form_main_layout = QVBoxLayout(form_container)
        form_main_layout.setContentsMargins(0, 0, 0, 0)
        form_main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        form_layout = QVBoxLayout()
        form_layout.setSpacing(11)
        form_main_layout.addLayout(form_layout)

        title = QLabel("Registro de Personal")
        title.setStyleSheet("""
            font-family: 'Poppins';
            font-size: 20px;
            font-weight: bold;
            color: #0F7E8D;
            padding-bottom: 15px;
        """)
        form_layout.addWidget(title)

        self.setup_form_fields(form_layout)

        self.lbl_fotos_capturadas = QLabel("0 / 6 fotos capturadas")
        self.lbl_fotos_capturadas.setStyleSheet("""
            font-family: 'Poppins';
            font-size: 12px;
            color: #555;
            padding-top: 10px;
        """)
        form_layout.addWidget(self.lbl_fotos_capturadas)

        self.setup_form_buttons(form_layout)
        form_main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # COLUMNA DERECHA - CÁMARA
        self.video_label = QLabel("Inicializando cámara...")
        self.video_label.setFixedSize(600, 450)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("""
            background-color: #eee; 
            border: 1px solid #ccc;
            border-radius: 8px;
        """)

        main_layout.addWidget(form_container)
        main_layout.addWidget(self.video_label)

    def setup_form_fields(self, layout):
        fields = [
            ("Nombre", "Se completará automáticamente con el ingreso del DNI", None, False, True),
            ("Apellidos", "Se completará automáticamente con el ingreso del DNI", None, False, True),
            ("DNI", "Ingrese DNI de 8 dígitos", QIntValidator(10000000, 99999999), False, False),
            ("Cargo", "Seleccione el cargo del usuario", None, True, False)
        ]

        for label_text, placeholder, validator, is_combo, is_readonly in fields:
            container = QWidget()
            container.setStyleSheet("background-color: white;")
            field_layout = QVBoxLayout(container)
            field_layout.setContentsMargins(0, 0, 0, 0)
            field_layout.setSpacing(6)

            label = QLabel(label_text)
            field_layout.addWidget(label)

            if is_combo:
                field = self.create_combobox()
                field.currentTextChanged.connect(self.handle_cargo_changed)
            else:
                field = self.create_lineedit(placeholder, validator, label_text == "DNI", is_readonly)

            if not hasattr(self, 'form_fields'):
                self.form_fields = {}
            self.form_fields[label_text.lower().replace(" ", "_")] = field

            field_layout.addWidget(field)
            layout.addWidget(container)

        # Campos adicionales para Personal de Seguridad (inicialmente ocultos)
        self.setup_security_fields(layout)

    def setup_security_fields(self, layout):
        """Configura los campos adicionales para Personal de Seguridad"""
        self.security_fields_container = QWidget()
        self.security_fields_container.setVisible(False)
        self.security_fields_container.setStyleSheet("background-color: white;")
        security_layout = QVBoxLayout(self.security_fields_container)
        security_layout.setContentsMargins(0, 0, 0, 0)
        security_layout.setSpacing(15)

        # Campo Usuario
        usuario_container = QWidget()
        usuario_container.setStyleSheet("background-color: white;")
        usuario_layout = QVBoxLayout(usuario_container)
        usuario_layout.setContentsMargins(0, 0, 0, 0)
        usuario_layout.setSpacing(6)

        lbl_usuario = QLabel("Usuario")
        usuario_layout.addWidget(lbl_usuario)

        self.usuario_field = self.create_lineedit("Se generará automáticamente", None, False, True)
        usuario_layout.addWidget(self.usuario_field)
        security_layout.addWidget(usuario_container)

        # Campo Contraseña
        contrasena_container = QWidget()
        contrasena_container.setStyleSheet("background-color: white;")
        contrasena_layout = QVBoxLayout(contrasena_container)
        contrasena_layout.setContentsMargins(0, 0, 0, 0)
        contrasena_layout.setSpacing(6)

        lbl_contrasena = QLabel("Contraseña")
        contrasena_layout.addWidget(lbl_contrasena)

        self.contrasena_field = QLineEdit()
        self.contrasena_field.setPlaceholderText("Ingrese contraseña para Personal de Seguridad")
        self.contrasena_field.setEchoMode(QLineEdit.Password)
        self.contrasena_field.setStyleSheet("""
            QLineEdit {
                font-family: 'Poppins';
                font-size: 11px;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                padding: 8px 12px;
                min-height: 25px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #0F7E8D;
            }
        """)
        regex = QRegularExpression("^(?=.*[A-Za-z])(?=.*\\d)[A-Za-z\\d]{6,}$")
        validator = QRegularExpressionValidator(regex)
        self.contrasena_field.setValidator(validator)
        contrasena_layout.addWidget(self.contrasena_field)
        security_layout.addWidget(contrasena_container)

        layout.addWidget(self.security_fields_container)

    def handle_cargo_changed(self, cargo):
        """Maneja el cambio de selección en el combobox de cargo"""
        if cargo == "Personal de Seguridad":
            self.security_fields_container.setVisible(True)
            self.generar_usuario_seguridad()
        else:
            self.security_fields_container.setVisible(False)
            self.usuario_field.setText("Se generará automáticamente")

    def generar_usuario_seguridad(self):
        """Genera un nombre de usuario automático para personal de seguridad."""
        if not self.db_conn:
            self.db_conn = self.connect_db()
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM usuarios_sistema WHERE rol = 'seguridad'")
            total = cursor.fetchone()[0] + 1

            apellido = self.form_fields['apellidos'].text().strip().upper()
            nombre = self.form_fields['nombre'].text().strip().upper()

            inicial_nombre = nombre[0] if nombre else ''
            partes_apellido = apellido.split()
            iniciales_apellido = ''.join([p[0] for p in partes_apellido[:2]])

            usuario_generado = f'US{total:03}{inicial_nombre}{iniciales_apellido}'
            self.usuario_field.setText(usuario_generado)
        except Exception as e:
            print(f"Error generando usuario: {e}")

    def create_lineedit(self, placeholder, validator, is_dni=False, is_readonly=False):
        field = QLineEdit()
        field.setPlaceholderText(placeholder)

        if is_readonly:
            field.setStyleSheet("""
                QLineEdit {
                    font-family: 'Poppins';
                    font-size: 11px;
                    border: 1px solid #e0e0e0;
                    border-radius: 5px;
                    padding: 8px 12px;
                    min-height: 25px;
                    background-color: #f5f5f5;
                    color: #555;
                }
            """)
            field.setReadOnly(True)
            field.setFocusPolicy(Qt.NoFocus)
        else:
            field.setStyleSheet("""
                QLineEdit {
                    font-family: 'Poppins';
                    font-size: 11px;
                    border: 1px solid #e0e0e0;
                    border-radius: 5px;
                    padding: 8px 12px;
                    min-height: 25px;
                    background-color: white;
                }
                QLineEdit:focus {
                    border: 1px solid #0F7E8D;
                }
            """)
            if validator:
                field.setValidator(validator)

            if is_dni:
                field.textEdited.connect(self.validate_dni)

        return field

    def create_combobox(self):
        field = QComboBox()
        field.addItems(["Seleccione un cargo", "Personal de Seguridad", "Administrativo", "Ejecutivo", "Desarrollador", "Limpieza", "Soporte"])

        class ComboBoxDelegate(QStyledItemDelegate):
            def sizeHint(self, option, index):
                size = super().sizeHint(option, index)
                size.setHeight(40)
                return size

        field.setItemDelegate(ComboBoxDelegate())
        field.setStyleSheet("""
            QComboBox {
                font-family: 'Poppins';
                font-size: 11px;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                padding: 8px;
                min-height: 35px;
                background-color: white;
            }
            QComboBox::drop-down {
                width: 25px;
                border: none;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 5px 0;
            }
        """)
        return field

    def validate_dni(self):
        dni_field = self.form_fields['dni']
        dni = dni_field.text().strip()

        if len(dni) == 8:
            self.show_message("Validando", "Consultando RENIEC...")
            self.worker = ApiPeruWorker(dni)
            self.worker.finished.connect(self.handle_apiperu_response)
            self.worker.error.connect(self.show_message)
            self.worker.start()

    def handle_apiperu_response(self, data):
        try:
            if 'nombres' in data:
                self.form_fields['nombre'].setText(data['nombres'])
            if 'apellido_paterno' in data and 'apellido_materno' in data:
                apellidos = f"{data['apellido_paterno']} {data['apellido_materno']}"
                self.form_fields['apellidos'].setText(apellidos)

            if self.form_fields['cargo'].currentText() == "Personal de Seguridad":
                self.generar_usuario_seguridad()

            self.show_message("Éxito", "DNI validado correctamente")
        except Exception as e:
            self.show_message("Error", f"Error al procesar respuesta: {str(e)}")

    def setup_form_buttons(self, layout):
        buttons_container = QWidget()
        buttons_container.setStyleSheet("background-color: white;")
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 20, 0, 0)
        buttons_layout.setSpacing(10)

        self.btn_capturar = QPushButton("📸 Capturar")
        self.btn_capturar.setFixedSize(100, 45)
        self.btn_capturar.setStyleSheet("""
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
        self.btn_capturar.clicked.connect(self.capture_image)

        self.btn_borrar = QPushButton("Borrar")
        self.btn_borrar.setFixedSize(120, 45)
        self.btn_borrar.setStyleSheet("""
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
        self.btn_borrar.clicked.connect(self.clear_form)

        self.btn_guardar = QPushButton("Registrar")
        self.btn_guardar.setFixedSize(120, 45)
        self.btn_guardar.setStyleSheet("""
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
        self.btn_guardar.clicked.connect(self.save_registration)

        buttons_layout.addStretch()
        buttons_layout.addWidget(self.btn_capturar)
        buttons_layout.addWidget(self.btn_borrar)
        buttons_layout.addWidget(self.btn_guardar)
        layout.addWidget(buttons_container)

    def init_camera(self):

        if self.cam is not None and self.cam.isOpened():
            self.cam.release()


        self.cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.cam.isOpened():

            self.cam = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        if not self.cam.isOpened():
            self.video_label.setText("No se pudo acceder a la cámara.\nVerifique que no esté siendo usada por otra aplicación.")
            self.show_message("Error", "No se pudo acceder a la cámara.\nVerifique que no esté siendo usada por otra aplicación.")
            self.camera_active = False
            return

        self.camera_active = True
        self.intentos_camara = 0

        if self.timer is None:
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_camera_view)
        self.timer.start(30)

    def reintentar_camara(self):
        """Reintenta abrir la cámara después de un fallo."""
        if self.timer:
            self.timer.stop()
        self.init_camera()
        if self.camera_active:
            self.timer.start(30)

    def update_camera_view(self):
        """Actualización de cámara con manejo de fallos."""
        if not self.camera_active or not self.cam:
            return

        ret, frame = self.cam.read()
        if not ret or frame is None:
            # Si falla varias veces seguidas, intentamos reinicializar la cámara
            self.intentos_camara += 1
            if self.intentos_camara > 5:
                self.video_label.setText("Error de cámara. Reintentando...")
                self.camera_active = False
                # Intentar reiniciar después de 1 segundo
                QTimer.singleShot(1000, self.reintentar_camara)
            return
        else:
            self.intentos_camara = 0

        try:
            frame_resized = cv2.resize(frame, (600, 450))
            rgb_frame = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)

            if not hasattr(self, 'frame_count'): self.frame_count = 0
            self.frame_count += 1

            if self.frame_count % 5 == 0:
                face_locations = face_recognition.face_locations(rgb_frame)
                for (top, right, bottom, left) in face_locations:
                    cv2.rectangle(rgb_frame, (left, top), (right, bottom), (0, 255, 0), 2)

            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            q_img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(q_img))
        except Exception as e:
            print(f"Error en video: {e}")

    def capture_image(self):
        if not self.camera_active or not self.cam:
            self.show_message("Error", "La cámara no está disponible")
            return

        dni = self.form_fields['dni'].text().strip()
        if not dni or len(dni) != 8:
            self.show_message("Error", "Debe ingresar un DNI válido (8 dígitos)")
            return

        ret, frame = self.cam.read()
        if not ret or frame is None:
            self.show_message("Error", "No se pudo capturar la imagen. Intente nuevamente.")
            return

        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb_frame = np.ascontiguousarray(rgb_frame, dtype=np.uint8)

            face_locations = face_recognition.face_locations(rgb_frame)

            if len(face_locations) != 1:
                self.show_message("Advertencia", "Debe haber exactamente un rostro visible")
                return

            face_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]
            encoding_binary = pickle.dumps(face_encoding)

            img_path = os.path.join("imagenes", f"{dni}_{len(self.captured_images) + 1}.jpg")
            if not os.path.exists("imagenes"):
                os.makedirs("imagenes")

            cv2.imwrite(img_path, frame)
            self.captured_images.append((img_path, encoding_binary))

            self.lbl_fotos_capturadas.setText(f"{len(self.captured_images)} / 6 fotos capturadas")

            if len(self.captured_images) >= 6:
                self.show_message("Éxito", "Se han capturado las 6 fotos requeridas")
        except Exception as e:
            print(f"Error en captura: {e}")
            self.show_message("Error", "Ocurrió un error al capturar la foto. Intente nuevamente.")

    def save_registration(self):
        nombre = self.form_fields['nombre'].text().strip()
        apellidos = self.form_fields['apellidos'].text().strip()
        dni = self.form_fields['dni'].text().strip()
        cargo = self.form_fields['cargo'].currentText()

        usuario = ""
        contrasena = ""
        user_id = None

        if cargo == "Seleccione un cargo":
            cargo = ""

        if not all([nombre, apellidos, dni, cargo]):
            self.show_message("Error", "Todos los campos obligatorios deben estar completos")
            return

        if len(dni) != 8 or not dni.isdigit():
            self.show_message("Error", "El DNI debe tener exactamente 8 dígitos")
            return

        if len(self.captured_images) < 6:
            self.show_message("Advertencia", "Debe capturar al menos 6 fotos para el registro")
            return

        try:
            cursor = self.db_conn.cursor()

            # Ejecutar SP para insertar personal y obtener el ID generado
            cursor.execute("EXEC sp_registrar_personal ?, ?, ?, ?, ?", nombre, apellidos, dni, cargo, 0)
            cursor.nextset()
            row = cursor.fetchone()
            person_id = row[0] if row else None

            if not person_id or person_id == 0:
                self.show_message("Error", "El DNI ya está registrado en el sistema")
                self.db_conn.rollback()
                return

            if cargo.strip().lower() == "personal de seguridad":
                contrasena = self.contrasena_field.text().strip()

                if not contrasena:
                    self.show_message("Error", "Debe ingresar una contraseña para el usuario")
                    return

                if len(contrasena) < 6:
                    self.show_message("Error", "La contraseña debe tener al menos 6 caracteres")
                    return


                inicial_nombre = nombre.strip().split()[0][0].upper() if nombre.strip() else ''
                apellidos_parts = apellidos.strip().upper().split()
                iniciales_apellido = ''.join([p[0] for p in apellidos_parts[:2]])
                cursor.execute("SELECT COUNT(*) FROM usuarios_sistema WHERE rol = 'seguridad'")
                count = cursor.fetchone()[0] + 1
                usuario = f"US{count:03}{inicial_nombre}{iniciales_apellido}"

                self.usuario_field.setText(usuario)

                # Insertar en usuarios_sistema
                cursor.execute("""
                    INSERT INTO usuarios_sistema (nombre, usuario, contrasena, rol, id_personal)
                    VALUES (?, ?, ?, ?, ?)
                """, (nombre, usuario, contrasena, "seguridad", person_id))

            # Insertar fotos en tabla con procedimiento almacenado
            for img_path, encoding in self.captured_images:
                cursor.execute(
                    "{CALL sp_insertar_foto_personal (?, ?, ?, ?)}",
                    (person_id, img_path, encoding, 0)
                )

            self.db_conn.commit()
            self.show_message("Éxito", "Registro completado correctamente")
            self.clear_form()

        except pyodbc.IntegrityError as e:
            error_msg = str(e)
            if "Violation of UNIQUE KEY constraint" in error_msg and "UQ_personal__D87608A783FCA2A6" in error_msg:
                self.show_message("Error", "El DNI ingresado ya está registrado en el sistema.")
            else:
                self.show_message("Error", f"Error de integridad:\n{error_msg}")
            self.db_conn.rollback()

        except pyodbc.Error as e:
            self.show_message("Error", f"No se pudo completar el registro:\n{str(e)}")
            self.db_conn.rollback()

        except Exception as e:
            self.show_message("Error", f"Error inesperado:\n{str(e)}")

    def clear_form(self):
        for field_name, field in self.form_fields.items():
            if isinstance(field, QLineEdit):
                is_readonly = field.isReadOnly()
                field.clear()
                if field_name in ['nombre', 'apellidos']:
                    field.setReadOnly(True)
                    field.setFocusPolicy(Qt.NoFocus)
            elif isinstance(field, QComboBox):
                field.setCurrentIndex(0)

        self.usuario_field.clear()
        self.contrasena_field.clear()
        self.security_fields_container.setVisible(False)

        self.captured_images = []
        self.lbl_fotos_capturadas.setText("0 / 6 fotos capturadas")

    def show_message(self, title, message, icon=QMessageBox.Information):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(icon)
        msg.setStyleSheet("""
            QMessageBox {
                font-family: 'Poppins';
                background-color: white;
            }
            QMessageBox QLabel {
                color: #333333;
            }
            QMessageBox QPushButton {
                min-width: 80px;
                padding: 5px;
            }
        """)
        msg.exec_()

    def closeEvent(self, event):
        if self.camera_active and self.cam:
            self.camera_active = False
            if self.timer:
                self.timer.stop()
            self.cam.release()

        if self.db_conn:
            self.db_conn.close()

        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("* { font-family: 'Poppins'; }")
    window = PersonalRegistrationPage()
    window.show()
    sys.exit(app.exec_())