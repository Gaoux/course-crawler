"""Compare courses and calculate similarity based on common words.

This module provides functionality to compare courses and calculate the similarity
between them based on the words they have in common. It loads the course index from
a CSV file and defines a function to compare two courses and calculate their similarity.

Functions:
    compare_courses(course1, course2, index):
        Compare two courses and calculate similarity based on common words.

Typical usage example:

    index = util.load_index("course_index.csv")
    similarity = compare_courses("C001", "C002", index)
    print(f"Similarity between courses: {similarity}")

"""

import util


def compare_courses(course1: str, course2: str, index: dict):
    """Compare two courses and calculate similarity based on common words.

    Args:
        course1 (str): ID of the first course.
        course2 (str): ID of the second course.
        index (dict): Course index dictionary mapping course IDs to lists of words.

    Returns:
        float: Similarity score between 0 and 1.
    """
    words1 = set(index.get(course1, []))
    words2 = set(index.get(course2, []))

    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))

    similarity = (intersection / union) if union != 0 else 0
    return similarity
