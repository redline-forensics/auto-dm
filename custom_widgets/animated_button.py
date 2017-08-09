from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QPushButton


class AnimatedButton(QPushButton):
    def __init__(self, *args):
        self.movie = None
        super(AnimatedButton, self).__init__(*args)

    def set_movie(self, movie):
        self.movie = movie
        if self.movie is None:
            self.setIcon(QIcon())
            return

        self.movie.frameChanged.connect(self.set_button_icon)
        if self.movie.loopCount() != -1:
            self.movie.finished.connect(self.movie.start())

        self.movie.start()

    def set_button_icon(self, frame):
        self.setIcon(QIcon(self.movie.currentPixmap()))
