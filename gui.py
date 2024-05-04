import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon #, QColor, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QHBoxLayout, QWidget, QVBoxLayout

from qframelesswindow import AcrylicWindow, StandardTitleBar


class Window(AcrylicWindow):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setTitleBar(StandardTitleBar(self))

        # главная верстка для отступа
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addSpacing(self.titleBar.height()) # отступ заголовка окна

        # главные виджеты
        widget_layout = QHBoxLayout() # вертикальная верстка для виджетов

        preview_main = QWidget(self)
        preview_main.setStyleSheet("background-color:white; border-radius:8px;")
        settings_main = QWidget(self)
        settings_main.setStyleSheet("background-color:white; border-radius:8px;")

        widget_layout.addWidget(preview_main)
        widget_layout.addWidget(settings_main)

        # скейл виджетов
        widget_layout.setStretchFactor(preview_main, 1)
        widget_layout.setStretchFactor(settings_main, 3)

        layout.addLayout(widget_layout)


        self.label = QLabel(self)
        self.label.setScaledContents(True)

        self.setWindowIcon(QIcon("logo.png")) #сделать иконку
        self.setWindowTitle("perper")
        self.setStyleSheet("background:white")

        self.titleBar.raise_()

        # изменение acrylic effect
        #self.windowEffect.setAcrylicEffect(self.winId(), "106EBE99")

        # mica effect on Win11
        #self.windowEffect.setMicaEffect(self.winId(), False) #True для темного режима?/следовать за системной темой (черн/белая) mica эффекта??

    def resizeEvent(self, e):
        # don't forget to call the resizeEvent() of super class
        super().resizeEvent(e)
        length = min(self.width(), self.height())
        self.label.resize(length, length)
        self.label.move(
            self.width() // 2 - length // 2,
            self.height() // 2 - length // 2
        )


if __name__ == '__main__':
    # enable dpi scale
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    demo = Window()
    demo.show()
    sys.exit(app.exec())
