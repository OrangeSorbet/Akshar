import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QPushButton
from ui import StartMenu, HomeScreen, FontEditor, GlyphEditor
from PyQt6.QtCore import pyqtSignal

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Akshar")
        self.resize(1000, 700)
        
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        # 1. Initialize Screens
        self.start_menu = StartMenu()
        self.home_screen = HomeScreen()
        self.font_editor = FontEditor()
        self.glyph_editor = GlyphEditor()
        
        # 2. Add to Stack
        self.stack.addWidget(self.start_menu)   # 0
        self.stack.addWidget(self.home_screen)  # 1
        self.stack.addWidget(self.font_editor)  # 2
        self.stack.addWidget(self.glyph_editor) # 3
        
        # --- SYNCHRONIZATION LOGIC ---
        
        # Connect Home signal to Sync
        self.home_screen.pin_toggled.connect(self.sync_pin_state)
        
        # Connect Font Editor signal to Sync
        self.font_editor.pin_toggled.connect(self.sync_pin_state)
        
        # --- NAVIGATION LOGIC ---
        
        self.start_menu.btn_start.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.home_screen.btn_new.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        
        # Back Button Logic
        self.font_editor.font_menu.back_callback = lambda: self.stack.setCurrentIndex(1)

    def sync_pin_state(self, is_pinned: bool):
        """
        Received a signal from one screen, force the state onto ALL screens.
        """
        # Update Home
        self.home_screen.set_pinned_state(is_pinned)
        
        # Update Font Editor
        self.font_editor.set_pinned_state(is_pinned)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())