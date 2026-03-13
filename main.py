from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QStackedLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PIL import Image
import sys
import os
from PyQt5.QtGui import QImage, QPainter, QMovie
from PIL import Image, ImageFilter
from dotenv import load_dotenv

from modules.gdrive_api import *

load_dotenv()
FOLDER_ID = os.getenv("FOLDER_ID")
LOCAL_PATH = os.getenv("LOCAL_PATH")
USE_EXT_DISPLAY = os.getenv("USE_EXT_DISPLAY")


def perror(str: str):
    print(f"\033[91m{str}\033[0m")


class MediaSequence:
    def __init__(self, dDur: int = 10000):
        self.seq: list[File] = []
        self.defaultDuration = dDur  # default duration of image still in ms
        self._len = len(self.seq)

    def __getitem__(self, item):
        return self.seq[item]

    def update(self):
        self.seq = fetchFiles(LOCAL_PATH, FOLDER_ID, self.seq)
        self._len = len(self.seq)


class ContentViewer(QWidget):
    def __init__(self, screen):
        super().__init__()
        # set screen for the display to show
        self.screen = screen

        self.media_sequence: MediaSequence = MediaSequence()
        self.media_sequence.update()

        self.index = 0

        self.imageLabel = QLabel()
        self.imageLabel.setAlignment(Qt.AlignCenter)  # centers the pixmap
        self.imageLabel.setStyleSheet("background:black;")

        self.videoWidget = QVideoWidget()
        self.videoPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.videoPlayer.setVideoOutput(self.videoWidget)
        self.videoPlayer.mediaStatusChanged.connect(self._on_media_status)

        self.stack = QStackedLayout(self)
        self.stack.addWidget(self.imageLabel)   # index 0
        self.stack.addWidget(self.videoWidget)  # index 1

        # Full screen on selected monitor
        self.setGeometry(self.screen.geometry())

    def start(self):
        if not self.media_sequence:
            return
        self._show_current()

    def _show_current(self):
        item: File = self.media_sequence[self.index]
        fType, subtype = item.mimeType.split("/")
        match fType:
            case "image":
                if subtype == "gif":
                    # funky gif logic -_-
                    self._show_gif(f"{LOCAL_PATH}/{item.name}", self.media_sequence.defaultDuration)
                else:
                    # normal image
                    self._show_image(f"{LOCAL_PATH}/{item.name}", self.media_sequence.defaultDuration)
            case "video":
                self._show_video(f"{LOCAL_PATH}/{item.name}")
            case _:
                print(f"Unrecognized mimeType: {item.mimeType}!")

    def _show_image(self, path, duration):
        if not os.path.exists(path):
            self._next()
            return

        PixelMap = QPixmap(path)  # Holds the image information
        if not PixelMap.isNull():

            screen_size = self.screen.size()
            screen_w, screen_h = screen_size.width(), screen_size.height()

            # If image is smaller than the screen in any dimension, create blurred background
            if PixelMap.width() < screen_w or PixelMap.height() < screen_h:
                try:
                    # Load with PIL for blur background
                    pil_img = Image.open(path).convert("RGB")
                    bg = pil_img.resize((screen_w, screen_h), Image.LANCZOS)
                    bg = bg.filter(ImageFilter.GaussianBlur(radius=60))

                    # Convert blurred background to QPixmap
                    bg_rgba = bg.convert("RGBA")
                    data = bg_rgba.tobytes("raw", "RGBA")
                    qimg = QImage(data, screen_w, screen_h,
                                  screen_w * 4, QImage.Format_RGBA8888)
                    bg_pix = QPixmap.fromImage(qimg.copy())

                    # Scale foreground image up as large as possible while fitting
                    img_w, img_h = PixelMap.width(), PixelMap.height()
                    scale = min(screen_w / img_w, screen_h / img_h)
                    new_w, new_h = int(img_w * scale), int(img_h * scale)
                    scaled_foreground = PixelMap.scaled(
                        new_w, new_h, Qt.KeepAspectRatio, Qt.SmoothTransformation)

                    # Compose final pixmap
                    final_pix = QPixmap(screen_size)
                    final_pix.fill(Qt.black)
                    painter = QPainter(final_pix)
                    painter.drawPixmap(0, 0, bg_pix)
                    x = (screen_w - scaled_foreground.width()) // 2
                    y = (screen_h - scaled_foreground.height()) // 2
                    painter.drawPixmap(x, y, scaled_foreground)
                    painter.end()

                    self.imageLabel.setPixmap(final_pix)
                except Exception:
                    # Fallback to normal scaling if anything fails
                    scaled = PixelMap.scaled(
                        screen_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.imageLabel.setPixmap(scaled)
            else:
                # Normal behavior (scale to fit while keeping aspect ratio)
                scaled = PixelMap.scaled(
                    screen_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.imageLabel.setPixmap(scaled)

        self.stack.setCurrentWidget(self.imageLabel)
        QTimer.singleShot(int(duration), self._next)

    def _show_video(self, path):
        if not os.path.exists(path):
            self._next()
            return
        url = QUrl.fromLocalFile(os.path.abspath(path))
        self.videoPlayer.setMedia(QMediaContent(url))
        self.stack.setCurrentWidget(self.videoWidget)
        self.videoPlayer.play()

    def _show_gif(self, path, duration):
            if not os.path.exists(path):
                self._next()
                return

            # In case a previous image was set
            self.imageLabel.setPixmap(QPixmap())

            movie = QMovie(path)
            if not movie.isValid():
                perror(f"Could not load gif: {path}")
                self._next()
                return

            self.imageLabel.setMovie(movie)

            # Scale the movie to fit the screen while keeping aspect ratio
            screen_size = self.screen.size()
            movie_size = movie.frameRect().size()
            if movie_size.isValid():
                scaled_size = movie_size.scaled(screen_size, Qt.KeepAspectRatio)
                movie.setScaledSize(scaled_size)

            movie.start()
            self.stack.setCurrentWidget(self.imageLabel)
            QTimer.singleShot(int(duration), self._next)


    def _on_media_status(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.videoPlayer.stop()
            self._next()

    def _next(self):
        self.index += 1
        if self.index >= self.media_sequence._len:
            self.index = 0
            self.media_sequence.update()
        self._show_current()

    def resizeEvent(self, event):
        # Rescale current image when window (screen) changes (e.g., resolution)
        if self.stack.currentWidget() is self.imageLabel and not self.imageLabel.pixmap() is None:
            pm = self.imageLabel.pixmap()
            if pm:
                scaled = pm.scaled(
                    self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.imageLabel.setPixmap(scaled)
        super().resizeEvent(event)


def main():
    

    # clear the folder on startup
    files_to_delete = set(os.listdir(LOCAL_PATH))
    if files_to_delete:
        for file_name in files_to_delete:
            if file_name.startswith("_COUNT"):
                continue
            local_file_path = os.path.join(LOCAL_PATH, file_name)
            # Use os.path.isfile to avoid deleting directories/sub-folders
            if os.path.isfile(local_file_path):
                os.remove(local_file_path)

    app = QApplication(sys.argv)
    screen = app.screens()[0 if not int(USE_EXT_DISPLAY) else 1]

    window: ContentViewer = ContentViewer(screen)
    window.showFullScreen()
    window.start()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
