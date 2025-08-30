from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QStackedLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PIL import Image
import sys
import os
from PyQt5.QtGui import QImage, QPainter
from PIL import Image, ImageFilter


def perror(str: str):
    print(f"\033[91m{str}\033[0m")


# program constants
USE_EXT_DISPLAY: bool = False
PATH_TO_MEDIA: str = os.path.expanduser("~") + "/bilboard"
try:
    if not os.path.exists(PATH_TO_MEDIA):
        raise Exception()
except:
    os.mkdir(os.path.expanduser("~") + "/bilboard")
    perror("Directory did not exist. created")


class MediaItem():
    def __init__(self, name: str, isImage: bool, dur: int = 0):
        self.name: str = name
        self.isImage: bool = isImage  # true if image. False if video
        self.duration: int = dur  # Duration in ms


class MediaSequence:
    def __init__(self, dDur: int = 3000):
        self.seq: list[MediaItem] = []
        self.defaultDuration = dDur  # default duration of image still in ms
        self._len = len(self.seq)

    def __getitem__(self, item):
        return self.seq[item]

    def update(self):
        self.seq = []
        for file in os.listdir(PATH_TO_MEDIA):

            name = file
            extention = name.split(".")[-1]
            match extention:
                case "png":
                    self.seq.append(
                        MediaItem(name, True, self.defaultDuration))
                case "jpg":
                    self.seq.append(
                        MediaItem(name, True, self.defaultDuration))
                case "mp4":
                    self.seq.append(MediaItem(name, False))
                case _:
                    perror(
                        f"Unrecognized file name extention: {extention}. Skipping!")
        self._len = len(self.seq)


class ContentViewer(QWidget):
    def __init__(self, screen):
        super().__init__()
        # set screen for the display to show
        self.screen = screen
        # TODO temporarry
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
        item: MediaItem = self.media_sequence[self.index]
        if item.isImage:
            self._show_image(f"{PATH_TO_MEDIA}/{item.name}", item.duration)
        else:
            self._show_video(f"{PATH_TO_MEDIA}/{item.name}")

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

    app = QApplication(sys.argv)
    screen = app.screens()[0 if not USE_EXT_DISPLAY else 1]

    window: ContentViewer = ContentViewer(screen)
    window.showFullScreen()
    window.start()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
