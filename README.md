# Intelligent Password Estimator

A production-oriented Python pipeline for defensive password-strength research using public password corpora. The project ingests a large legal password list, cleans and normalizes it, extracts salient keywords using YAKE!, generates additional password candidates with OpenAI GPT-style completions, and evaluates top-k candidate coverage lift against a held-out test set.

## Ethical use

This repository is for authorized security research, password auditing in controlled environments, and password strength evaluation only. Do not use it against accounts, systems, or data without explicit permission.

## Project structure

```text
Intelligent-Password-Estimator/
├── data/
│   ├── raw/
│   ├── processed/
│   └── keywords/
├── src/
│   ├── scraper.py
│   ├── preprocessor.py
│   ├── keyword_extractor.py
│   ├── gpt_password_generator.py
│   ├── evaluator.py
│   └── main.py
├── notebooks/
│   └── exploratory_analysis.ipynb
├── requirements.txt
├── .env.example
├── README.md
└── LICENSE
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Usage

1. Put a legal public password corpus into `data/raw/combined_password_corpus.parquet`
2. Set `OPENAI_API_KEY` in `.env`
3. Run:

```bash
cd src
python main.py --raw-input ../data/raw/combined_password_corpus.parquet
```

## Suggested research workflow

- Download public benchmark corpora or frequency lists.
- Clean passwords to remove noise and invalid rows.
- Extract up to 15,000 keywords with YAKE!.
- Generate new candidate passwords from keyword batches.
- Evaluate baseline top-k coverage vs enhanced candidate coverage.

## Results reporting

Expected outcomes depend heavily on the chosen corpus and split strategy. In practice, preprocessing often improves effective candidate coverage by removing malformed or low-value rows, while generated candidates may improve held-out coverage further when the corpus contains reusable motifs. Report:
- Top-1000 coverage
- Top-10k coverage
- Top-100k coverage
- Relative lift percentages

## Timeline

- Data acquisition
- Preprocessing and quality checks
- Keyword extraction
- Candidate generation
- Evaluation and visualization

## Notes

`text-davinci-003` is included to match the requested dependency. For modern OpenAI deployments, adapting the generator to current completion or chat APIs may be necessary depending on account availability.
