from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, Iterable

import matplotlib.pyplot as plt
import pandas as pd

LOGGER = logging.getLogger(__name__)


class PasswordEvaluator:
    @staticmethod
    def _coverage(test_passwords: pd.Series, guesses: list[str], k: int) -> float:
        guess_set = set(guesses[:k])
        matched = test_passwords.astype(str).isin(guess_set).mean()
        return float(matched)

    def evaluate(
        self,
        train_df: pd.DataFrame,
        test_df: pd.DataFrame,
        generated_df: pd.DataFrame,
        password_col: str = "password",
    ) -> Dict[str, float]:
        baseline_guesses = (
            train_df[password_col].value_counts().index.astype(str).tolist()
        )
        generated_guesses = (
            pd.concat(
                [
                    pd.Series(baseline_guesses, name=password_col),
                    generated_df[password_col].astype(str),
                ],
                ignore_index=True,
            )
            .drop_duplicates()
            .tolist()
        )

        ks = [1000, 10000, 100000]
        metrics = {}
        for k in ks:
            base = self._coverage(test_df[password_col], baseline_guesses, k)
            enhanced = self._coverage(test_df[password_col], generated_guesses, k)
            lift = ((enhanced - base) / max(base, 1e-9)) * 100
            metrics[f"baseline_top_{k}"] = base
            metrics[f"enhanced_top_{k}"] = enhanced
            metrics[f"lift_top_{k}_pct"] = lift
        return metrics

    def plot_metrics(self, metrics: Dict[str, float], output_path: str | Path) -> Path:
        output_path = Path(output_path)
        ks = ["1000", "10000", "100000"]
        baseline = [metrics[f"baseline_top_{k}"] for k in ks]
        enhanced = [metrics[f"enhanced_top_{k}"] for k in ks]

        plt.figure(figsize=(10, 6))
        x = range(len(ks))
        width = 0.35
        plt.bar([i - width / 2 for i in x], baseline, width=width, label="Baseline")
        plt.bar([i + width / 2 for i in x], enhanced, width=width, label="Enhanced")
        plt.xticks(list(x), [f"Top-{k}" for k in ks])
        plt.ylabel("Coverage")
        plt.title("Password Guess Coverage Lift")
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
        LOGGER.info("Saved evaluation plot to %s", output_path)
        return output_path
