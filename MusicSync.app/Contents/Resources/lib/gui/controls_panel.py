# gui/controls_panel.py
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QPushButton, QSlider, 
                            QLabel, QFrame)
from PyQt6.QtCore import Qt, QTimer

class ControlsPanel(QWidget):
    def __init__(self, player):
        super().__init__()
        self.player = player
        self.setup_ui()
    
    def setup_ui(self):
        self.setFixedHeight(80)  # Fixed height for controls
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Add playback controls
        self.prev_button = QPushButton("⏮")
        self.play_button = QPushButton("⏵")
        self.next_button = QPushButton("⏭")
        
        # Set fixed size for buttons
        for button in [self.prev_button, self.play_button, self.next_button]:
            button.setFixedSize(40, 40)
        
        # Add time labels
        self.time_current = QLabel("0:00")
        self.time_total = QLabel("0:00")
        
        # Add progress slider
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setMinimum(0)
        self.progress_slider.setMaximum(1000)
        
        # Add all widgets to layout
        layout.addWidget(self.prev_button)
        layout.addWidget(self.play_button)
        layout.addWidget(self.next_button)
        layout.addSpacing(20)
        layout.addWidget(self.time_current)
        layout.addWidget(self.progress_slider)
        layout.addWidget(self.time_total)
        
        # Connect signals
        self.play_button.clicked.connect(self.toggle_playback)
        self.progress_slider.sliderPressed.connect(self.on_slider_pressed)
        self.progress_slider.sliderReleased.connect(self.on_slider_released)
        
        # Setup update timer
        self.update_timer = QTimer()
        self.update_timer.setInterval(1000)
        self.update_timer.timeout.connect(self.update_ui)
        self.update_timer.start()
        
        # Slider dragging state
        self.is_slider_dragging = False
    
    def toggle_playback(self):
        if self.player.is_playing():
            self.player.pause()
            self.play_button.setText("⏵")
        else:
            self.player.play()
            self.play_button.setText("⏸")
    
    def format_time(self, ms):
        """Convert milliseconds to MM:SS format"""
        if ms <= 0:
            return "0:00"
        seconds = int(ms / 1000)
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02d}"
    
    def on_slider_pressed(self):
        self.is_slider_dragging = True
    
    def on_slider_released(self):
        self.is_slider_dragging = False
        position = self.progress_slider.value() / 1000.0
        self.player.set_position(position)
    
    def update_ui(self):
        try:
            if not self.is_slider_dragging:
                position = self.player.get_position()
                self.progress_slider.setValue(int(position * 1000))
            
            # Update time labels
            current_time = self.player.get_time()
            total_time = self.player.get_length()
            
            self.time_current.setText(self.format_time(current_time))
            self.time_total.setText(self.format_time(total_time))
            
            # Update play/pause button text
            self.play_button.setText("⏸" if self.player.is_playing() else "⏵")
            
        except Exception as e:
            print(f"Error updating UI: {str(e)}")