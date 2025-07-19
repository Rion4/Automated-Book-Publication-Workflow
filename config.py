import os
from dotenv import load_dotenv
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") 
GEMINI_MODEL = "gemini-1.5-flash"

TARGET_URL = "https://en.wikisource.org/wiki/The_Gates_of_Morning/Book_1/Chapter_1"

CONTENT_SELECTOR = "div.mw-parser-output.ws-page-container"

#ChromaDB Configuration
# Defines the path where the local ChromaDB database will be stored.
# Storing it in a dedicated 'db' directory keeps the project organized.
CHROMA_DB_PATH = "./db"

CHROMA_COLLECTION_NAME = "book_versions"



# These weights are used in our reward function to score
# the quality of the scraped text. They can be tuned to prioritize certain
# quality metrics over others.
REWARD_WEIGHTS = {
    "length": 0.4,      
    "keywords": 0.4,    
    "noise": -0.2       
}

# Keywords to look for in the scraped text.
REWARD_KEYWORDS = ["chapter", "morning", "gates", "book"]

# Words that are considered "noise" and indicate a poor scrape
NOISE_WORDS = ["menu", "search", "login", "portal", "navigation", "edit"]

# The minimum acceptable reward score. If a scrape's score falls below
# this threshold, the system will flag it as potentially low quality.
REWARD_THRESHOLD = 70.0 
