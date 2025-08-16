import requests
import re
import json
from bs4 import BeautifulSoup
from dataclasses import dataclass
from datetime import datetime
from typing import Iterator
from functools import cache, cached_property


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


@dataclass(kw_only=True)
class Episode:
    """Episode dataclass."""

    title: str
    airdate: datetime
    episode_number: int
    season: int
    season_year: datetime
    url: str

    @cached_property
    def script(self) -> str:
        resp = requests.get(self.url, headers=HEADERS)
        soup = BeautifulSoup(resp.text, "html.parser")

        content_div = soup.find("div", id="content")

        return content_div.text


def build_episode_map() -> Iterator[Episode]:
    resp = requests.get(INDEX_URL, headers=HEADERS)

    soup = BeautifulSoup(resp.text, "html.parser")

    current_season = None
    season_year = None
    ep_counter = 0

    for row in soup.find_all("tr"):
        text = row.get_text(" ", strip=True)

        # Detect season header row
        if row.find("b") and ("Season" in text or "Pilot" in text):
            current_season = text
            # Extract just the season number if possible
            m = re.search(r"Season\s+(\d+)", text, re.IGNORECASE)
            if m:
                current_season = int(m.group(1))
            else:
                # Pilot gets treated as season 0
                current_season = 0

            # Extract year from header if present
            m2 = re.search(r"\((\d{4})\)", text)
            season_year = datetime.strptime(m2.group(1), "%Y") if m2 else None
            continue

        # Regular episode rows
        cells = row.find_all("td")
        if len(cells) >= 2 and cells[0].get_text(strip=True).isdigit():
            ep_counter += 1

            ep_num = int(cells[0].get_text(strip=True))
            a = cells[1].find("a")
            title = a.get_text(strip=True) if a else cells[1].get_text(strip=True)
            href = BASE_URL + a["href"].strip() if a else None

            # Match airdate like (7/5/89)
            date_match = re.search(r"\((\d{1,2}/\d{1,2}/\d{2})\)", cells[1].get_text())
            airdate = (
                datetime.strptime(date_match.group(1), "%m/%d/%y")
                if date_match
                else None
            )

            episode = Episode(
                title=title,
                airdate=airdate,
                episode_number=ep_num,
                season=current_season,
                season_year=season_year,
                url=href,
            )

            yield episode


lines = []


with open("example.txt", "r") as f:
    raw_data = f.read()


pattern = r"(?:^|\n)([A-Za-z]+:)(.*?)(?=(?:\n[A-Za-z]+:)|\Z)"
matches = re.findall(pattern, raw_data, flags=re.DOTALL)

for speaker, text in matches:
    text = re.sub(r"\[[^\]]*\]", "", text)
    lines.append({"speaker": speaker.removesuffix(":"), "line": text})

print(lines[:10])
with open("parsed_lines.json", "w") as f:
    json.dump(lines, f, indent=4)
# TODO: Tokenize this guy
