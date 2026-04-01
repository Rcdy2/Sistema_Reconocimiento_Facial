import cv2
import face_recognition
import pyodbc
import pickle
import os
from datetime import datetime
import customtkinter as ctk
from PIL import Image, ImageTk
from database_connection import get_db_connection

# Configurar conexión
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=.;DATABASE=UTP_SECURITYFACIAL;Trusted_Connection=yes')
cursor = conn.cursor()


def cargar_codificaciones():
    cursor.execute("""
        SELECT p.id, p.nombre, p.apellido, f.codificacion_facial
        FROM personal p
        JOIN fotos_personal f ON p.id = f.id_personal
        WHERE f.codificacion_facial IS NOT NULL
    """)
    datos = cursor.fetchall()
    codificaciones = []
    nombres = []

    for fila in datos:
        try:
            encoding = pickle.loads(fila.codificacion_facial)
            codificaciones.append(encoding)
            nombres.append((fila.id, f"{fila.nombre} {fila.apellido}"))
        except Exception as e:
            print("Error al cargar una codificación:", e)

    return codificaciones, nombres

# Guardar asistencia
def registrar_asistencia(id_personal, nombre_completo, ruta_imagen, valido, usuario_seguridad="seguridad"):
    if id_personal is not None:
        cursor.execute("""
            SELECT COUNT(*) FROM asistencias
            WHERE id_personal = ? AND CONVERT(DATE, fecha_hora) = CONVERT(DATE, GETDATE())
        """, id_personal)
        ya_registrado = cursor.fetchone()[0]

        if ya_registrado:
            print(f"[INFO] Ya se registró asistencia hoy para: {nombre_completo}")
            return

    cursor.execute("""
        INSERT INTO asistencias (id_personal, fecha_hora, ruta_imagen_captura, validado_por, es_valido)
        VALUES (?, GETDATE(), ?, ?, ?)
    """, id_personal, ruta_imagen, usuario_seguridad, valido)
    conn.commit()
    print(f"[LOG] Registro guardado para: {nombre_completo} ({'Autorizado' if valido else 'Denegado'})")

def iniciar_reconocimiento_gui():
    conocidos, nombres = cargar_codificaciones()

    # Crear ventana
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    ventana = ctk.CTk()
    ventana.title("Validación de Acceso")
    ventana.geometry("1000x600")

    # Título
    titulo = ctk.CTkLabel(ventana, text="Validación de Acceso", font=("Arial", 24, "bold"))
    titulo.pack(pady=10)

    # Frame principal (cámara + asistencias)
    frame_main = ctk.CTkFrame(ventana)
    frame_main.pack(fill="both", expand=True, padx=10, pady=10)

    # Cámara en el lado izquierdo
    lbl_video = ctk.CTkLabel(frame_main, text="")
    lbl_video.pack(side="left", padx=10, pady=10)

    # Asistencias en el lado derecho
    frame_lista = ctk.CTkFrame(frame_main, width=300)
    frame_lista.pack(side="right", fill="y", padx=10, pady=10)
    lista_asistencias = ctk.CTkTextbox(frame_lista, width=300, height=500, font=("Consolas", 12))
    lista_asistencias.pack()

    # Función para actualizar asistencias
    def actualizar_lista():
        cursor.execute("""
            SELECT p.nombre, p.apellido, a.fecha_hora
            FROM asistencias a
            JOIN personal p ON a.id_personal = p.id
            WHERE CONVERT(DATE, a.fecha_hora) = CONVERT(DATE, GETDATE())
            ORDER BY a.fecha_hora DESC
        """)
        filas = cursor.fetchall()
        lista_asistencias.delete("0.0", "end")
        for fila in filas:
            lista_asistencias.insert("end", f"{fila.nombre} {fila.apellido} - {fila.fecha_hora.strftime('%H:%M:%S')}\n")

    # Captura desde cámara
    cam = cv2.VideoCapture(0)

    def procesar_frame():
        ret, frame = cam.read()
        if not ret:
            ventana.after(10, procesar_frame)
            return

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        ubicaciones = face_recognition.face_locations(rgb)
        codigos = face_recognition.face_encodings(rgb, ubicaciones)

        for (top, right, bottom, left), cod in zip(ubicaciones, codigos):
            matches = face_recognition.compare_faces(conocidos, cod)
            face_distances = face_recognition.face_distance(conocidos, cod)

            mejor_match = None
            if len(face_distances) > 0:
                mejor_match = face_distances.argmin()

            if mejor_match is not None and matches[mejor_match]:
                id_personal, nombre = nombres[mejor_match]
                color = (0, 255, 0)
                texto = f"{nombre} - Autorizado"
                ruta = f"capturas/{id_personal}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
                os.makedirs("capturas", exist_ok=True)
                cv2.imwrite(ruta, frame)
                registrar_asistencia(id_personal, nombre, ruta, 1)
                actualizar_lista()

            else:
                texto = "❌ Acceso Denegado"
                color = (0, 0, 255)
                ruta = f"capturas/desconocido_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
                os.makedirs("capturas", exist_ok=True)
                cv2.imwrite(ruta, frame)
                registrar_asistencia(None, "Desconocido", ruta, 0)

            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, texto, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        # Mostrar frame en GUI
        imagen = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        imagen_pil = Image.fromarray(imagen)
        imagen_tk = ImageTk.PhotoImage(image=imagen_pil)
        lbl_video.configure(image=imagen_tk)
        lbl_video.image = imagen_tk

        ventana.after(60, procesar_frame)

    procesar_frame()
    actualizar_lista()
    ventana.mainloop()

# Ejecutar
if __name__ == "__main__":
    iniciar_reconocimiento_gui()
