import os
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QRadioButton, QButtonGroup, QHBoxLayout, QMenuBar, QAction, QFileDialog, QMessageBox
from .flashcard_window import FlashCardWindow

class FlashCardApp(QMainWindow):  # Inherit from QMainWindow for menu bar functionality
    def __init__(self):
        super().__init__()
        self.selected_folder = None
        self.is_random = True
        self.current_index = 0
        self.flashcard_files = []
        self.flashcard_directory = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Flashcard - Start Menu")
        self.setGeometry(100, 100, 400, 300)

        # Create a central widget and set layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create a menu bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')

        # Add the "Select Directory" action to the File menu
        select_dir_action = QAction('Select Flashcard Directory', self)
        select_dir_action.triggered.connect(self.select_flashcard_directory)
        file_menu.addAction(select_dir_action)

        # Instruction label for folder selection
        folder_label = QLabel("Select Folder:", self)
        layout.addWidget(folder_label)

        # Folder selection dropdown
        self.folder_combo = QComboBox(self)
        layout.addWidget(self.folder_combo)

        # Instruction label for mode selection
        mode_label = QLabel("Select Mode:", self)
        layout.addWidget(mode_label)

        # Mode selection
        mode_layout = QHBoxLayout()
        self.random_radio = QRadioButton("Random")
        self.sequential_radio = QRadioButton("Sequential")
        self.random_radio.setChecked(True)  # Default to random selection
        mode_layout.addWidget(self.random_radio)
        mode_layout.addWidget(self.sequential_radio)
        layout.addLayout(mode_layout)

        # Button group for the radio buttons
        self.mode_group = QButtonGroup(self)
        self.mode_group.addButton(self.random_radio)
        self.mode_group.addButton(self.sequential_radio)

        # Instruction label for start button
        start_label = QLabel("Click Start to Begin:", self)
        layout.addWidget(start_label)

        # Start button
        self.start_button = QPushButton("Start", self)
        self.start_button.clicked.connect(self.start_flashcards)
        layout.addWidget(self.start_button)

    def select_flashcard_directory(self):
        # Open a dialog to select the flashcard directory
        dir_path = QFileDialog.getExistingDirectory(self, "Select Flashcard Directory")
        if dir_path:
            self.flashcard_directory = dir_path
            print(f"Selected Flashcard Directory: {self.flashcard_directory}")
            self.load_folders(self.flashcard_directory)

    def load_folders(self, flashcard_folder):
        # Load available folders into the combo box
        self.folder_combo.clear()  # Clear the combo box before adding items
        if os.path.exists(flashcard_folder):
            for root, dirs, files in os.walk(flashcard_folder):
                for dir_name in dirs:
                    self.folder_combo.addItem(dir_name)
                break  # Only consider the first level of directories
        else:
            print(f"Path does not exist: {flashcard_folder}")

    def start_flashcards(self):
        # Check if the flashcard directory has been selected
        if not self.flashcard_directory:
            QMessageBox.warning(self, "No Directory Selected", "Please select a folder where your flashcards are located.")
            return  # Exit the function if no directory is selected

        # Get the selected folder and mode
        self.selected_folder = self.folder_combo.currentText()
        self.is_random = self.random_radio.isChecked()

        if self.selected_folder:
            # Prepare the flashcard list based on the selected folder
            flashcard_folder = os.path.join(self.flashcard_directory, self.selected_folder)
            self.flashcard_files = self.get_flashcard_files(flashcard_folder)

            # Open the flashcard window
            self.open_flashcard_window()
        else:
            QMessageBox.warning(self, "No Folder Selected", "Please select a folder within the directory to continue.")

    def get_flashcard_files(self, folder):
        # List to hold all text file paths in the selected folder
        flashcard_files = []

        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.endswith(".txt"):
                    flashcard_files.append(os.path.join(root, file))

        if not flashcard_files:
            raise FileNotFoundError("No flashcard text files found in the selected directory.")

        return flashcard_files

    def open_flashcard_window(self):
        # Create a new flashcard window
        self.flashcard_window = FlashCardWindow(self.flashcard_files, self.is_random)
        self.flashcard_window.show()
