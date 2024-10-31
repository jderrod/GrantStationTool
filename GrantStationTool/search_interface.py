# search_interface.py

import tkinter as tk
from tkinter import ttk
import urllib.parse

class SearchInterface:
    def __init__(self, callback):
        self.callback = callback
        self.root = tk.Tk()
        self.root.title("GrantStation Search")
        self.root.geometry("600x400")
        self.setup_ui()

    def setup_ui(self):
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(
            main_frame, 
            text="GrantStation Search Tool", 
            font=('Helvetica', 16, 'bold')
        )
        title_label.pack(pady=20)

        # Search frame
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=20)

        # Search label
        search_label = ttk.Label(
            search_frame, 
            text="Enter search keyword or phrase:",
            font=('Helvetica', 10)
        )
        search_label.pack(pady=(0, 5))

        # Search entry
        self.search_entry = ttk.Entry(search_frame, width=50)
        self.search_entry.pack(pady=5)
        
        # Add debug checkbox
        self.debug_var = tk.BooleanVar()
        debug_checkbox = ttk.Checkbutton(
            search_frame,
            text="Show Debug Information",
            variable=self.debug_var
        )
        debug_checkbox.pack(pady=5)
        
        # Bind Enter key to search function
        self.search_entry.bind('<Return>', lambda e: self.perform_search())

        # Search button
        search_button = ttk.Button(
            search_frame,
            text="Search",
            command=self.perform_search
        )
        search_button.pack(pady=10)

        # Status label
        self.status_label = ttk.Label(
            main_frame,
            text="",
            font=('Helvetica', 9, 'italic')
        )
        self.status_label.pack(pady=10)

    def perform_search(self):
        search_term = self.search_entry.get().strip()
        if search_term:
            encoded_term = urllib.parse.quote(search_term)
            url = f"https://grantstation.com/search/us-federal?keyword={encoded_term}&opp_number=&cfda="
            
            self.status_label.config(text="Starting search...")
            self.root.update()
            
            # Pass both URL and debug flag to callback
            self.callback([url], self.debug_var.get())
            self.root.destroy()
        else:
            self.status_label.config(text="Please enter a search term")

    def run(self):
        self.root.mainloop()