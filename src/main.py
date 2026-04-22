from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import pandas as pd

from scraper import PasswordCorpusScraper
from preprocessor import PasswordPreprocessor
from keyword_extractor import PasswordKeywordExtractor
from evaluator import PasswordEvaluator


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Intelligent Password Estimator")
    parser.add_argument("--raw-input", type=str, default="data/raw/combined_password_corpus.csv")
    parser.add_argument("--processed-output", type=str, default="data/processed/clean_passwords.csv")
    parser.add_argument("--keywords-output", type=str, default="data/keywords/top_keywords.csv")
    parser.add_argument("--generated-output", type=str, default="data/processed/generated_passwords.csv")
    parser.add_argument("--chart-output", type=str, default="data/processed/accuracy_lift.png")
    parser.add_argument("--top-k-keywords", type=int, default=500)
    parser.add_argument("--total-generations", type=int, default=1000)
    return parser.parse_args()


def ensure_directories(*paths):
    for path in paths:
        Path(path).parent.mkdir(parents=True, exist_ok=True)


def fallback_generator(keywords, total_generations):
    generated = []
    for kw in keywords[:total_generations]:
        generated.append(f"{kw}123")
        generated.append(f"{kw}@2024")
        generated.append(f"{kw}!")
        generated.append(f"{kw}#1")
    return generated


def main() -> None:
    configure_logging()
    args = parse_args()

    raw_path = Path(args.raw_input)
    processed_path = Path(args.processed_output)
    keywords_path = Path(args.keywords_output)
    generated_path = Path(args.generated_output)
    chart_path = Path(args.chart_output)

    # Ensure folders exist
    ensure_directories(processed_path, keywords_path, generated_path, chart_path)

    # 1. Preprocessing
    preprocessor = PasswordPreprocessor()
    preprocessing_metrics = preprocessor.process_file(raw_path, processed_path)

    processed_df = pd.read_csv(processed_path)

    train_df, test_df = preprocessor.split_train_test(processed_df)

    # 2. Keyword Extraction
    extractor = PasswordKeywordExtractor(top_k=args.top_k_keywords)
    extractor.extract_from_file(processed_path, keywords_path)

    keywords_df = pd.read_csv(keywords_path)
    keywords = keywords_df.iloc[:, 0].astype(str).tolist()

    # 3. Password Generation (Fallback instead of GPT)
    generated_passwords = fallback_generator(keywords, args.total_generations)

    generated_df = pd.DataFrame({"password": generated_passwords})
    generated_df.to_csv(generated_path, index=False)

    # 4. Evaluation
    evaluator = PasswordEvaluator()
    evaluation_metrics = evaluator.evaluate(train_df, test_df, generated_df)
    evaluator.plot_metrics(evaluation_metrics, chart_path)

    # 5. Summary
    summary = {
        "preprocessing_metrics": preprocessing_metrics,
        "evaluation_metrics": evaluation_metrics,
        "processed_path": str(processed_path),
        "keywords_path": str(keywords_path),
        "generated_path": str(generated_path),
        "chart_path": str(chart_path),
    }

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()