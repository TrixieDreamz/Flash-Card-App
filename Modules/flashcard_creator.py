import os
from PyQt5.QtWidgets import QWidget, QInputDialog, QFileDialog, QMessageBox, QPlainTextEdit, QVBoxLayout, QDialog, QPushButton, QLabel

class FlashCardCreator(QWidget):
    def __init__(self, flashcard_directory):
        super().__init__()
        self.flashcard_directory = flashcard_directory
        self.selected_folder = None
        self.flashcard_content = {"Topic": "", "Question": "", "Answer": ""}

    def start_flashcard_creation(self):
        # Step 1: Select or Create Folder
        self.select_or_create_folder()

        if self.selected_folder:
            self.create_flashcard_loop()

    def select_or_create_folder(self):
        options = ("Select existing folder", "Create new folder")
        option, ok = QInputDialog.getItem(self, "Flashcard Folder", "Would you like to select an existing folder or create a new one?", options, 0, False)

        if ok and option:
            if option == "Select existing folder":
                self.selected_folder = QFileDialog.getExistingDirectory(self, "Select Folder", self.flashcard_directory)
            elif option == "Create new folder":
                folder_name, ok = QInputDialog.getText(self, "New Folder", "Enter the name for the new folder:")
                if ok and folder_name:
                    self.selected_folder = os.path.join(self.flashcard_directory, folder_name)
                    os.makedirs(self.selected_folder, exist_ok=True)
            
            if not self.selected_folder:
                QMessageBox.warning(self, "No Folder Selected", "You must select or create a folder to proceed.")
                self.select_or_create_folder()

    def create_flashcard_loop(self):
        while True:
            # Step 2: Prompt for Topic, Question, Answer
            if not self.prompt_flashcard_content():
                break  # Exit loop if the user cancels

            # Step 3: Review Flashcard
            if not self.review_flashcard():
                break  # Exit loop if the user cancels

            # Step 4: Save Flashcard
            self.save_flashcard()

            # Step 5: Ask to Continue
            continue_choice = QMessageBox.question(self, "Continue?", "Do you want to create another flashcard?",
                                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

            if continue_choice == QMessageBox.No:
                break

            switch_folder_choice = QMessageBox.question(self, "Switch Folder?", "Do you want to switch folders?",
                                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if switch_folder_choice == QMessageBox.Yes:
                self.select_or_create_folder()

    def prompt_flashcard_content(self):
        # Single-line input for Topic
        topic, ok = QInputDialog.getText(self, "Topic", "Enter the topic of the flashcard:")
        if not ok:
            return False
        self.flashcard_content["Topic"] = topic

        # Multi-line input for Question and Answer using custom dialog
        self.flashcard_content["Question"] = self.multi_line_input_dialog("Question")
        self.flashcard_content["Answer"] = self.multi_line_input_dialog("Answer")

        return True

    def multi_line_input_dialog(self, title):
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        layout = QVBoxLayout(dialog)

        label = QLabel(f"Enter the {title.lower()} of the flashcard:", dialog)
        layout.addWidget(label)

        text_edit = QPlainTextEdit(dialog)
        text_edit.setFixedSize(400, 200)  # Set larger size for the text edit area
        layout.addWidget(text_edit)

        button_box = QWidget(dialog)
        button_layout = QVBoxLayout(button_box)
        ok_button = QPushButton("OK", dialog)
        cancel_button = QPushButton("Cancel", dialog)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addWidget(button_box)

        def on_ok():
            dialog.accept()

        def on_cancel():
            dialog.reject()

        ok_button.clicked.connect(on_ok)
        cancel_button.clicked.connect(on_cancel)

        if dialog.exec_() == QDialog.Accepted:
            return text_edit.toPlainText()
        return ""

    def review_flashcard(self):
        review_text = "\n".join([f"{key}:\n{value}" for key, value in self.flashcard_content.items()])
        choice = QMessageBox.question(self, "Review Flashcard", f"Please review your flashcard:\n\n{review_text}",
                                      QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)
        if choice == QMessageBox.Cancel:
            return False

        # Ask if the user wants to redo any part
        redo_choice, ok = QInputDialog.getItem(self, "Redo Part", "Do you want to redo any part of the flashcard?", 
                                               ("No", "Topic", "Question", "Answer"), 0, False)
        if ok and redo_choice != "No":
            self.prompt_flashcard_content_part(redo_choice)
            return self.review_flashcard()  # Review again after editing
        return True

    def prompt_flashcard_content_part(self, part):
        if part in ["Question", "Answer"]:
            content = self.multi_line_input_dialog(part)
        else:
            content, ok = QInputDialog.getText(self, part, f"Enter the {part.lower()} of the flashcard:")
            if ok:
                self.flashcard_content[part] = content

    def save_flashcard(self):
        # Save the flashcard as a .txt file
        index = len([f for f in os.listdir(self.selected_folder) if f.endswith('.txt')]) + 1
        filename = os.path.join(self.selected_folder, f"{self.flashcard_content['Topic'].replace(' ', '_')}_{index:03d}.txt")

        with open(filename, 'w') as file:
            file.write(f"Topic: {self.flashcard_content['Topic']}\n\n")
            file.write(f"Question:\n{self.flashcard_content['Question']}\n\n")
            file.write(f"Answer:\n{self.flashcard_content['Answer']}\n")

        QMessageBox.information(self, "Flashcard Saved", f"Your flashcard has been saved as {filename}.")
