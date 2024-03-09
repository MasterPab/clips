import os
import yt_dlp
from moviepy.video.io.VideoFileClip import VideoFileClip

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
# Para hacer funcionar el código, debes poner en los "intervals" todos los clips que vas a usar en su rango de tiempo. Por ejemplo intervals = [("0:15", "0:30"), ("0:45", "1:00")]
if __name__ == "__main__":
    url = "tuvideoaquí"
    intervals = [("42:55", "43:48"), ("01:04:08", "01:04:28")]

    download_clips(url, intervals)
