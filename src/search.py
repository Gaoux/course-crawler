"""
Course Search System

This module provides functionality for searching relevant courses based on user-provided keywords.
It includes a method to determine the similarity between courses and user interests and implements
a relevance measure to list the most relevant courses first.

Typical usage example:

    # Define the keywords, index, and course URLs.
    keywords = ["luminosidad", "enfoque", "composición"]
    index = {...}  # Dictionary containing the index of courses.
    course_urls = {...}  # Dictionary containing course IDs mapped to URLs.

    # Search for relevant courses.
    relevant_courses = search(keywords, index, course_urls)
    print(relevant_courses)  # Output list of relevant course URLs.

"""


def search(keywords: list, index: dict, course_urls: dict):
    """Searches for relevant courses based on user-provided keywords.

    Args:
        keywords (list): List of user-provided keywords of interest.
        index (dict): Dictionary containing the index of courses.
        course_urls (dict): Dictionary containing course IDs mapped to their URLs.

    Returns:
        list: List of course URLs ordered by relevance.
    """

    keywords = set(keyword.lower() for keyword in keywords)

    similarity_scores = []
    for course_id, words in index.items():
        similarity = len(keywords.intersection(words))
        if similarity > 0:
            similarity_scores.append((course_id, similarity))

    similarity_scores.sort(reverse=True, key=lambda x: x[1])

    relevant_courses = [course_urls[course_id] for course_id, _ in similarity_scores]

    return relevant_courses
