import os
import threading
import re
import customtkinter as ctk
from tkinter import filedialog, messagebox

from config import FPS_PERMITIDOS
from video_utils import obtener_info_video
from xml_resolve import generar_xml_fcp7
from srt_utils import unir_srts
from renamer_utils import obtener_preview_renombrado, aplicar_renombrado


ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class TimelineApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Timeline Builder Pro")
        self.geometry("950x760")
        self.resizable(False, False)

        self.crear_tabs()

    # ======================================================
    # TABS
    # ======================================================

    def crear_tabs(self):

        self.tabview = ctk.CTkTabview(self, width=900, height=700)
        self.tabview.pack(pady=20)

        self.tab_generador = self.tabview.add("Timeline Builder")
        self.tab_renombrar = self.tabview.add("Renombrador Inteligente")

        self.crear_tab_generador()
        self.crear_tab_renombrar()

    # ======================================================
    # TAB 1 — TIMELINE BUILDER
    # ======================================================

    def crear_tab_generador(self):

        self.carpeta = ctk.StringVar()
        self.fps = ctk.StringVar(value=str(FPS_PERMITIDOS[0]))
        self.timecode = ctk.StringVar(value="01:00:00:00")
        self.tipo_audio = ctk.StringVar(value="Stereo (2 canales)")

        titulo = ctk.CTkLabel(
            self.tab_generador,
            text="Timeline Builder Pro",
            font=("Arial", 24, "bold")
        )
        titulo.pack(pady=15)

        # selector modo
        modo_selector = ctk.CTkOptionMenu(
            self.tab_generador,
            values=["System", "Light", "Dark"],
            command=self.cambiar_modo
        )
        modo_selector.set("System")
        modo_selector.pack()

        # seleccionar carpeta
        ctk.CTkLabel(self.tab_generador, text="Carpeta de trabajo").pack(pady=(20, 5))

        frame_carpeta = ctk.CTkFrame(self.tab_generador)
        frame_carpeta.pack()

        entry = ctk.CTkEntry(frame_carpeta, textvariable=self.carpeta, width=560)
        entry.pack(side="left", padx=5, pady=10)

        btn = ctk.CTkButton(frame_carpeta, text="Seleccionar", command=self.seleccionar_carpeta)
        btn.pack(side="left")

        # FPS
        ctk.CTkLabel(self.tab_generador, text="FPS").pack(pady=(20, 5))

        fps_menu = ctk.CTkOptionMenu(
            self.tab_generador,
            values=[str(f) for f in FPS_PERMITIDOS],
            variable=self.fps
        )
        fps_menu.pack()

        # AUDIO
        ctk.CTkLabel(self.tab_generador, text="Tipo de Audio").pack(pady=(20, 5))

        audio_menu = ctk.CTkOptionMenu(
            self.tab_generador,
            values=["Stereo (2 canales)", "4 canales", "8 canales"],
            variable=self.tipo_audio
        )
        audio_menu.pack()

        # TIMECODE
        ctk.CTkLabel(self.tab_generador, text="Timecode Inicial").pack(pady=(20, 5))

        entry_tc = ctk.CTkEntry(self.tab_generador, textvariable=self.timecode)
        entry_tc.pack()

        # BOTONES
        frame_btn = ctk.CTkFrame(self.tab_generador)
        frame_btn.pack(pady=20)

        btn_generar = ctk.CTkButton(
            frame_btn,
            text="Generar Timeline",
            height=45,
            command=self.ejecutar_proceso
        )
        btn_generar.pack(side="left", padx=10)

        btn_limpiar = ctk.CTkButton(
            frame_btn,
            text="Limpiar Log",
            command=self.limpiar_log
        )
        btn_limpiar.pack(side="left", padx=10)

        btn_abrir = ctk.CTkButton(
            frame_btn,
            text="Abrir Carpeta",
            command=self.abrir_carpeta
        )
        btn_abrir.pack(side="left", padx=10)

        # PROGRESS BAR
        self.progress = ctk.CTkProgressBar(self.tab_generador, width=500)
        self.progress.pack(pady=10)
        self.progress.set(0)

        # LOG
        ctk.CTkLabel(self.tab_generador, text="Log").pack()

        self.log_text = ctk.CTkTextbox(self.tab_generador, width=820, height=180)
        self.log_text.pack(pady=10)

    # ======================================================
    # TAB 2 — RENOMBRADOR
    # ======================================================

    def crear_tab_renombrar(self):

        self.carpeta_renombrar = ctk.StringVar()

        titulo = ctk.CTkLabel(
            self.tab_renombrar,
            text="Renombrador Inteligente",
            font=("Arial", 22, "bold")
        )
        titulo.pack(pady=20)

        frame = ctk.CTkFrame(self.tab_renombrar)
        frame.pack()

        entry = ctk.CTkEntry(frame, textvariable=self.carpeta_renombrar, width=560)
        entry.pack(side="left", padx=5, pady=10)

        btn = ctk.CTkButton(frame, text="Seleccionar", command=self.seleccionar_carpeta_renombrar)
        btn.pack(side="left")

        btn_preview_v = ctk.CTkButton(
            self.tab_renombrar,
            text="Vista previa Videos",
            command=lambda: self.mostrar_preview((".mp4", ".mov", ".mxf")),
            height=40
        )
        btn_preview_v.pack(pady=10)

        btn_preview_s = ctk.CTkButton(
            self.tab_renombrar,
            text="Vista previa Subtítulos",
            command=lambda: self.mostrar_preview((".srt",)),
            height=40
        )
        btn_preview_s.pack()

        self.log_text_renombrar = ctk.CTkTextbox(self.tab_renombrar, width=820, height=260)
        self.log_text_renombrar.pack(pady=20)

    # ======================================================
    # FUNCIONES GENERALES
    # ======================================================

    def cambiar_modo(self, modo):
        ctk.set_appearance_mode(modo)

    def limpiar_log(self):
        self.log_text.delete("1.0", "end")

    def abrir_carpeta(self):

        carpeta = self.carpeta.get()

        if os.path.isdir(carpeta):
            os.startfile(carpeta)

    def seleccionar_carpeta(self):
        carpeta = filedialog.askdirectory()
        if carpeta:
            self.carpeta.set(carpeta)

    def log(self, texto):
        self.log_text.insert("end", texto + "\n")
        self.log_text.see("end")

    # ======================================================
    # VALIDAR TIMECODE
    # ======================================================

    def validar_timecode(self, tc):

        patron = r"\d{2}:\d{2}:\d{2}:\d{2}"

        if not re.fullmatch(patron, tc):
            return False

        return True

    # ======================================================
    # PROCESO TIMELINE
    # ======================================================

    def ejecutar_proceso(self):
        hilo = threading.Thread(target=self.proceso)
        hilo.start()

    def proceso(self):

        carpeta = self.carpeta.get()
        fps = float(self.fps.get())
        tc = self.timecode.get()
        tipo_audio = self.tipo_audio.get()

        if not os.path.isdir(carpeta):
            messagebox.showerror("Error", "Carpeta inválida.")
            return

        if not self.validar_timecode(tc):
            messagebox.showerror("Error", "Timecode inválido.")
            return

        if "Stereo" in tipo_audio:
            canales_audio = 2
        elif "4" in tipo_audio:
            canales_audio = 4
        else:
            canales_audio = 8

        archivos = os.listdir(carpeta)

        videos = sorted([
            os.path.join(carpeta, f)
            for f in archivos
            if f.lower().endswith((".mp4", ".mov", ".mxf"))
        ])

        if not videos:
            messagebox.showerror("Error", "No se encontraron videos.")
            return

        self.progress.set(0.2)

        xml_output = os.path.join(carpeta, "timeline_generado.xml")

        self.log("Generando XML timeline...")

        generar_xml_fcp7(
            videos,
            fps,
            tc,
            xml_output,
            canales_audio
        )

        self.progress.set(0.6)

        # SRT
        srts = sorted([
            os.path.join(carpeta, f)
            for f in archivos
            if f.lower().endswith(".srt")
        ])

        if len(srts) == len(videos):

            self.log("Generando SRT combinado...")

            duraciones = []

            for v in videos:
                d, _ = obtener_info_video(v)
                duraciones.append(d)

            srt_out = os.path.join(carpeta, "subtitulos_combinados.srt")

            unir_srts(srts, duraciones, srt_out)

            self.log("SRT combinado generado.")

        else:
            self.log("⚠ Cantidad de SRT no coincide con videos.")

        self.progress.set(1)

        self.log("Proceso finalizado.")

        messagebox.showinfo("Finalizado", "Timeline generada correctamente.")

    # ======================================================
    # RENOMBRADOR
    # ======================================================

    def seleccionar_carpeta_renombrar(self):

        carpeta = filedialog.askdirectory()

        if carpeta:
            self.carpeta_renombrar.set(carpeta)

    def mostrar_preview(self, extensiones):

        carpeta = self.carpeta_renombrar.get()

        if not os.path.isdir(carpeta):
            messagebox.showerror("Error", "Carpeta inválida.")
            return

        preview = obtener_preview_renombrado(carpeta, extensiones)

        if not preview:
            messagebox.showinfo("Info", "No se encontraron archivos.")
            return

        self.log_text_renombrar.delete("1.0", "end")

        for original, nuevo in preview:
            self.log_text_renombrar.insert("end", f"{original}  →  {nuevo}\n")

        confirmar = messagebox.askyesno(
            "Confirmar",
            "¿Aplicar estos cambios?"
        )

        if confirmar:

            cantidad = aplicar_renombrado(carpeta, preview)

            messagebox.showinfo(
                "Listo",
                f"{cantidad} archivos renombrados."
            )


if __name__ == "__main__":
    app = TimelineApp()
    app.mainloop()