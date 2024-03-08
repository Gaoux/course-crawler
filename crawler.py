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
word_pattern = re.compile(r"\b[A-Za-zÁ-Úá-ú][A-Za-z0-9Á-Úá-ú_]+(?<![!:.])\b")


def identify_common_words(course_blocks, threshold: int = 10):
    """Identify common words from the list of words.

    Args:
        course_blocks (list): List of BeautifulSoup elements representing course blocks.
        threshold (int): Threshold frequency for a word to be considered common.

    Returns:
        list: List of common words.
    """
    # Count the frequency of each word

    COMMON_WORDS = {
        "hora",
        "horas",
        "duración",
        "precio",
        "de",
        "la",
        "al",
        "el",
        "en",
        "su",
        "con",
    }

    combined_text = ""
    for block in course_blocks:
        # Extract course title
        course_title_element = block.find("b", class_="card-title")
        if course_title_element:
            course_title = course_title_element.text.strip()
        else:
            course_title = ""

        # Extract course description
        description_elements = block.find_all("p", class_="card-text")
        if description_elements:
            description = " ".join([p.text.strip() for p in description_elements])
        else:
            description = ""

        # Combine title and description text
        combined_text += course_title + " " + description

    # Find all words in the combined text
    words = word_pattern.findall(combined_text.lower())
    word_count = Counter(words)

    # Identify common words based on threshold frequency
    common_words = [word for word, count in word_count.items() if count >= threshold]

    # Add the preset common words
    common_words += COMMON_WORDS
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

    # Identify common words from 'words'
    common_words = identify_common_words(course_blocks)

    # Iterate over each course block
    for block in course_blocks:
        # Implementing find_sequence to process sub-sequences
        sequences = util.find_sequence(block)

        # Extract title
        course_title = util.extract_course_title(block)
        if course_title == "":
            continue

        # Initialize combined text
        combined_text = course_title
        # Extract description if there are no sequences
        if len(sequences) == 0:
            description = util.extract_course_description(block)
            combined_text += " " + description

        # Find all words in the combined text
        words = word_pattern.findall(combined_text.lower())
        # Filter out common words
        words = [word for word in words if word not in common_words]

        # Get course id from the course dictionary file
        course_id = course_dict.get(course_title, "ID not found")
        if course_id != "ID not found":
            if course_id not in index:
                index[course_id] = []

            # Map each word to the course ID
            for word in words:
                if word not in index[course_id]:
                    index[course_id].append(word)

        # Iterate over each subsequences in the block
        for sequence in sequences:
            # Extract title of subsequence
            course_title = util.extract_course_title(sequence)
            if course_title == "":
                continue
            else:
                course_id = course_dict.get(course_title, "ID not found")
                if course_id == "ID not found":
                    continue
                if course_id not in index:
                    index[course_id] = []
            # Extract description of subsequence
            description = util.extract_course_description(sequence)
            if description == "":
                continue

            sequence_words = word_pattern.findall(description.lower())
            for word in sequence_words:
                if word not in index[course_id]:
                    index[course_id].append(word)
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

    index = {}  # Course ID -> Words

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
        csvwriter = csv.writer(csvfile, delimiter="|")
        csvwriter.writerow(["Course ID", "Word"])
        for id, words in index.items():
            for word in words:
                csvwriter.writerow([id, word])


go(5, "test.json", "test.csv")
#### FALTA ESTO ............................
# Una función útil, llamada util.find_sequence(tag), para trabajar con subsecuencias. Esta función
# toma una etiqueta bs4 y comprueba las subsecuencias asociadas. Si existen subsecuencias, la
# función devuelve una lista de los objetos de etiqueta div para la subsecuencia; de lo contrario,
# devuelve una lista vacía.

# Salida
