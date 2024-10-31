# results_window.py

import tkinter as tk
from tkinter import ttk

class ResultsWindow:
    def __init__(self, filtered_results, all_results, debug_text="", debug_mode=False, 
                 on_new_search=None, on_save_results=None):
        self.filtered_results = filtered_results
        self.all_results = all_results
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

        # Filtered Results tab
        filtered_frame = ttk.Frame(notebook)
        notebook.add(filtered_frame, text="Filtered Results")
        self.setup_results_tab(filtered_frame, self.filtered_results, is_filtered=True)

        # All Results tab
        all_results_frame = ttk.Frame(notebook)
        notebook.add(all_results_frame, text="All Results")
        self.setup_results_tab(all_results_frame, self.all_results, is_filtered=False)

        # Debug tab (if debug mode is on)
        if self.debug_mode:
            debug_frame = ttk.Frame(notebook)
            notebook.add(debug_frame, text="Debug Info")
            self.setup_debug_tab(debug_frame)

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

    def setup_results_tab(self, parent, results_text, is_filtered=False):
        """Setup a results tab with text widget and scrollbar"""
        # Create main container
        main_container = ttk.Frame(parent)
        main_container.pack(fill="both", expand=True)

        # Add summary at top if this is the filtered results
        if is_filtered:
            summary_frame = ttk.Frame(main_container)
            summary_frame.pack(fill="x", pady=(5, 10), padx=10)
            
            filtered_count = results_text.count("Opportunity Title:")
            total_count = self.all_results.count("Opportunity Title:")
            
            summary_text = (f"Found {filtered_count} matching opportunities "
                          f"out of {total_count} total opportunities")
            ttk.Label(
                summary_frame, 
                text=summary_text,
                font=('Helvetica', 10, 'bold')
            ).pack(anchor='w')

        # Create text widget with scrollbar
        text_frame = ttk.Frame(main_container)
        text_frame.pack(expand=True, fill="both", padx=10)
        
        text_widget = tk.Text(text_frame, wrap="word")
        scrollbar = ttk.Scrollbar(text_frame)
        
        scrollbar.pack(side="right", fill="y")
        text_widget.pack(side="left", expand=True, fill="both")
        
        # Configure tags for formatting
        text_widget.tag_configure('header', font=('Helvetica', 12, 'bold'))
        text_widget.tag_configure('subheader', font=('Helvetica', 10, 'bold'))
        text_widget.tag_configure('normal', font=('Helvetica', 10))
        text_widget.tag_configure('separator', font=('Helvetica', 10), spacing3=20)
        
        text_widget.insert("1.0", results_text)
        scrollbar.config(command=text_widget.yview)
        text_widget.config(yscrollcommand=scrollbar.set)
        
        # Make text widget read-only
        text_widget.configure(state='disabled')

    def setup_debug_tab(self, parent):
        """Setup the debug tab"""
        text_widget = tk.Text(parent, wrap="word")
        scrollbar = ttk.Scrollbar(parent)
        
        scrollbar.pack(side="right", fill="y")
        text_widget.pack(side="left", expand=True, fill="both")
        
        text_widget.insert("1.0", self.debug_text)
        scrollbar.config(command=text_widget.yview)
        text_widget.config(yscrollcommand=scrollbar.set)
        
        # Make text widget read-only
        text_widget.configure(state='disabled')

    def handle_new_search(self):
        self.window.destroy()
        if self.on_new_search:
            self.on_new_search()