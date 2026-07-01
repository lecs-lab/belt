import json
import os
import re
import unicodedata
import urllib.request

# The GitHub repository where the course corpora are stored
CORPUS_REPO = "lecs-lab/belt"


def download_corpus(corpus_name: str) -> str:
    """Downloads one of the course corpora from GitHub into a local folder.

    For example, download_corpus("usp") creates a folder called
    corpora/usp with all of the Uspanteko text files in it.
    Returns the path to the new folder, so you can pass it
    straight to load_raw_text().
    """
    local_directory = os.path.join("corpora", corpus_name)
    os.makedirs(local_directory, exist_ok=True)

    # Ask the GitHub API for the list of files in the corpus folder
    api_url = f"https://api.github.com/repos/{CORPUS_REPO}/contents/corpora/{corpus_name}"
    with urllib.request.urlopen(api_url) as response:
        files = json.load(response)

    # Download each text file into the local folder
    for file_info in files:
        if file_info["name"].endswith(".txt"):
            local_path = os.path.join(local_directory, file_info["name"])
            urllib.request.urlretrieve(file_info["download_url"], local_path)

    print(f"Downloaded {corpus_name} corpus to {local_directory}")
    return local_directory


def strip_accents(text: str) -> str:
    """Removes accents from text."""
    return ''.join(c for c in unicodedata.normalize('NFD', text)
                  if unicodedata.category(c) != 'Mn')


def load_raw_text(corpus_directory: str, file_names=None) -> str:
    """Loads all the text files in a directory into one large string"""
    corpus = ""
    
    for file_name in os.listdir(corpus_directory):
        # Read the file as a string
        file_path = os.path.join(corpus_directory, file_name)
        if os.path.isdir(file_path):
            continue
            
        #  Make sure we only read text files
        if ".txt" not in file_name:
            continue
            
        with open(file_path, 'r') as file:
            file_contents = file.read()
            corpus += (file_contents + "\n")
    return corpus


word_regex = r"[\w|\']+"
def tokenize(text):
    return re.findall(word_regex, text)


def preprocess(text):
    """Tokenizes and processes text which is already separated by spaces into words. Designed for English punctuation."""
    text = strip_accents(text)
    text = text.lower()

    tokens = text.split(" ")

    tokens_filtered = []
    for token in tokens:
        # Skip any tokens with special characters
        if re.match(r"[\w|\']+|[\.|\,|\?|\!]", token):
            tokens_filtered.append(token)
    return tokens_filtered


def pad(text: list, num_padding: int):
    """Pads the given text, as a list of strings, with <s> characters between sentences."""
    padded_text = []
    
    # Add initial padding to the first sentence
    for _ in range(num_padding):
        padded_text.append("<s>")
    
    for word in text:
        padded_text.append(word)

        # Every time we see an end punctuation mark, add <s> tokens before it
        # REPLACE IF YOUR LANGUAGE USES DIFFERENT END PUNCTUATION
        if word in [".", "?", "!"]:
            for _ in range(num_padding):
                padded_text.append("<s>")
        
        
    return padded_text
