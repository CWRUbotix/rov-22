from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QWidget


class VideoControlsWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.horizontal_layout = QHBoxLayout(self)

        self.play_pause_button = QPushButton(self)
        self.play_pause_button.setText("Play/Pause")
        self.horizontal_layout.addWidget(self.play_pause_button)

        self.restart_button = QPushButton(self)
        self.restart_button.setText("Restart")
        self.horizontal_layout.addWidget(self.restart_button)

        self.toggle_rewind_button = QPushButton(self)
        self.toggle_rewind_button.setText("Toggle Rewind")
        self.horizontal_layout.addWidget(self.toggle_rewind_button)

        self.prev_frame_button = QPushButton(self)
        self.prev_frame_button.setText("<")
        self.horizontal_layout.addWidget(self.prev_frame_button)

        self.next_frame_button = QPushButton(self)
        self.next_frame_button.setText(">")
        self.horizontal_layout.addWidget(self.next_frame_button)

        self.setLayout(self.horizontal_layout)
