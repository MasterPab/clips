# YouTube Clips por MasterPab

Este repositorio contiene un script en Python que te permite descargar y recortar clips de videos de YouTube en segmentos específicos. La herramienta utiliza las bibliotecas yt-dlp y moviepy para lograr esto.

## Instrucciones de Uso

1. Asegúrate de tener Python instalado en tu sistema. Aquí está el enlace (recuerda añadir a PATH): https://www.python.org/downloads/
2. Instala las bibliotecas necesarias ejecutando `pip install yt-dlp moviepy tkinter`
3. Copia el enlace del video de YouTube que te interesa y reemplaza la variable `url` en el código con tu enlace.
4. Define los intervalos de tiempo deseados en la variable `intervals` para crear clips personalizados. Ejemplo:

```python
url = "https://www.youtube.com/watch?v=K007dTYLsko&pp=ygUYdW5kZXJ0YWxlIHZpbmVzYXVjZSBqb2Vs"
intervals = [("42:55", "43:48"), ("01:04:08", "01:04:28")]
```

5. Ejecuta el código en la terminal mediante `python clips.py` o en caso de usar la interfaz gráfica `python clips_grafico.py`
## Personalización

Puedes ajustar los intervalos según tus necesidades para obtener los clips deseados. Además, puedes modificar la calidad del video ajustando los parámetros en la sección **ydl_opts** del código.

## Interfaz gráfica

Si quieres usar Clips con una interfaz gráfica, puedes hacerlo mediante el archivo **clips_grafico.py**. Para esto necesitas la librería `tkinter` mencionada en las instrucciones de uso. 

Ejemplo:

![Demostración interfaz gráfica](https://i.imgur.com/rUd6x4G.png)

## Demostración en imagen del uso en código

![Demostración en imagen](https://github.com/MasterPab/clips/blob/main/demo.gif)
