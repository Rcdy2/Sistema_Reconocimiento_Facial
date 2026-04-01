from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame, QLineEdit,
                             QComboBox, QHBoxLayout, QPushButton, QStackedWidget,
                             QStyledItemDelegate, QApplication, QMessageBox, QFileDialog)
from PyQt5.QtGui import QFont, QIntValidator, QRegExpValidator, QPixmap, QIcon
from PyQt5.QtCore import Qt, QRegExp, QSize, QPoint

import customtkinter as ctk
from database_connection import get_db_connection
from tkinter import messagebox
import cv2
import face_recognition
import pyodbc
import os
import sys
import pickle
import threading
from PIL import Image, ImageTk

class PersonalRegistrationPagex(QWidget):
    class PersonalRegistrationPagex(QWidget):
        def darken_color(self, hex_color, percent):
            hex_color = hex_color.lstrip('#')
            rgb = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
            darkened = tuple(max(0, int(c * (100 - percent) / 100)) for c in rgb)
            return '#%02x%02x%02x' % darkened



    def __init__(self):
        super().__init__()
        #self.archivo_biometrico = None  # Variable para almacenar la ruta del archivo biométrico
        #self.setup_ui()

        # Configuración inicial
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Conexión a SQL Server
        self.conn = get_db_connection()
        if self.conn:
            self.cursor = self.conn.cursor()
        else:
            print("Error de conexión en Registro")

        # Carpeta para guardar imágenes
        RUTA_IMAGENES = "imagenes"
        os.makedirs(RUTA_IMAGENES, exist_ok=True)

        fotos_capturadas = []
        cam = None
        camara_activa = False

        # Interfaz gráfica
        app = ctk.CTk()
        app.title("🧍 Registro de Personal - NovaMarket")
        app.geometry("1000x600")
        # Título
        titulo = ctk.CTkLabel(app, text="🧍 Registro de Personal", font=("Arial", 24, "bold"))
        titulo.pack(pady=10)

        # Panel principal
        frame_main = ctk.CTkFrame(app)
        frame_main.pack(fill="both", expand=True, padx=20, pady=10)

        # Subpanel izquierdo (formulario)
        frame_form = ctk.CTkFrame(frame_main, width=300)
        frame_form.pack(side="left", fill="y", padx=10, pady=10)

        entry_nombre = ctk.CTkEntry(frame_form, placeholder_text="Nombre")
        entry_nombre.pack(pady=10)

        entry_apellido = ctk.CTkEntry(frame_form, placeholder_text="Apellido")
        entry_apellido.pack(pady=10)

        entry_dni = ctk.CTkEntry(frame_form, placeholder_text="DNI")
        entry_dni.pack(pady=10)

        entry_cargo = ctk.CTkEntry(frame_form, placeholder_text="Cargo")
        entry_cargo.pack(pady=10)

        btn_capturar = ctk.CTkButton(frame_form, text="📸 Capturar Foto",
                                     command=lambda: self.capturar_foto(self.entry_dni.get()))
        btn_capturar.pack(pady=10)

        lbl_fotos_capturadas = ctk.CTkLabel(frame_form, text="0 / 6 fotos capturadas")
        lbl_fotos_capturadas.pack(pady=5)

        btn_guardar = ctk.CTkButton(frame_form, text="✅ Guardar Registro", command=self.guardar_todo)
        btn_guardar.pack(pady=20)

        # Subpanel derecho (cámara)
        frame_video = ctk.CTkFrame(frame_main)
        frame_video.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        video_label = ctk.CTkLabel(frame_video, text="")
        video_label.pack(padx=10, pady=10)

        # Iniciar video en hilo
        video_thread = threading.Thread(target=self.iniciar_video)
        video_thread.start()
        # video_thread = threading.Thread(target=iniciar_video)
        # video_thread.start()

        #app.mainloop()

    def iniciar_video(self):
        global camara_activa, cam
        cam = cv2.VideoCapture(0)
        camara_activa = True
        self.mostrar_video()
        self.deteccion_periodica()

    def actualizar_video(self):
        global camara_activa, cam
        if camara_activa and cam is not None:
            ret, frame = cam.read()
            if ret:
                frame = cv2.resize(frame, (400, 300))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img_pil = Image.fromarray(frame)  # <-- Conversión correcta
                img = ctk.CTkImage(light_image=img_pil, size=(400, 300))
                self.video_label.configure(image=img)
                self.video_label.image = img
            self.video_label.after(30, self.actualizar_video)

    def registrar_personal(self, nombre, apellido, dni, cargo):
        id_personal = None
        self.cursor.execute("{CALL sp_registrar_personal (?, ?, ?, ?, ?)}", (nombre, apellido, dni, cargo, id_personal))
        self.cursor.nextset()
        id_personal = self.cursor.fetchval()
        self.conn.commit()
        return id_personal

    def capturar_foto(self, dni):
        global fotos_capturadas, cam

        ret, frame = cam.read()
        if not ret:
            messagebox.showerror("Error", "No se pudo acceder a la cámara.")
            return

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        caras = face_recognition.face_locations(rgb)

        if len(caras) != 1:
            messagebox.showwarning("Advertencia", "Debe haber exactamente un rostro visible.")
            return

        codificacion = face_recognition.face_encodings(rgb, caras)[0]
        cod_bin = pickle.dumps(codificacion)
        ruta_imagen = os.path.join(self.RUTA_IMAGENES, f"{dni}_{len(fotos_capturadas)+1}.jpg")
        cv2.imwrite(ruta_imagen, frame)
        fotos_capturadas.append((ruta_imagen, cod_bin))
        self.lbl_fotos_capturadas.configure(text=f"{len(fotos_capturadas)} / 6 fotos capturadas")

    def registrar(self):
        nombre = self.entry_nombre.get()
        apellido = self.entry_apellido.get()
        dni = self.entry_dni.get()
        cargo = self.entry_cargo.get()

        if not (nombre and apellido and dni and cargo):
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        try:
            id_personal = self.registrar_personal(nombre, apellido, dni, cargo)
            #capturar_fotos(id_personal, dni)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def guardar_todo(self):
        global fotos_capturadas

        nombre = self.entry_nombre.get().strip()
        apellido = self.entry_apellido.get().strip()
        dni = self.entry_dni.get().strip()
        cargo = self.entry_cargo.get().strip()

        if not (nombre and apellido and dni and cargo):
            messagebox.showerror("Error", "Completa todos los campos antes de guardar.")
            return

        if len(fotos_capturadas) < 6:
            messagebox.showwarning("Advertencia", "Debes capturar al menos 6 fotos.")
            return

        try:
            # Registrar persona
            id_personal = self.registrar_personal(nombre, apellido, dni, cargo)

            # Guardar fotos
            for ruta, codificacion in fotos_capturadas:
                self.cursor.execute("{CALL sp_insertar_foto_personal (?, ?, ?, ?)}",
                               (id_personal, ruta, codificacion, 0))
            self.conn.commit()

            messagebox.showinfo("Éxito", "Registro completado con éxito.")
            # Limpiar todo
            self.entry_nombre.delete(0, 'end')
            self.entry_apellido.delete(0, 'end')
            self.entry_dni.delete(0, 'end')
            self.entry_cargo.delete(0, 'end')
            fotos_capturadas = []
            self.lbl_fotos_capturadas.configure(text="0 / 6 fotos capturadas")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {e}")

    def cam_loop(self):
        self.mostrar_video()
        #deteccion_periodica()

    def mostrar_video(self):
        global cam, camara_activa
        if not (camara_activa and cam):
            return
        ret, frame = cam.read()
        if not ret:
            self.video_label.after(30, self.mostrar_video)
            return
        #if ret:
        frame_resized = cv2.resize(frame, (400, 300))
        frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(frame_rgb)
        img_tk = ImageTk.PhotoImage(image=img_pil)
        self.video_label.configure(image=img_tk, text="")
        self.video_label.image = img_tk
        self.video_label.after(30, self.mostrar_video)  # 30 ms = ~33 FPS

    def deteccion_periodicasa(self):
        global cam
        if cam is not None:
            ret, frame = cam.read()
            if ret:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                ubicaciones = face_recognition.face_locations(rgb, model="hog")

                for (top, right, bottom, left) in ubicaciones:
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    cv2.putText(frame, "✅ Rostro Detectado", (left, top - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                # Mostrar el frame con recuadro en el label
                imagen = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                imagen_pil = Image.fromarray(imagen)
                imagen_ctk = ImageTk.PhotoImage(image=imagen_pil)
                self.video_label.configure(image=imagen_ctk, text="")
                self.video_label.image = imagen_ctk

                self.video_label.after(60, self.deteccion_periodica)


                #imagen = Image.fromarray(rgb)
                #imagen_tk = ImageTk.PhotoImage(image=imagen)
                #video_label.configure(image=imagen_tk, text="")
                #video_label.image = imagen_tk

        #app.after(500, deteccion_periodica)

    def deteccion_periodicaxd(self):
        global cam
        if cam is not None:
            ret, frame = cam.read()
            if ret:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                ubicaciones = face_recognition.face_locations(rgb)
                if ubicaciones:
                    print("✅ Rostro Detectado")
                    # Aquí podrías guardar, validar, etc.
        app.after(500, self.deteccion_periodica)  # Cada 500ms

    # Variables globales necesarias
    frame_counter = 0
    ubicaciones_detectadas = []

    def deteccion_periodica(self):
        global camara_activa, cam, frame_counter

        if not (camara_activa and cam):
            return

        ret, frame = cam.read()
        if not ret:
            self.video_label.after(30, self.procesar_frame)
            return

        frame_counter += 1

        # Solo procesar rostro cada 2 fotogramas (reduce carga)
        if frame_counter % 2 == 0:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            ubicaciones = face_recognition.face_locations(rgb, model="hog")

            for (top, right, bottom, left) in ubicaciones:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, "✅ Rostro Detectado", (left, top - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Convertir y mostrar frame
        imagen = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        imagen_pil = Image.fromarray(imagen)
        imagen_tk = ImageTk.PhotoImage(image=imagen_pil)

        self.video_label.configure(image=imagen_tk, text="")
        self.video_label.image = imagen_tk

        self.video_label.after(60, self.procesar_frame)


    def procesar_frame(self):
        global camara_activa, cam
        if not (camara_activa and cam):
            return

        ret, frame = cam.read()
        if not ret:
            self.video_label.after(30, self.procesar_frame)
            return

        # Convertir a RGB para reconocimiento
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        ubicaciones = face_recognition.face_locations(rgb, model="hog")  # más rápido que cnn

        for (top, right, bottom, left) in ubicaciones:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, "✅ Rostro Detectado", (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Mostrar en customtkinter
        imagen = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        imagen_pil = Image.fromarray(imagen)
        imagen_tk = ImageTk.PhotoImage(image=imagen_pil)

        self.video_label.configure(image=imagen_tk, text="")
        self.video_label.image = imagen_tk

        # Llamar de nuevo luego de 60 ms
        self.video_label.after(60, self.procesar_frame)

    def procesar_frameold(self):
        global camara_activa, cam, frame_counter, ubicaciones_detectadas
        if camara_activa and cam is not None:
            ret, frame = cam.read()
            if not ret:
                self.video_label.after(60, self.procesar_frame)
                return

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Detectar rostros solo cada 5 frames para reducir carga
            if frame_counter % 5 == 0:
                ubicaciones_detectadas = face_recognition.face_locations(rgb)

            for (top, right, bottom, left) in ubicaciones_detectadas:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, "✅ Rostro Detectado", (left, top - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            # Convertir y mostrar en customtkinter
            imagen = Image.fromarray(rgb)
            imagen_tk = ImageTk.PhotoImage(image=imagen)

            self.video_label.configure(image=imagen_tk, text="")  # Borra texto anterior
            self.video_label.image = imagen_tk

            frame_counter += 1
            self.video_label.after(60, self.procesar_frame)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("* { font-family: 'Poppins'; }")
    window = PersonalRegistrationPagex()
    window.show()

    sys.exit(app.exec_())