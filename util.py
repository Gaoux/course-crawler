from urllib.parse import urlparse, urljoin


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
    # Check if the URL is absolute
    if not url.startswith("http"):
        return False

    # Parse the URL
    parsed_url = urlparse(url)

    # Check if the domain matches the specified domain
    if parsed_url.netloc != domain:
        return False

    # Check if the URL contains "@" or "mailto:"
    if "@" in url or "mailto:" in url:
        return False

    # Check if the URL ends with an extension or "html"
    path = parsed_url.path
    if path.endswith("/") or path.endswith(".html"):
        return True

    # Check if the URL ends with a file name without an extension
    if "." not in path.split("/")[-1]:
        return True

    return False
