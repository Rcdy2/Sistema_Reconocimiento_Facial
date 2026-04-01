from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame, QLineEdit, QTextEdit,
                             QComboBox, QHBoxLayout, QPushButton, QStackedWidget,
                             QStyledItemDelegate, QApplication, QMessageBox, QFileDialog)
from PyQt5.QtGui import QFont, QIntValidator, QRegExpValidator, QPixmap, QIcon, QImage
from PyQt5.QtCore import Qt, QTimer, QRegExp, QSize, QPoint
import cv2
import dlib
import face_recognition
import pyodbc
import pickle
import os
import numpy as np
from database_connection import get_db_connection
from datetime import datetime
import traceback
import time


class ValidarAccesoPage(QWidget):
    def __init__(self):
        super().__init__()


        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        if self.face_cascade.empty():
            QMessageBox.critical(self, "Error", "No se pudo cargar el clasificador Haar.")
            self.close()
            return

        # CONEXIÓN
        self.conn = get_db_connection()
        if not self.conn:
            QMessageBox.critical(self, "Error", "No se pudo conectar a la base de datos.")
            self.close()
            return
        self.cursor = self.conn.cursor()

        #  CARGA DE DATOS
        self.conocidos, self.nombres_data = self.cargar_codificaciones()
        if len(self.conocidos) == 0:
            print("[ADVERTENCIA] No se encontraron codificaciones faciales en la BD.")
            QMessageBox.warning(self, "Aviso", "No hay rostros registrados. Todos serán considerados desconocidos.")


        self.nombre_visible = ""
        self.rect_visible = None
        self.color_visible = (0, 255, 0)
        self.tiempo_visible = 0

        self.contador_frames = 0
        self.ultima_deteccion = []
        self.ultimo_registro_tiempo = {}

        # 3. DISEÑO ORIGINAL (1000x600)
        self.setWindowTitle("Validación de Acceso")
        self.setFixedSize(1000, 600)
        self.setStyleSheet("""
            QTextEdit {
                font-family: Consolas;
                font-size: 12px;
                background-color: #f8f8f8;
                border: 1px solid #ccc;
                padding: 10px;
            }
            QLabel#titulo {
                font-size: 24px;
                font-weight: bold;
            }
        """)

        layout_principal = QVBoxLayout(self)
        titulo = QLabel("Validación de Acceso")
        titulo.setObjectName("titulo")
        titulo.setAlignment(Qt.AlignCenter)
        layout_principal.addWidget(titulo)

        frame_central = QHBoxLayout()

        # Cámara (Izquierda)
        self.lbl_video = QLabel()
        self.lbl_video.setFixedSize(640, 480)
        self.lbl_video.setStyleSheet("background-color: #ddd; border: 1px solid #aaa;")
        self.lbl_video.setAlignment(Qt.AlignCenter)
        frame_central.addWidget(self.lbl_video)

        # Panel de asistencias (Derecha)
        panel_derecho = QVBoxLayout()
        panel_derecho.addWidget(QLabel("<b>REGISTROS RECIENTES</b>"))
        self.lista_asistencias = QTextEdit()
        self.lista_asistencias.setReadOnly(True)
        self.lista_asistencias.setFixedWidth(300)
        panel_derecho.addWidget(self.lista_asistencias)
        frame_central.addLayout(panel_derecho)
        layout_principal.addLayout(frame_central)


        if not os.path.exists("capturas"):
            os.makedirs("capturas")


        self.cam = cv2.VideoCapture(0)
        if not self.cam.isOpened():
            QMessageBox.critical(self, "Error", "No se pudo abrir la cámara.")
            self.close()
            return

        self.actualizar_lista()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.procesar_frame)
        self.timer.start(30)  # ~33 fps

    def cargar_codificaciones(self):

        cods = []
        noms = []
        try:
            self.cursor.execute("""
                SELECT p.id, p.nombre, p.apellido, f.codificacion_facial
                FROM personal p
                JOIN fotos_personal f ON p.id = f.id_personal
                WHERE f.codificacion_facial IS NOT NULL
            """)
            datos = self.cursor.fetchall()
            for row in datos:
                try:
                    encoding = pickle.loads(row[3])
                    cods.append(encoding)
                    noms.append({'id': row[0], 'nombre': f"{row[1]} {row[2]}"})
                except Exception as e:
                    print(f"Error al cargar encoding para {row[1]}: {e}")
        except Exception as e:
            print(f"Error en la consulta de codificaciones: {e}")
        return cods, noms

    def registrar_asistencia(self, id_p, nombre, valido, frame_actual):

        try:
            ahora = datetime.now()
            clave = id_p if id_p else "DESCONOCIDO"

            # Evita registros repetidos en menos de 60 segundos
            if clave in self.ultimo_registro_tiempo:
                if (ahora - self.ultimo_registro_tiempo[clave]).total_seconds() < 60:
                    return


            ruta = f"capturas/{clave}_{ahora.strftime('%H%M%S')}.jpg"
            cv2.imwrite(ruta, frame_actual)


            self.cursor.execute("""
                INSERT INTO asistencias (id_personal, fecha_hora, ruta_imagen_captura, validado_por, es_valido)
                VALUES (?, GETDATE(), ?, 'seguridad', ?)
            """, (id_p, ruta, valido))
            self.conn.commit()
            self.ultimo_registro_tiempo[clave] = ahora
            self.actualizar_lista()
        except Exception as e:
            print(f"Error al registrar asistencia: {e}")

    def actualizar_lista(self):

        try:
            self.cursor.execute("""
                SELECT TOP 10 ISNULL(p.nombre, 'DESCONOCIDO'), a.fecha_hora
                FROM asistencias a
                LEFT JOIN personal p ON a.id_personal = p.id
                WHERE CONVERT(DATE, a.fecha_hora) = CONVERT(DATE, GETDATE())
                ORDER BY a.fecha_hora DESC
            """)
            self.lista_asistencias.clear()
            for r in self.cursor.fetchall():
                self.lista_asistencias.append(f"[{r[1].strftime('%H:%M:%S')}] {r[0]}")
        except Exception as e:
            print(f"Error al actualizar lista: {e}")

    def procesar_frame(self):
        try:
            ret, frame = self.cam.read()
            if not ret or frame is None:
                return

            self.contador_frames += 1


            if frame.shape[2] == 4:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            if frame.dtype != np.uint8:
                frame = frame.astype(np.uint8)

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img_ia = np.ascontiguousarray(frame_rgb, dtype=np.uint8)


            hubo_deteccion = False

            if self.contador_frames % 3 == 0:
                # Reducir imagen
                img_small = cv2.resize(img_ia, (0, 0), fx=0.5, fy=0.5)
                img_small = np.ascontiguousarray(img_small, dtype=np.uint8)

                gray_small = cv2.cvtColor(img_small, cv2.COLOR_RGB2GRAY)
                rostros = self.face_cascade.detectMultiScale(gray_small, scaleFactor=1.1,
                                                             minNeighbors=5, minSize=(30, 30))

                self.ultima_deteccion = []

                for (x, y, w, h) in rostros:
                    # Recortar la cara
                    face_roi = img_small[y:y + h, x:x + w]
                    face_roi = np.ascontiguousarray(face_roi, dtype=np.uint8)

                    codigos = face_recognition.face_encodings(face_roi)
                    if not codigos:
                        continue

                    cod = codigos[0]

                    if len(self.conocidos) == 0:
                        nombre_txt, color, id_p, valido = "DESCONOCIDO", (0, 0, 255), None, 0
                    else:
                        distancias = face_recognition.face_distance(self.conocidos, cod)
                        mejor_match = np.argmin(distancias)
                        if distancias[mejor_match] < 0.6:
                            user = self.nombres_data[mejor_match]
                            nombre_txt, color, id_p, valido = user['nombre'], (0, 255, 0), user['id'], 1
                        else:
                            nombre_txt, color, id_p, valido = "DESCONOCIDO", (0, 0, 255), None, 0

                    # Registrar asistencia
                    self.registrar_asistencia(id_p, nombre_txt, valido, frame)

                    # Almacenar para dibujo inmediato (este frame)
                    rect = (x * 2, y * 2, (x + w) * 2, (y + h) * 2)
                    self.ultima_deteccion.append({
                        'rect': rect,
                        'txt': nombre_txt,
                        'color': color
                    })


                    if not hubo_deteccion:
                        hubo_deteccion = True
                        self.nombre_visible = nombre_txt
                        self.rect_visible = rect
                        self.color_visible = color
                        self.tiempo_visible = time.time() + 2.0   # 2 segundos de persistencia

            # Dibujo principal: combinar detecciones del frame actual + persistencia
            # Primero dibujar las detecciones actuales (ya están en self.ultima_deteccion)
            for d in self.ultima_deteccion:
                l, t, r, b = d['rect']
                cv2.rectangle(frame, (l, t), (r, b), d['color'], 2)
                cv2.rectangle(frame, (l, b - 30), (r, b), d['color'], cv2.FILLED)
                cv2.putText(frame, d['txt'], (l + 5, b - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)


            if not hubo_deteccion and self.rect_visible and time.time() < self.tiempo_visible:
                l, t, r, b = self.rect_visible
                cv2.rectangle(frame, (l, t), (r, b), self.color_visible, 2)
                cv2.rectangle(frame, (l, b - 30), (r, b), self.color_visible, cv2.FILLED)
                cv2.putText(frame, self.nombre_visible, (l + 5, b - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)


            if self.rect_visible and time.time() >= self.tiempo_visible:
                self.nombre_visible = ""
                self.rect_visible = None
                self.color_visible = (0, 255, 0)

            # Mostrar en PyQt5
            h, w, ch = frame.shape
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            bytes_per_line = ch * w
            qimg = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.lbl_video.setPixmap(QPixmap.fromImage(qimg))

        except Exception as e:
            print(f"Error en procesar_frame: {e}")
            traceback.print_exc()

    def closeEvent(self, event):

        if self.cam.isOpened():
            self.cam.release()
        if self.conn:
            self.conn.close()
        event.accept()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    ventana = ValidarAccesoPage()
    ventana.show()
    sys.exit(app.exec_())