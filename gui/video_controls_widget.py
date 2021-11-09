from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QWidget

class VideoControlsWidget(QWidget):
    def __init__(self, thread):
        super().__init__()

        self.thread = thread

        self.horizontal_layout = QHBoxLayout(self)

        self.play_pause_button = QPushButton(self)
        self.play_pause_button.setText("Play/Pause")
        self.play_pause_button.clicked.connect(self.thread.toggle_play_pause)
        self.horizontal_layout.addWidget(self.play_pause_button)

        self.toggle_rewind_button = QPushButton(self)
        self.toggle_rewind_button.setText("Toggle Rewind")
        self.toggle_rewind_button.clicked.connect(self.thread.toggle_rewind)
        self.horizontal_layout.addWidget(self.toggle_rewind_button)

        self.prev_frame_button = QPushButton(self)
        self.prev_frame_button.setText("<")
        self.prev_frame_button.clicked.connect(self.thread.prev_frame)
        self.horizontal_layout.addWidget(self.prev_frame_button)

        self.next_frame_button = QPushButton(self)
        self.next_frame_button.setText(">")
        self.next_frame_button.clicked.connect(self.thread.next_frame)
        self.horizontal_layout.addWidget(self.next_frame_button)

        self.setLayout(self.horizontal_layout)