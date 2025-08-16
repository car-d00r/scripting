import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.seinfeldscripts.com/"
INDEX_URL = BASE_URL + "seinfeld-scripts.html"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


resp = requests.get(INDEX_URL, headers=HEADERS)

soup = BeautifulSoup(resp.text, "html.parser")


for table in soup.find_all("table", attrs={"border": "1"}):
    print(table)