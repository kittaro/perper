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
from mutagen.wave import WAVE

def extract_metadata_and_cover(audio_file_path):
    # создание каталога с произвольным именем внутри temp
    random_dir_name = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    dir_path = os.path.join('temp', random_dir_name)
    os.makedirs(dir_path, exist_ok=True)

    # определяем тип аудиофайла
    file_extension = os.path.splitext(audio_file_path)[1].lower()
    if file_extension == '.mp3':
        audio = MP3(audio_file_path, ID3=EasyID3)
    elif file_extension == '.flac':
        audio = FLAC(audio_file_path)
    elif file_extension == '.ogg':
        audio = OggFileType(audio_file_path)
        if isinstance(audio, OggVorbis):
            print("Ogg Vorbis")
        elif isinstance(audio, OggOpus):
            print("Ogg Opus")
        elif isinstance(audio, OggFLAC):
            print("Ogg FLAC")
        else:
            print("неизвестный тип Ogg")
    elif file_extension == '.aac':
        audio = AAC(audio_file_path)
    elif file_extension == '.wav':
        audio = WAVE(audio_file_path)
    else:
        print(f'неподдерживаемый тип: {file_extension}')
        return

    # извлечение метаданных и сохранение в txt файл
    with open(os.path.join(dir_path, 'metadata.txt'), 'w', encoding='utf-8') as f:
        for key, value in audio.items():
            f.write(f'{key}: {value}\n')

    # извлечение обложки и сохранение в jpg файл
    if isinstance(audio, (FLAC, OggFLAC)):
        pictures = audio.pictures
        if pictures:
            with open(os.path.join(dir_path, 'cover.jpg'), 'wb') as f:
                f.write(pictures[0].data)
#    elif isinstance(audio, MP3):
#        if 'APIC:' in audio:
#            with open(os.path.join(dir_path, 'cover.jpg'), 'wb') as f:
#                f.write(audio.tags['APIC:'].data)
    if 'APIC:' in audio or 'COVERART' in audio:
        if 'APIC:' in audio:
            cover_data = audio.tags['APIC:'].data
        else:
            cover_data = audio.tags['COVERART'].data

        with open(os.path.join(dir_path, 'cover.jpg'), 'wb') as f:
            f.write(cover_data)
extract_metadata_and_cover(r"j:\bukup\Music\exteraGram\Midix_-_Frnxx_64576463.mp3")