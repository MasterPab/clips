import os
import threading
import subprocess
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import yt_dlp
import re

# Configuración visual
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ClipsApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Clips Downloader Ultimate")
        self.geometry("700x550")
        self.resizable(False, False)

        # Estado y Variables
        self.file_path_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Listo para trabajar")
        self.video_title_var = tk.StringVar(value="---")
        self.use_nvenc_var = tk.BooleanVar(value=True)
        self.output_folder = os.getcwd()  # Por defecto carpeta actual
        
        # Verificar dependencias al inicio
        self.check_dependencies()
        self.create_widgets()

    def check_dependencies(self):
        if not shutil.which("ffmpeg"):
            messagebox.showwarning("Falta FFmpeg", "No se detectó FFmpeg en el sistema.\nEl programa no funcionará correctamente sin él.")

    def create_widgets(self):
        # --- Frame Principal ---
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # --- Sección 1: Fuente ---
        ctk.CTkLabel(main_frame, text="1. Fuente del Video", font=("Roboto", 14, "bold")).pack(anchor="w", pady=(5, 5))
        
        src_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        src_frame.pack(fill="x", pady=5)
        
        self.entry_url = ctk.CTkEntry(src_frame, placeholder_text="Pega la URL de YouTube o selecciona archivo local...")
        self.entry_url.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        btn_browse = ctk.CTkButton(src_frame, text="Archivo Local", width=100, command=self.browse_file, fg_color="#444")
        btn_browse.pack(side="right")

        # --- Sección 2: Configuración de Clips ---
        ctk.CTkLabel(main_frame, text="2. Configuración de Tiempos", font=("Roboto", 14, "bold")).pack(anchor="w", pady=(15, 5))
        
        self.entry_intervals = ctk.CTkEntry(main_frame, placeholder_text="Ejemplos: 10-20, 01:30-02:00, 150-180")
        self.entry_intervals.pack(fill="x", pady=5)
        
        # Opciones avanzadas en una fila
        opts_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        opts_frame.pack(fill="x", pady=10)
        
        self.chk_nvenc = ctk.CTkCheckBox(opts_frame, text="Aceleración GPU (NVENC)", variable=self.use_nvenc_var)
        self.chk_nvenc.pack(side="left")
        
        self.btn_folder = ctk.CTkButton(opts_frame, text="Carpeta Salida", width=100, command=self.choose_output_folder, fg_color="#555")
        self.btn_folder.pack(side="right")

        # --- Sección 3: Información y Progreso ---
        info_frame = ctk.CTkFrame(main_frame, fg_color=("#2b2b2b", "#2b2b2b"))
        info_frame.pack(fill="x", pady=15, padx=5)
        
        ctk.CTkLabel(info_frame, text="Video detectado:", font=("Roboto", 12)).pack(side="left", padx=10, pady=5)
        ctk.CTkLabel(info_frame, textvariable=self.video_title_var, font=("Roboto", 12, "bold"), text_color="#4da6ff").pack(side="left", pady=5)

        self.lbl_status = ctk.CTkLabel(main_frame, textvariable=self.status_var, text_color="gray")
        self.lbl_status.pack(pady=(5, 5))

        self.progress_bar = ctk.CTkProgressBar(main_frame)
        self.progress_bar.pack(fill="x", pady=5)
        self.progress_bar.set(0)

        # --- Botones Finales ---
        action_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        action_frame.pack(fill="x", pady=(10, 0))

        self.btn_download = ctk.CTkButton(action_frame, text="INICIAR PROCESO", height=45, font=("Roboto", 16, "bold"), command=self.start_thread)
        self.btn_download.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.btn_open_folder = ctk.CTkButton(action_frame, text="Abrir Carpeta", height=45, fg_color="green", state="disabled", command=self.open_destination)
        self.btn_open_folder.pack(side="right")

    # --- Lógica de Interfaz ---
    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.mkv;*.avi;*.mov")])
        if file_path:
            self.entry_url.delete(0, tk.END)
            self.entry_url.insert(0, file_path)
            self.video_title_var.set(os.path.basename(file_path))

    def choose_output_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder = folder
            self.status_var.set(f"Destino: .../{os.path.basename(folder)}")

    def open_destination(self):
        if os.path.exists(self.output_folder):
            os.startfile(self.output_folder)

    # --- Lógica de Negocio ---
    def parse_time(self, time_str):
        try:
            parts = list(map(int, time_str.split(':')))
            if len(parts) == 1: return parts[0]
            if len(parts) == 2: return parts[0] * 60 + parts[1]
            if len(parts) == 3: return parts[0] * 3600 + parts[1] * 60 + parts[2]
        except:
            return None
        return None

    def start_thread(self):
        url = self.entry_url.get()
        intervals_raw = self.entry_intervals.get()
        
        # Validación básica
        if not url:
            self.shake_widget(self.entry_url)
            return
        if not intervals_raw:
            self.shake_widget(self.entry_intervals)
            return

        # Preparar intervalos
        intervals = []
        try:
            for pair in intervals_raw.split(","):
                s, e = pair.strip().split("-")
                t_s, t_e = self.parse_time(s), self.parse_time(e)
                if t_s is not None and t_e is not None:
                    intervals.append((t_s, t_e))
                else:
                    raise ValueError
        except:
            messagebox.showerror("Error de Formato", "Revisa los intervalos. Usa formato 'inicio-fin' (ej: 10-20, 01:05-01:30)")
            return

        # Bloquear UI
        self.btn_download.configure(state="disabled")
        self.btn_open_folder.configure(state="disabled")
        self.progress_bar.set(0)
        
        threading.Thread(target=self.process_video, args=(url, intervals), daemon=True).start()

    def process_video(self, url, intervals):
        temp_video = os.path.join(self.output_folder, "temp_full_video.mp4")
        is_local = os.path.exists(url)
        video_title = "video"

        try:
            # 1. DESCARGA (si no es local)
            if is_local:
                temp_video = url
                video_title = os.path.splitext(os.path.basename(url))[0]
                self.progress_bar.set(0.5) # Salto directo al 50%
            else:
                self.status_var.set("Analizando URL...")
                
                # Opciones YT-DLP con Hook de progreso
                ydl_opts = {
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
                    'outtmpl': temp_video,
                    'progress_hooks': [self.yt_dlp_hook],
                    'quiet': True,
                    'no_warnings': True
                }
                
                # Primero sacamos info para el título
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    video_title = re.sub(r'[\\/*?:"<>|]', "", info.get('title', 'video')) # Sanitize filename
                    self.video_title_var.set(video_title)
                    
                    self.status_var.set(f"Descargando: {video_title[:30]}...")
                    ydl.download([url])

            # 2. PROCESAMIENTO (FFMPEG)
            self.status_var.set("Iniciando corte de clips...")
            total_clips = len(intervals)
            
            for i, (start, end) in enumerate(intervals):
                # Calcular progreso (mitad descarga, mitad proceso)
                # Escala el progreso del 50% al 100%
                base_prog = 0.5
                step_prog = 0.5 * ((i + 1) / total_clips)
                self.progress_bar.set(base_prog + step_prog)
                
                duration = end - start
                safe_title = video_title.replace(" ", "_")[:20]
                output_name = os.path.join(self.output_folder, f"clip_{i+1}_{safe_title}_{start}s.mp4")
                
                self.status_var.set(f"Renderizando clip {i+1}/{total_clips} (NVENC)..." if self.use_nvenc_var.get() else f"Renderizando clip {i+1}/{total_clips} (CPU)...")
                
                cmd = ['ffmpeg', '-y', '-ss', str(start)]
                cmd.extend(['-i', temp_video])
                cmd.extend(['-t', str(duration)])
                
                if self.use_nvenc_var.get():
                    cmd.extend(['-c:v', 'h264_nvenc', '-preset', 'p4', '-rc', 'vbr', '-cq', '24', '-c:a', 'copy'])
                else:
                    cmd.extend(['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23', '-c:a', 'copy'])
                
                cmd.append(output_name)
                
                subprocess.run(cmd, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)

            self.status_var.set("¡Proceso Finalizado!")
            self.btn_open_folder.configure(state="normal")
            messagebox.showinfo("Éxito", f"Se generaron {total_clips} clips correctamente.")

        except Exception as e:
            self.status_var.set("Error crítico")
            messagebox.showerror("Error", str(e))
        
        finally:
            if not is_local and os.path.exists(temp_video):
                try:
                    os.remove(temp_video)
                except:
                    pass
            self.btn_download.configure(state="normal")

    def yt_dlp_hook(self, d):
        if d['status'] == 'downloading':
            try:
                p = d.get('_percent_str', '0%').replace('%','')
                # Mapeamos 0-100% de descarga al 0-50% de la barra total
                val = float(p) / 200 
                self.progress_bar.set(val)
            except:
                pass
        elif d['status'] == 'finished':
            self.progress_bar.set(0.5)

    def shake_widget(self, widget):
        # Efecto visual simple para error
        orig_color = widget.cget("fg_color")
        widget.configure(fg_color="darkred")
        self.after(500, lambda: widget.configure(fg_color=orig_color))

if __name__ == "__main__":
    app = ClipsApp()
    app.mainloop()