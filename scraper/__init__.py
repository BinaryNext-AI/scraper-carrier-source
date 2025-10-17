# This file makes the 'scraper' directory a Python package
# It allows importing modules from this directory using 'from scraper import X' syntax

from scraper.scraper import scrape_company_data, main

__all__ = ['scrape_company_data', 'main'] 