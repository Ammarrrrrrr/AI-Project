import sys
import random
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
import concurrent.futures
try:
    from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QComboBox, QColorDialog, QFrame, QGroupBox, QStatusBar, QMessageBox, QSizePolicy
    from PyQt5.QtGui import QMovie, QPixmap, QPainter, QColor, QFont, QIcon
    from PyQt5.QtCore import Qt, QTimer, QUrl, pyqtSignal, QThread
    from PyQt5.QtMultimedia import QSoundEffect
except ImportError as e:
    print('PyQt5 is not installed. Please install it with: pip install PyQt5')
    sys.exit(1)

try:
    from .nqueens_ai import NQueensSolver
    from .ai_learning import QLearningAI
except (ImportError, SystemError):
    from nqueens_ai import NQueensSolver
    from ai_learning import QLearningAI
import os

IDLE_ANIMATIONS = [
    ('happy', 'I love helping you!'),
    ('thinking', 'I am thinking about queens...'),
    ('excited', 'This is fun!'),
    ('neutral', 'Just waiting for your move!'),
    ('confused', 'What will you do next?'),
]

ANIMAL_TYPES = ['cat', 'fox', 'dog']
ANIMAL_SYMBOLS = {'cat': '🐱', 'fox': '🦊', 'dog': '🐶'}
DARK_BG = '#23272e'
DARK_PANEL = '#2c313a'
DARK_ACCENT = '#3c4452'
DARK_TEXT = '#e0e0e0'
DARK_GREEN = '#2ecc40'
DARK_RED = '#e74c3c'

class BoardWidget(QWidget):
    place_message = pyqtSignal(bool, str)  # True/False, reason
    solved_signal = pyqtSignal()  # Signal to notify when solved
    def __init__(self, n=8, animal_type='cat', parent=None):
        super().__init__(parent)
        self.n = n
        self.animal_type = animal_type
        self.setMinimumSize(400, 400)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.queen_color = QColor(0, 0, 0)  # Default queen color: black
        self.queen_symbol = ANIMAL_SYMBOLS.get(self.animal_type, '♛')
        self.queen_pixmap = self.create_symbol_pixmap()
        self.queens = []  # List of (row, col) tuples
        self.user_state = [None] * self.n
        self.invalid_flashes = []  # List of (row, col) to flash red
        self.valid_flash = None    # (row, col) to flash green
        self.flash_timers = []  # List of QTimers for each invalid flash
        self.hint_highlights = []  # List of (row, col) to highlight for hint
        self.hint_timer = None
        # Dark theme board colors
        self.bg_color1 = QColor(60, 65, 82)
        self.bg_color2 = QColor(44, 49, 58)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Update queen pixmap when widget is resized
        self.queen_pixmap = self.create_symbol_pixmap()
        self.update()

    def set_queen_color(self, color):
        self.queen_color = color
        self.queen_pixmap = self.create_symbol_pixmap()
        self.update()

    def create_symbol_pixmap(self):
        # Calculate symbol size based on board size
        cell_size = self.width() // self.n
        symbol_size = min(32, cell_size - 4)  # Ensure symbol fits in cell with padding
        
        pixmap = QPixmap(symbol_size, symbol_size)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setPen(self.queen_color)
        font = self.font()
        font.setPointSize(symbol_size // 2)  # Adjust font size proportionally
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignCenter, self.queen_symbol)
        painter.end()
        return pixmap

    def set_animal_type(self, animal_type):
        self.animal_type = animal_type
        self.queen_symbol = ANIMAL_SYMBOLS.get(self.animal_type, '♛')
        self.queen_pixmap = self.create_symbol_pixmap()
        self.update()

    def set_bg_colors(self, color1, color2):
        self.bg_color1 = color1
        self.bg_color2 = color2
        self.update()

    def set_hint_highlights(self, squares, duration=7000):
        self.hint_highlights = list(squares)
        self.update()
        if self.hint_timer:
            self.hint_timer.stop()
        self.hint_timer = QTimer(self)
        self.hint_timer.setSingleShot(True)
        self.hint_timer.timeout.connect(self.clear_hint_highlights)
        self.hint_timer.start(duration)

    def clear_hint_highlights(self):
        self.hint_highlights = []
        self.update()

    def mousePressEvent(self, event):
        # Make the board always square and centered
        size = min(self.width(), self.height())
        x_offset = (self.width() - size) // 2
        y_offset = (self.height() - size) // 2
        cell_size = size // self.n
        x = event.x() - x_offset
        y = event.y() - y_offset
        if x < 0 or y < 0 or x >= size or y >= size:
            return  # Click outside the board
        col = x // cell_size
        row = y // cell_size
        if row < self.n and col < self.n:
            # Remove queen if present
            if (row, col) in self.queens:
                self.queens.remove((row, col))
                self.update()
                self.check_solved()
                return
            # Place queen if not already present and under N queens
            if len(self.queens) < self.n and (row, col) not in self.queens:
                valid, reason = self.is_valid(row, col)
                self.queens.append((row, col))
                if valid:
                    self.valid_flash = (row, col)
                    QTimer.singleShot(300, self.clear_valid_flash)
                    self.place_message.emit(True, '')
                else:
                    self.add_invalid_flash(row, col)
                    self.place_message.emit(False, reason)
                self.update()
                self.check_solved()

    def add_invalid_flash(self, row, col):
        # Add a new invalid flash and set a timer to remove it after 1500ms
        self.invalid_flashes.append((row, col))
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(lambda: self.remove_invalid_flash(row, col, timer))
        timer.start(1500)
        self.flash_timers.append(timer)
        self.update()

    def remove_invalid_flash(self, row, col, timer):
        if (row, col) in self.invalid_flashes:
            self.invalid_flashes.remove((row, col))
        if timer in self.flash_timers:
            self.flash_timers.remove(timer)
        self.update()

    def clear_valid_flash(self):
        self.valid_flash = None
        self.update()

    def is_valid(self, row, col):
        for r, c in self.queens:
            if r == row and c == col:
                continue  # skip self
            if c == col:
                return False, 'Column is already occupied by another queen.'
            if r == row:
                return False, 'Row is already occupied by another queen.'
            if abs(row - r) == abs(col - c):
                return False, 'This diagonal is attacked by another queen.'
        return True, ''

    def paintEvent(self, event):
        painter = QPainter(self)
        # Make the board always square and centered
        size = min(self.width(), self.height())
        x_offset = (self.width() - size) // 2
        y_offset = (self.height() - size) // 2
        cell_size = size // self.n
        # Draw board
        for row in range(self.n):
            for col in range(self.n):
                color = self.bg_color1 if (row + col) % 2 == 0 else self.bg_color2
                if (row, col) in self.invalid_flashes:
                    color = QColor(255, 80, 80)
                elif self.valid_flash == (row, col):
                    color = QColor(80, 255, 80)
                elif (row, col) in self.hint_highlights:
                    color = QColor(255, 255, 100)
                painter.fillRect(x_offset + col * cell_size, y_offset + row * cell_size, cell_size, cell_size, color)
        # Draw queens
        for row, col in self.queens:
            symbol_size = min(32, cell_size - 4)
            x = x_offset + col * cell_size + (cell_size - symbol_size) // 2
            y = y_offset + row * cell_size + (cell_size - symbol_size) // 2
            painter.drawPixmap(x, y, self.queen_pixmap)
        painter.end()

    def reset_board(self):
        self.queens = []
        self.user_state = [None] * self.n
        self.invalid_flashes = []
        self.valid_flash = None
        self.hint_highlights = []
        self.update()

    def set_board(self, queens):
        self.queens = list(queens)
        self.user_state = list(queens)
        self.invalid_flashes = []
        self.valid_flash = None
        self.hint_highlights = []
        self.update()

    def check_solved(self):
        # Check if the board is solved: N queens, all valid
        if len(self.queens) == self.n:
            for idx, (row, col) in enumerate(self.queens):
                # Remove this queen and check if it's still valid
                temp_queens = self.queens[:idx] + self.queens[idx+1:]
                for r, c in temp_queens:
                    if c == col or r == row or abs(row - r) == abs(col - c):
                        return
            self.solved_signal.emit()

# --- Top-level multiprocessing helpers ---
def is_safe(state, row, col):
    for r, c in enumerate(state):
        if c == col or abs(row - r) == abs(col - c):
            return False
    return True

def solve_partial(args):
    n, start_col = args
    solutions = []
    def backtrack(state):
        row = len(state)
        if row == n:
            solutions.append([(r, c) for r, c in enumerate(state)])
            return
        for col in range(n):
            if is_safe(state, row, col):
                backtrack(state + [col])
    backtrack([start_col])
    return solutions

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Initialize core attributes first
        self.n = 8
        self.animal_type = 'cat'
        self.solver = NQueensSolver(self.n)
        self.ai = QLearningAI(self.n)
        self.solutions = []
        self.current_solution_idx = 0
        self.solver_worker = None
        self.is_solved = False
        
        # Window setup
        self.setWindowTitle('N-Queens AI Animal Game')
        self.setGeometry(100, 100, 1000, 700)
        self.setMinimumSize(800, 600)  # Set minimum window size
        self.setStyleSheet(f"""
            QMainWindow {{
                background: {DARK_BG};
                color: {DARK_TEXT};
            }}
            QWidget {{
                background: {DARK_BG};
                color: {DARK_TEXT};
            }}
            QGroupBox {{
                background: {DARK_PANEL};
                color: {DARK_TEXT};
                border-radius: 8px;
                border: 1px solid {DARK_ACCENT};
                margin-top: 1em;
                padding-top: 1em;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }}
            QPushButton {{
                background: {DARK_ACCENT};
                color: #fff;
                padding: 8px;
                border-radius: 8px;
                font-weight: bold;
                min-height: 30px;
                border: none;
            }}
            QPushButton:checked, QPushButton:pressed {{
                background: {DARK_GREEN};
                color: #fff;
            }}
            QPushButton:disabled {{
                background: #444;
                color: #888;
            }}
            QPushButton:hover:!disabled {{
                background: #444b5a;
            }}
            QComboBox, QComboBox QAbstractItemView {{
                background: {DARK_PANEL};
                color: {DARK_TEXT};
                border-radius: 6px;
                min-height: 30px;
                selection-background-color: {DARK_ACCENT};
                selection-color: #fff;
            }}
            QComboBox QAbstractItemView {{
                border: 1px solid {DARK_ACCENT};
                selection-background-color: {DARK_GREEN};
                selection-color: #fff;
            }}
            QComboBox::drop-down {{
                background: {DARK_ACCENT};
                border-left: 1px solid {DARK_ACCENT};
            }}
            QComboBox::down-arrow {{
                image: none;
                border: none;
                width: 0;
                height: 0;
            }}
            QLabel {{
                background: transparent;
                color: {DARK_TEXT};
                padding: 4px;
            }}
            QStatusBar {{
                background: {DARK_ACCENT};
                color: {DARK_TEXT};
                font-size: 14px;
                padding: 5px;
                border-top: 1px solid {DARK_PANEL};
            }}
            QScrollBar:vertical, QScrollBar:horizontal {{
                background: {DARK_PANEL};
                border: none;
                width: 12px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{
                background: {DARK_ACCENT};
                min-height: 20px;
                border-radius: 6px;
            }}
            QScrollBar::add-line, QScrollBar::sub-line {{
                background: none;
                border: none;
            }}
            QMessageBox {{
                background-color: {DARK_PANEL};
                color: {DARK_TEXT};
                border: 2px solid {DARK_GREEN};
            }}
            QMessageBox QLabel {{
                color: {DARK_GREEN};
                font-size: 18px;
            }}
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)  # Increased spacing between elements
        central_widget.setLayout(main_layout)
        
        # Header with app name and animal icon row
        header = QHBoxLayout()
        header.setSpacing(20)
        title = QLabel('N-Queens AI Animal Game')
        title.setFont(QFont('Segoe UI', 24, QFont.Bold))
        title.setStyleSheet(f'color: {DARK_GREEN}; padding: 10px;')
        header.addWidget(title)
        header.addStretch()
        
        # Animal icon choice row (for queen icon)
        self.animal_buttons = {}
        icon_row = QHBoxLayout()
        icon_row.setSpacing(10)
        for animal in ANIMAL_TYPES:
            btn = QPushButton(ANIMAL_SYMBOLS[animal])
            btn.setCheckable(True)
            btn.setFixedSize(50, 50)  # Fixed size for animal buttons
            btn.setStyleSheet(f"""
                font-size: 28px;
                background: {DARK_PANEL};
                color: {DARK_TEXT};
                border-radius: 10px;
                padding: 6px;
            """)
            btn.clicked.connect(lambda checked, a=animal: self.change_animal(a))
            icon_row.addWidget(btn)
            self.animal_buttons[animal] = btn
        self.animal_buttons[self.animal_type].setChecked(True)
        header.addLayout(icon_row)
        main_layout.addLayout(header)
        
        # Main content area
        content = QHBoxLayout()
        content.setSpacing(30)  # Increased spacing between board and controls
        main_layout.addLayout(content)
        
        # Board frame with shadow
        board_frame = QFrame()
        board_frame.setStyleSheet(f"""
            background: {DARK_PANEL};
            border-radius: 16px;
            border: 2px solid {DARK_ACCENT};
        """)
        board_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.board_layout = QVBoxLayout()
        self.board_layout.setSpacing(0)
        self.board_layout.setContentsMargins(0, 0, 0, 0)
        board_frame.setLayout(self.board_layout)
        self.board_widget = BoardWidget(self.n, self.animal_type)
        self.board_layout.addWidget(self.board_widget)
        
        # Next solution button
        self.next_solution_btn = QPushButton('Show Next Solution')
        self.next_solution_btn.setIcon(QIcon.fromTheme('go-down') or QIcon(''))
        self.next_solution_btn.setStyleSheet(f"""
            font-size: 16px;
            background: {DARK_ACCENT};
            color: {DARK_GREEN};
            border-radius: 8px;
            padding: 10px;
            min-height: 40px;
        """)
        self.next_solution_btn.clicked.connect(self.show_next_solution)
        self.next_solution_btn.setVisible(False)
        self.board_layout.addWidget(self.next_solution_btn)
        
        # Add board frame to content with stretch
        content.addWidget(board_frame, stretch=2)
        
        # Right panel for controls and info
        right_panel = QVBoxLayout()
        right_panel.setSpacing(20)
        content.addLayout(right_panel, stretch=1)
        
        # Board size selector
        size_group = QGroupBox('Board Size')
        size_layout = QVBoxLayout()
        size_layout.setSpacing(10)
        self.size_selector = QComboBox()
        solvable_ns = [str(i) for i in range(4, 21) if i not in (2, 3)]
        self.size_selector.addItems(solvable_ns)
        self.size_selector.setCurrentText(str(self.n))
        self.size_selector.currentTextChanged.connect(self.change_board_size)
        size_layout.addWidget(self.size_selector)
        size_group.setLayout(size_layout)
        right_panel.addWidget(size_group)
        
        # Speech bubble
        self.speech_label = QLabel(f'{ANIMAL_SYMBOLS[self.animal_type]} Hello! I am your animal AI friend!')
        self.speech_label.setAlignment(Qt.AlignCenter)
        self.speech_label.setWordWrap(True)  # Enable word wrap
        self.speech_label.setStyleSheet(f"""
            font-size: 18px;
            background: {DARK_BG};
            border-radius: 10px;
            padding: 15px;
            color: #fffbe6;
            min-height: 60px;
        """)
        right_panel.addWidget(self.speech_label)
        
        # Controls group
        controls_group = QGroupBox('Controls')
        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(12)
        
        self.hint_button = QPushButton('Hint')
        self.hint_button.setStyleSheet(f'background: {DARK_GREEN}; color: #fff;')
        self.hint_button.clicked.connect(self.give_hint)
        controls_layout.addWidget(self.hint_button)
        
        self.solve_button = QPushButton('AI Solve')
        self.solve_button.setStyleSheet(f'background: {DARK_ACCENT}; color: #fff;')
        self.solve_button.clicked.connect(self.solve_board)
        controls_layout.addWidget(self.solve_button)
        
        self.reset_button = QPushButton('Reset')
        self.reset_button.setStyleSheet(f'background: {DARK_RED}; color: #fff;')
        self.reset_button.clicked.connect(self.reset_board)
        controls_layout.addWidget(self.reset_button)
        
        self.color_button = QPushButton('Change Board Colors')
        self.color_button.setStyleSheet(f'background: {DARK_ACCENT}; color: #fff;')
        self.color_button.clicked.connect(self.pick_board_colors)
        controls_layout.addWidget(self.color_button)
        
        controls_group.setLayout(controls_layout)
        right_panel.addWidget(controls_group)
        
        # Solution selector
        self.solution_selector = QComboBox()
        self.solution_selector.currentIndexChanged.connect(self.select_solution)
        self.solution_selector.setStyleSheet(f'background: {DARK_PANEL}; color: {DARK_TEXT};')
        right_panel.addWidget(self.solution_selector)
        
        right_panel.addStretch()
        
        # Status bar
        self.status = QStatusBar()
        self.status.setStyleSheet(f"""
            background: {DARK_ACCENT};
            color: {DARK_TEXT};
            font-size: 14px;
            padding: 5px;
        """)
        self.setStatusBar(self.status)
        self.status.showMessage('Ready to play!')
        
        # Connect signals
        self.board_widget.place_message.connect(self.show_place_message)
        self.board_widget.solved_signal.connect(self.show_congratulations)
        
        # Sound effect
        self.sound = QSoundEffect()
        self.sound.setVolume(0.5)
        
        # Idle timer
        self.idle_timer = QTimer()
        self.idle_timer.setInterval(8000)
        self.idle_timer.timeout.connect(self.idle_animation)
        self.idle_timer.start()
        
        # Reset idle timer on user interaction
        for btn in [self.hint_button, self.solve_button, self.reset_button, 
                   self.solution_selector, self.size_selector, self.color_button]:
            btn.installEventFilter(self)
        self.board_widget.installEventFilter(self)
        
        # Highlight selected animal button
        self.update_animal_buttons()

    def _animal_asset(self, filename):
        path = os.path.join('assets', self.animal_type, filename)
        return path

    def play_sound(self, emotion):
        sound_path = self._animal_asset(f'{emotion}.wav')
        if os.path.exists(sound_path):
            self.sound.setSource(QUrl.fromLocalFile(sound_path))
            self.sound.play()

    def set_animal_emotion(self, emotion, message, duration=2000):
        # Just show the message, no animal symbol
        self.speech_label.setText(message)
        self.play_sound(emotion)
        self.idle_timer.start()
        # Return to neutral after duration
        if emotion != 'neutral':
            QTimer.singleShot(duration, lambda: self.set_animal_emotion('neutral', 'Ready for your next move!'))

    def board_is_solved(self):
        if len(self.board_widget.queens) != self.n:
            return False
        # Check if all queens are mutually non-attacking
        for idx, (row, col) in enumerate(self.board_widget.queens):
            temp_queens = self.board_widget.queens[:idx] + self.board_widget.queens[idx+1:]
            for r, c in temp_queens:
                if c == col or r == row or abs(row - r) == abs(col - c):
                    return False
        return True

    def give_hint(self):
        if self.is_solved or self.board_is_solved():
            self.set_animal_emotion('happy', '🎉 The board is already solved! Great job!', duration=4000)
            self.status.showMessage('Board is already solved!')
            self.board_widget.set_hint_highlights([])
            return
        # Suggest a valid move for the current board (any empty square that is valid)
        for row in range(self.n):
            for col in range(self.n):
                if (row, col) not in self.board_widget.queens:
                    valid, _ = self.board_widget.is_valid(row, col)
                    if valid:
                        self.board_widget.queens.append((row, col))
                        self.board_widget.valid_flash = (row, col)
                        QTimer.singleShot(300, self.board_widget.clear_valid_flash)
                        self.board_widget.update()
                        self.set_animal_emotion('thinking', f'Hint: Try placing at row {row+1}, col {col+1}!', duration=7000)
                        self.board_widget.set_hint_highlights([(row, col)], duration=7000)
                        return
        # If no valid move, suggest which queen to move and where
        for idx, (qrow, qcol) in enumerate(self.board_widget.queens):
            temp_queens = self.board_widget.queens[:idx] + self.board_widget.queens[idx+1:]
            for new_row in range(self.n):
                for new_col in range(self.n):
                    if (new_row, new_col) not in temp_queens and (new_row, new_col) != (qrow, qcol):
                        # Temporarily check validity
                        is_valid = True
                        for r, c in temp_queens:
                            if c == new_col or r == new_row or abs(new_row - r) == abs(new_col - c):
                                is_valid = False
                                break
                        if is_valid:
                            msg = f'No valid moves! Try moving queen from row {qrow+1}, col {qcol+1} to row {new_row+1}, col {new_col+1}.'
                            self.set_animal_emotion('confused', msg, duration=7000)
                            self.board_widget.set_hint_highlights([(qrow, qcol), (new_row, new_col)], duration=7000)
                            return
        # Fallback: suggest removing one or more queens
        suggestions = []
        for idx, (qrow, qcol) in enumerate(self.board_widget.queens):
            temp_queens = self.board_widget.queens[:idx] + self.board_widget.queens[idx+1:]
            for row in range(self.n):
                for col in range(self.n):
                    if (row, col) not in temp_queens:
                        is_valid = True
                        for r, c in temp_queens:
                            if c == col or r == row or abs(row - r) == abs(col - c):
                                is_valid = False
                                break
                        if is_valid:
                            suggestions.append((qrow, qcol))
                            break
                if suggestions and suggestions[-1] == (qrow, qcol):
                    break
        if suggestions:
            msg = 'No valid moves! Try removing queen(s) at: '
            msg += ', '.join([f'row {r+1}, col {c+1}' for r, c in suggestions])
            self.set_animal_emotion('confused', msg, duration=7000)
            self.board_widget.set_hint_highlights(suggestions, duration=7000)
        else:
            self.set_animal_emotion('surprised', 'No valid moves! Try removing one or more queens to continue.', duration=7000)
            self.board_widget.set_hint_highlights([], duration=7000)

    def solve_board(self):
        print(f"AI Solve called. Board size: {self.n}")
        self.board_widget.set_board([])
        self.solutions = []
        self.current_solution_idx = 0
        self.is_solved = False
        self.hint_button.setDisabled(True)
        self.solve_button.setDisabled(True)
        self.status.showMessage('Solving N-Queens puzzle (multi-core)...')
        self.set_animal_emotion('thinking', 'Solving... Please wait!')

        cpu_count = os.cpu_count() or 2
        n = self.n
        with concurrent.futures.ProcessPoolExecutor(max_workers=cpu_count) as executor:
            futures = [executor.submit(solve_partial, (n, col)) for col in range(n)]
            all_solutions = []
            for future in concurrent.futures.as_completed(futures):
                all_solutions.extend(future.result())
        self.solutions = all_solutions
        print(f"Found {len(self.solutions)} solutions (multi-core)")
        self.solution_selector.clear()
        for i in range(len(self.solutions)):
            self.solution_selector.addItem(f"Solution {i+1}")
        if self.solutions:
            self.current_solution_idx = 0
            self.board_widget.set_board(self.solutions[0])
            self.next_solution_btn.setVisible(len(self.solutions) > 1)
            if len(self.solutions) > 1:
                self.set_animal_emotion('excited', f'I found {len(self.solutions)} solutions!')
            else:
                self.set_animal_emotion('happy', 'I solved it for you!')
            self.show_congratulations()
        else:
            msg = QMessageBox(self)
            msg.setWindowTitle('No Solution')
            msg.setText('No solution exists for this board.')
            msg.setIcon(QMessageBox.Warning)
            msg.setStyleSheet('QLabel{color: #e74c3c; font-size: 18px;} QMessageBox{background-color: #232; border: 2px solid #e74c3c;}')
            msg.exec_()
            self.set_animal_emotion('sad', 'No solutions from here!')
        self.hint_button.setDisabled(False)
        self.solve_button.setDisabled(False)
        self.status.showMessage(f'Found {len(self.solutions)} solutions!')

    def select_solution(self, idx):
        if 0 <= idx < len(self.solutions):
            self.board_widget.set_board(self.solutions[idx])
            self.set_animal_emotion('excited', f'Showing solution {idx+1} of {len(self.solutions)}')

    def reset_board(self):
        self.is_solved = False
        self.board_widget.reset_board()
        self.set_animal_emotion('neutral', 'Board reset!')
        self.next_solution_btn.setVisible(False)
        self.status.showMessage('Board has been reset. Ready to play!')
        self.hint_button.setDisabled(False)
        self.solve_button.setDisabled(False)

    def change_animal(self, animal):
        self.animal_type = animal
        self.set_animal_emotion('neutral', f'You selected {animal}!')
        self.board_widget.set_animal_type(animal)
        self.update_animal_buttons()

    def change_board_size(self, size):
        self.n = int(size)
        self.solver = NQueensSolver(self.n)
        self.ai = QLearningAI(self.n)
        self.board_layout.removeWidget(self.board_widget)
        self.board_widget.deleteLater()
        self.board_widget = BoardWidget(self.n, self.animal_type)
        self.board_layout.insertWidget(0, self.board_widget)
        self.board_layout.addWidget(self.next_solution_btn)
        self.board_widget.installEventFilter(self)
        self.board_widget.place_message.connect(self.show_place_message)
        self.board_widget.solved_signal.connect(self.show_congratulations)
        self.solutions = []
        self.solution_selector.clear()
        self.set_animal_emotion('neutral', f'Changed to {self.n}x{self.n} board!')
        self.next_solution_btn.setVisible(False)
        self.status.showMessage(f'Board size changed to {self.n}x{self.n}. Ready to play!')
        self.is_solved = False
        self.hint_button.setDisabled(False)
        self.solve_button.setDisabled(False)

    def idle_animation(self):
        emotion, message = random.choice(IDLE_ANIMATIONS)
        self.set_animal_emotion(emotion, message, duration=2500)

    def eventFilter(self, obj, event):
        # Reset idle timer on any user interaction
        if event.type() in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12):  # Mouse/keyboard events
            self.idle_timer.start()
        return super().eventFilter(obj, event)

    def show_place_message(self, valid, reason):
        if self.is_solved:
            self.status.showMessage('Board is already solved!')
            return
        if valid:
            self.set_animal_emotion('happy', 'Good move!')
            self.status.showMessage('Valid move! Keep going!')
        else:
            msg = 'Wrong place!'
            if reason:
                msg += f' Reason: {reason}'
            self.set_animal_emotion('confused', msg, duration=2500)
            self.status.showMessage(msg)

    def pick_board_colors(self):
        color1 = QColorDialog.getColor(self.board_widget.bg_color1, self, 'Pick Light Square Color')
        if color1.isValid():
            color2 = QColorDialog.getColor(self.board_widget.bg_color2, self, 'Pick Dark Square Color')
            if color2.isValid():
                self.board_widget.set_bg_colors(color1, color2)

    def update_animal_buttons(self):
        for animal, btn in self.animal_buttons.items():
            if animal == self.animal_type:
                btn.setChecked(True)
                btn.setStyleSheet(f"font-size: 28px; background: {DARK_GREEN}; color: #fff; border-radius: 10px; padding: 6px;")
            else:
                btn.setChecked(False)
                btn.setStyleSheet(f"font-size: 28px; background: {DARK_PANEL}; color: {DARK_TEXT}; border-radius: 10px; padding: 6px;")

    def show_congratulations(self):
        self.is_solved = True
        self.hint_button.setDisabled(True)
        self.solve_button.setDisabled(True)
        self.board_widget.set_hint_highlights([])
        msg = QMessageBox(self)
        msg.setWindowTitle('Congratulations!')
        msg.setText('🎉 Congratulations, well done! You solved the N-Queens puzzle! 🎉')
        msg.setStyleSheet('QLabel{color: #27ae60; font-size: 20px;} QMessageBox{background-color: #232; border: 2px solid #27ae60;}')
        msg.setIcon(QMessageBox.Information)
        msg.exec_()
        self.next_solution_btn.setVisible(len(self.solutions) > 1)

    def show_next_solution(self):
        if not self.solutions:
            return
        self.current_solution_idx = (self.current_solution_idx + 1) % len(self.solutions)
        self.board_widget.set_board(self.solutions[self.current_solution_idx])
        self.set_animal_emotion('excited', f'Showing solution {self.current_solution_idx+1} of {len(self.solutions)}')

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f'Error: {e}')
        print('Make sure all dependencies and assets are installed and available.') 