from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame, QTableWidget,
                             QTableWidgetItem, QHeaderView, QPushButton, QHBoxLayout,
                             QMessageBox, QDialog, QLineEdit, QSizePolicy, QScrollArea)
from PyQt5.QtGui import QIcon, QFont, QPixmap, QPainter, QColor, QIntValidator, QRegExpValidator
from PyQt5.QtCore import Qt, QSize, QRegExp
from database_connection import get_db_connection
import pyodbc


class AsistenciaListPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_data()  # Cargar datos al inicializar

    def setup_ui(self):
        """Configura la interfaz principal"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(65, 60, 0, 0)
        self.main_layout.setSpacing(0)

        # Configurar contenido principal
        self.setup_main_content()

    def setup_main_content(self):
        """Configura el área de contenido principal"""
        # Contenedor principal con tamaño fijo
        self.content = QFrame()
        self.content.setFixedSize(900, 600)
        self.content.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 0px;

            }
        """)

        # Layout del contenido
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(40, 40, 40, 40)
        self.content_layout.setSpacing(11)

        # Configurar componentes
        self.setup_title()
        self.setup_search_box()
        self.setup_table()
        self.setup_action_buttons()

        # Añadir el contenido dentro de un QScrollArea para mejor manejo del espacio
        scroll = QScrollArea()
        scroll.setWidget(self.content)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        self.main_layout.addWidget(scroll)

    def setup_title(self):
        """Configura el título de la página"""
        title_container = QFrame()
        title_container.setStyleSheet("background-color: transparent;")
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 7)

        self.title_label = QLabel("CONTROL DE ASISTENCIA")
        self.title_label.setStyleSheet("""
            QLabel {
                font-family: 'Open Sans';
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                padding-bottom: 1px;
            }
        """)
        self.title_label.setAlignment(Qt.AlignCenter)

        title_layout.addWidget(self.title_label)
        self.content_layout.addWidget(title_container)

    def setup_search_box(self):
        """Configura el cuadro de búsqueda con icono"""
        search_container = QFrame()
        search_container.setStyleSheet("""
            QFrame {
                background-color: transparent;
                padding: 0;
            }
        """)

        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(10)

        # Campo de búsqueda
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Buscar empleado...")
        self.search_field.setStyleSheet("""
            QLineEdit {
                font-family: 'Open Sans';
                font-size: 11px;
                padding: 10px 15px;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #0F7E8D;
            }
        """)
        self.search_field.setMinimumHeight(40)

        # Botón de búsqueda con icono y texto
        search_btn = QPushButton(" Buscar")
        search_btn.setIcon(QIcon("icons/Recurso 7A_Blanco.png"))
        search_btn.setIconSize(QSize(16, 16))
        search_btn.setFixedSize(100, 40)
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #0F7E8D;
                color: white;
                border-radius: 6px;
                border: none;
                font-family: 'Open Sans';
                font-size: 11px;
                padding-left: 10px;
                padding-right: 15px;
            }
            QPushButton:hover {
                background-color: #0d6e7b;
            }
            QPushButton:pressed {
                background-color: #0b5d6a;
            }
        """)
        search_btn.clicked.connect(self.search_employee)

        search_layout.addWidget(self.search_field)
        search_layout.addWidget(search_btn)

        self.content_layout.addWidget(search_container)

    def setup_table(self):

        table_container = QFrame()
        table_container.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border-radius: 0;
                padding: 0;
            }
        """)

        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "NOMBRE", "APELLIDO", "DNI", "CARGO", "FECHA ASISTENCIA"])

        header = self.table.horizontalHeader()

        # Configuración del cabezal
        header.setFixedHeight(40)
        header.setDefaultAlignment(Qt.AlignCenter)
        header.setHighlightSections(False)
        self.table.setStyleSheet("""
            QTableWidget {
                border: none;
                font-family: 'Open Sans';
                font-size: 10px;
                alternate-background-color: #f9f9f9;
                selection-background-color: #e3f2fd;
                selection-color: #000;
                border-radius: 0 0 8px 8px;
                background-color: white;
            }

            QHeaderView {
                background-color: transparent;
                border: none;
            }

            QHeaderView::section {
                background-color: #0F7E8D;
                color: white;
                padding: 12px;
                font-family: 'Open Sans';
                font-size: 10px;
                border: none;
                border-left: 1px solid rgba(255, 255, 255, 0.2);
            }

            QHeaderView::section:first {
                border-left: none;
                border-top-left-radius: 5px;
                border-bottom-left-radius: 5px;
            }

            QHeaderView::section:last {
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
            }

            QTableCornerButton::section {
                background-color: #0F7E8D;
                border-top-left-radius: 8px;
            }

            /* Estilo para las filas al pasar el mouse */
            QTableWidget::item:hover {
                background-color: #e3f2fd;
            }

            /* Estilo para resaltar toda la fila al pasar el mouse */
            QTableWidget {
                gridline-color: transparent;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: black;
            }
            QTableWidget::item:hover {
                background-color: #e3f2fd;
            }

            QScrollBar:vertical {
                border: none;
                background: #f5f5f5;
                width: 5px;
                margin: 0;
            }

            QScrollBar::handle:vertical {
                background: #c1c1c1;
                min-height: 20px;
                border-radius: 20px;
            }

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
                background: none;
            }
        """)

        self.table.setMouseTracking(True)
        self.table.viewport().setAttribute(Qt.WA_Hover)

        # Ajustes de visualización

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.setColumnWidth(0, 60)  # ID
        self.table.setColumnWidth(1, 150)  # Nombre
        self.table.setColumnWidth(2, 150)  # Apellido
        self.table.setColumnWidth(3, 100)  # DNI
        self.table.setColumnWidth(4, 180)  # Cargo
        self.table.setColumnWidth(5, 150)  # Fecha Registro
        self.table.horizontalHeader().setStretchLastSection(True)

        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setDefaultSectionSize(35)
        # Eliminar el borde punteado de enfoque
        self.table.setFocusPolicy(Qt.NoFocus)

        # Asegurar que el cabezal tenga esquinas redondeadas?
        self.table.setViewportMargins(0, 0, 0, 0)

        table_layout.addWidget(self.table)
        self.content_layout.addWidget(table_container,
                                      1)  # para que ocupe el espacio disponible

    def setup_action_buttons(self):

        buttons_container = QFrame()
        buttons_container.setStyleSheet("background-color: transparent;")
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 10, 0, 0)
        buttons_layout.setSpacing(15)

        # Botón Actualizar
        self.refresh_btn = QPushButton("Actualizar")
        self.refresh_btn.setFixedSize(120, 40)
        self.refresh_btn.setIcon(QIcon("icons/refresh.png"))
        self.refresh_btn.setIconSize(QSize(16, 16))
        self.refresh_btn.clicked.connect(self.load_data)
        self.refresh_btn.setStyleSheet("""
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


        # Espaciador
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        buttons_layout.addWidget(self.refresh_btn)
        buttons_layout.addWidget(spacer)

        self.content_layout.addWidget(buttons_container)

    def create_button(self, text, color, hover_color, icon_path, callback):

        btn = QPushButton(text)
        btn.setFixedSize(120, 40)
        btn.setIcon(QIcon(f"icons/{icon_path}"))
        btn.setIconSize(QSize(16, 16))
        btn.clicked.connect(callback)

        btn.setStyleSheet(f"""
            QPushButton {{
                font-family: 'Poppins Medium';
                font-size: 12px;
                background-color: {color};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """)

        return btn

    def connect_db(self):

        return get_db_connection()

    def load_data(self):

        conn = self.connect_db()
        if not conn:
            return

        try:
            cursor = conn.cursor()
            query = """
            SELECT 
                CASE 
                    WHEN us.id IS NOT NULL THEN us.id  -- 'U001', 'U002' si es de seguridad
                    ELSE CAST(p.id AS VARCHAR)         -- ID numérico si no está en usuarios_sistema
                END AS id,
                p.nombre,
                p.apellido,
                p.dni,
                p.cargo,
                p.fecha_registro
            FROM personal p
            LEFT JOIN usuarios_sistema us ON p.id = us.id_personal
            """
            cursor.execute(query)

            data = cursor.fetchall()

            self.table.setRowCount(0)

            for row_num, row_data in enumerate(data):
                self.table.insertRow(row_num)
                for col_num, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value).strip())
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row_num, col_num, item)

            conn.close()
        except Exception as e:
            self.show_message("Error", f"No se pudieron cargar los datos:\n{str(e)}", QMessageBox.Critical)

    def search_employee(self):

        search_text = self.search_field.text().strip().lower()
        if not search_text:
            self.load_data()
            return

        conn = self.connect_db()
        if not conn:
            return

        try:
            cursor = conn.cursor()
            query = """
                SELECT p.id, p.nombre, p.apellido, p.dni, p.cargo, a.fecha_hora 
                FROM personal p
                INNER JOIN [dbo].[asistencias] a ON a.id_personal = p.id
                WHERE LOWER(p.nombre) LIKE ? OR LOWER(p.apellido) LIKE ? OR p.dni LIKE ? 
            """
            search_param = f"%{search_text}%"
            cursor.execute(query, (search_param, search_param, search_param))
            data = cursor.fetchall()

            self.table.setRowCount(0)

            for row_num, row_data in enumerate(data):
                self.table.insertRow(row_num)
                for col_num, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value).strip())
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row_num, col_num, item)

            conn.close()
        except Exception as e:
            self.show_message("Error", f"No se pudieron cargar los datos:\n{str(e)}", QMessageBox.Critical)

    def delete_employee(self):
        """Elimina el empleado seleccionado"""
        selected = self.table.selectedItems()
        if not selected:
            self.show_message("Advertencia", "Por favor, seleccione un empleado para eliminar.", QMessageBox.Warning)
            return

        row = selected[0].row()
        emp_id = self.table.item(row, 0).text()
        name = f"{self.table.item(row, 1).text()} {self.table.item(row, 2).text()}"

        confirm = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            f"¿Está seguro que desea eliminar al empleado:\n\n{name} (ID: {emp_id})?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            try:
                conn = self.connect_db()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM personal WHERE id = ?", (emp_id,))
                conn.commit()
                conn.close()

                self.show_message("Éxito", f"Empleado {name} eliminado correctamente.", QMessageBox.Information)
                self.load_data()
            except Exception as e:
                self.show_message("Error", f"No se pudo eliminar el empleado:\n{str(e)}", QMessageBox.Critical)

    def edit_employee(self):
        """Abre diálogo para editar empleado"""
        selected = self.table.selectedItems()
        if not selected:
            self.show_message("Advertencia", "Por favor, seleccione un empleado para editar.", QMessageBox.Warning)
            return

        row = selected[0].row()
        emp_data = {
            'id': self.table.item(row, 0).text(),
            'nombre': self.table.item(row, 1).text(),
            'apellido': self.table.item(row, 2).text(),
            'dni': self.table.item(row, 3).text(),
            'cargo': self.table.item(row, 4).text()
        }

        dialog = EmployeeEditDialog(self, emp_data)
        if dialog.exec_():
            self.load_data()

    def add_employee(self):
        """Abre diálogo para añadir nuevo empleado"""
        # Implementar lógica para añadir nuevo empleado
        self.show_message("Información", "Funcionalidad para añadir nuevo empleado no implementada aún.",
                          QMessageBox.Information)

    def show_message(self, title, message, icon):
        msg = QMessageBox(self)
        msg.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)

        # Configurar el ícono según el tipo de mensaje
        if icon == QMessageBox.Information:
            icon_color = "#0F7E8D"  # Azul turquesa para información
            icon_text = "INFO"
        elif icon == QMessageBox.Warning:
            icon_color = "#ffb347"  # Amarillo/naranja para advertencia
            icon_text = "ADVERTENCIA"
        elif icon == QMessageBox.Critical:
            icon_color = "#d32f2f"  # Rojo para error
            icon_text = "ERROR"
        else:
            icon_color = "#0F7E8D"  # Por defecto azul turquesa
            icon_text = "MENSAJE"

        # Estilo personalizado
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

        # Configurar el contenido del mensaje
        msg.setWindowTitle(title)
        msg.setText(f"<b>{icon_text}</b>")
        msg.setInformativeText(message)

        # Botón OK
        ok_button = msg.addButton("Aceptar", QMessageBox.AcceptRole)
        ok_button.setCursor(Qt.PointingHandCursor)

        return msg.exec_()

    def darken_color(self, hex_color, percent):
        """Función auxiliar para oscurecer un color hex"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
        darkened = tuple(max(0, int(c * (100 - percent) / 100)) for c in rgb)
        return '#%02x%02x%02x' % darkened


class EmployeeEditDialog(QDialog):
    """Diálogo para editar información de empleado"""

    def __init__(self, parent, employee_data):
        super().__init__(parent)
        self.employee_data = employee_data
        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz del diálogo"""
        self.setWindowTitle(f"Editar Empleado: {self.employee_data['nombre']} {self.employee_data['apellido']}")
        self.setFixedSize(450, 350)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)

        self.setStyleSheet("""
            QDialog {
                background-color: white;
                font-family: 'Poppins';
                border: 2px solid #0F7E8D;
                border-radius: 8px;
            }
            QLabel {
                font-family: 'Poppins Medium';
                color: #333333;
            }
            QLineEdit {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #0F7E8D;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Añadir los campos del formulario
        self.setup_form_fields(layout)

        # Añadir los botones del diálogo
        self.setup_dialog_buttons(layout)

    def setup_form_fields(self, layout):
        """Configura los campos del formulario"""
        form_frame = QFrame()
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(20)

        # Nombre
        self.name_field = self.create_form_row("Nombre:", self.employee_data['nombre'], form_layout)
        self.name_field.setValidator(QRegExpValidator(QRegExp("[a-zA-ZáéíóúÁÉÍÓÚñÑ ]+")))

        # Apellido
        self.lastname_field = self.create_form_row("Apellido:", self.employee_data['apellido'], form_layout)
        self.lastname_field.setValidator(QRegExpValidator(QRegExp("[a-zA-ZáéíóúÁÉÍÓÚñÑ ]+")))

        # DNI
        self.dni_field = self.create_form_row("DNI:", self.employee_data['dni'], form_layout)
        self.dni_field.setValidator(QIntValidator(10000000, 99999999))

        # Cargo
        self.position_field = self.create_form_row("Cargo:", self.employee_data['cargo'], form_layout)

        layout.addWidget(form_frame)

    def create_form_row(self, label, value, layout):
        """Crea una fila del formulario"""
        row = QFrame()
        row.setStyleSheet("background-color: white;")
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(10)

        lbl = QLabel(label)
        lbl.setStyleSheet("font-family: 'Poppins Medium';" "background-color: white;")
        lbl.setFixedWidth(100)

        field = QLineEdit(value)
        field.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #0F7E8D;
            }
        """)

        row_layout.addWidget(lbl)
        row_layout.addWidget(field)
        layout.addWidget(row)

        return field

    def setup_dialog_buttons(self, layout):
        """Configura los botones del diálogo"""
        buttons_frame = QFrame()
        buttons_layout = QHBoxLayout(buttons_frame)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(15)

        # Botón Guardar
        save_btn = QPushButton("Guardar Cambios")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #0F7E8D;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-family: 'Poppins Medium';
            }
            QPushButton:hover {
                background-color: #0d6e7b;
            }
        """)
        save_btn.clicked.connect(self.accept)

        # Botón Cancelar
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-family: 'Poppins Medium';
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        cancel_btn.clicked.connect(self.reject)

        buttons_layout.addStretch()
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addWidget(buttons_frame)

    def save_changes(self):
        """trae los datos del formulario y los guarda en la base de datos"""
        # para validar campos obligatorios
        if not all([
            self.name_field.text().strip(),
            self.lastname_field.text().strip(),
            self.dni_field.text().strip(),
            self.position_field.text().strip()
        ]):
            self.parent().show_message("Error", "Todos los campos son obligatorios", QMessageBox.Warning)
            return False

        # Validar DNI
        if len(self.dni_field.text().strip()) != 8:
            self.parent().show_message("Error", "El DNI debe tener 8 dígitos", QMessageBox.Warning)
            return False

        conn = self.parent().connect_db()
        if not conn:
            return False

        try:
            cursor = conn.cursor()
            query = """
                UPDATE personal 
                SET nombre = ?, apellido = ?, dni = ?, cargo = ?
                WHERE id = ?
            """
            cursor.execute(query, (
                self.name_field.text().strip(),
                self.lastname_field.text().strip(),
                self.dni_field.text().strip(),
                self.position_field.text().strip(),
                self.employee_data['id']
            ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            self.parent().show_message("Error", f"No se pudieron guardar los cambios:\n{str(e)}", QMessageBox.Critical)
            return False

    def accept(self):
        """Sobrescribir el método accept para guardar antes de cerrar"""
        if self.save_changes():
            super().accept()


