from PyQt6.QtCore import QSize
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow, QLineEdit, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QCheckBox
from PyQt6.QtGui import QGuiApplication 
import sys
import os
import urllib.parse

# only need one QApplication call in the whole program, sys.argv to allow CLI arguments.
app = QApplication(sys.argv)

class ConsoleOutput(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)  # Make it read-only
        self.setPlaceholderText("Console output will be shown here...")

    def write(self, message):
        self.append(message)  # Append new message to QTextEdit

    def flush(self):
        pass  # Flush does nothing, as we're appending directly

class SearchWindow(QMainWindow):
    def __init__(self, scraper):
        super().__init__()
        self.scraper = scraper
        self.debug_var = False

        # Window name
        self.setWindowTitle("DSALA GrantStation Interface")

        # Resize window to 1/3 of screen size
        screen = QGuiApplication.primaryScreen().availableGeometry()
        width = screen.width() // 2
        height = screen.height() // 2
        self.resize(width, height)
        

        # Image setup
        self.image_label = QLabel()
        image_path = "GrantStationTool/images/DSALA.png"  # Replace with the path to your image file

        if not os.path.exists(image_path):  # Check if the file exists
            print(f"Error: Image file does not exist at {image_path}")
        else:
            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                print("Failed to load image.")
            else:
                print("Image loaded successfully.")
                self.image_label.setPixmap(pixmap)
                self.image_label.setScaledContents(False)

        # Search bar setup
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Enter your search query...")

        # Button setup
        self.search_button = QPushButton("Search!")
        self.search_button.clicked.connect(self.search_button_clicked)

        # Filter button setup
        self.filter_button = QPushButton("Filters")
        self.filter_button.clicked.connect(self.filter_button_clicked)


        # Console output widget
        self.console_output = ConsoleOutput()

        ## Debug Checkbox widget
        self.debug_box = QCheckBox("Debug Mode")
        self.debug_box.toggled.connect(self.debug_mode)

        # Layout for checkbox, search, and filter buttons (stacked horizontally)
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.debug_box)
        button_layout.addWidget(self.search_button)
        button_layout.addWidget(self.filter_button)

        interact_container = QWidget()
        interact_container.setLayout(button_layout)

        # Layout for the image, search bar, checkbox, and button (stacked vertically)
        main_layout = QVBoxLayout()  
        main_layout.addWidget(self.image_label)  
        main_layout.addWidget(self.search_bar)
        main_layout.addWidget(interact_container)

        

        # Main container widget for the top part (image, search bar, button)
        main_container = QWidget()
        main_container.setLayout(main_layout)

        # Layout for the console output (at the bottom)
        console_layout = QVBoxLayout()  # This layout will hold the console output
        console_layout.addWidget(self.console_output)

        # Container for the console output at the bottom
        console_container = QWidget()
        console_container.setLayout(console_layout)

        # Set the central widget for the main window (combining both containers)
        central_layout = QVBoxLayout()
        central_layout.addWidget(main_container)  # Add the top section (image, search bar, button)
        central_layout.addWidget(console_container)  # Add the console output at the bottom

        central_widget = QWidget()
        central_widget.setLayout(central_layout)

        self.setCentralWidget(central_widget)

        # Redirect stdout to our ConsoleOutput widget
        sys.stdout = self.console_output  # Redirect print statements to the QTextEdit


    def filter_button_clicked():
        print("clicked")


    def debug_mode(self):
        # Update the label text based on the checkbox state
        if self.checkbox.isChecked():
            self.debug_var = True
        else:
            self.debug_var = False

    def search_button_clicked(self):
        query = self.search_bar.text().strip()
        if query:
            encoded_term = urllib.parse.quote(query)  # URL encode the search term
            url = f"https://grantstation.com/search/us-federal?keyword={encoded_term}&opp_number=&cfda="
            
            self.search_button.setEnabled(False)  # Disable search button during search
            
            # Simulate callback with the parameters
            self.scraper([url], self.debug_var, self.selected_filter)

            # Close the window after the search is performed
            # self.close()
        else:
            self.status_label.setText("Please enter a search term")

    def update_label(self):
        # Update the label text based on the checkbox state
        if self.checkbox.isChecked():
            self.label.setText("Checkbox is checked")
        else:
            self.label.setText("Checkbox is unchecked")

    def run(self):

        window = SearchWindow(self.scraper)
        window.show()  # IMPORTANT!!!!! Windows are hidden by default.
        app.exec()