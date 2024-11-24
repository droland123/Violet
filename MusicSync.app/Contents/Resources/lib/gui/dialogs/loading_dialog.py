# gui/dialogs/loading_dialog.py
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QProgressBar, QLabel
from PyQt6.QtCore import Qt

class LoadingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Loading Library")
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Status label
        self.status_label = QLabel("Initializing...")
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)
        
        self.setFixedSize(300, 100)
        self.setStyleSheet("""
            QDialog {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
            }
            QLabel {
                color: #ffffff;
                font-size: 12px;
                margin-bottom: 5px;
            }
            QProgressBar {
                border: 1px solid #3d3d3d;
                border-radius: 3px;
                text-align: center;
                color: #ffffff;
                background-color: #1d1d1d;
            }
            QProgressBar::chunk {
                background-color: #0a84ff;
                border-radius: 2px;
            }
        """)

    def update_progress(self, value, status):
        """Update progress bar and status text"""
        self.progress_bar.setValue(value)
        self.status_label.setText(status)