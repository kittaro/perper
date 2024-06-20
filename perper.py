import os
import random
import string
from tinytag import TinyTag, TinyTagException
import telebot
import sys
import json
import shutil
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout

from qframelesswindow import AcrylicWindow, StandardTitleBar
from qfluentwidgets import PrimaryPushButton, TitleLabel, BodyLabel, ComboBox, SubtitleLabel, CheckBox, HorizontalFlipView, HorizontalPipsPager, AvatarWidget, ImageLabel, CaptionLabel, StrongBodyLabel, ToolButton, FluentIcon, MessageBoxBase, LineEdit

CONFIGS_DIR = 'configs'
TEMP_DIR = 'temp'
CONFIG_EXTENSION = '.cfg'
SINGLE_FILE_SUFFIX = '_single'
MULTIPLE_FILES_SUFFIX = '_multiple'

extracted_metadata = {}
image_paths = []
content_comboboxes = []

def clear_temp_folder():
    # очистка временной папочки ^_^
    if os.path.exists(TEMP_DIR):  # существует ли папочка
        try:
            shutil.rmtree(TEMP_DIR)
        except Exception as e:
            print(f"Ошибка при удалении папки temp: {e}")

class TelegramWorker(QThread):
    # только не подвисай
    message_sent = pyqtSignal(str, str)

    def __init__(self, token, channel_id, message_text, photo_path=None):
        super().__init__()
        self.token = token
        self.channel_id = channel_id
        self.message_text = message_text
        self.photo_path = photo_path

    def run(self):
        # публикация но отправка и в канал
        bot = telebot.TeleBot(self.token)
        try:
            if self.photo_path:
                with open(self.photo_path, 'rb') as photo:
                    bot.send_photo(self.channel_id, photo, caption=self.message_text, timeout=5)
                self.message_sent.emit("Сообщение с фото отправлено.", "green")
            else:
                bot.send_message(self.channel_id, self.message_text, timeout=5)
                self.message_sent.emit("Текстовое сообщение отправлено.", "green")
        except Exception as e:
            self.message_sent.emit(f"Ошибка при отправке сообщения: {e}", "red")


def extract_mdata(file_paths):
    # метаданные и обложка
    global extracted_metadata, image_paths

    extracted_metadata.clear()
    image_paths.clear()

    if not isinstance(file_paths, list):
        file_paths = [file_paths]

    supported_files_found = False

    for file_path in file_paths:
        dir_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))
        dir_path = os.path.join(TEMP_DIR, dir_name)
        os.makedirs(dir_path, exist_ok=True)

        try:
            tag = TinyTag.get(file_path, image=True)
            supported_files_found = True

            metadata = {
                'Пустое поле': "",
                'Название трека': tag.title,
                'Название альбома': tag.album,
                'Исполнитель трека': tag.artist,
                'Исполнитель альбома': tag.albumartist,
                'Композитор': tag.composer,
                'Жанр': tag.genre,
                'Битрейт': f"{round(tag.bitrate)} kBits/s" if tag.bitrate else "Данные недоступны",
                'Частота дискретизации': f"{tag.samplerate} Hz" if tag.samplerate else "Данные недоступны",
                'Каналы': tag.channels,
                'Номер трека': tag.track,
                'Всего треков': tag.track_total,
                'Диск': tag.disc,
                'Всего дисков': tag.disc_total,
                'Дата': tag.year,
                'Комментарий': tag.comment,
            }

            for key, value in metadata.items():
                extracted_metadata.setdefault(key, []).append(value)

            if tag.get_image():
                cover_data = tag.get_image()
                file_name = os.path.splitext(os.path.basename(file_path))[0]
                cover_path = os.path.join(dir_path, f'{file_name}.png')
                with open(cover_path, 'wb') as f:
                    f.write(cover_data)
                image_paths.append(cover_path)

        except TinyTagException as e:
            print(f"Ошибка при обработке файла {file_path}: {e}")

    return supported_files_found


def create_content_combobox(index):
    # комбобоксы содержания
    combo_pub = QHBoxLayout()

    checkBox = CheckBox()
    combo_pub.addWidget(checkBox)

    emoji_combo = ComboBox()
    emoji_list = ['', '🎵', '🎶', '💽', '💿', '📀', '👤', '👥', '📅', '©️', '®️']
    emoji_combo.addItems(emoji_list)
    emoji_combo.setFixedWidth(70)
    combo_pub.addWidget(emoji_combo)

    text_edit = LineEdit()
    text_edit.setMaxLength(50)
    combo_pub.addWidget(text_edit)

    from_file = ComboBox()
    from_file.setFixedWidth(180) # 150 - неплохо
#    from_file.setMinimumWidth(180)
    combo_pub.addWidget(from_file)

    return combo_pub


def update_content_comboboxes():
    # списки ключей метаданных в комбобоксе from_file
    global content_comboboxes

    for combo_pub in content_comboboxes:
        from_file_combo = combo_pub.itemAt(3).widget()
        from_file_combo.clear()

    if extracted_metadata:
        # разделение на 1/несколько файлов
        if len(extracted_metadata.get('Название трека', [])) > 1:
            keys_to_add = ['Пустое поле', 'Название альбома', 'Исполнитель альбома', 'Всего дисков', 'Дата', 'Всего треков']
        else:
            keys_to_add = ['Пустое поле','Название трека', 'Название альбома', 'Исполнитель трека', 'Исполнитель альбома', 'Композитор', 'Жанр',
                'Битрейт', 'Частота дискретизации', 'Каналы', 'Номер трека', 'Всего треков', 'Диск', 'Всего дисков', 'Дата', 'Комментарий']

        # добавление ключи метаданных в from_file (порядок ключей НЕ менять)
        for key in keys_to_add:
            if key in extracted_metadata:
                for combo_pub in content_comboboxes:
                    from_file_combo = combo_pub.itemAt(3).widget()
                    from_file_combo.addItem(key)


def update_message_container():
    # как то обновляет содержимое message_label
    message_text = ""
    current_index = window.flipView.currentIndex()

    for combo_pub in content_comboboxes:
        checkbox = combo_pub.itemAt(0).widget()
        if checkbox.isChecked():
            emoji_combo = combo_pub.itemAt(1).widget()
            emoji = emoji_combo.currentText()

            text_edit = combo_pub.itemAt(2).widget()
            text = text_edit.text()

            from_file_combo = combo_pub.itemAt(3).widget()
            metadata_key = from_file_combo.currentText()

            metadata_value = ""
            if metadata_key in extracted_metadata:
                metadata_values = extracted_metadata[metadata_key]
                if len(metadata_values) > current_index:
                    metadata_value = metadata_values[current_index]
                    if metadata_value is None: metadata_value = "Данные недоступны"

            message_text += f"\n{emoji} {text} {metadata_value}"
            

    message_label.setText(message_text.strip())
#    message_label.


def save_config(config_name):
    # !!!НЕ ЗАБЫТЬ ОБНОВИТЬ ВЕРСИЮ КОНФИГА
    # сохранение конфига 1/несколько файлов
    file_type_suffix = SINGLE_FILE_SUFFIX if len(extracted_metadata.get('Название трека', [])) == 1 else MULTIPLE_FILES_SUFFIX
    config_path = os.path.join(CONFIGS_DIR, config_name + file_type_suffix + CONFIG_EXTENSION)

    config_data = {
        'test_version': '1.6_empty_first_one',
        'api_token': window.api_token_edit.text(),
        'group_id': window.group_edit.text(),
        'content': []
    }

    for combo_pub in content_comboboxes:
        emoji_index = combo_pub.itemAt(1).widget().currentIndex()
        text = combo_pub.itemAt(2).widget().text()
        from_file_index = combo_pub.itemAt(3).widget().currentIndex()
        config_data['content'].append({
            'emoji_index': emoji_index,
            'text': text,
            'from_file_index': from_file_index
        })

    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4)
        print(f"Конфигурация сохранена в файл: {config_path}")
    except Exception as e:
        print(f"Ошибка при сохранении конфигурации: {e}")


def load_config(config_name):
    # загрузка из файла (1/несколько файлов)
    file_type_suffix = SINGLE_FILE_SUFFIX if len(extracted_metadata.get('Название трека', [])) == 1 else MULTIPLE_FILES_SUFFIX
    config_path = os.path.join(CONFIGS_DIR, config_name + file_type_suffix + CONFIG_EXTENSION)

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        window.api_token_edit.setText(config_data.get('api_token', ''))
        window.group_edit.setText(config_data.get('group_id', ''))

        for i, content_data in enumerate(config_data.get('content', [])):
            if i < len(content_comboboxes):
                combo_pub = content_comboboxes[i]
                combo_pub.itemAt(1).widget().setCurrentIndex(content_data.get('emoji_index', 0))
                combo_pub.itemAt(2).widget().setText(content_data.get('text', ''))
                combo_pub.itemAt(3).widget().setCurrentIndex(content_data.get('from_file_index', 0))
        print(f"Конфигурация загружена из файла: {config_path}")

    except FileNotFoundError:
        print(f"Файл конфигурации не найден: {config_path}")
    except json.JSONDecodeError:
        print(f"Ошибка чтения файла конфигурации: {config_path}")


class SaveConfigDialog(MessageBoxBase):
    # окно сохранения конф
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Сохранить конфигурацию")
        self.titleLabel = SubtitleLabel("Введите название конфигурации:")
        self.nameLineEdit = LineEdit()
        self.nameLineEdit.setPlaceholderText("Название конфигурации")
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.nameLineEdit)
        self.widget.setMinimumWidth(350)

        self.yesButton.setText("Сохранить")
        self.cancelButton.setText("Отмена")


class Window(AcrylicWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.resize(1200, 800)
        self.setTitleBar(StandardTitleBar(self))
        self.setWindowIcon(QIcon("logo.ico"))
        self.setWindowTitle("perper")
        self.setAcceptDrops(True)
        self.windowEffect.setMicaEffect(self.winId(), False)  # !!!убрать для поддержки Win10!!! # переключатель - следовать системной теме оформления
        #self.windowEffect.addShadowEffect(self.winId())        # windows10 - 1
        #self.windowEffect.removeBackgroundEffect(self.winId()) # windows10 - 2
        self.interface_created = False

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addSpacing(self.titleBar.height())

        icon = FluentIcon.DOWNLOAD.icon()
        pixmap = icon.pixmap(icon.actualSize(QSize(64, 64)))  # ПОЧЕМУ НАПРЯМУЮ НЕЛЬЗЯ ПЕРЕДАТЬ
        self.icon_label = ImageLabel(pixmap)
        self.icon_label.setFixedSize(64, 64)
        self.main_layout.addWidget(self.icon_label, alignment=Qt.AlignCenter | Qt.AlignBottom)

        self.drop_label = TitleLabel("Перетащите файлы в окно для продолжения работы")
        self.main_layout.addWidget(self.drop_label, alignment=Qt.AlignCenter | Qt.AlignBottom)

        self.drop_subtext = BodyLabel("Поддерживаемые типы файлов: mp3, ogg, m4a, flac, opus, wma и wave")
        self.main_layout.addWidget(self.drop_subtext, alignment=Qt.AlignCenter | Qt.AlignTop)

        clear_temp_folder()

    def create_main_interface(self):
        # основной интерфейс
        self.drop_label.hide()
        self.drop_subtext.hide()
        self.icon_label.hide()

        containers_main = QHBoxLayout()
        self.main_layout.addLayout(containers_main)

        preview_main = QWidget(self)
        containers_main.addWidget(preview_main)

        settings_main = QWidget(self)
        settings_main.setStyleSheet("background-color:white; border-radius:8px;")
        containers_main.addWidget(settings_main)

        # --- preview_main ---
        preview_layout = QHBoxLayout()
        preview_main.setLayout(preview_layout)

        self.avatar_widget = AvatarWidget("avatar.png")
        self.avatar_widget.setRadius(24)
        preview_layout.addWidget(self.avatar_widget, alignment=Qt.AlignBottom)
        preview_layout.addSpacing(10)

        # --- message_container ---
        global message_container
        message_container = QWidget(self)
        message_container.setStyleSheet("background-color:white; border-radius:24px; border-bottom-left-radius: 4px")
        message_container.setMinimumHeight(50)
        message_container.setMaximumHeight(900)
        message_container.setFixedWidth(400)
        preview_layout.addWidget(message_container, alignment=Qt.AlignBottom)
        preview_layout.addStretch()

        global message_layout
        message_layout = QVBoxLayout()
        message_container.setLayout(message_layout)

        # --- album_art ---
        global album_art
        album_art = ImageLabel()
        album_art.setBorderRadius(16, 16, 16, 16)
        album_art.scaledToWidth(message_container.width() - 18)
        message_layout.addWidget(album_art, alignment=Qt.AlignTop)

        # --- message_label ---
        global message_label
        message_label = BodyLabel("")
        message_label.setWordWrap(True)
        message_layout.addWidget(message_label, alignment=Qt.AlignTop)

        # --- settings_main ---
        settings_layout = QVBoxLayout()
        settings_main.setLayout(settings_layout)
        settings_layout.setContentsMargins(20, 20, 20, 20)

        settings_title = TitleLabel("Параметры")
        settings_layout.addWidget(settings_title)
        settings_layout.addSpacing(10)

        # --- настройки бота ---
        setting_publish_title = SubtitleLabel("Бот")
        settings_layout.addWidget(setting_publish_title)

        combo_bot = QHBoxLayout()
        settings_layout.addLayout(combo_bot)
        combo_bot.addSpacing(20)

        api_token_label = BodyLabel("API Token")
        combo_bot.addWidget(api_token_label)
        self.api_token_edit = LineEdit()
        combo_bot.addWidget(self.api_token_edit)
        combo_bot.addSpacing(20)

        self.bublish_label = BodyLabel("Место публикации")
        combo_bot.addWidget(self.bublish_label)
        self.group_edit = LineEdit()
        self.group_edit.setText("@")
        combo_bot.addWidget(self.group_edit)
        settings_layout.addSpacing(10)

        # --- настройки содержания ---
        setting_publish_title = SubtitleLabel("Содержание публикации")
        settings_layout.addWidget(setting_publish_title)

        # --- конфигурации ---
        config_layout = QHBoxLayout()
        settings_layout.addLayout(config_layout)
        config_layout.addSpacing(20)

        config_load_label = StrongBodyLabel("Загрузить конфигурацию:")
        config_layout.addWidget(config_load_label)

        self.config_combobox = ComboBox()
        self.config_combobox.currentIndexChanged.connect(self.load_selected_config)
        config_layout.addWidget(self.config_combobox)

        config_save = ToolButton(FluentIcon.SAVE)
        config_save.clicked.connect(self.save_current_config)
        config_layout.addWidget(config_save)

        config_delete = ToolButton(FluentIcon.DELETE)
        config_delete.clicked.connect(self.delete_selected_config)
        config_layout.addWidget(config_delete)

        # --- комбобоксы содержания ---
        global content_comboboxes
        for i in range(8):
            content_combobox = create_content_combobox(i)
            content_comboboxes.append(content_combobox)
            settings_layout.addLayout(content_combobox)

        # --- текст о FlipView и Pager ---
        self.choose_cover_label = SubtitleLabel("Выберите обложку")
        settings_layout.addWidget(self.choose_cover_label)

        self.current_file_label = CaptionLabel("Текущий файл для информации:")
        self.current_file_label.setWordWrap(True)
        settings_layout.addWidget(self.current_file_label)

        # --- контейнер для FlipView и Pager ---
        self.flipView_container = QWidget()
        self.flipView_container.setFixedHeight(140)
        self.flipView_layout = QVBoxLayout()
        self.flipView_container.setLayout(self.flipView_layout)

        self.flipView = HorizontalFlipView()
        self.flipView.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)
        self.flipView.setItemSize(QSize(320, 100))
        self.flipView.setFixedHeight(100)
        self.flipView.setSpacing(10)
        self.flipView.setBorderRadius(10)
        self.flipView.currentIndexChanged.connect(self.update_album_art)
        self.flipView_layout.addWidget(self.flipView)

        self.pager = HorizontalPipsPager()
        self.pager.currentIndexChanged.connect(self.flipView.setCurrentIndex)
        self.flipView.currentIndexChanged.connect(self.pager.setCurrentIndex)
        self.flipView_layout.addWidget(self.pager, alignment=Qt.AlignCenter)
        settings_layout.addWidget(self.flipView_container)

        # --- ни:З ---
        settings_layout.addStretch()
        self.log_text = CaptionLabel("Здесь будут логи")
        self.log_text.setWordWrap(True)
        settings_layout.addWidget(self.log_text)

        button_send_to = PrimaryPushButton('Опубликовать')
        button_send_to.clicked.connect(self.send_message_to_channel)
        settings_layout.addWidget(button_send_to, alignment=Qt.AlignRight)

        containers_main.setStretchFactor(preview_main, 1)
        containers_main.setStretchFactor(settings_main, 2)

        # сигналы всех элементов интерфейса (!!после создания)
        for i, combo_pub in enumerate(content_comboboxes):
            checkBox = combo_pub.itemAt(0).widget()
            emoji_combo = combo_pub.itemAt(1).widget()
            text = combo_pub.itemAt(2).widget()
            from_file = combo_pub.itemAt(3).widget()
            checkBox.stateChanged.connect(update_message_container)
            emoji_combo.currentIndexChanged.connect(update_message_container)
            text.textChanged.connect(update_message_container)
            from_file.currentIndexChanged.connect(update_message_container)

    def resizeEvent(self, e):
        super().resizeEvent(e)

    def update_album_art(self, index):
        # обновить обложку в превью на ту из FlipView 
        global album_art
        if 0 <= index < len(image_paths):
            image_path = image_paths[index]
            album_art.setImage(image_path)
            album_art.setBorderRadius(16, 16, 16, 16)
            album_art.scaledToWidth(message_container.width() - 18) # почему -18 ? +_ёто костыль
            message_layout.update()


    def send_message_to_channel(self):
        # отправка !ПРОВЕРКУ ПРОВЕРКУ ПРОВЕРКУ ПРОВЕРКУ
        token = self.api_token_edit.text()
        channel_id = self.group_edit.text()
        message_text = message_label.text()

        if not token:
            self.log_to_widget("Ошибка: не указан API токен.", "red")
            return
        if not channel_id or not channel_id.startswith("@"):
            self.log_to_widget("Ошибка: некорректный ID канала. ID должен начинаться с '@'.", "red")
            return

        current_image_index = self.flipView.currentIndex()
        photo_path = image_paths[current_image_index] if 0 <= current_image_index < len(image_paths) else None

        self.telegram_worker = TelegramWorker(token, channel_id, message_text, photo_path)
        self.telegram_worker.message_sent.connect(self.log_to_widget)
        self.telegram_worker.start()

    def log_to_widget(self, message, color="black"):
        #
        # вывод логов + цвет
        # проверка на первый экран0.5
        # !поправить немного
        #
        if self.interface_created:
            self.log_text.setText(f'<font color="{color}">{message}</font>')
        else:
            print(message)  # в терминал если нет

    def dragEnterEvent(self, event):
        # обработка ПЕРЕТАКСИВАНИЯ только
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        # ну literally дроп ивент
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()

            file_paths = []
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if os.path.isfile(file_path):
                    file_paths.append(file_path)

            if file_paths:
                # !проверка поддерживаемых файлов ПЕРЕД обработкой
                if any(self.is_supported_file(file_path) for file_path in file_paths):
                    supported_files_found = extract_mdata(file_paths)

                    if supported_files_found:
                        if not self.interface_created:
                            self.create_main_interface()
                            self.interface_created = True

                        album_art.setImage() # очистить наконец обложку
                        self.update_flipview()
                        self.update_album_art(0)
                        update_content_comboboxes()
                        self.update_config_combobox()
                        self.load_last_config()
                    else:
                        # проверка на первый экран1
                        if self.interface_created:
                            self.log_to_widget(
                                "Ошибка: Перетащите хотя бы один поддерживаемый аудиофайл.", "red")
                        else:
                            print("Ошибка: Перетащите хотя бы один поддерживаемый аудиофайл.")
                else:
                    # проверка на первый экран2
                    if self.interface_created:
                        self.log_to_widget(
                            "Ошибка: Перетаскиваемые файлы не поддерживаются.", "red")
                    else:
                        print("Ошибка: Перетаскиваемые файлы не поддерживаются.")
        else:
            event.ignore()

    def is_supported_file(self, file_path):
        # проверяет, поддерживается ли файл
        try:
            TinyTag.get(file_path)  # пробует извлечь метаданные 
            return True
        except TinyTagException:
            return False

    def update_flipview(self):
        # обновляет FlipView с новыми обложками
        self.flipView.clear()
        self.flipView.addImages(image_paths)
        self.pager.setPageNumber(self.flipView.count())
        self.pager.setVisibleNumber(self.flipView.count())

        self.update_current_file_label(0)
        self.flipView.currentIndexChanged.connect(self.update_current_file_label)
        self.flipView.currentIndexChanged.connect(update_message_container)

        if len(image_paths) <= 1:
            self.flipView_container.hide()
            self.choose_cover_label.hide()
            self.current_file_label.hide()
        else:
            self.flipView_container.show()
            self.choose_cover_label.show()
            self.current_file_label.show()

        self.update_config_combobox()

    def update_current_file_label(self, index):
        # обновляет текст с названием текущего файла
        if 0 <= index < len(image_paths):
            file_path = image_paths[index]
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            self.current_file_label.setText(
                f"Текущий файл для информации: {file_name}")

    def update_config_combobox(self):
        # обновляет список доступных конфигураций
        self.config_combobox.clear()
        file_type_suffix = SINGLE_FILE_SUFFIX if len(
            extracted_metadata.get('Название трека', [])) == 1 else MULTIPLE_FILES_SUFFIX
        config_files = [f for f in os.listdir(CONFIGS_DIR) if
                        f.endswith(file_type_suffix + CONFIG_EXTENSION)]
        self.config_combobox.addItems([f[:-len(file_type_suffix + CONFIG_EXTENSION)] for f in config_files])

    def create_new_config(self):
        # создает новую конфигурацию((
        dialog = SaveConfigDialog(self)
        if dialog.exec():
            config_name = dialog.nameLineEdit.text()
            if config_name:
                save_config(config_name)
                self.update_config_combobox()

    def save_current_config(self):
        # сохранить ТЕКУЩУЮ (вызвать safeconfig)
        dialog = SaveConfigDialog(self)
        if dialog.exec():
            config_name = dialog.nameLineEdit.text()
            if config_name:
                save_config(config_name)
                self.update_config_combobox()

    def delete_selected_config(self):
        # удаляет выбранную (текущую) конфигурацию
        config_name = self.config_combobox.currentText()
        if config_name:
            file_type_suffix = SINGLE_FILE_SUFFIX if len(
                extracted_metadata.get('Название трека', [])) == 1 else MULTIPLE_FILES_SUFFIX
            config_path = os.path.join(CONFIGS_DIR, config_name + file_type_suffix + CONFIG_EXTENSION)
            if os.path.exists(config_path):
                os.remove(config_path)
                self.update_config_combobox()

    def load_selected_config(self):
        # загружает выбранную конфигурацию (сразу из комбобокса)
        config_name = self.config_combobox.currentText()
        if config_name:
            load_config(config_name)

    def load_last_config(self):
        # загружает последнюю использованную конфигурацию (авто)
        file_type_suffix = SINGLE_FILE_SUFFIX if len(
            extracted_metadata.get('Название трека', [])) == 1 else MULTIPLE_FILES_SUFFIX
        config_files = [f for f in os.listdir(CONFIGS_DIR) if
                        f.endswith(file_type_suffix + CONFIG_EXTENSION)]
        if config_files:
            last_config = sorted(config_files)[-1]
            self.config_combobox.setCurrentText(last_config[:-len(file_type_suffix + CONFIG_EXTENSION)])
            self.load_selected_config()


if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough) #  # #   ###  ### #
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)                                             #### #   #  # # # #
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)                                                #  # #   ###  #   #

    os.makedirs(CONFIGS_DIR, exist_ok=True) # может перенести в функцию создания конфигов?

    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())