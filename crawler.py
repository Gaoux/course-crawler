from bs4 import BeautifulSoup
from collections import Counter
from urllib.parse import urljoin
from queue import Queue
import requests
import json
import csv
import re
import util


# Initial URL
START_URL = "https://educacionvirtual.javeriana.edu.co/nuestros-programas-nuevo"
DOMAIN = "educacionvirtual.javeriana.edu.co"


# Regular expression to identify words
word_pattern = re.compile(r"\b[A-Za-z][A-Za-z0-9_]*(?<![!:.])\b")


def identify_common_words(words: list, threshold: int = 10):
    """Identify common words from the list of words.

    Args:
        words (list): List of words.
        threshold (int): Threshold frequency for a word to be considered common.

    Returns:
        list: List of common words.
    """
    # Count the frequency of each word
    word_count = Counter(words)

    # Identify common words based on threshold frequency
    common_words = [word for word, count in word_count.items() if count >= threshold]

    return common_words


def build_index(index: dict, soup, course_dict: dict):
    """Builds an index mapping words to a list of course IDs.

    Args:
        index (dict): The existing index dictionary.
        soup (BeautifulSoup): The parsed HTML content.
        course_dict (dict): A dictionary containing course IDs mapped to titles.

    Returns:
        dict: The updated index dictionary.
    """

    # Find all course blocks
    course_blocks = soup.find_all("div", class_="card-body")

    # List of common words that do not provide useful information
    common_words = []

    for block in course_blocks:
        # Extract title and descriptions
        course_title_element = block.find("b", class_="card-title")
        if course_title_element:
            course_title = course_title_element.text.strip()
        else:
            course_title = ""

        description_elements = block.find_all("p", class_="card-text")
        if description_elements:
            description = " ".join([p.text.strip() for p in description_elements])
        else:
            description = ""

        # Combine title and description text
        combined_text = course_title + " " + description

        # Find all words in the combined text
        words = word_pattern.findall(combined_text.lower())

        # Identify common words from 'words'
        common_words = identify_common_words(words)

        # Filter out common words
        words = [word for word in words if word not in common_words]

        # Map each word to the course ID
        for word in words:
            if word not in index:
                index[word] = []
            # Add course ID to word
            index[word].append(course_dict.get(course_title, "Not found"))

    return index


def go(n: int, dictionary: str, output: str):
    """Crawl the course catalog to create an index mapping words to course IDs
    and generate a CSV file from the index.

    Args:
        n (int): The number of pages to crawl.
        dictionary (str): The filename of the JSON dictionary containing course IDs.
        output (str): The filename of the output CSV file.
    """
    # Read course ID dictionary from JSON file
    with open(dictionary, "r") as file:
        course_dict = json.load(file)

    index = {}  # Word -> List of course IDs

    visited = set()
    queue = Queue()
    queue.put(START_URL)

    while not queue.empty() and len(visited) < n:
        current_url = queue.get()
        if current_url in visited:
            continue
        visited.add(current_url)
        # HTTP request to url
        request = requests.get(current_url)
        if request.status_code == 200:
            text = request.text
            soup = BeautifulSoup(text, "html5lib")

            for link in soup.find_all("a", href=True):
                full_url = urljoin(current_url, link["href"])
                if full_url not in visited:
                    if util.is_url_ok_to_follow(full_url, DOMAIN):
                        queue.put(full_url)
                    else:
                        # If the URL is not suitable to follow based on the domain criteria,
                        # convert any relative URLs to absolute URLs and enqueue them if possible
                        converted_url = util.convert_if_relative_url(
                            current_url, full_url
                        )
                        if converted_url:
                            queue.put(converted_url)

            index = build_index(index, soup, course_dict)
    # Write index to a CSV file
    with open(output, "w", newline="", encoding="utf-8") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["Word", "Course IDs"])
        for word, ids in index.items():
            csvwriter.writerow([word, ", ".join(map(str, ids))])


go(10, "test.json", "test.csv")
