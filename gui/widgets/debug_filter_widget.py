from PyQt5.QtWidgets import QComboBox, QHBoxLayout, QWidget
from gui.debug_filter_functions import filter_dropdown
from gui.data_classes import Frame

class DebugFilterWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.horizontal_layout = QHBoxLayout(self)
        self.horizontal_layout.setContentsMargins(0, 0, 0, 0)

        self.current_filter = "None"

        self.combo_box = QComboBox()

        # Adding functions to the combo box
        for func_name in filter_dropdown.func_dictionary.keys():
            self.combo_box.addItem(func_name)

        self.combo_box.currentTextChanged.connect(self.update_current_filter)
        self.update_current_filter(self.combo_box.currentText())

        self.horizontal_layout.addWidget(self.combo_box)

    def update_current_filter(self, text):
        """
        Calls the function selected in the dropdown menu
        :param text: Name of the function to call
        """

        self.current_filter = text

    def apply_filter(self, frame: Frame):
        """
        Applies filter from the dropdown menu to the given frame
        :param frame: frame to apply filter to
        :return: frame with filter applied
        """
        return filter_dropdown.func_dictionary.get(self.current_filter)(frame)