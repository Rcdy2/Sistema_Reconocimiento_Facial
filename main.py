import sys
from PyQt5.QtGui import QFont, QFontDatabase, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QStackedWidget, QHBoxLayout, QVBoxLayout, QLabel, \
    QPushButton, QSpacerItem, QSizePolicy, QMessageBox
from PyQt5.QtCore import Qt, QSize
from Login1 import LoginPage  # Importación local para evitar circular imports

from sidebar import CustomSidebar
from registrarpersonal import PersonalRegistrationPage
from listaEmpleados import EmployeesListPage
from dashboard import DashboardPage
from listaAsistencia import AsistenciaListPage


class ModernAdminPanel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_main_window()
        self.load_fonts()
        self.setup_ui()
        self.setup_window_controls()
        self.login_window = None

    def setup_main_window(self):
        self.setWindowTitle("CFBD S.A.C - Panel Administrativo")
        self.setFixedSize(1280, 720)
        self.setStyleSheet("background-color: #ECECF0; border: none;")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.center_window()

    def setup_window_controls(self):
        self.control_buttons = QWidget(self)
        self.control_buttons.setStyleSheet("background-color: transparent;")
        self.control_buttons.setFixedSize(105, 30)

        buttons_layout = QHBoxLayout(self.control_buttons)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(3)

        btn_minimize = QPushButton()
        btn_minimize.setFixedSize(30, 30)
        btn_minimize.setIcon(QIcon("icons/Recurso 14Con_Colores.png"))
        btn_minimize.setIconSize(QSize(12, 12))
        btn_minimize.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
            }
        """)
        btn_minimize.clicked.connect(self.showMinimized)

        self.btn_maximize = QPushButton()
        self.btn_maximize.setFixedSize(30, 30)
        self.btn_maximize.setIcon(QIcon("icons/Recurso 5Con_Colores.png"))
        self.btn_maximize.setIconSize(QSize(12, 12))
        self.btn_maximize.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
            }
        """)
        self.btn_maximize.clicked.connect(self.toggle_maximize)

        btn_close = QPushButton()
        btn_close.setFixedSize(30, 30)
        btn_close.setIcon(QIcon("icons/Recurso 3Con_Colores.png"))
        btn_close.setIconSize(QSize(10, 10))
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #F04747;
            }
        """)
        btn_close.clicked.connect(self.close)

        buttons_layout.addWidget(btn_minimize)
        buttons_layout.addWidget(self.btn_maximize)
        buttons_layout.addWidget(btn_close)

        self.control_buttons.move(self.width() - 104, 1)
        self.control_buttons.raise_()

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
            self.btn_maximize.setIcon(QIcon("icons/maximizar.png"))
        else:
            self.showMaximized()
            self.btn_maximize.setIcon(QIcon("icons/restore.png"))
        self.control_buttons.move(self.width() - 105, 10)

    def center_window(self):
        frame_geometry = self.frameGeometry()
        center_point = QApplication.desktop().availableGeometry().center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())

    def load_fonts(self):
        font_dir = "fonts/"
        QFontDatabase.addApplicationFont(font_dir + "Poppins-Medium.ttf")
        QFontDatabase.addApplicationFont(font_dir + "Poppins-Regular.ttf")

    def setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Barra lateral
        self.sidebar = CustomSidebar()
        self.main_layout.addWidget(self.sidebar)

        # Área de contenido
        self.content_stack = QStackedWidget()
        self.main_layout.addWidget(self.content_stack, stretch=4)

        # Configurar páginas
        self.setup_pages()

        # Conectar señales de la barra lateral
        self.connect_sidebar_signals()

    def setup_pages(self):
        # Dashboard principal
        self.dashboard_page = DashboardPage()

        # Página de registro de usuarios
        self.registration_page = PersonalRegistrationPage()

        # Página de lista de empleados
        self.employees_list_page = EmployeesListPage()
        self.asistencia_list_page = AsistenciaListPage()

        # Agregar páginas al stack
        self.content_stack.addWidget(self.dashboard_page)
        self.content_stack.addWidget(self.registration_page)
        self.content_stack.addWidget(self.employees_list_page)
        self.content_stack.addWidget(self.asistencia_list_page)

    def connect_sidebar_signals(self):
        """Conecta las señales de la barra lateral"""
        self.sidebar.dashboard_clicked.connect(self.show_dashboard)
        self.sidebar.registration_clicked.connect(self.show_registration)
        self.sidebar.users_list_clicked.connect(self.show_employees_list)
        self.sidebar.asistencia_list_clicked.connect(self.show_asistencia_list)
        self.sidebar.logout_clicked.connect(self.handle_logout)
        # Mostrar dashboard por defecto
        self.show_dashboard()

    def show_dashboard(self):
        """Muestra la página del dashboard"""
        self.content_stack.setCurrentWidget(self.dashboard_page)
        self.sidebar.set_active_button("Dashboard")
        if hasattr(self.dashboard_page, 'load_data'):
            self.dashboard_page.load_data()

    def show_registration(self):
        """Muestra la página de registro"""
        self.content_stack.setCurrentWidget(self.registration_page)
        self.sidebar.set_active_button("Registro de Usuarios")

    def show_employees_list(self):
        """Muestra la página de lista de empleados"""
        self.content_stack.setCurrentWidget(self.employees_list_page)
        self.sidebar.set_active_button("Lista de Usuarios")
        if hasattr(self.employees_list_page, 'load_data'):
            self.employees_list_page.load_data()

    def show_asistencia_list(self):
        """Muestra la página de lista de empleados"""
        self.content_stack.setCurrentWidget(self.asistencia_list_page)
        self.sidebar.set_active_button("Control de Asistencia")
        if hasattr(self.asistencia_list_page, 'load_data'):
            self.asistencia_list_page.load_data()

    def handle_logout(self):
        """cierre de sesión y muestra la ventana de login"""

        reply = QMessageBox.question(
            self, 'Cerrar sesión',
            '¿Estás seguro que deseas cerrar sesión?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Crear y mostrar ventana de login
            self.login_window = LoginPage()
            self.login_window.show()

            # Cerrar ventana actual
            self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Configurar fuente global
    app_font = QFont('Poppins Medium', 12)
    app_font.setWeight(QFont.Medium)
    app.setFont(app_font)

    window = ModernAdminPanel()
    window.show()

    sys.exit(app.exec_())