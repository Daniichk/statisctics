import yt_dlp

def download_video(url):
    # Настройки загрузки
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',  # Выбирает лучшее качество видео и аудио
        'outtmpl': '%(title)s.%(ext)s',        # Имя файла: Название_видео.расширение
        'postprocessors': [{                   # Использует FFmpeg для объединения видео и звука
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',           # Конвертировать в mp4
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Начинаю загрузку: {url}")
            ydl.download([url])
            print("Загрузка завершена!")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    # Сюда можно вставить ссылку на видео, плейлист или канал
    video_url = input("Введите ссылку на YouTube видео/плейлист: ")
    download_video(video_url)
