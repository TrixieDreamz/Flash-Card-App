import sys
from PyQt5.QtWidgets import QApplication
from Modules.flashcard_app import FlashCardApp

if __name__ == '__main__':
    app = QApplication(sys.argv)
    flashcard = FlashCardApp()
    flashcard.show()
    sys.exit(app.exec_())
