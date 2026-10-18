import os
import unittest
from src.scraper import fetch_url_cached

class TestScraper(unittest.TestCase):
    def test_cache_mechanism(self):
        cache_dir = "/Users/steve/Downloads/Trails_Walkthrough_PDFs/data/cache"
        test_url = "https://trails-game.com/data/terminology-translations/"
        content = fetch_url_cached(test_url, "test_cache.html")
        self.assertTrue(len(content) > 100)
        self.assertTrue(os.path.exists(os.path.join(cache_dir, "test_cache.html")))

if __name__ == '__main__':
    unittest.main()
