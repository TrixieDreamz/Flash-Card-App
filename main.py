import sys
import os
import random
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

class FlashCardApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Flashcard")
        self.setGeometry(100, 100, 800, 600)  # Increase the window size for better visibility

        # Main layout
        self.layout = QVBoxLayout()

        # Label to display the flashcard background image
        self.image_label = QLabel(self)
        self.pixmap = QPixmap(r"C:\Users\User\Desktop\Projects\Flash-Card-App\images\FC.jpg")  # Path to your image
        self.image_label.setPixmap(self.pixmap)
        self.image_label.setScaledContents(True)
        self.layout.addWidget(self.image_label)

        # Label to display question/answer on top of the image
        self.text_label = QLabel(self.image_label)
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setStyleSheet("font-size: 36px; color: black;")  # Adjusted font size and color
        self.text_label.setGeometry(0, 0, self.width(), self.height() - 50)  # Adjusted to take the full image space

        # Button to flip the flashcard
        self.flip_button = QPushButton("Flip Card", self)
        self.flip_button.clicked.connect(self.flip_card)
        self.layout.addWidget(self.flip_button)

        # Set the layout
        self.setLayout(self.layout)

        # Get a random flashcard file from the main folder
        base_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current script
        flashcard_folder = os.path.join(base_dir, "Flash Card")
        random_file = self.get_random_flashcard(flashcard_folder)

        # Load the question and answer from the randomly selected file
        self.load_flashcard(random_file)

        # Show the question initially
        self.show_question()

    def get_random_flashcard(self, folder):
        # List to hold all text file paths
        flashcard_files = []

        # Walk through the directory structure
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.endswith(".txt"):  # Only consider text files
                    flashcard_files.append(os.path.join(root, file))

        # Check if any flashcard files were found
        if not flashcard_files:
            raise FileNotFoundError("No flashcard text files found in the specified directory.")

        # Return a randomly selected flashcard file
        return random.choice(flashcard_files)

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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    flashcard = FlashCardApp()
    flashcard.show()
    sys.exit(app.exec_())
