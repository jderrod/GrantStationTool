# results_window.py

import tkinter as tk
from tkinter import ttk

class ResultsWindow:
    def __init__(self, results_text, debug_text="", debug_mode=False, on_new_search=None, on_save_results=None):
        self.results_text = results_text
        self.debug_text = debug_text
        self.debug_mode = debug_mode
        self.on_new_search = on_new_search
        self.on_save_results = on_save_results

    def display(self):
        """Display results in a tkinter window"""
        self.window = tk.Tk()
        self.window.title("GrantStation Search Results")
        
        # Configure the window
        self.window.geometry("1000x800")
        
        # Create main frame with padding
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Add notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Results tab
        results_frame = ttk.Frame(notebook)
        notebook.add(results_frame, text="Results")

        # Debug tab (if debug mode is on)
        if self.debug_mode:
            debug_frame = ttk.Frame(notebook)
            notebook.add(debug_frame, text="Debug Info")
            
            debug_text = tk.Text(debug_frame, wrap="word")
            debug_scrollbar = ttk.Scrollbar(debug_frame)
            
            debug_scrollbar.pack(side="right", fill="y")
            debug_text.pack(side="left", expand=True, fill="both")
            
            debug_text.insert("1.0", self.debug_text)
            debug_scrollbar.config(command=debug_text.yview)
            debug_text.config(yscrollcommand=debug_scrollbar.set)

        # Results text widget
        results_text = tk.Text(results_frame, wrap="word")
        results_scrollbar = ttk.Scrollbar(results_frame)
        
        results_scrollbar.pack(side="right", fill="y")
        results_text.pack(side="left", expand=True, fill="both")
        
        results_text.insert("1.0", self.results_text)
        results_scrollbar.config(command=results_text.yview)
        results_text.config(yscrollcommand=results_scrollbar.set)

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        save_results_button = ttk.Button(
            button_frame, 
            text="Save Results", 
            command=self.on_save_results
        )
        save_results_button.pack(side="left", padx=5)
        
        new_search_button = ttk.Button(
            button_frame,
            text="New Search",
            command=lambda: self.handle_new_search()
        )
        new_search_button.pack(side="left", padx=5)
        
        self.window.mainloop()

    def handle_new_search(self):
        self.window.destroy()
        if self.on_new_search:
            self.on_new_search()