import os
import random
import string
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.ogg import OggFileType
from mutagen.oggflac import OggFLAC
from mutagen.oggopus import OggOpus
from mutagen.oggvorbis import OggVorbis
from mutagen.aac import AAC

def extract_metadata_and_cover(file_path):
    # создание каталога с произвольным именем внутри temp
    dir_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    dir_path = os.path.join('temp', dir_name)
    os.makedirs(dir_path, exist_ok=True)

    # определяем тип аудиофайла
    if file_path.endswith('.mp3'):
        audio = MP3(file_path, ID3=EasyID3)
    elif file_path.endswith('.flac'):
        audio = FLAC(file_path)
    elif file_path.endswith('.ogg'):
        audio = OggFileType(file_path)
    elif file_path.endswith('.opus'):
        audio = OggOpus(file_path)
    elif file_path.endswith('.aac'):
        audio = AAC(file_path)
    else:
        print(f"Unsupported file type for file {file_path}")
        return

    # извлечение метаданных и сохранение в txt файл
    with open(os.path.join(dir_path, 'metadata.txt'), 'w', encoding='utf-8') as f:
        for key, value in audio.items():
            f.write(f"{key}: {value}\n")

    # извлечение обложки и сохранение в jpg файл
    if isinstance(audio, (FLAC, OggFLAC)):
        pictures = audio.pictures
        if pictures:
            with open(os.path.join(dir_path, 'cover.jpg'), 'wb') as f:
                f.write(pictures[0].data)
    elif isinstance(audio, MP3):
        if 'APIC:' in audio:
            with open(os.path.join(dir_path, 'cover.jpg'), 'wb') as f:
                f.write(audio['APIC:'].data)

extract_metadata_and_cover(r'j:\bukup\Music\exteraGram\Midix_-_Frnxx_64576463.mp3')
