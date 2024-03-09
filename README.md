# Course crawler

This repository contains the work of an assignment for the subject "Data analytics" in the "Pontificia Universidad Javeriana" institution.

## Description

This repository contains a collection of modules and SQL files designed for analyzing course catalogs from educational websites. The main focus is on crawling course catalog websites, extracting course information, and performing analyses based on them.

### Modules:

#### crawler.py

The `src/crawler.py` module provides the core functionality for crawling a specified website and extracting information about courses. It includes the following functions:

```python
def go(n: int, dictionary: str, output: str)
def build_index(index: dict, course_urls: dict, request, course_dict: dict)
def identify_common_words(course_blocks, threshold: int = 10)
```

The function `go()` crawls the specified website, extracts information about courses, builds an index mapping words to course IDs based on the course titles and descriptions, and saves the index to a CSV file. Additionally, it builds a dictionary mapping course IDs to URLs and saves it to another CSV file.

#### compare.py

The **`src/compare.py`** module offers a function to compare the similarities between two courses. The similarity between courses is determined based on the words they have in common. It includes the following function:

```python
def compare(course1, course2)
```

This function calculates a similarity score between two courses, indicating how similar they are based on their shared words, it returns a float with a value between 0 and 1.

##### How did the function calculate the similarities?

The function calculates the similarity score using the formula:

```python
intersection = len(words1.intersection(words2))
union = len(words1.union(words2))
similarity = (intersection / union) if union != 0 else 0
```

Where words1 and words2 represent sets of words that represents the two courses. The intersection variable counts the number of words that both courses have in common, while the union variable counts the total number of unique words in both courses. The similarity score is then calculated as the ratio of the intersection to the union, ensuring a value between 0 and 1. If the union is zero (indicating that both courses have no words), the similarity score is set to 0 to avoid division by zero errors.

#### search.py

The **`src/search.py`** module provides the functionality for searching relevant courses based on user-provided keywords. It includes a function to compare the similarities between courses and user interests, returning the URLs of courses that match those interests. The main function in this module is:

```python
def search(keywords: list, index: dict, course_urls: dict)
```

This function takes a list of user-provided keywords, an index mapping words to course IDs, and a dictionary mapping course IDs to URLs. It returns a list of URLs for courses relevant to the user's interests.

#### util.py

The util.py module contains utility functions used across different modules in the repository. It includes functions for handling URLs, extracting course titles and descriptions from HTML elements, and finding sequences within HTML content.

#### SQL Table and Queries

The repository also includes an SQL file **`sql/course.sql`** containing a table with the output of the crawler. Additionally, there is a SQL query provided for identifying the URL of a given word in the file **`sql/queries.sql`**.

## Requirements / Questions

##### Given the query of a word in the University courses, how to display the URLs in order of relevance?

The search functionality implemented in search.py fulfills the requirement to display URLs by relevance. It returns a list of course URLs sorted by relevance, which is determined based on the similarity between user-provided keywords and course descriptions and titles.

##### Define a similarity metric to compare two courses.

The `compare()` function in **`compare.py`** calculates the similarity between two courses. It assesses the shared words between courses, providing a quantitative measure of their similarity.

##### How do you define a measure of similarity between courses, and between courses and interests? Are they two different metrics? Can you use the same metric as the previous point?

The measure of similarity **between courses** is determined by assessing the overlap of words in their titles and descriptions. This is calculated by counting the number of words they have in common and dividing it by the total number of unique words between both courses. This approach provides a quantitative measure of how closely related the courses are based on their content.

When comparing courses to user interests, a similar approach is employed, but with a slight variation. Here, we calculate the similarity by counting the number of user-provided keywords that intersect with the words associated with the courses. The formula for this similarity calculation is as follows:

```python
similarity = len(keywords.intersection(words))
```

This formula counts the number of shared keywords between the user's interests and the course content, providing a measure of how relevant the course is to the user's preferences. While the underlying concept remains similar, the implementation differs slightly to accommodate the different contexts of comparison.

##### Which are the disadvantages of using the same metric, and how do you measure performance?

Using the same metric for comparing courses and user interests may lead to certain disadvantages. One such disadvantage is that the relevance of a course to a user's interests may not solely depend on the overlap of words between the course content and the user's interests. Other factors such as course level, topic coverage, and user preferences may also influence the relevance.

## Conclusions

Through the development of this project, the following objectives have been achieved:

- **Creation of a Web Crawler:** The crawler.py module facilitates the extraction of course information from a university's course catalog website. It traverses the website, collects data, and builds a simple index, making it easier to search and compare courses.

- **Construction of a Course Search Engine**: The project includes modules such as crawler.py, compare.py, and search.py, which collectively form a functional course search engine. This engine enables users to find relevant courses based on their interests by comparing keywords with the content of course descriptions and titles.

In summary, this project has successfully addressed the objectives outlined, providing practical experience in building search engines, web crawling, and data analysis within the context of educational course catalogs. These skills are valuable for various applications, including information retrieval, e-commerce, and academic research.
