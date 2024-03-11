import os
import yt_dlp
from moviepy.video.io.VideoFileClip import VideoFileClip
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

def download_clips(url, intervals):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': 'temp_video.%(ext)s',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    input_video = 'temp_video.mp4'

    for i, interval in enumerate(intervals):
        start_time, end_time = interval
        output_video = f'output_clip_{i+1}.mp4'

        clip = VideoFileClip(input_video).subclip(start_time, end_time)
        clip.write_videofile(output_video, codec="libx264", audio_codec="aac", fps=24)

        print(f"El clip {i+1} se ha creado exitosamente: {output_video}")

        clip.close()

    os.remove(input_video)

def browse_file():
    file_path = filedialog.askopenfilename()
    entry_url.delete(0, tk.END)
    entry_url.insert(0, file_path)

def start_download():
    url = entry_url.get()
    intervals = parse_intervals(entry_intervals.get())
    download_clips(url, intervals)

def parse_intervals(interval_str):
    intervals = []
    pairs = interval_str.split(",")
    for pair in pairs:
        start, end = pair.strip().split("-")
        intervals.append((start, end))
    return intervals

# Interfaz gráfica
root = tk.Tk()
root.title("Clips por MasterPab")

label_url = ttk.Label(root, text="URL del video:")
label_url.grid(row=0, column=0, padx=10, pady=10)

entry_url = ttk.Entry(root, width=40)
entry_url.grid(row=0, column=1, padx=10, pady=10)

label_intervals = ttk.Label(root, text="Intervalos (Formato: inicio-fin, inicio-fin):")
label_intervals.grid(row=1, column=0, padx=10, pady=10)

entry_intervals = ttk.Entry(root, width=40)
entry_intervals.grid(row=1, column=1, padx=10, pady=10)

btn_download = ttk.Button(root, text="Descargar Clips", command=start_download)
btn_download.grid(row=2, column=1, pady=20)

root.mainloop()
