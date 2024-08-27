import sys
import os
import random
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QRadioButton, QButtonGroup, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

class FlashCardApp(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_folder = None
        self.is_random = True
        self.current_index = 0
        self.flashcard_files = []
        self.init_start_menu()

    def init_start_menu(self):
        self.setWindowTitle("Flashcard - Start Menu")
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()

        # Folder selection
        self.folder_combo = QComboBox(self)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        flashcard_folder = os.path.join(base_dir, "Flash Card")
        self.load_folders(flashcard_folder)
        layout.addWidget(self.folder_combo)

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

        # Start button
        self.start_button = QPushButton("Start", self)
        self.start_button.clicked.connect(self.start_flashcards)
        layout.addWidget(self.start_button)

        self.setLayout(layout)

    def load_folders(self, flashcard_folder):
        # Load available folders into the combo box
        for root, dirs, files in os.walk(flashcard_folder):
            for dir_name in dirs:
                self.folder_combo.addItem(dir_name)
            break  # Only consider the first level of directories

    def start_flashcards(self):
        # Get the selected folder and mode
        self.selected_folder = self.folder_combo.currentText()
        self.is_random = self.random_radio.isChecked()

        # Prepare the flashcard list based on the selected folder
        base_dir = os.path.dirname(os.path.abspath(__file__))
        flashcard_folder = os.path.join(base_dir, "Flash Card", self.selected_folder)
        self.flashcard_files = self.get_flashcard_files(flashcard_folder)

        # Open the flashcard window
        self.open_flashcard_window()

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

class FlashCardWindow(QWidget):
    def __init__(self, flashcard_files, is_random):
        super().__init__()
        self.flashcard_files = flashcard_files
        self.is_random = is_random
        self.current_index = 0
        self.current_file = None

        if self.is_random:
            self.current_file = random.choice(self.flashcard_files)
        else:
            self.current_file = self.flashcard_files[self.current_index]

        self.initUI()

    def initUI(self):
        # Set the window title with the file name
        self.setWindowTitle(f"Flashcard - {os.path.basename(self.current_file)}")
        self.setGeometry(100, 100, 800, 600)

        self.layout = QVBoxLayout()

        # Label to display the flashcard background image
        self.image_label = QLabel(self)
        self.pixmap = QPixmap(r"C:\Users\User\Desktop\Projects\Flash-Card-App\images\FC.jpg")
        self.image_label.setPixmap(self.pixmap)
        self.image_label.setScaledContents(True)
        self.layout.addWidget(self.image_label)

        # Label to display question/answer on top of the image
        self.text_label = QLabel(self.image_label)
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setStyleSheet("font-size: 36px; color: black;")
        self.text_label.setGeometry(0, 0, self.width(), self.height() - 50)

        # Button to flip the flashcard
        self.flip_button = QPushButton("Flip Card", self)
        self.flip_button.clicked.connect(self.flip_card)
        self.layout.addWidget(self.flip_button)

        # Button to go to the next flashcard
        self.next_button = QPushButton("Next Card", self)
        self.next_button.clicked.connect(self.next_flashcard)
        self.layout.addWidget(self.next_button)

        self.setLayout(self.layout)

        # Load the question and answer from the selected file
        self.load_flashcard(self.current_file)

        # Show the question initially
        self.show_question()

    def load_flashcard(self, filepath):
        try:
            with open(filepath, "r") as file:
                lines = file.readlines()

                # Debug: Print the lines read from the file
                print("File content:", lines)

                # Find the indices of "Question:" and "Answer:"
                question_index = None
                answer_index = None

                for i, line in enumerate(lines):
                    if "Question:" in line:
                        question_index = i
                    elif "Answer:" in line:
                        answer_index = i

                if question_index is None or answer_index is None:
                    raise ValueError("File does not contain the required 'Question:' and 'Answer:' headers.")

                # Extract the question and answer sections
                self.question = "".join(lines[question_index + 1:answer_index]).strip()
                self.answer = "".join(lines[answer_index + 1:]).strip()

                self.showing_answer = False

        except ValueError as e:
            print(f"ValueError: {e}")
            print("Please ensure the flashcard file contains the 'Question:' and 'Answer:' headers correctly.")
            self.question = "Error loading question."
            self.answer = "Error loading answer."
        except Exception as e:
            print(f"An error occurred: {e}")
            self.question = "Error loading question."
            self.answer = "Error loading answer."

    def show_question(self):
        self.text_label.setText(self.question)
        self.showing_answer = False

    def show_answer(self):
        self.text_label.setText(self.answer)
        self.showing_answer = True

    def flip_card(self):
        if self.showing_answer:
            self.show_question()
        else:
            self.show_answer()

    def next_flashcard(self):
        if self.is_random:
            self.current_file = random.choice(self.flashcard_files)
        else:
            self.current_index += 1
            if self.current_index >= len(self.flashcard_files):
                self.current_index = 0  # Loop back to the start
            self.current_file = self.flashcard_files[self.current_index]

        # Update window title with new file name
        self.setWindowTitle(f"Flashcard - {os.path.basename(self.current_file)}")

        # Load the new flashcard
        self.load_flashcard(self.current_file)

        # Show the question initially
        self.show_question()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    flashcard = FlashCardApp()
    flashcard.show()
    sys.exit(app.exec_())
