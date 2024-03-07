from requests import get_request, read_request

# Info on beautifulsoup4 lib: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from . import Queue
from . import util
import json
import csv


# Initial URL
START_URL = "https://educacionvirtual.javeriana.edu.co/nuestros-programas-nuevo"
DOMAIN = "educacionvirtual.javeriana.edu.co"


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

    visited = set()
    queue = Queue()
    queue.put(START_URL)

    index = {}  # Word -> List of course IDs

    while not queue.empty() and len(visited) < n:
        current_url = queue.get()
        if current_url in visited:
            continue
        visited.add(current_url)

        # HTTP request to url
        request = get_request(current_url)
        if request:
            text = read_request(request)
            soup = BeautifulSoup(text, "html5lib")

            for link in soup.find_all("a", href=True):
                full_url = urljoin(current_url, link["href"])
                if (
                    util.is_url_ok_to_follow(full_url, DOMAIN)
                    and full_url not in visited
                ):
                    queue.put(full_url)
            # Extract course titles and descriptions
            for div in soup.find_all("div", class_="col"):
                course_title = div.find("b", class_="card-title").text.strip()
                if course_title:
                    words = course_title.split()
                    for desc in div.find_all("p", class_="card-text"):
                        description = desc.text.strip()
                        words += description.split()
                    for word in words:
                        word = word.lower()
                        if word not in index:
                            index[word] = []
                        # Add course ID to word
                        index[word].append(
                            course_dict.get(course_title, "ID not found")
                        )

    # Write index to a CSV file
    with open(output, "w", newline="", encoding="utf-8") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["Word", "Course IDs"])
        for word, ids in index.items():
            csvwriter.writerow([word, ", ".join(map(str, ids))])


# ---- EXAMPLE ----
# <div class="col">
# <div class="card-body">
# <a href="/errores-innatos-metabolismo" target="_blank">
# <b class="card-title text-primary font-weight-bold">Errores innatos del
# metabolismo de molécula pequeña</b> </a>
# <p class="card-text mt-2 mb-0"><small class="text-muted"><i class="fas fa-clock
# iconnn" aria-hidden="true"></i>
# <b>Duración: </b>116 Horas</small></p>
# <p class="card-text mb-0"><small class="text-muted">
# <i class="fas fa-list-alt iconnn" aria-hidden="true"></i>
# <b> Nivel: </b> Intermedio</small></p>
# <p class="card-text mb-0"><small class="text-muted">
# <i class="fas fa-calendar-alt iconnn" aria-hidden="true"></i>
# <b> Fecha de inicio:
# </b>Próximamente</small>
# </p>
# <p class="card-text"><small class="text-muted">
# <i class="fas fa-coins iconnn" aria-hidden="true"></i>
# <b> Precio: </b> $ 3.190.000</small>
# </p>
# </div>
