from __future__ import annotations

import io
import logging
from pathlib import Path
from typing import Iterable, List, Optional

import pandas as pd
import requests
from bs4 import BeautifulSoup

LOGGER = logging.getLogger(__name__)


class PasswordCorpusScraper:
    """Downloads legal, public password corpora or password frequency lists.

    This module intentionally supports only openly published datasets intended for
    research, benchmarking, or password-strength testing. It avoids any workflow
    involving unauthorized leaked credentials handling beyond legal public corpora.
    """

    def __init__(self, output_dir: str | Path) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def download_csv(self, url: str, filename: str, password_column: str = "password") -> Path:
        response = requests.get(url, timeout=60)
        response.raise_for_status()

        out_path = self.output_dir / filename
        out_path.write_bytes(response.content)

        LOGGER.info("Downloaded dataset to %s", out_path)
        return out_path

    def scrape_passwords_from_html(self, url: str, css_selector: Optional[str] = None) -> List[str]:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        if css_selector:
            nodes = soup.select(css_selector)
            values = [node.get_text(strip=True) for node in nodes if node.get_text(strip=True)]
        else:
            values = [line.strip() for line in soup.get_text("\n").splitlines() if line.strip()]

        LOGGER.info("Scraped %d candidate text rows from %s", len(values), url)
        return values

    def save_password_list(self, passwords: Iterable[str], filename: str) -> Path:
        out_path = self.output_dir / filename
        df = pd.DataFrame({"password": list(passwords)})
        if out_path.suffix == ".parquet":
            df.to_parquet(out_path, index=False)
        else:
            df.to_csv(out_path, index=False)
        LOGGER.info("Saved %d passwords to %s", len(df), out_path)
        return out_path

    def build_combined_corpus(
        self,
        input_files: list[str | Path],
        output_filename: str = "combined_password_corpus.parquet",
        password_column: str = "password",
    ) -> Path:
        frames = []
        for file_path in input_files:
            path = Path(file_path)
            if path.suffix == ".parquet":
                df = pd.read_parquet(path)
            else:
                df = pd.read_csv(path)
            if password_column not in df.columns:
                raise ValueError(f"Missing '{password_column}' in {path}")
            frames.append(df[[password_column]].rename(columns={password_column: "password"}))

        combined = pd.concat(frames, ignore_index=True)
        out_path = self.output_dir / output_filename
        combined.to_parquet(out_path, index=False)
        LOGGER.info("Built combined corpus with %d rows at %s", len(combined), out_path)
        return out_path
