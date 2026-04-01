import numpy as np
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
                             QPushButton, QSizePolicy, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QComboBox)
from PyQt5.QtGui import QFont, QPixmap, QIcon, QColor, QPainter
from PyQt5.QtCore import Qt, QSize, QTimer
import pyodbc
from datetime import datetime
from database_connection import get_db_connection
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import time


class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.data_cache = {
            'metrics': {'timestamp': None, 'data': None},
            'attendance': {'timestamp': None, 'data': None},
            'roles': {'timestamp': None, 'data': None}
        }

        self.setup_ui()
        self.load_data()  # Carga inicial de datos

        # Configurar timer para actualización automática
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(30000)  # 30 segundos

    def setup_ui(self):
        """Configura la interfaz principal del dashboard"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(40, 40, 40, 40)
        self.main_layout.setSpacing(20)

        # Título del dashboard
        title = QLabel("DashBoard")
        title.setStyleSheet("font-family: 'Poppins Medium'; font-size: 16px;")
        self.main_layout.addWidget(title)

        # Fila de métricas rápidas
        self.setup_metrics_row()

        # Fila de gráficos
        self.setup_charts_row()

        # Últimos registros y alertas
        self.setup_activity_section()

    def refresh_data(self):
        """Método para refrescar datos sin recursión"""
        try:
            self.load_metrics()
            self.load_charts()
            self.load_recent_activity()
            self.load_recent_alerts()
        except Exception as e:
            self.show_error_message(f"Error al actualizar datos: {str(e)}")

    def load_data(self):
        """Carga todos los datos para el dashboard"""
        try:
            self.load_metrics()
            self.load_charts()
            self.load_recent_activity()
            self.load_recent_alerts()
        except Exception as e:
            self.show_error_message(f"Error al cargar datos: {str(e)}")

    def setup_metrics_row(self):
        """Configura la fila con las métricas clave en estilo KPI moderno"""
        # Contenedor principal
        metrics_container = QFrame()
        metrics_container.setStyleSheet("""
            QFrame {
                background-color: transparent;
            }
        """)

        # Layout tipo grid (simulado con HBox y stretch)
        metrics_layout = QHBoxLayout(metrics_container)
        metrics_layout.setContentsMargins(0, 0, 0, 0)
        metrics_layout.setSpacing(20)  # gap: 1.5rem

        self.metrics = [
            {"title": "Empleados Registrados", "value": "0", "icon": "icons/usuarios (2).png",
             "color": "#0F7E8D", "query": "SELECT COUNT(*) FROM personal", "key": "total_employees",
             "trend": "up", "trend_value": "12%", "comparison": "vs mes anterior"},
            {"title": "Ingresos Hoy", "value": "0", "icon": "icons/login_today.png",
             "color": "#0F7E8D",
             "query": "SELECT COUNT(DISTINCT id_personal) FROM asistencias WHERE CONVERT(date, fecha_hora) = CONVERT(date, GETDATE())",
             "key": "today_entries", "trend": "up", "trend_value": "0%", "comparison": "vs ayer"},
            {"title": "Ingresos Semanales", "value": "0", "icon": "icons/weekly.png",
             "color": "#0F7E8D",
             "query": "SELECT COUNT(DISTINCT id_personal) FROM asistencias WHERE DATEPART(week, fecha_hora) = DATEPART(week, GETDATE()) AND YEAR(fecha_hora) = YEAR(GETDATE())",
             "key": "weekly_entries", "trend": "up", "trend_value": "0%", "comparison": "vs semana anterior"},
            {"title": "Ingresos Mensuales", "value": "0", "icon": "icons/monthly.png",
             "color": "#0F7E8D",
             "query": "SELECT COUNT(DISTINCT id_personal) FROM asistencias WHERE MONTH(fecha_hora) = MONTH(GETDATE()) AND YEAR(fecha_hora) = YEAR(GETDATE())",
             "key": "monthly_entries", "trend": "up", "trend_value": "0%", "comparison": "vs mes anterior"},
        ]

        for metric in self.metrics:
            metric_widget = self.create_kpi_card(
                metric["title"],
                metric["value"],
                metric["icon"],
                metric["color"],
                metric.get("trend"),
                metric.get("trend_value"),
                metric.get("comparison", "")
            )
            metric["widget"] = metric_widget.findChild(QLabel, "value_label")
            metrics_layout.addWidget(metric_widget)

        self.main_layout.addWidget(metrics_container)

    def create_kpi_card(self, title, value, icon_path, color, trend=None, trend_value=None, comparison_text=""):
        """Crea una tarjeta KPI sin iconos"""
        # Tarjeta principal
        card = QFrame()
        card.setObjectName("KpiCard")
        card.setStyleSheet(f"""
            QFrame#KpiCard {{
                background: white;
                border-radius: 0px;
                padding: 15px;
                border-radius: 0px 0px 0px 0px;
                border-left: 4px solid {color};
                border-top: none;
                border-right: none;
                border-bottom: none;
            }}
            QLabel {{
                background-color: white;
            }}
        """)
        card.setFixedHeight(95)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Layout principal
        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Encabezado (solo título) - eliminado el icono
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-family: 'Poppins';
                font-size: 12px;
                color: #555;
                background-color: white;
            }
        """)
        layout.addWidget(title_label)

        # Valor KPI
        value_label = QLabel(value)
        value_label.setObjectName("value_label")
        value_label.setStyleSheet("""
            QLabel {
                font-family: 'Poppins Medium';
                font-size: 20px;
                font-weight: bold;
                color: #030238;
                background-color: white;
            }
        """)
        layout.addWidget(value_label)

        # Comparación y tendencia
        if trend or comparison_text:
            comparison = QWidget()
            comparison.setStyleSheet("background-color: white;")
            comparison_layout = QHBoxLayout(comparison)
            comparison_layout.setContentsMargins(0, 0, 0, 0)
            comparison_layout.setSpacing(5)

            if trend:
                trend_icon = QLabel("↑" if trend == "up" else "↓")
                trend_icon.setStyleSheet(f"""
                    QLabel {{
                        font-family: 'Poppins';
                        font-size: 10px;
                        font-weight: bold;
                        color: {'#2ecc71' if trend == 'up' else '#e74c3c'};
                        background-color: white;
                    }}
                """)
                comparison_layout.addWidget(trend_icon)

                trend_value_label = QLabel(trend_value)
                trend_value_label.setStyleSheet(f"""
                    QLabel {{
                        font-family: 'Poppins';
                        font-size: 11px;
                        font-weight: bold;
                        color: {'#2ecc71' if trend == 'up' else '#e74c3c'};
                        background-color: white;
                    }}
                """)
                comparison_layout.addWidget(trend_value_label)

            comparison_text_label = QLabel(comparison_text)
            comparison_text_label.setStyleSheet("""
                QLabel {
                    font-family: 'Poppins';
                    font-size: 11px;
                    color: #777;
                    background-color: white;
                }
            """)
            comparison_layout.addWidget(comparison_text_label)
            comparison_layout.addStretch()

            layout.addWidget(comparison)

        return card

    def setup_charts_row(self):
        """Configura la fila con gráficos estadísticos"""
        charts_frame = QFrame()
        charts_frame.setStyleSheet("background-color: transparent;")
        charts_layout = QHBoxLayout(charts_frame)
        charts_layout.setContentsMargins(0, 0, 0, 0)
        charts_layout.setSpacing(20)

        # Gráfico de asistencias con filtro de tiempo
        self.attendance_chart = self.create_chart_widget_with_filter("Asistencias por Período")
        self.attendance_chart.setFixedHeight(300)

        # Gráfico de distribución por cargo
        self.roles_chart = self.create_chart_widget("Distribución por Cargo")
        self.roles_chart.setFixedHeight(300)

        charts_layout.addWidget(self.attendance_chart)
        charts_layout.addWidget(self.roles_chart)

        self.main_layout.addWidget(charts_frame)

    def create_chart_widget(self, title):
        """Crea un widget de gráfico matplotlib básico"""
        chart_frame = QFrame()
        chart_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
            }
        """)

        chart_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QVBoxLayout(chart_frame)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Título
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-family: 'Poppins Medium';
                font-size: 13px;
            }
        """)
        layout.addWidget(title_label)

        # Figura matplotlib
        figure = plt.figure()
        canvas = FigureCanvas(figure)
        layout.addWidget(canvas)

        # Guardar referencias
        if "Distribución" in title:
            self.roles_figure = figure
            self.roles_canvas = canvas
        else:
            self.attendance_figure = figure
            self.attendance_canvas = canvas

        return chart_frame

    def create_chart_widget_with_filter(self, title):
        """Crea un widget de gráfico con combobox de filtro de tiempo"""
        chart_frame = QFrame()
        chart_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
            }
            QComboBox {
                font-family: 'Poppins';
                font-size: 11px;
                padding: 3px;
                border: 1px solid #ddd;
                border-radius: 4px;
                min-width: 120px;
                background-color: white;
            }
            
            QComboBox:hover {
                border: 1px solid #0F7E8D;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 15px;
            }
            
            QComboBox QAbstractItemView {
                font-family: 'Poppins';
                font-size: 11px;
                padding: 4px;
                border: 1px solid #ddd;
                background-color: white;
                outline: none;  /* Elimina el borde de enfoque */
            }
            
            QComboBox QAbstractItemView::item {
                padding: 5px;
                border: none;
                background-color: white;
                color: #555;
            }
            
            QComboBox QAbstractItemView::item:hover {
                background-color: #0F7E8D;
                color: #0F7E8D;  /* Color cuando el mouse pasa sobre el ítem */
            }
            
            QComboBox QAbstractItemView::item:selected {
                background-color: #0F7E8D;
                color: #0F7E8D;
            }
        """)

        chart_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QVBoxLayout(chart_frame)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Fila de título y combobox
        title_row = QWidget()
        title_row_layout = QHBoxLayout(title_row)
        title_row_layout.setContentsMargins(0, 0, 0, 0)
        title_row_layout.setSpacing(10)

        # Título
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-family: 'Poppins Medium';
                font-size: 13px;
            }
        """)
        title_row_layout.addWidget(title_label)
        title_row_layout.addStretch()

        # Combobox de filtro
        self.time_filter = QComboBox()
        self.time_filter.addItems(["Últimos 7 días", "Este mes", "Este año"])
        self.time_filter.setCurrentIndex(0)
        self.time_filter.currentIndexChanged.connect(self.update_attendance_chart)
        title_row_layout.addWidget(self.time_filter)

        layout.addWidget(title_row)

        # Figura matplotlib
        self.attendance_figure = plt.figure()
        self.attendance_canvas = FigureCanvas(self.attendance_figure)
        layout.addWidget(self.attendance_canvas)

        return chart_frame

    def update_attendance_chart(self):
        """Maneja el cambio de selección en el combobox"""
        self.generate_attendance_chart()

    def setup_activity_section(self):
        """Configura la sección de actividad con tabla compacta"""
        activity_frame = QFrame()
        activity_frame.setStyleSheet("background-color: transparent;")
        activity_layout = QHBoxLayout(activity_frame)
        activity_layout.setContentsMargins(0, 0, 0, 0)
        activity_layout.setSpacing(15)

        # Contenedor de últimas asistencias
        recent_frame = QFrame()
        recent_frame.setStyleSheet("background-color: white; border-radius: 8px;")
        recent_frame.setFixedHeight(165)
        recent_layout = QVBoxLayout(recent_frame)
        recent_layout.setContentsMargins(12, 12, 12, 12)
        recent_layout.setSpacing(8)

        # Título
        recent_title = QLabel("Últimas Asistencias")
        recent_title.setStyleSheet("""
            QLabel {
                font-family: 'Open Sans';
                font-size: 12px;
                
                color: #2c3e50;
                padding-bottom: 2px;
            }
        """)
        recent_layout.addWidget(recent_title)

        # Tabla
        self.recent_table = QTableWidget()
        self.recent_table.setColumnCount(5)
        self.recent_table.setHorizontalHeaderLabels(["Nombre", "Fecha/Hora", "Validado", "Estado", ""])

        # Estilo
        self.recent_table.setStyleSheet("""
            QTableWidget {
                border: none;
                font-family: 'Open Sans';
                font-size: 9px;
                alternate-background-color: #f9f9f9;
                selection-background-color: #e3f2fd;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #0F7E8D;
                color: white;
                padding: 6px;
                font-size: 9px;
                border: none;
            }
            QTableWidget::item {
                padding: 2px;
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
            QScrollBar::add-line:vertical, 
            QScrollBar::sub-line:vertical {
                height: 0;
                background: none;
            }
        """)

        # Configuración de columnas
        self.recent_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.recent_table.setColumnWidth(0, 180)
        self.recent_table.setColumnWidth(1, 120)
        self.recent_table.setColumnWidth(2, 90)
        self.recent_table.setColumnWidth(3, 130)
        self.recent_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)

        # Configuración general
        self.recent_table.verticalHeader().setVisible(False)
        self.recent_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.recent_table.setAlternatingRowColors(True)
        self.recent_table.setShowGrid(False)
        self.recent_table.verticalHeader().setDefaultSectionSize(28)
        self.recent_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.recent_table.setFocusPolicy(Qt.NoFocus)

        recent_layout.addWidget(self.recent_table)

        # Contenedor de alertas
        alerts_frame = QFrame()
        alerts_frame.setStyleSheet("background-color: white; border-radius: 8px;")
        alerts_frame.setFixedWidth(280)
        alerts_frame.setFixedHeight(165)
        alerts_layout = QVBoxLayout(alerts_frame)
        alerts_layout.setContentsMargins(12, 12, 12, 12)
        alerts_layout.setSpacing(8)

        # Título alertas
        alerts_title = QLabel("Alertas Recientes")
        alerts_title.setStyleSheet("""
            QLabel {
                font-family: 'Open Sans';
                font-size: 12px;
                
                color: #2c3e50;
                padding-bottom: 2px;
            }
        """)
        alerts_layout.addWidget(alerts_title)

        # Tabla de alertas
        self.alerts_list = QTableWidget()
        self.alerts_list.setColumnCount(3)
        self.alerts_list.setHorizontalHeaderLabels(["Fecha", "Tipo", "Descripción"])

        # Estilo
        self.alerts_list.setStyleSheet("""
            QTableWidget {
                border: none;
                font-family: 'Open Sans';
                font-size: 9px;
                alternate-background-color: #f9f9f9;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #e74c3c;
                color: white;
                padding: 6px;
                font-size: 9px;
                border: none;
            }
            QTableWidget::item {
                padding: 2px;
            }
        """)

        # Configuración
        self.alerts_list.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.alerts_list.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.alerts_list.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.alerts_list.verticalHeader().setVisible(False)
        self.alerts_list.setSelectionBehavior(QTableWidget.SelectRows)
        self.alerts_list.setAlternatingRowColors(True)
        self.alerts_list.setShowGrid(False)
        self.alerts_list.verticalHeader().setDefaultSectionSize(28)
        self.alerts_list.setEditTriggers(QTableWidget.NoEditTriggers)
        self.alerts_list.setFocusPolicy(Qt.NoFocus)

        alerts_layout.addWidget(self.alerts_list)

        activity_layout.addWidget(recent_frame)
        activity_layout.addWidget(alerts_frame)
        self.main_layout.addWidget(activity_frame)

    def load_metrics(self):
        """Carga las métricas desde la base de datos"""
        conn = self.connect_db()
        if not conn:
            return

        try:
            cursor = conn.cursor()

            for metric in self.metrics:
                cursor.execute(metric["query"])
                value = str(cursor.fetchone()[0])
                metric["widget"].setText(value)

            conn.close()
        except Exception as e:
            self.show_error_message(f"Error al cargar métricas: {str(e)}")

    def load_charts(self):
        """Genera los gráficos con datos actualizados"""
        self.generate_attendance_chart()
        self.generate_roles_chart()

    def generate_attendance_chart(self):
        """Genera el gráfico de asistencias según el filtro seleccionado"""
        time_range = self.time_filter.currentText()

        conn = self.connect_db()
        if not conn:
            return

        try:
            cursor = conn.cursor()

            # Definir consulta según el filtro seleccionado
            if time_range == "Últimos 7 días":
                query = """
                    SELECT CONVERT(date, fecha_hora) as fecha, COUNT(*) as total
                    FROM asistencias
                    WHERE fecha_hora >= DATEADD(day, -7, GETDATE())
                    GROUP BY CONVERT(date, fecha_hora)
                    ORDER BY fecha
                """
                date_format = "%d/%m"
                group_by = "day"
            elif time_range == "Este mes":
                query = """
                    SELECT DATEPART(day, fecha_hora) as dia, COUNT(*) as total
                    FROM asistencias
                    WHERE MONTH(fecha_hora) = MONTH(GETDATE()) 
                    AND YEAR(fecha_hora) = YEAR(GETDATE())
                    GROUP BY DATEPART(day, fecha_hora)
                    ORDER BY dia
                """
                date_format = "Día %d"
                group_by = "day_of_month"
            else:  # Este año
                query = """
                    SELECT DATEPART(month, fecha_hora) as mes, COUNT(*) as total
                    FROM asistencias
                    WHERE YEAR(fecha_hora) = YEAR(GETDATE())
                    GROUP BY DATEPART(month, fecha_hora)
                    ORDER BY mes
                """
                date_format = "Mes %m"
                group_by = "month"

            cursor.execute(query)
            data = cursor.fetchall()

            if not data:
                self.set_no_data_message(self.attendance_figure, "No hay datos de asistencias")
                self.attendance_canvas.draw()
                return

            # Procesar datos según el tipo de agrupación
            if group_by == "day":
                dates = [row[0].strftime(date_format) for row in data]
                counts = [row[1] for row in data]
            elif group_by == "day_of_month":
                dates = [date_format % row[0] for row in data]
                counts = [row[1] for row in data]
            else:  # month
                month_names = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
                               "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
                dates = [month_names[row[0] - 1] for row in data]
                counts = [row[1] for row in data]

            max_count = max(counts) if counts else 1

            self.attendance_figure.clear()
            ax = self.attendance_figure.add_subplot(111)

            # Configuración del estilo del gráfico
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['bottom'].set_visible(False)

            # Generar colores para cada barra
            def color_gradient(start_hex, end_hex, n):
                from matplotlib.colors import LinearSegmentedColormap, to_rgb
                start = to_rgb(start_hex)
                end = to_rgb(end_hex)
                cmap = LinearSegmentedColormap.from_list('custom', [start, end], N=n)
                return [cmap(i) for i in np.linspace(0, 1, n)]

            colors = color_gradient('#92CAD2', '#0F7E8D', len(dates))

            # Dibujar barras y agregar etiquetas con los valores
            bars = []
            for i, (date, count) in enumerate(zip(dates, counts)):
                bar = ax.bar(date, count, color=colors[i], width=0.55,
                             edgecolor='white', linewidth=0.5, zorder=3)
                bars.append(bar)

                # Agregar etiqueta con el valor encima de cada barra
                if count > 0:
                    ax.text(bar[0].get_x() + bar[0].get_width() / 2.,
                            count + (max_count * 0.02),
                            f'{count}',
                            ha='center', va='bottom',
                            fontsize=7, color='#555555')

                # LÍNEA HORIZONTAL EN EL TOPE DE CADA BARRA (SOLO LO QUE QUIERES)
                ax.hlines(y=count,
                          xmin=bar[0].get_x(),
                          xmax=bar[0].get_x() + bar[0].get_width(),
                          colors='#555555', linewidth=1.2, zorder=4)

            # Configuración del eje Y
            y_margin = max_count * 0.15
            ax.set_ylim(0, max_count + y_margin)

            if max_count > 14:
                ax.set_yticks([0, max_count])
            else:
                step = 1 if max_count <= 10 else max(1, round(max_count / 10))
                ax.set_yticks(np.arange(0, max_count + y_margin + step, step))

            ax.tick_params(axis='y', which='both', labelsize=6, colors='#555555', left=False)

            # Configurar etiquetas del eje X
            ax.set_xticks(range(len(dates)))
            ax.set_xticklabels(dates, rotation=25 if group_by != "month" else 45,
                               ha='right', fontsize=6, color='#555555')

            # Añadir línea horizontal de referencia en el eje Y
            ax.axhline(y=0, color='#DDDDDD', linewidth=0.8, zorder=0)

            # Ajustar márgenes
            plt.tight_layout()
            self.attendance_canvas.draw()

        except Exception as e:
            self.set_error_message(self.attendance_figure, f"Error: {str(e)}")
            self.attendance_canvas.draw()
        finally:
            conn.close()

    def generate_roles_chart(self):
        """Genera el gráfico de distribución por cargo con estilo mejorado"""
        conn = self.connect_db()
        if not conn:
            return

        try:
            cursor = conn.cursor()
            query = """
                SELECT 
                    CASE 
                        WHEN cargo IS NULL OR cargo = '' THEN 'Sin cargo especificado'
                        ELSE cargo 
                    END as cargo,
                    COUNT(*) as total
                FROM personal
                GROUP BY CASE 
                        WHEN cargo IS NULL OR cargo = '' THEN 'Sin cargo especificado'
                        ELSE cargo 
                    END
                ORDER BY COUNT(*) DESC, cargo
            """
            cursor.execute(query)
            data = cursor.fetchall()

            if not data:
                self.set_no_data_message(self.roles_figure, "No hay datos de cargos")
                self.roles_canvas.draw()
                return

            # Preparar datos
            labels = [row[0] for row in data]
            sizes = [row[1] for row in data]
            total_empleados = sum(sizes)

            # Paleta de colores profesional
            colors = [
                '#0C0923', '#EF8354', '#BBBDF6', '#107C8C',
                '#5674C9', '#DF3B56', '#EAD1C0', '#0F6A76', '#11EDF6'
            ]

            # Si hay más cargos que colores, repetimos la paleta
            colors = colors * (len(labels) // len(colors) + 1)

            self.roles_figure.clear()
            ax = self.roles_figure.add_subplot(111)

            # Gráfico de pastel sin separación blanca
            wedges, texts, autotexts = ax.pie(
                sizes,
                labels=None,
                colors=colors,
                startangle=90,
                wedgeprops={
                    'linewidth': 0,
                    'edgecolor': 'none',
                    'width': 0.4
                },
                pctdistance=0.8,
                autopct=lambda p: f'{p:.1f}%' if p >= 5 else '',
                textprops={
                    'color': 'white',
                    'fontsize': 6.5,
                    'fontweight': 'bold'
                }
            )

            # Crear leyenda con círculos usando Line2D
            from matplotlib.lines import Line2D
            legend_elements = [
                Line2D([0], [0],
                       marker='o',
                       color='w',
                       label=f'{label} ({size})',
                       markerfacecolor=color,
                       markersize=8)
                for color, label, size in zip(colors, labels, sizes)
            ]

            legend = ax.legend(
                handles=legend_elements,
                loc="center left",
                bbox_to_anchor=(1, 0.5),
                fontsize=7,
                frameon=False,
                handletextpad=0.5,
                handlelength=1.0
            )

            # Ajustar layout
            self.roles_figure.tight_layout(rect=[0, 0, 0.85, 1])
            self.roles_canvas.draw()

        except Exception as e:
            self.set_error_message(self.roles_figure, f"Error: {str(e)}")
            self.roles_canvas.draw()
        finally:
            conn.close()

    def load_recent_activity(self):
        """Carga las últimas asistencias registradas"""
        conn = self.connect_db()
        if not conn:
            return

        try:
            cursor = conn.cursor()
            query = """
                SELECT TOP 10 
                    p.nombre + ' ' + p.apellido as nombre_completo,
                    a.fecha_hora,
                    CASE WHEN a.validado_por IS NULL THEN 'Pendiente' ELSE a.validado_por END as validado_por,
                    CASE WHEN a.es_valido = 1 THEN 'Válido' 
                         WHEN a.es_valido = 0 THEN 'Inválido' 
                         ELSE 'Por validar' END as estado,
                    a.id
                FROM asistencias a
                JOIN personal p ON a.id_personal = p.id
                ORDER BY a.fecha_hora DESC
            """
            cursor.execute(query)
            records = cursor.fetchall()

            self.recent_table.setRowCount(0)

            for row_num, row_data in enumerate(records):
                self.recent_table.insertRow(row_num)

                # Nombre
                name_item = QTableWidgetItem(row_data[0])
                name_item.setTextAlignment(Qt.AlignCenter)
                self.recent_table.setItem(row_num, 0, name_item)

                # Fecha/Hora
                date_item = QTableWidgetItem(row_data[1].strftime("%d/%m/%Y %H:%M"))
                date_item.setTextAlignment(Qt.AlignCenter)
                self.recent_table.setItem(row_num, 1, date_item)

                # Validado por
                validated_item = QTableWidgetItem(row_data[2])
                validated_item.setTextAlignment(Qt.AlignCenter)
                self.recent_table.setItem(row_num, 2, validated_item)

                # Estado
                status_item = QTableWidgetItem(row_data[3])
                status_item.setTextAlignment(Qt.AlignCenter)
                if row_data[3] == 'Inválido':
                    status_item.setForeground(QColor('#e74c3c'))
                elif row_data[3] == 'Válido':
                    status_item.setForeground(QColor('#2ecc71'))
                self.recent_table.setItem(row_num, 3, status_item)

                # Botón de acción
                action_btn = QPushButton("Ver Detalle")
                action_btn.setStyleSheet("""
                    QPushButton {
                        font-family: 'Poppins';
                        font-size: 10px;
                        padding: 3px 8px;
                        background-color: #3498db;
                        color: white;
                        border-radius: 4px;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                    }
                """)
                action_btn.clicked.connect(lambda _, id=row_data[4]: self.show_attendance_detail(id))
                self.recent_table.setCellWidget(row_num, 4, action_btn)

        except Exception as e:
            self.show_error_message(f"Error al cargar actividad reciente: {str(e)}")
        finally:
            conn.close()

    def load_recent_alerts(self):
        """Carga las alertas recientes desde los logs"""
        conn = self.connect_db()
        if not conn:
            return

        try:
            cursor = conn.cursor()
            query = """
                SELECT TOP 5 
                    fecha_hora,
                    accion,
                    descripcion
                FROM logs_actividad
                WHERE accion LIKE '%error%' OR accion LIKE '%alerta%'
                ORDER BY fecha_hora DESC
            """
            cursor.execute(query)
            alerts = cursor.fetchall()

            self.alerts_list.setRowCount(0)

            for row_num, alert in enumerate(alerts):
                self.alerts_list.insertRow(row_num)

                # Fecha
                date_item = QTableWidgetItem(alert[0].strftime("%d/%m %H:%M"))
                date_item.setTextAlignment(Qt.AlignCenter)
                self.alerts_list.setItem(row_num, 0, date_item)

                # Tipo
                type_item = QTableWidgetItem(alert[1])
                type_item.setTextAlignment(Qt.AlignCenter)
                self.alerts_list.setItem(row_num, 1, type_item)

                # Descripción
                desc_item = QTableWidgetItem(alert[2])
                desc_item.setToolTip(alert[2])
                self.alerts_list.setItem(row_num, 2, desc_item)

        except Exception as e:
            self.show_error_message(f"Error al cargar alertas: {str(e)}")
        finally:
            conn.close()

    def show_attendance_detail(self, attendance_id):
        """Muestra el detalle de una asistencia"""
        QMessageBox.information(self, "Detalle de Asistencia",
                                f"Mostrando detalles para asistencia ID: {attendance_id}")

    def connect_db(self):
        """Establece conexión centralizada"""
        conn = get_db_connection()
        if not conn:
            self.show_error_message("Error crítico: No se pudo conectar al servidor SQL.")
        return conn

    def colorize_pixmap(self, pixmap, color):
        """Coloriza un pixmap con el color especificado"""
        colored_pixmap = QPixmap(pixmap.size())
        colored_pixmap.fill(Qt.transparent)

        painter = QPainter(colored_pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.drawPixmap(0, 0, pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(colored_pixmap.rect(), color)
        painter.end()

        return colored_pixmap

    def set_no_data_message(self, figure, message):
        """Muestra mensaje cuando no hay datos"""
        figure.clear()
        ax = figure.add_subplot(111)
        ax.text(0.5, 0.5, message,
                ha='center', va='center',
                fontsize=12, color='gray')
        ax.axis('off')

    def set_error_message(self, figure, message):
        """Muestra mensaje de error"""
        figure.clear()
        ax = figure.add_subplot(111)
        ax.text(0.5, 0.5, message,
                ha='center', va='center',
                fontsize=10, color='red')
        ax.axis('off')

    def show_error_message(self, message):
        """Muestra un mensaje de error al usuario"""
        QMessageBox.critical(self, "Error", message)