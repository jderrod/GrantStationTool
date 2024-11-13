from PyQt6.QtCore import QSize
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow, QLineEdit, QVBoxLayout, QHBoxLayout, QLabel

# allows access to command line elements
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # name of window
        self.setWindowTitle("DSALA GrantStation Interface")

        # search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Enter your search query...")


        self.button = QPushButton("Search!")
        self.button.clicked.connect(self.the_button_was_clicked)

        #image
        self.image_label = QLabel()
        pixmap = QPixmap("DSALA_350.png")  # Replace with the path to your image file
        self.image_label.setPixmap(pixmap)
        self.image_label.setScaledContents(True)

        # layout
        layout = QHBoxLayout()
        layout.addWidget(self.search_bar)
        layout.addWidget(self.button)
        layout.addWidget(self.image_label)

        # main widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def the_button_was_clicked(self):
        query = self.search_bar.text()
        print(f"Search query: {query}")

# only need one QApplication call in whole program, sys.argv to allow CLI arguments.
# If we dont end up using CLI arguement, swap too QApplication([]) works too.
app = QApplication(sys.argv)

# Create a Qt widget, which will be our window.
window = MainWindow()
window.show()  # IMPORTANT!!!!! Windows are hidden by default.

# Start the event loop.
app.exec()


# Your application won't reach here until you exit and the event
# loop has stopped.
