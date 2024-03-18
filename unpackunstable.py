import os
import random
import string
from tinytag import TinyTag, TinyTagException

def extract_metadata_and_cover(file_path):
    # создание каталога с произвольным именем внутри temp
    dir_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    dir_path = os.path.join('temp', dir_name)
    os.makedirs(dir_path, exist_ok=True)

    try:
        # извлечение метаданных
        tag = TinyTag.get(file_path, image=True)

        metadata = {
            'album': tag.album,
            'albumartist': tag.albumartist,
            'artist': tag.artist,
            'audio_offset': tag.audio_offset,
            'bitrate': tag.bitrate,
            'channels': tag.channels,
            'comment': tag.comment,
            'composer': tag.composer,
            'disc': tag.disc,
            'disc_total': tag.disc_total,
            'duration': tag.duration,
            'filesize': tag.filesize,
            'genre': tag.genre,
            'samplerate': tag.samplerate,
            'title': tag.title,
            'track': tag.track,
            'track_total': tag.track_total,
            'year': tag.year,
            # доп информация
            'extra': str(tag.extra)  # преобразование extra в строку
        }

        # метаданные в txt файл
        with open(os.path.join(dir_path, 'metadata.txt'), 'w', encoding='utf-8') as f:
            for key, value in metadata.items():
                f.write(f"{key}: {value}\n")

        # извлечение обложки
        if tag.get_image():
            cover_data = tag.get_image()
            with open(os.path.join(dir_path, 'cover.png'), 'wb') as f:
                f.write(cover_data)
    except TinyTagException as e:
        print(f"Ошибка при обработке файла {file_path}: {e}")


file_path = r"j:\Limbus Company\[8] [ Limbus Company ] - Mili - Fly, My Wings (Instrumental).wav"
extract_metadata_and_cover(file_path)