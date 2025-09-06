import requests
import re
from bs4 import BeautifulSoup
from dataclasses import dataclass
from datetime import datetime
from typing import Iterator, Dict, List, Any
from functools import cached_property
import pandas as pd
from pathlib import Path


BAD_SPEAKERS = ["and", "with", "cast", "any", "also"]
KNOWN_SPEAKER_SWAPS = {
    "gx": "george",
    "geoprge": "george",
    "geoge": "george",
    "geroge": "george",
    "georgge": "george",
    "jery": "jerry",
    "krame": "kramer",
    "kramert": "kramer",
    "krmaer": "kramer",
    "nx": "neuman",
    "yyy": "barbara",
    "fa": "flight attendant",
    "jx": "jerry",
    "wx": "waiter",
    "mm": "morgan",
    "xx": "brady",
    "dx": "doctor",
    "fd": "patrice",
    "js": "jerry",
}
BASE_URL = "https://www.seinfeldscripts.com/"
INDEX_URL = BASE_URL + "seinfeld-scripts.html"
LINES_PATTERN = r"(?:^|\n)([A-Z][a-zA-Z]+:)(.*?)(?=(?:\n[A-Za-z]+:)|\Z)"
TOKEN_PATTERN = r"\b\w+'?\w*\b"
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

    @cached_property
    def line_tokens(self) -> List[Dict[str, Any]]:
        lines = []
        matches = re.findall(LINES_PATTERN, self.script, flags=re.DOTALL)

        for speaker, text in matches:
            clean_speaker = speaker.removesuffix(":").lower()
            text = re.sub(r"\[[^\]]*\]", "", text)
            tokens = re.findall(TOKEN_PATTERN, text.lower())
            if clean_speaker in BAD_SPEAKERS:
                continue
            if clean_speaker in KNOWN_SPEAKER_SWAPS:
                clean_speaker = KNOWN_SPEAKER_SWAPS[clean_speaker]
            lines.append({"speaker": clean_speaker, "tokens": tokens})
        return lines


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


def load_episodes(expected_path: Path | str) -> pd.DataFrame:
    expected_path = Path(expected_path)
    if expected_path.exists():
        return pd.read_parquet(expected_path)
    else:
        episodes = build_episode_map()
        episode_dfs = []
        for episode in episodes:
            rows = []
            for line in episode.line_tokens:
                row = {
                    "title": episode.title,
                    "airdate": episode.airdate,
                    "episode_number": episode.episode_number,
                    "season": episode.season,
                    "season_year": episode.season_year,
                    "url": episode.url,
                    "speaker": line["speaker"],
                    "tokens": line["tokens"],
                }
                rows.append(row)
            episode_dfs.append(pd.DataFrame(rows))
        df = pd.concat(episode_dfs)
        df.to_parquet(
            expected_path, index=False
        )  # Let pandas choose the backend       return lines
        return df
