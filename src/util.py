"""Utility Functions for Web Scraping.

This module provides various utility functions for web scraping tasks,
including checking URL properties, extracting information from BeautifulSoup
elements, and manipulating URLs.

Functions:
- is_absolute_url(url): Checks if a URL is absolute.
- convert_if_relative_url(url1, url2): Converts a relative URL to an absolute URL if necessary.
- remove_fragment(url): Removes the fragment part from the URL.
- is_url_ok_to_follow(url, domain): Checks if a URL is suitable for following based on specified criteria.
- find_sequence(tag): Finds sub-sequences associated with a BeautifulSoup tag.
- extract_course_title(block, tag, class_): Extracts the title of a course from a BeautifulSoup element representing a course block.
- extract_course_description(block, tag, class_): Extracts the description of a course from a BeautifulSoup element representing a course block.
- load_index(csv_file): Load course index from a CSV file.
"""

from urllib.parse import urlparse, urljoin
import csv


def is_absolute_url(url):
    """Checks if a URL is absolute.

    Args:
        url (str): The URL to check.

    Returns:
        bool: True if the URL is absolute, False otherwise.
    """
    return bool(urlparse(url).netloc)


def convert_if_relative_url(url1, url2):
    """Converts a relative URL to an absolute URL if necessary.

    Args:
        url1 (str): The base URL of the page.
        url2 (str): The URL found on the page.

    Returns:
        str or None: The absolute URL if url2 is relative and can be converted, None otherwise.
    """
    if not is_absolute_url(url2):
        return urljoin(url1, url2)
    return


def remove_fragment(url):
    """Removes the fragment part (the portion after the '#' symbol) from the URL.

    Args:
        url (str): The URL to remove the fragment from.

    Returns:
        str: The URL without the fragment part.
    """
    return url.split("#")[0]


def is_url_ok_to_follow(url, domain):
    """Checks if a URL is suitable for following based on specified criteria.

    Args:
        url (str): The URL to check.
        domain (str): The specified domain to check against.

    Returns:
        bool: True if the URL meets the criteria, False otherwise.
    """

    if not url.startswith("http"):
        return False

    parsed_url = urlparse(url)

    if parsed_url.netloc != domain:
        return False

    if "@" in url or "mailto:" in url:
        return False

    path = parsed_url.path
    if path.endswith("/") or path.endswith(".html"):
        return True

    if "." not in path.split("/")[-1]:
        return True

    return False


def find_sequence(tag):
    """Find sub-sequences associated with a BeautifulSoup tag.

    Args:
        tag (bs4.element.Tag): BeautifulSoup tag.

    Returns:
        list: List of BeautifulSoup objects for the sub-sequences, or an empty list if no sub-sequences are found.
    """
    sub_sequences = tag.find_all("div")

    return sub_sequences


def extract_course_title(block, tag: str = "b", class_: str = "card-title"):
    """Extracts the title of a course from a BeautifulSoup element representing a course block.

    Args:
        block (bs4.element.Tag): BeautifulSoup element representing a course block.
        tag (str, optional): The HTML tag used to identify the title element. Defaults to "b".
        class_ (str, optional): The CSS class used to identify the title element. Defaults to "card-title".

    Returns:
        str: The title of the course.
    """

    course_title_element = block.find(tag, class_=class_)

    if course_title_element:
        course_title = course_title_element.text.strip()
    else:
        course_title = ""

    return course_title


def extract_course_description(block, tag: str = "p", class_: str = "card-text"):
    """Extracts the description of a course from a BeautifulSoup element representing a course block.

    Args:
        block (bs4.element.Tag): BeautifulSoup element representing a course block.
        tag (str, optional): The HTML tag used to identify the description elements. Defaults to "p".
        class_ (str, optional): The CSS class used to identify the description elements. Defaults to "card-text".

    Returns:
        str: The description of the course.
    """

    description_elements = block.find_all(tag, class_=class_)

    if description_elements:
        description = " ".join([p.text.strip() for p in description_elements])
    else:
        description = ""

    return description


def load_index(csv_file: str):
    """Load course index from a CSV file.

    Args:
        csv_file (str): Path to the CSV file containing the course index.

    Returns:
        dict: Course index dictionary mapping course IDs to lists of words.
    """
    index = {}
    with open(csv_file, "r", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter="|")
        next(reader)
        for row in reader:
            course_id, word = row
            if course_id not in index:
                index[course_id] = []
            index[course_id].append(word)
    return index
