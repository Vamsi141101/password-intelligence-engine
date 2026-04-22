from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Dict, Tuple

import pandas as pd

LOGGER = logging.getLogger(__name__)

VALID_PATTERN = re.compile(r"^[ -~]+$")


class PasswordPreprocessor:
    def __init__(self, min_len: int = 4, max_len: int = 32, lowercase: bool = True) -> None:
        self.min_len = min_len
        self.max_len = max_len
        self.lowercase = lowercase

    def _normalize(self, value: str) -> str:
        value = str(value).strip()
        if self.lowercase:
            value = value.lower()
        return value

    def clean_dataframe(self, df: pd.DataFrame, password_col: str = "password") -> pd.DataFrame:
        work = df.copy()
        work[password_col] = work[password_col].astype(str).map(self._normalize)
        before = len(work)

        work = work.dropna(subset=[password_col])
        work = work[work[password_col].str.len().between(self.min_len, self.max_len)]
        work = work[work[password_col].map(lambda x: bool(VALID_PATTERN.match(x)))]
        work = work.drop_duplicates(subset=[password_col]).reset_index(drop=True)

        LOGGER.info("Preprocessed passwords from %d to %d rows", before, len(work))
        return work

    def split_train_test(
        self,
        df: pd.DataFrame,
        test_size: float = 0.2,
        random_state: int = 42,
        password_col: str = "password",
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        df = df.sample(frac=1.0, random_state=random_state).reset_index(drop=True)
        split = int(len(df) * (1 - test_size))
        return df.iloc[:split].copy(), df.iloc[split:].copy()

    def preprocessing_metrics(
        self,
        raw_df: pd.DataFrame,
        clean_df: pd.DataFrame,
        password_col: str = "password",
    ) -> Dict[str, float]:
        raw_unique = raw_df[password_col].astype(str).nunique()
        clean_unique = clean_df[password_col].astype(str).nunique()

        raw_guessable_share = raw_df[password_col].astype(str).str.len().between(self.min_len, self.max_len).mean()
        clean_guessable_share = clean_df[password_col].astype(str).str.len().between(self.min_len, self.max_len).mean()

        improvement_pct = ((clean_guessable_share - raw_guessable_share) / max(raw_guessable_share, 1e-9)) * 100

        return {
            "raw_rows": float(len(raw_df)),
            "clean_rows": float(len(clean_df)),
            "raw_unique": float(raw_unique),
            "clean_unique": float(clean_unique),
            "raw_guessable_share": float(raw_guessable_share),
            "clean_guessable_share": float(clean_guessable_share),
            "preprocessing_improvement_pct": float(improvement_pct),
        }

    def process_file(self, input_path: str | Path, output_path: str | Path, password_col: str = "password") -> dict:
        input_path = Path(input_path)
        output_path = Path(output_path)

        df = pd.read_parquet(input_path) if input_path.suffix == ".parquet" else pd.read_csv(input_path)
        clean_df = self.clean_dataframe(df, password_col=password_col)

        if output_path.suffix == ".parquet":
            clean_df.to_parquet(output_path, index=False)
        else:
            clean_df.to_csv(output_path, index=False)

        metrics = self.preprocessing_metrics(df, clean_df, password_col=password_col)
        LOGGER.info("Saved processed data to %s", output_path)
        return metrics
