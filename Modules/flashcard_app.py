import os
import json
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QRadioButton, QButtonGroup, QHBoxLayout, QMenuBar, QAction, QFileDialog, QMessageBox, QInputDialog
from .flashcard_window import FlashCardWindow
from .flashcard_creator import FlashCardCreator  # Import the new FlashCardCreator module

class FlashCardApp(QMainWindow):  # Inherit from QMainWindow for menu bar functionality
    def __init__(self):
        super().__init__()
        self.selected_folder = None
        self.is_random = True
        self.current_index = 0
        self.flashcard_files = []
        self.flashcard_directory = None
        self.json_path = "flashcard_results.json"
        self.typing_speed = 50  # Default typing speed (characters per second)
        self.sound_enabled = True  # Default sound setting

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Flashcard - Start Menu")
        self.setGeometry(100, 100, 400, 150)

        # Create a central widget and set layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create a menu bar
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu('File')
        select_dir_action = QAction('Select Flashcard Directory', self)
        select_dir_action.triggered.connect(self.select_flashcard_directory)
        file_menu.addAction(select_dir_action)

        # Clear Results action
        clear_results_action = QAction('Clear Results', self)
        clear_results_action.triggered.connect(self.clear_results)
        file_menu.addAction(clear_results_action)

        # Flashcards menu
        flashcards_menu = menubar.addMenu('Flashcards')
        create_flashcards_action = QAction('Create New Flashcards', self)
        create_flashcards_action.triggered.connect(self.create_flashcards)
        flashcards_menu.addAction(create_flashcards_action)

        # Settings menu
        settings_menu = menubar.addMenu('Settings')

        # Adjust typing speed action
        adjust_speed_action = QAction('Adjust Typing Speed', self)
        adjust_speed_action.triggered.connect(self.adjust_typing_speed)
        settings_menu.addAction(adjust_speed_action)

        # Toggle sound action
        self.toggle_sound_action = QAction('Enable Sounds', self, checkable=True)
        self.toggle_sound_action.setChecked(self.sound_enabled)
        self.toggle_sound_action.triggered.connect(self.toggle_sound)
        settings_menu.addAction(self.toggle_sound_action)

        # Instruction label for folder selection
        folder_label = QLabel("Select Folder:", self)
        layout.addWidget(folder_label)

        # Folder selection dropdown
        self.folder_combo = QComboBox(self)
        self.folder_combo.currentIndexChanged.connect(self.update_flashcard_count)
        layout.addWidget(self.folder_combo)

        # Label to show the number of flashcards in the selected folder
        self.flashcard_count_label = QLabel("Number of Flashcards: 0", self)
        layout.addWidget(self.flashcard_count_label)

        # Instruction label for mode selection
        mode_label = QLabel("Select Mode:", self)
        layout.addWidget(mode_label)

        # Mode selection
        mode_layout = QHBoxLayout()
        self.random_radio = QRadioButton("Random")
        self.sequential_radio = QRadioButton("Sequential")
        self.load_incorrect_radio = QRadioButton("Load Incorrect")  # New radio button
        self.random_radio.setChecked(True)  # Default to random selection
        mode_layout.addWidget(self.random_radio)
        mode_layout.addWidget(self.sequential_radio)
        mode_layout.addWidget(self.load_incorrect_radio)  # Add to layout
        layout.addLayout(mode_layout)

        # Button group for the radio buttons
        self.mode_group = QButtonGroup(self)
        self.mode_group.addButton(self.random_radio)
        self.mode_group.addButton(self.sequential_radio)
        self.mode_group.addButton(self.load_incorrect_radio)  # Add to group

        # Instruction label for start button
        start_label = QLabel("Click Start to Begin:", self)
        layout.addWidget(start_label)

        # Start button
        self.start_button = QPushButton("Start", self)
        self.start_button.clicked.connect(self.start_flashcards)
        layout.addWidget(self.start_button)

    def clear_results(self):
        """Clear results from the JSON file based on the selected category."""
        if not self.selected_folder:
            QMessageBox.information(self, "No Folder Selected", "Please select a folder to clear results.")
            return

        if os.path.exists(self.json_path):
            with open(self.json_path, "r") as file:
                results = json.load(file)

            # Extract the category name from the selected folder
            selected_category = self.selected_folder

            # Prompt the user to confirm deletion of the category
            reply = QMessageBox.question(
                self, 'Clear Results', 
                f"Do you want to clear the results for category '{selected_category}'?", 
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                # Remove all entries for the selected category
                results["flashcards"] = {k: v for k, v in results["flashcards"].items() if selected_category not in k}

                # Save the updated results back to the JSON file
                with open(self.json_path, "w") as file:
                    json.dump(results, file, indent=4)

                QMessageBox.information(self, "Results Cleared", f"Results for category '{selected_category}' have been cleared.")
            else:
                QMessageBox.information(self, "Results Not Cleared", f"Results for category '{selected_category}' have not been cleared.")

        else:
            QMessageBox.information(self, "No Results Found", "No results file found to clear.")
    
    def create_flashcards(self):
        flashcard_creator = FlashCardCreator(self.flashcard_directory)
        flashcard_creator.start_flashcard_creation()

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

    def update_flashcard_count(self):
        # Update the label showing the number of flashcards in the selected folder
        if self.flashcard_directory:
            selected_folder = self.folder_combo.currentText()
            if selected_folder:
                self.selected_folder = selected_folder  # Update the selected folder
                folder_path = os.path.join(self.flashcard_directory, selected_folder)
                flashcard_files = self.get_flashcard_files(folder_path)
                self.flashcard_count_label.setText(f"Number of Flashcards: {len(flashcard_files)}")
            else:
                self.flashcard_count_label.setText("Number of Flashcards: 0")

    def adjust_typing_speed(self):
        # Open an input dialog to adjust the typing speed
        speed, ok = QInputDialog.getInt(self, "Adjust Typing Speed", "Enter characters per second:", self.typing_speed, 10, 200, 1)
        if ok:
            self.typing_speed = speed
            print(f"Typing speed adjusted to: {self.typing_speed} characters per second")

    def toggle_sound(self):
        # Toggle sound on or off
        self.sound_enabled = not self.sound_enabled
        if self.sound_enabled:
            self.toggle_sound_action.setText("Disable Sounds")
        else:
            self.toggle_sound_action.setText("Enable Sounds")

    def start_flashcards(self):
        # Check if the flashcard directory has been selected
        if not self.flashcard_directory:
            QMessageBox.warning(self, "No Directory Selected", "Please select a folder where your flashcards are located.")
            return  # Exit the function if no directory is selected

        # Get the selected folder and mode
        self.selected_folder = self.folder_combo.currentText()
        self.is_random = self.random_radio.isChecked()

        if self.load_incorrect_radio.isChecked():
            # Load only incorrect flashcards
            self.load_incorrect_flashcards()
        elif self.selected_folder:
            # Prepare the flashcard list based on the selected folder
            flashcard_folder = os.path.join(self.flashcard_directory, self.selected_folder)
            self.flashcard_files = self.get_flashcard_files(flashcard_folder)

            # Open the flashcard window
            self.open_flashcard_window()
        else:
            QMessageBox.warning(self, "No Folder Selected", "Please select a folder within the directory to continue.")

    def load_incorrect_flashcards(self):
        # Load incorrect flashcards based on the JSON file
        if os.path.exists(self.json_path):
            with open(self.json_path, "r") as file:
                results = json.load(file)
                incorrect_files = [file for file, correct in results.get("flashcards", {}).items() if not correct and file.startswith(os.path.join(self.flashcard_directory, self.selected_folder))]
                
                if not incorrect_files:
                    QMessageBox.information(self, "No Incorrect Answers", "You have no flashcards marked as incorrect in this folder.")
                    return

                # Load the incorrect flashcards
                self.flashcard_files = incorrect_files
                self.open_flashcard_window()
        else:
            QMessageBox.information(self, "No Results Found", "No previous flashcard results found.")

    def get_flashcard_files(self, folder=None):
        while True:
            if not folder:
                folder = QFileDialog.getExistingDirectory(self, "Select Flashcard Folder", self.flashcard_directory)
            
            if not folder:
                QMessageBox.warning(self, "No Folder Selected", "You must select a folder containing flashcard text files.")
                continue  # Prompt again

            # List to hold all text file paths in the selected folder
            flashcard_files = []

            for root, dirs, files in os.walk(folder):
                for file in files:
                    if file.endswith(".txt"):
                        flashcard_files.append(os.path.join(root, file))

            if not flashcard_files:
                QMessageBox.warning(self, "No Flashcards Found", "The selected folder does not contain any flashcard text files. Please select another folder.")
                folder = None  # Reset folder to prompt again
            else:
                return flashcard_files

    def open_flashcard_window(self):
        # Create a new flashcard window
        self.flashcard_window = FlashCardWindow(self.flashcard_files, self.is_random, typing_speed=self.typing_speed, sound_enabled=self.sound_enabled)
        self.flashcard_window.show()
