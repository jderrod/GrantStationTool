# main.py

from search_interface import SearchInterface
from scraper import GrantStationScraper
from results_window import ResultsWindow
from config import USERNAME, PASSWORD

def start_new_search():
    """Initialize a new search session"""
    scraper = GrantStationScraper(USERNAME, PASSWORD)
    search_ui = SearchInterface(scraper.run)
    search_ui.run()

if __name__ == "__main__":
    print("Starting GrantStation search tool...")
    start_new_search()