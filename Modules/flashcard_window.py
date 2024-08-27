import os
import random
import json
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QCheckBox, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

class FlashCardWindow(QWidget):
    def __init__(self, flashcard_files, is_random, json_path="flashcard_results.json"):
        super().__init__()
        self.flashcard_files = flashcard_files
        self.is_random = is_random
        self.current_index = 0
        self.current_file = None
        self.correct_answers = 0
        self.incorrect_answers = 0
        self.json_path = json_path

        # Load existing results from the JSON file or create a new one
        self.load_or_create_json()

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

        # Checkboxes for marking right or wrong answers
        checkbox_layout = QHBoxLayout()
        self.right_checkbox = QCheckBox("Right", self)
        self.wrong_checkbox = QCheckBox("Wrong", self)
        self.right_checkbox.stateChanged.connect(self.mark_correct)
        self.wrong_checkbox.stateChanged.connect(self.mark_incorrect)
        checkbox_layout.addWidget(self.right_checkbox)
        checkbox_layout.addWidget(self.wrong_checkbox)
        self.layout.addLayout(checkbox_layout)

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

    def load_or_create_json(self):
        # Load existing results from the JSON file or create a new one
        if os.path.exists(self.json_path):
            with open(self.json_path, "r") as file:
                self.results = json.load(file)
        else:
            self.results = {"flashcards": {}}

    def save_json(self):
        # Save the current results to the JSON file
        with open(self.json_path, "w") as file:
            json.dump(self.results, file, indent=4)

    def load_flashcard(self, filepath):
        try:
            with open(filepath, "r") as file:
                lines = file.readlines()

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
        self.right_checkbox.setChecked(False)
        self.wrong_checkbox.setChecked(False)

    def show_answer(self):
        self.text_label.setText(self.answer)
        self.showing_answer = True

    def flip_card(self):
        if self.showing_answer:
            self.show_question()
        else:
            self.show_answer()

    def mark_correct(self, state):
        if state == Qt.Checked:
            self.wrong_checkbox.setChecked(False)
            self.results["flashcards"][self.current_file] = True
            self.save_json()

    def mark_incorrect(self, state):
        if state == Qt.Checked:
            self.right_checkbox.setChecked(False)
            self.results["flashcards"][self.current_file] = False
            self.save_json()

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
