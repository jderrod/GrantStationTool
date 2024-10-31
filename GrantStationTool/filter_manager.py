# filter_manager.py

import json
from datetime import datetime, timedelta  # Change this line
from dataclasses import dataclass, asdict
from typing import List, Optional
import tkinter as tk
from tkinter import ttk, messagebox

@dataclass
class SearchFilter:
    name: str
    keywords: List[str]
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class FilterManager:
    def __init__(self):
        self.filters = self.load_filters()
        
    def load_filters(self):
        try:
            with open('saved_filters.json', 'r') as f:
                data = json.load(f)
                return {name: SearchFilter.from_dict(filter_data) 
                       for name, filter_data in data.items()}
        except FileNotFoundError:
            # Create some default filters
            default_filters = {
                "High Value Opportunities": SearchFilter(
                    name="High Value Opportunities",
                    keywords=["grant", "funding"],
                    min_amount=500000,
                    max_amount=None
                ),
                "Closing Soon": SearchFilter(
                    name="Closing Soon",
                    keywords=[],
                    end_date=(datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
                ),
                "New Opportunities": SearchFilter(
                    name="New Opportunities",
                    keywords=[],
                    start_date=datetime.now().strftime("%Y-%m-%d")
                )
            }
            self.save_filters(default_filters)
            return default_filters
            
    def save_filters(self, filters=None):
        if filters is None:
            filters = self.filters
        with open('saved_filters.json', 'w') as f:
            json.dump({name: filter_obj.to_dict() 
                      for name, filter_obj in filters.items()}, f)
            
    def add_filter(self, filter_obj: SearchFilter):
        self.filters[filter_obj.name] = filter_obj
        self.save_filters()
        
    def remove_filter(self, filter_name: str):
        if filter_name in self.filters:
            del self.filters[filter_name]
            self.save_filters()
            
    def apply_filter(self, filter_obj: SearchFilter, opportunities: List[dict]) -> List[dict]:
        filtered_results = []
        
        for opp in opportunities:
            matches = True
            
            # Check keywords in title and description
            if filter_obj.keywords:
                text_to_search = (
                    f"{opp.get('title', '')} {opp.get('description', '')}".lower()
                )
                if not all(kw.lower() in text_to_search for kw in filter_obj.keywords):
                    matches = False
                    
            # Check amount range if specified in the opportunity
            if 'amount' in opp:
                try:
                    amount = float(opp['amount'])
                    if filter_obj.min_amount and amount < filter_obj.min_amount:
                        matches = False
                    if filter_obj.max_amount and amount > filter_obj.max_amount:
                        matches = False
                except (ValueError, TypeError):
                    pass
                
            # Check dates
            try:
                if filter_obj.start_date and opp.get('post_date'):
                    post_date = datetime.strptime(opp['post_date'], "%m/%d/%Y")
                    filter_start = datetime.strptime(filter_obj.start_date, "%Y-%m-%d")
                    if post_date < filter_start:
                        matches = False
                        
                if filter_obj.end_date and opp.get('close_date'):
                    close_date = datetime.strptime(opp['close_date'], "%m/%d/%Y")
                    filter_end = datetime.strptime(filter_obj.end_date, "%Y-%m-%d")
                    if close_date > filter_end:
                        matches = False
            except ValueError:
                # Handle date parsing errors
                pass
                
            if matches:
                filtered_results.append(opp)
                
        return filtered_results

class FilterWindow:
    def __init__(self, parent=None, callback=None):
        self.filter_manager = FilterManager()
        self.callback = callback
        
        # Create new window
        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        self.window.title("Search Filters")
        self.window.geometry("800x600")
        
        self.setup_ui()
        
    def setup_ui(self):
        # Create notebook for tabs
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Preset Filters Tab
        preset_frame = ttk.Frame(notebook)
        notebook.add(preset_frame, text="Preset Filters")
        self.setup_preset_filters(preset_frame)
        
        # Create Filter Tab
        create_frame = ttk.Frame(notebook)
        notebook.add(create_frame, text="Create Filter")
        self.setup_create_filter(create_frame)
        
    def setup_preset_filters(self, parent):
        # List of preset filters
        self.preset_list = tk.Listbox(parent, width=50, height=10)
        self.preset_list.pack(pady=10)
        
        # Load preset filters
        for filter_name in self.filter_manager.filters:
            self.preset_list.insert(tk.END, filter_name)
            
        # Buttons frame
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Select Filter", 
                  command=self.select_preset_filter).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Delete Filter", 
                  command=self.delete_preset_filter).pack(side='left', padx=5)
                  
    def setup_create_filter(self, parent):
        # Filter name
        ttk.Label(parent, text="Filter Name:").pack(pady=5)
        self.name_entry = ttk.Entry(parent, width=50)
        self.name_entry.pack(pady=5)
        
        # Keywords
        ttk.Label(parent, text="Keywords (comma-separated):").pack(pady=5)
        self.keywords_entry = ttk.Entry(parent, width=50)
        self.keywords_entry.pack(pady=5)
        
        # Amount range
        amount_frame = ttk.Frame(parent)
        amount_frame.pack(pady=10)
        
        ttk.Label(amount_frame, text="Min Amount: $").pack(side='left')
        self.min_amount_entry = ttk.Entry(amount_frame, width=15)
        self.min_amount_entry.pack(side='left', padx=5)
        
        ttk.Label(amount_frame, text="Max Amount: $").pack(side='left')
        self.max_amount_entry = ttk.Entry(amount_frame, width=15)
        self.max_amount_entry.pack(side='left', padx=5)
        
        # Date range
        date_frame = ttk.Frame(parent)
        date_frame.pack(pady=10)
        
        ttk.Label(date_frame, text="Start Date:").pack(side='left')
        self.start_date_entry = ttk.Entry(date_frame, width=15)
        self.start_date_entry.pack(side='left', padx=5)
        
        ttk.Label(date_frame, text="End Date:").pack(side='left')
        self.end_date_entry = ttk.Entry(date_frame, width=15)
        self.end_date_entry.pack(side='left', padx=5)
        
        ttk.Label(parent, text="Date format: YYYY-MM-DD").pack()
        
        # Save button
        ttk.Button(parent, text="Save Filter", 
                  command=self.save_new_filter).pack(pady=20)
                  
    def save_new_filter(self):
        try:
            name = self.name_entry.get().strip()
            if not name:
                raise ValueError("Filter name is required")
                
            keywords = [k.strip() for k in self.keywords_entry.get().split(',') if k.strip()]
            
            # Parse amounts
            min_amount = None
            if self.min_amount_entry.get().strip():
                min_amount = float(self.min_amount_entry.get())
                
            max_amount = None
            if self.max_amount_entry.get().strip():
                max_amount = float(self.max_amount_entry.get())
                
            # Create new filter
            new_filter = SearchFilter(
                name=name,
                keywords=keywords,
                min_amount=min_amount,
                max_amount=max_amount,
                start_date=self.start_date_entry.get().strip() or None,
                end_date=self.end_date_entry.get().strip() or None
            )
            
            self.filter_manager.add_filter(new_filter)
            self.preset_list.insert(tk.END, name)
            messagebox.showinfo("Success", "Filter saved successfully!")
            
            # Clear entries
            self.name_entry.delete(0, tk.END)
            self.keywords_entry.delete(0, tk.END)
            self.min_amount_entry.delete(0, tk.END)
            self.max_amount_entry.delete(0, tk.END)
            self.start_date_entry.delete(0, tk.END)
            self.end_date_entry.delete(0, tk.END)
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save filter: {str(e)}")
            
    def select_preset_filter(self):
        selection = self.preset_list.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a filter")
            return
            
        filter_name = self.preset_list.get(selection[0])
        selected_filter = self.filter_manager.filters[filter_name]
        
        if self.callback:
            self.callback(selected_filter)
            self.window.destroy()
            
    def delete_preset_filter(self):
        selection = self.preset_list.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a filter")
            return
            
        filter_name = self.preset_list.get(selection[0])
        if messagebox.askyesno("Confirm Delete", 
                             f"Are you sure you want to delete '{filter_name}'?"):
            self.filter_manager.remove_filter(filter_name)
            self.preset_list.delete(selection[0])
            
    def run(self):
        self.window.mainloop()