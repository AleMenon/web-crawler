import requests

from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urldefrag, urlsplit, urlunsplit
from requests.exceptions import RequestException

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    )
}

def normalize(url):
    parts = urlsplit(url)
    path = parts.path.rstrip("/") or "/"
    return urlunsplit((parts.scheme, parts.netloc, path, "", ""))

def make_session(workers):
    session = requests.Session()
    session.headers.update(HEADERS)
    retry = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=workers, pool_maxsize=workers)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

def _extract_links(html, page_url):
    soup = BeautifulSoup(html, "lxml")
    links = set()
    for tag in soup.find_all("a", href=True):
        full_url, _ = urldefrag(urljoin(page_url, str(tag["href"])))
        if full_url.startswith(("http://", "https://")):
            links.add(full_url)
    return sorted(links)

def fetch(session, url):
    try:
        response = session.get(url, timeout=15)
    except RequestException as e:
        return url, None, None, None, str(e)

    content_type = response.headers.get("Content-Type", "")
    if response.status_code != 200 or "text/html" not in content_type:
        return url, response.status_code, None, [], None

    html = response.text
    return url, 200, html, _extract_links(html, url), None
