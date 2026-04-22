from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd
import yake

LOGGER = logging.getLogger(__name__)


class PasswordKeywordExtractor:
    def __init__(
        self,
        top_k: int = 15000,
        language: str = "en",
        max_ngram_size: int = 2,
        deduplication_threshold: float = 0.9,
    ) -> None:
        self.top_k = top_k
        self.language = language
        self.max_ngram_size = max_ngram_size
        self.deduplication_threshold = deduplication_threshold

    def extract(self, df: pd.DataFrame, password_col: str = "password") -> pd.DataFrame:
        text_blob = " ".join(df[password_col].astype(str).tolist())
        extractor = yake.KeywordExtractor(
            lan=self.language,
            n=self.max_ngram_size,
            dedupLim=self.deduplication_threshold,
            top=self.top_k,
        )
        keywords = extractor.extract_keywords(text_blob)
        out = pd.DataFrame(keywords, columns=["keyword", "score"]).sort_values("score", ascending=True)
        LOGGER.info("Extracted %d keywords", len(out))
        return out

    def extract_from_file(self, input_path: str | Path, output_path: str | Path, password_col: str = "password") -> Path:
        input_path = Path(input_path)
        output_path = Path(output_path)

        df = pd.read_parquet(input_path) if input_path.suffix == ".parquet" else pd.read_csv(input_path)
        keywords_df = self.extract(df, password_col=password_col)

        if output_path.suffix == ".parquet":
            keywords_df.to_parquet(output_path, index=False)
        else:
            keywords_df.to_csv(output_path, index=False)

        LOGGER.info("Saved keywords to %s", output_path)
        return output_path
