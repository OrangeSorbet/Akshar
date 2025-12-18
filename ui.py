import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QSpacerItem, QSizePolicy, QFrame, QScrollArea, 
    QGridLayout, QGraphicsOpacityEffect
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, QSize, QTimer, QParallelAnimationGroup, pyqtSignal
from PyQt6.QtGui import QFont

# --- 1. UTILS & OVERLAYS ---

class DimOverlay(QWidget):
    def __init__(self, parent=None, close_callback=None):
        super().__init__(parent)
        self.close_callback = close_callback
        self.setStyleSheet("background-color: rgba(0, 0, 0, 150);")
        self.hide()

    def mousePressEvent(self, event):
        if self.close_callback:
            self.close_callback()

# --- 2. THE DRAWER MENU ---

class HomeHamburgerMenu(QFrame):
    def __init__(self, parent=None, close_callback=None, pin_callback=None):
        super().__init__(parent)
        self.close_callback = close_callback
        self.pin_callback = pin_callback
        self.setFixedWidth(280)
        self.setStyleSheet("""
            QFrame { background-color: #252525; border-right: 1px solid #333333; }
            QLabel { color: #888888; font-weight: bold; font-size: 12px; margin-top: 10px; margin-bottom: 5px; }
            QPushButton {
                background-color: transparent;
                color: #dddddd;
                text-align: left;
                padding: 10px 15px;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #333333; color: #ffffff; }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(5)

        # -- Header (X and Pin) --
        header = QHBoxLayout()
        header.setContentsMargins(5, 0, 5, 10)
        icon_btn_style = """
            QPushButton { 
                background-color: transparent; 
                border: none; 
                color: #666666; 
                padding: 0px;
                margin: 0px;
                text-align: center;
            }
            QPushButton:hover { color: #ffffff; background-color: #333333; border-radius: 4px; }
        """

        # Close button (Left)
        btn_close = QPushButton("✕")
        btn_close.setFixedSize(45, 45)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setFont(QFont("Segoe UI Symbol", 18))
        btn_close.setStyleSheet(icon_btn_style)
        btn_close.clicked.connect(self.close_callback)

        # Pin button (Right)
        self.btn_pin = QPushButton("📌")
        self.btn_pin.setFixedSize(45, 45)
        self.btn_pin.setCheckable(True)
        self.btn_pin.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pin.setFont(QFont("Segoe UI Emoji", 18))
        self.btn_pin.setStyleSheet("""
            QPushButton { color: #666666; border: none; padding: 0px; border-radius: 4px; margin: 0px; text-align: center; }
            QPushButton:checked { color: #dddddd; background-color: #444444; }
            QPushButton:hover { background-color: #333333; }
        """)
        self.btn_pin.clicked.connect(self.pin_callback)

        # Header layout
        header = QHBoxLayout()
        header.setContentsMargins(5, 0, 5, 10)
        header.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignLeft)
        header.addStretch()
        header.addWidget(self.btn_pin, alignment=Qt.AlignmentFlag.AlignRight)

        layout.addLayout(header)

        # -- Menu Helper --
        def add_btn(text, icon=""):
            # Truncate logic handled naturally by Qt layout, usually ok.
            btn = QPushButton(f"{icon}  {text}" if icon else text)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            layout.addWidget(btn)
            return btn

        def add_sep():
            line = QFrame()
            line.setFrameShape(QFrame.Shape.HLine)
            line.setFrameShadow(QFrame.Shadow.Sunken)
            line.setStyleSheet("background-color: #333333; max-height: 1px; margin: 5px 0;")
            layout.addWidget(line)

        # -- Menu Items --
        add_btn("New Font", "+")
        add_btn("Open Font (.varn)", "📂")
        add_btn("Recent Fonts ▶", "🕒")
        add_sep()
        
        add_btn("Open Projects Folder", "📁")
        add_btn("Refresh Font List", "🔄")
        add_sep()
        
        add_btn("Settings", "⚙")
        add_sep()
        
        add_btn("How to Use", "📘")
        add_btn("Keyboard Shortcuts", "⌨")
        add_btn("About Akshar", "ℹ")
        
        layout.addStretch()
        
        add_sep()
        btn_exit = add_btn("Exit", "🚪")
        btn_exit.setStyleSheet("color: #ff6666; text-align: left; padding: 10px 15px;")

        self.setLayout(layout)

# --- 3. HOME SCREEN (FIXED) ---

class HomeScreen(QWidget):
    pin_toggled = pyqtSignal(bool)
    def __init__(self):
        super().__init__()
        self.data = []
        self.is_menu_pinned = False
        self.is_menu_open = False
        
        self.init_ui()
        self.load_dummy_data()

    def init_ui(self):
        self.setStyleSheet("background-color: #1e1e1e; font-family: Segoe UI, sans-serif;")
        
        self.resize_timer = QTimer(self)
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self.animate_cards)

        # Root Layout (Horizontal) handles Pinned State logic
        self.root_layout = QHBoxLayout(self)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)

        # --- Main Content Area ---
        self.content_widget = QWidget()
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Top Bar
        top_bar = QFrame()
        top_bar.setFixedHeight(60)
        top_bar.setStyleSheet("background-color: #252525; border-bottom: 1px solid #333333;")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(20, 0, 20, 0)

        # Hamburger Button
        self.btn_menu = QPushButton("☰")
        self.btn_menu.setFixedSize(40, 36)
        self.btn_menu.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_menu.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #dddddd;
                font-size: 18px;
                border: 1px solid #444444;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #333333; }
        """)
        self.btn_menu.clicked.connect(self.open_menu)
        top_layout.addWidget(self.btn_menu)

        top_layout.addSpacing(15)
        logo = QLabel("Akshar")
        logo.setStyleSheet("color: #888888; font-weight: bold; font-size: 16px;")
        top_layout.addWidget(logo)
        top_layout.addStretch()

        self.btn_new = QPushButton("+ New Font")
        self.btn_new.setFixedSize(120, 36)
        self.btn_new.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_new.setStyleSheet("""
            QPushButton {
                background-color: #dddddd;
                color: #1e1e1e;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #ffffff; }
        """)
        top_layout.addWidget(self.btn_new)

        content_layout.addWidget(top_bar)

        # Grid Scroll Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background-color: #1e1e1e; }")
        
        self.container = QWidget()
        self.container.setStyleSheet("background-color: #1e1e1e;")
        self.grid_layout = QGridLayout(self.container)
        self.grid_layout.setContentsMargins(40, 40, 40, 40)
        self.grid_layout.setSpacing(25)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        self.scroll.setWidget(self.container)
        content_layout.addWidget(self.scroll)

        # Add content to root
        self.root_layout.addWidget(self.content_widget)

        # --- Menu System Components ---
        self.overlay = DimOverlay(self, close_callback=self.close_menu)
        
        self.side_menu = HomeHamburgerMenu(
            parent=self, 
            close_callback=self.close_menu, 
            pin_callback=self.toggle_pin
        )
        self.side_menu.hide()

        # Animation Setup
        self.anim = QPropertyAnimation(self.side_menu, b"pos")
        self.anim.setDuration(250)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def showEvent(self, event):
        self.repopulate_grid()
        super().showEvent(event)

    def resizeEvent(self, event):
        if self.overlay.isVisible():
            self.overlay.resize(self.size())

        if not self.is_menu_pinned and self.is_menu_open:
            self.side_menu.resize(self.side_menu.width(), self.height())

        self.repopulate_grid()
        self.resize_timer.start(150)
        super().resizeEvent(event)

    # --- Menu Logic (Fixed) ---

    def open_menu(self):
        if self.is_menu_open: return
        self.is_menu_open = True
        
        try:
            self.anim.finished.disconnect()
        except TypeError:
            pass # No signal connected, which is fine

        if self.is_menu_pinned:
            pass 
        else:
            self.overlay.resize(self.size())
            self.overlay.show()
            self.overlay.raise_()
            
            self.side_menu.setParent(self)
            self.side_menu.resize(self.side_menu.width(), self.height())
            self.side_menu.show()
            self.side_menu.raise_()
            
            start_pos = QPoint(-self.side_menu.width(), 0)
            end_pos = QPoint(0, 0)
            self.side_menu.move(start_pos)
            
            self.anim.setStartValue(start_pos)
            self.anim.setEndValue(end_pos)
            self.anim.start()
        self.repopulate_grid()

    def close_menu(self):
        if not self.is_menu_open: return
        
        # If closing while pinned, we unpin first
        if self.is_menu_pinned:
            self.toggle_pin()
        
        self.is_menu_open = False
        self.overlay.hide()
        
        # Disconnect old signals just in case
        try:
            self.anim.finished.disconnect()
        except TypeError:
            pass

        start_pos = self.side_menu.pos()
        end_pos = QPoint(-self.side_menu.width(), 0)
        
        self.anim.setStartValue(start_pos)
        self.anim.setEndValue(end_pos)
        
        self.anim.finished.connect(self.side_menu.hide) 
        self.anim.start()
        self.repopulate_grid()

    def toggle_pin(self):
        new_state = not self.is_menu_pinned
        self.set_pinned_state(new_state)
        self.pin_toggled.emit(new_state)

    def set_pinned_state(self, pinned: bool):
        if self.is_menu_pinned == pinned:
            return
            
        self.is_menu_pinned = pinned
        self.side_menu.btn_pin.setChecked(pinned)
        
        if self.is_menu_pinned:
            # Pinned Logic
            self.overlay.hide()
            self.side_menu.setParent(None) 
            self.root_layout.insertWidget(0, self.side_menu) 
            self.side_menu.show()
            self.side_menu.setFixedHeight(self.height())
            
            if hasattr(self.side_menu, 'btn_close'):
                 self.side_menu.btn_close.hide()
        else:
            if hasattr(self.side_menu, 'btn_close'):
                 self.side_menu.btn_close.show()

            self.root_layout.removeWidget(self.side_menu)
            self.side_menu.setParent(self)
            self.side_menu.resize(self.side_menu.width(), self.height())
            self.side_menu.move(0, 0)
            self.side_menu.show()
            
            if self.is_menu_open:
                self.overlay.show()
                self.overlay.raise_()
                self.side_menu.raise_()
            else:
                self.side_menu.hide()

        self.repopulate_grid()

    def animate_cards(self):
            for i in range(self.grid_layout.count()):
                widget = self.grid_layout.itemAt(i).widget()
                if not widget: continue

                # 1. Setup Opacity Effect
                effect = QGraphicsOpacityEffect(widget)
                widget.setGraphicsEffect(effect)
                
                # 2. Define Animations
                # Opacity: 0 -> 1
                anim_op = QPropertyAnimation(effect, b"opacity")
                anim_op.setStartValue(0)
                anim_op.setEndValue(1)
                anim_op.setDuration(400)
                
                # Position: Slide Up (Fly)
                # We use the widget's current layout position as the END point
                end_pos = widget.pos()
                start_pos = end_pos + QPoint(0, 50) # Start 50px lower
                
                anim_pos = QPropertyAnimation(widget, b"pos")
                anim_pos.setStartValue(start_pos)
                anim_pos.setEndValue(end_pos)
                anim_pos.setDuration(400)
                anim_pos.setEasingCurve(QEasingCurve.Type.OutBack) # "Fly" bounce effect

                # 3. Group and Stagger
                group = QParallelAnimationGroup(self)
                group.addAnimation(anim_op)
                group.addAnimation(anim_pos)
                
                # Delay based on index (50ms stagger)
                QTimer.singleShot(i * 50, group.start)
                
    # --- Grid Logic (Unchanged) ---
    def load_dummy_data(self):
        self.data = [
            ("MyFirstFont", "Latin", "2m ago"),
            ("Devanagari Test", "Devanagari", "1h ago"),
            ("Pixel Art", "Symbols", "Yesterday"),
            ("Logos", "Symbols", "2 days ago"),
            ("Handwritten", "Latin", "Last week"),
            ("Tech Mono", "Latin", "2 weeks ago"),
            ("Ancient", "Runes", "1 month ago"),
        ]
        self.repopulate_grid()

    def repopulate_grid(self):
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        available_width = self.scroll.viewport().width() - 100 
        if available_width < 100: available_width = 100

        min_card_width = 220
        spacing = self.grid_layout.spacing()
        max_cols = max(1, available_width // min_card_width)
        card_width = (available_width - ((max_cols - 1) * spacing)) // max_cols

        card_height = int(card_width * 1.414)

        row, col = 0, 0
        for title, script, date in self.data:
            card = FontCard(title, script, date)
            
            card.setFixedSize(card_width, card_height)
            
            self.grid_layout.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        self.container.layout().update() 

# --- 4. START MENU (Unchanged) ---
class StartMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Akshar")
        self.resize(800, 600)
        self.setStyleSheet("background-color: #1e1e1e; font-family: Segoe UI, sans-serif;")
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(50, 50, 50, 30)
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        title = QLabel("AKSHAR")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 72px; font-weight: bold; letter-spacing: 5px; color: #f0f0f0;")
        layout.addWidget(title)
        subtitle = QLabel("Font Creator")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("font-size: 22px; color: #888888; margin-top: -10px;")
        layout.addWidget(subtitle)
        layout.addSpacerItem(QSpacerItem(20, 60, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        btn_style = "QPushButton { background-color: transparent; border: 2px solid #444444; border-radius: 10px; color: #dddddd; font-size: 16px; padding: 12px; } QPushButton:hover { border-color: #666666; background-color: #2d2d2d; }"
        start_btn_style = "QPushButton { background-color: #dddddd; border: none; border-radius: 10px; color: #1e1e1e; font-size: 18px; font-weight: bold; padding: 14px; } QPushButton:hover { background-color: #ffffff; }"
        
        self.btn_start = QPushButton("Start")
        self.btn_start.setFixedSize(260, 55)
        self.btn_start.setStyleSheet(start_btn_style)
        self.btn_start.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.btn_start, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(20)
        self.btn_how_to = QPushButton("How to Use")
        self.btn_how_to.setFixedSize(260, 50)
        self.btn_how_to.setStyleSheet(btn_style)
        self.btn_how_to.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.btn_how_to, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(15)
        self.btn_settings = QPushButton("Settings")
        self.btn_settings.setFixedSize(260, 50)
        self.btn_settings.setStyleSheet(btn_style)
        self.btn_settings.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.btn_settings, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        version = QLabel("v0.1")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version.setStyleSheet("color: #444444; font-size: 12px;")
        layout.addWidget(version)
        self.setLayout(layout)

# --- 5. COMPONENT HELPERS (FontCard, GlyphCell, Editors) ---

class FontCard(QFrame):
    def __init__(self, title, script, date):
        super().__init__()
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(280)
        self.setMinimumWidth(200)
        self.setStyleSheet("""QFrame { background-color: #252525; border-radius: 12px; border: 1px solid #333333; } QFrame:hover { background-color: #2d2d2d; border-color: #555555; }""")
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 15)
        layout.setSpacing(5)
        self.preview = QLabel()
        self.preview.setStyleSheet("background-color: #1a1a1a; border-radius: 8px; border: none;")
        self.preview.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.preview)
        self.lbl_title = QLabel(title)
        self.lbl_title.setStyleSheet("color: #f0f0f0; font-weight: bold; font-size: 14px; border: none; background: transparent;")
        layout.addWidget(self.lbl_title)
        self.lbl_script = QLabel(script)
        self.lbl_script.setStyleSheet("color: #888888; font-size: 12px; border: none; background: transparent;")
        layout.addWidget(self.lbl_script)
        self.lbl_date = QLabel(f"Edited: {date}")
        self.lbl_date.setStyleSheet("color: #555555; font-size: 11px; border: none; background: transparent;")
        layout.addWidget(self.lbl_date)
        self.setLayout(layout)

class GlyphCell(QFrame):
    def __init__(self, char, unicode_text, status="empty"):
        super().__init__()
        self.setFixedSize(100, 120)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        bg = "#252525" if status == "empty" else "#2d2d2d"
        border = "#333333" if status == "empty" else "#555555"
        text = "#666666" if status == "empty" else "#f0f0f0"
        self.setStyleSheet(f"QFrame {{ background-color: {bg}; border: 1px solid {border}; border-radius: 8px; }} QFrame:hover {{ border-color: #888888; background-color: #333333; }}")
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(5)
        self.lbl_char = QLabel(char)
        self.lbl_char.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_char.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {text}; border: none; background: transparent;")
        layout.addWidget(self.lbl_char)
        self.lbl_code = QLabel(unicode_text)
        self.lbl_code.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_code.setStyleSheet("font-size: 10px; color: #666666; border: none; background: transparent;")
        layout.addWidget(self.lbl_code)
        self.setLayout(layout)

class FontHamburgerMenu(QFrame):
    def __init__(self, parent=None, close_callback=None, pin_callback=None, back_callback=None):
        super().__init__(parent)
        self.close_callback = close_callback
        self.pin_callback = pin_callback
        self.back_callback = back_callback 
        
        self.setFixedWidth(280)
        self.setStyleSheet("""
            QFrame { background-color: #252525; border-right: 1px solid #333333; }
            QPushButton {
                background-color: transparent; color: #dddddd; text-align: left;
                padding: 10px 15px; border: none; border-radius: 4px; font-size: 14px;
            }
            QPushButton:hover { background-color: #333333; color: #ffffff; }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(5)

        # -- Header (X and Pin) --
        header = QHBoxLayout()
        header.setContentsMargins(5, 0, 5, 10)
        
        icon_btn_style = """
            QPushButton { 
                background-color: transparent; border: none; color: #666666; 
                padding: 0px; margin: 0px; text-align: center;
            }
            QPushButton:hover { color: #ffffff; background-color: #333333; border-radius: 4px; }
        """

        # EXPOSED AS SELF.BTN_CLOSE
        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(45, 45)
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setFont(QFont("Segoe UI Symbol", 18))
        self.btn_close.setStyleSheet(icon_btn_style)
        self.btn_close.clicked.connect(self.close_callback)

        self.btn_pin = QPushButton("📌")
        self.btn_pin.setFixedSize(45, 45)
        self.btn_pin.setCheckable(True)
        self.btn_pin.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pin.setFont(QFont("Segoe UI Emoji", 18))
        self.btn_pin.setStyleSheet("""
            QPushButton { color: #666666; border: none; padding: 0px; border-radius: 4px; margin: 0px; text-align: center; }
            QPushButton:checked { color: #dddddd; background-color: #444444; }
            QPushButton:hover { background-color: #333333; }
        """)
        self.btn_pin.clicked.connect(self.pin_callback)

        header.addWidget(self.btn_close, alignment=Qt.AlignmentFlag.AlignLeft)
        header.addStretch()
        header.addWidget(self.btn_pin, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addLayout(header)

        # -- Helpers --
        def add_btn(text, icon=""):
            btn = QPushButton(f"{icon}  {text}" if icon else text)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            layout.addWidget(btn)
            return btn

        def add_sep():
            line = QFrame()
            line.setFrameShape(QFrame.Shape.HLine)
            line.setStyleSheet("background-color: #333333; max-height: 1px; margin: 5px 0;")
            layout.addWidget(line)

        # -- Content --
        btn_back = add_btn("Back", "⬅")
        if self.back_callback: btn_back.clicked.connect(self.back_callback)
        add_sep()

        add_btn("Save Progress", "💾")
        add_btn("Save As…", "📝")
        add_sep()
        
        add_btn("Export Font (.ttf)", "T")
        add_btn("Export Font (.otf)", "O")
        add_sep()

        add_btn("Font Information", "ℹ️")
        add_btn("Script & Unicode Range", "🌐")
        add_sep()

        add_btn("Validate Font", "✅")
        add_btn("Generate Preview", "🖼️")
        
        layout.addStretch()
        add_sep()
        
        btn_close_font = add_btn("Close Font", "🚪")
        btn_close_font.setStyleSheet("color: #ff6666; text-align: left; padding: 10px 15px;")
        if self.back_callback: btn_close_font.clicked.connect(self.back_callback)

        self.setLayout(layout)

class FontEditor(QWidget):
    pin_toggled = pyqtSignal(bool)
    def __init__(self):
        super().__init__()
        self.is_menu_pinned = False
        self.is_menu_open = False
        self.init_ui()
        self.load_dummy_glyphs()

    def init_ui(self):
        self.setStyleSheet("background-color: #1e1e1e; font-family: Segoe UI, sans-serif;")
        
        # 1. ROOT LAYOUT (Horizontal - Matches Home Screen)
        self.root_layout = QHBoxLayout(self)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)

        # 2. CONTENT CONTAINER (Holds TopBar, Body, Footer)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)

        # --- TOP BAR ---
        top_bar = QFrame()
        top_bar.setFixedHeight(60)
        top_bar.setStyleSheet("background-color: #252525; border-bottom: 1px solid #333333;")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(20, 0, 20, 0)

        self.btn_menu = QPushButton("☰")
        self.btn_menu.setFixedSize(40, 36)
        self.btn_menu.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_menu.setStyleSheet("""
            QPushButton { 
                background-color: transparent; color: #dddddd; font-size: 18px; 
                border: 1px solid #444444; border-radius: 6px; 
            }
            QPushButton:hover { background-color: #333333; }
        """)
        self.btn_menu.clicked.connect(self.open_menu)
        top_layout.addWidget(self.btn_menu)
        top_layout.addSpacing(15)

        self.lbl_title = QLabel("MyFont (Latin)")
        self.lbl_title.setStyleSheet("color: #f0f0f0; font-weight: bold; font-size: 16px;")
        top_layout.addWidget(self.lbl_title)
        top_layout.addStretch()

        self.content_layout.addWidget(top_bar)

        # --- BODY (Sidebar + Grid) ---
        body_layout = QHBoxLayout()
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(80)
        self.sidebar.setStyleSheet("background-color: #222222; border-right: 1px solid #333333;")
        side_layout = QVBoxLayout(self.sidebar)
        side_layout.setContentsMargins(10, 20, 10, 20)
        side_layout.setSpacing(15)
        actions = ["Undo", "Redo", "Save", "Export"]
        for action in actions:
            btn = QPushButton(action)
            btn.setFixedHeight(40)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("QPushButton { color: #aaaaaa; border: 1px solid #333333; border-radius: 5px; font-size: 12px; } QPushButton:hover { background-color: #333333; color: #ffffff; }")
            side_layout.addWidget(btn)
        side_layout.addStretch()
        body_layout.addWidget(self.sidebar)

        # Grid
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background-color: #1e1e1e; }")
        self.container = QWidget()
        self.container.setStyleSheet("background-color: #1e1e1e;")
        self.grid_layout = QGridLayout(self.container)
        self.grid_layout.setContentsMargins(40, 40, 40, 40)
        self.grid_layout.setSpacing(15)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.scroll.setWidget(self.container)
        body_layout.addWidget(self.scroll)

        self.content_layout.addLayout(body_layout)

        # --- ADD CONTENT TO ROOT ---
        self.root_layout.addWidget(self.content_widget)

        # 3. MENU SYSTEM
        self.overlay = DimOverlay(self, close_callback=self.close_menu)
        
        self.font_menu = FontHamburgerMenu(
            parent=self,
            close_callback=self.close_menu,
            pin_callback=self.toggle_pin,
            back_callback=self.go_back_home
        )
        self.font_menu.hide()

        self.anim = QPropertyAnimation(self.font_menu, b"pos")
        self.anim.setDuration(250)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def go_back_home(self):
        print("Back/Close clicked")

    def showEvent(self, event):
        self.repopulate_grid()
        super().showEvent(event)

    def resizeEvent(self, event):
        if self.overlay.isVisible():
            self.overlay.resize(self.size())
        
        if not self.is_menu_pinned and self.is_menu_open:
            self.font_menu.resize(self.font_menu.width(), self.height())
            
        self.repopulate_grid()
        super().resizeEvent(event)

    def open_menu(self):
        if self.is_menu_open: return
        self.is_menu_open = True
        
        try: self.anim.finished.disconnect()
        except: pass

        if not self.is_menu_pinned:
            self.overlay.resize(self.size())
            self.overlay.show()
            self.overlay.raise_()
            
            self.font_menu.setParent(self)
            self.font_menu.resize(self.font_menu.width(), self.height())
            self.font_menu.show()
            self.font_menu.raise_()
            
            start_pos = QPoint(-self.font_menu.width(), 0)
            end_pos = QPoint(0, 0)
            self.font_menu.move(start_pos)
            
            self.anim.setStartValue(start_pos)
            self.anim.setEndValue(end_pos)
            self.anim.start()

    def close_menu(self):
        if not self.is_menu_open: return
        
        # KEY CHANGE: If pinned, we do NOTHING. Pin = Forever.
        if self.is_menu_pinned:
            return 
        
        self.is_menu_open = False
        self.overlay.hide()
        
        try: self.anim.finished.disconnect()
        except: pass

        start_pos = self.font_menu.pos()
        end_pos = QPoint(-self.font_menu.width(), 0)
        
        self.anim.setStartValue(start_pos)
        self.anim.setEndValue(end_pos)
        self.anim.finished.connect(self.font_menu.hide)
        self.anim.start()

    def toggle_pin(self):
        new_state = not self.is_menu_pinned
        self.set_pinned_state(new_state)
        self.pin_toggled.emit(new_state)

    def set_pinned_state(self, pinned: bool):
        if self.is_menu_pinned == pinned:
            return

        self.is_menu_pinned = pinned
        self.font_menu.btn_pin.setChecked(pinned)

        if self.is_menu_pinned:
            self.overlay.hide()
            self.font_menu.setParent(None)
            self.root_layout.insertWidget(0, self.font_menu)
            self.font_menu.show()
            self.font_menu.setFixedHeight(self.height())
            self.font_menu.btn_close.hide()
        else:
            self.font_menu.btn_close.show()

            self.root_layout.removeWidget(self.font_menu)
            self.font_menu.setParent(self)
            self.font_menu.resize(self.font_menu.width(), self.height())
            self.font_menu.move(0, 0)
            self.font_menu.show()

            if self.is_menu_open:
                self.overlay.show()
                self.overlay.raise_()
                self.font_menu.raise_()
            else:
                self.font_menu.hide()

        self.repopulate_grid()

    def load_dummy_glyphs(self):
        self.data = []
        for i in range(65, 91):
            char = chr(i)
            code = f"U+{i:04X}"
            status = "filled" if i % 3 == 0 else "empty"
            self.data.append((char, code, status))
        self.repopulate_grid()

    def repopulate_grid(self):
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget: widget.setParent(None)
        
        avail = self.scroll.viewport().width() - 40
        if avail < 100: avail = 100
        
        max_cols = max(1, avail // 115)
        row, col = 0, 0
        for char, code, status in self.data:
            cell = GlyphCell(char, code, status)
            self.grid_layout.addWidget(cell, row, col)
            col += 1
            if col >= max_cols: col, row = 0, row + 1

class GlyphEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    def init_ui(self):
        self.setStyleSheet("background-color: #1e1e1e; font-family: Segoe UI, sans-serif;")
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        top_bar = QFrame()
        top_bar.setFixedHeight(50)
        top_bar.setStyleSheet("background-color: #252525; border-bottom: 1px solid #333333;")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(15, 0, 15, 0)
        self.btn_back = QPushButton("← Back")
        self.btn_back.setFixedSize(70, 28)
        self.btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_back.setStyleSheet("color: #dddddd; border: 1px solid #444444; border-radius: 4px; background: transparent;")
        top_layout.addWidget(self.btn_back)
        top_layout.addStretch()
        self.lbl_info = QLabel("Glyph: अ (U+0905)")
        self.lbl_info.setStyleSheet("color: #f0f0f0; font-weight: bold; font-size: 14px;")
        top_layout.addWidget(self.lbl_info)
        top_layout.addStretch()
        self.btn_menu = QPushButton("☰")
        self.btn_menu.setFixedSize(40, 30)
        self.btn_menu.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_menu.setStyleSheet("color: #dddddd; font-size: 16px; border: none; background: transparent;")
        top_layout.addWidget(self.btn_menu)
        main_layout.addWidget(top_bar)
        workspace = QHBoxLayout()
        workspace.setContentsMargins(0, 0, 0, 0)
        workspace.setSpacing(0)
        toolbar = QFrame()
        toolbar.setFixedWidth(50)
        toolbar.setStyleSheet("background-color: #222222; border-right: 1px solid #333333;")
        tool_layout = QVBoxLayout(toolbar)
        tool_layout.setContentsMargins(5, 15, 5, 15)
        tool_layout.setSpacing(10)
        tools = ["🖌️", "✒️", "🧽", "🔲", "📥"]
        for t in tools:
            btn = QPushButton(t)
            btn.setFixedSize(40, 40)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("QPushButton { background-color: transparent; border: 1px solid transparent; border-radius: 4px; font-size: 20px; } QPushButton:hover { background-color: #333333; border: 1px solid #555555; }")
            tool_layout.addWidget(btn)
        tool_layout.addStretch()
        workspace.addWidget(toolbar)
        canvas_bg = QFrame()
        canvas_bg.setStyleSheet("background-color: #181818;")
        canvas_layout = QVBoxLayout(canvas_bg)
        canvas_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.canvas = QFrame()
        self.canvas.setFixedSize(500, 500)
        self.canvas.setStyleSheet("background-color: white; border: 1px solid #444444;")
        baseline = QFrame(self.canvas)
        baseline.setGeometry(0, 350, 500, 1)
        baseline.setStyleSheet("background-color: #ff0000; opacity: 0.5;")
        canvas_layout.addWidget(self.canvas)
        workspace.addWidget(canvas_bg)
        main_layout.addLayout(workspace)
        bottom_bar = QFrame()
        bottom_bar.setFixedHeight(40)
        bottom_bar.setStyleSheet("background-color: #252525; border-top: 1px solid #333333;")
        bottom_layout = QHBoxLayout(bottom_bar)
        bottom_layout.setContentsMargins(15, 0, 15, 0)
        zoom_lbl = QLabel("Zoom: 100%")
        zoom_lbl.setStyleSheet("color: #888888; font-size: 12px;")
        bottom_layout.addWidget(zoom_lbl)
        bottom_layout.addStretch()
        undo_redo = QLabel("⟲ Undo  |  Redo ⟳")
        undo_redo.setStyleSheet("color: #888888; font-size: 12px;")
        bottom_layout.addWidget(undo_redo)
        main_layout.addWidget(bottom_bar)
        self.setLayout(main_layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HomeScreen() 
    window.resize(1000, 700)
    window.show()
    sys.exit(app.exec())