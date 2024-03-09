"""Course Catalog Indexing System.urls_to_visit

This module is designed to crawl a specified website, extract information about courses,
and build an index mapping words to course IDs based on the course titles and descriptions.
The index is then saved to a CSV file. This system is specifically tailored for the course
catalog of the Javeriana University's virtual education programs but can be adapted for similar
websites.

Typical usage example:

  # Define the number of pages to crawl, the dictionary JSON file, and the output CSV file name.
  num_pages_to_crawl = 5
  dictionary_file = "course_dictionary.json"
  output_file = "course_index.csv"
  
  # Run the indexing process.
  go(num_pages_to_crawl, dictionary_file, output_file)
"""

from bs4 import BeautifulSoup
from collections import Counter
from urllib.parse import urljoin
from queue import Queue
import requests
import json
import csv
import re
import util as util


START_URL = "https://educacionvirtual.javeriana.edu.co/nuestros-programas-nuevo"
DOMAIN = "educacionvirtual.javeriana.edu.co"


word_pattern = re.compile(r"\b[A-Za-zÁ-Úá-ú][A-Za-z0-9Á-Úá-ú_]+(?<![!:.])\b")


def identify_common_words(course_blocks, threshold: int = 10):
    """Identify common words from the list of words.

    Args:
        course_blocks (list): List of BeautifulSoup elements representing course blocks.
        threshold (int): Threshold frequency for a word to be considered common.

    Returns:
        list: List of common words.
    """

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
    for card in course_blocks:

        course_title_element = card.find("b", class_="card-title")
        if course_title_element:
            course_title = course_title_element.text.strip()
        else:
            course_title = ""

        description_elements = card.find_all("p", class_="card-text")
        if description_elements:
            description = " ".join([p.text.strip() for p in description_elements])
        else:
            description = ""

        combined_text += course_title + " " + description

    words = word_pattern.findall(combined_text.lower())
    word_count = Counter(words)

    common_words = [word for word, count in word_count.items() if count >= threshold]

    common_words += COMMON_WORDS
    return common_words


def build_index(index: dict, course_urls: dict, request, course_dict: dict):
    """Builds an index mapping words to a list of course IDs.

    Args:
        index (dict): The existing index dictionary.
        soup (BeautifulSoup): The parsed HTML content.
        course_dict (dict): A dictionary containing course IDs mapped to titles.

    Returns:
        dict: The updated index dictionary.
    """

    soup = BeautifulSoup(request.text, "html5lib")
    course_cards = soup.find_all("div", class_="card-body")

    common_words = identify_common_words(course_cards)

    for card in course_cards:

        sequences = util.find_sequence(card)

        course_title = util.extract_course_title(card)
        if course_title == "":
            continue

        combined_text = course_title

        if len(sequences) == 0:
            description = util.extract_course_description(card)
            combined_text += " " + description

        words = word_pattern.findall(combined_text.lower())

        words = [word for word in words if word not in common_words]

        course_id = course_dict.get(course_title, "ID not found")
        if course_id != "ID not found":
            if course_id not in course_urls:
                current_url = request.url
                card_a_element = card.find("a", href=True)
                course_urls[course_id] = urljoin(current_url, card_a_element["href"])
            if course_id not in index:
                index[course_id] = []

            for word in words:
                if word not in index[course_id]:
                    index[course_id].append(word)

        for sequence in sequences:
            course_title = util.extract_course_title(sequence)
            if course_title == "":
                continue
            else:
                course_id = course_dict.get(course_title, "ID not found")
                if course_id == "ID not found":
                    continue
                if course_id not in index:
                    index[course_id] = []

            description = util.extract_course_description(sequence)
            if description == "":
                continue

            sequence_words = word_pattern.findall(description.lower())
            for word in sequence_words:
                if word not in index[course_id]:
                    index[course_id].append(word)
    return index, course_urls


def go(n: int, dictionary: str, output: str):
    """Crawl the course catalog to create an index mapping courseIDs to words and an
    course_urls mapping to courseIDs to URL. Then generates a CSV file from the
    index and a CSV file from the course_urls.

    Args:
        n (int): The number of pages to crawl.
        dictionary (str): The filename of the JSON dictionary containing course IDs.
        output (str): The filename of the output CSV file.
    """

    with open(dictionary, "r") as file:
        course_dict = json.load(file)

    index = {}
    course_urls = {}

    visited_urls = set()
    urls_to_visit = Queue()
    urls_to_visit.put(START_URL)

    while not urls_to_visit.empty() and len(visited_urls) < n:
        current_url = urls_to_visit.get()
        if current_url in visited_urls:
            continue
        visited_urls.add(current_url)

        request = requests.get(current_url)
        if request.status_code == 200:
            text = request.text
            soup = BeautifulSoup(text, "html5lib")

            for link in soup.find_all("a", href=True):
                full_url = urljoin(current_url, link["href"])
                if full_url not in visited_urls:
                    if util.is_url_ok_to_follow(full_url, DOMAIN):
                        urls_to_visit.put(full_url)
                    else:
                        converted_url = util.convert_if_relative_url(
                            current_url, full_url
                        )
                        if converted_url:
                            urls_to_visit.put(converted_url)

            index, course_urls = build_index(index, course_urls, request, course_dict)

    with open("data/course_urls.csv", "w", newline="", encoding="utf-8") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["Course ID", "URL"])
        for id, url in course_urls.items():
            csvwriter.writerow([id, url])

    with open(output, "w", newline="", encoding="utf-8") as csvfile:
        csvwriter = csv.writer(csvfile, delimiter="|")
        csvwriter.writerow(["Course ID", "Word"])
        for id, words in index.items():
            for word in words:
                csvwriter.writerow([id, word])


go(5, "./data/test.json", "./data/test.csv")
