import argparse
import json
from pathlib import Path

from sseleak.attack import accuracy, baseline_accuracy, guess_keywords
from sseleak.crypto import derive_keys, generate_master_key


def load_json(path):
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def run_attack(observed, reference_records, keywords, n_private, truth, seed):
    guesses, tie_count = guess_keywords(observed, n_private, reference_records, keywords, seed)
    return accuracy(guesses, truth), baseline_accuracy(len(keywords)), tie_count


def main():
    parser = argparse.ArgumentParser(description="Run the encrypted search experiment.")
    parser.add_argument("--data-dir", type=Path, required=True, help="Folder containing private.json, reference.json, and vocabulary.json")
    args = parser.parse_args()

    try:
        private_data = load_json(args.data_dir / "private.json")
        reference_data = load_json(args.data_dir / "reference.json")
        vocabulary_data = load_json(args.data_dir / "vocabulary.json")
    except FileNotFoundError as error:
        parser.error(f"Missing data file: {error.filename}. Run the data generator first.")

    private_records = private_data["records"]
    reference_records = reference_data["records"]
    keywords = [entry["word"] for entry in vocabulary_data["words"]]

    keys = derive_keys(generate_master_key())

    print(f"Private records: {len(private_records)}")
    print(f"Reference records: {len(reference_records)}")
    print(f"Candidate keywords: {len(keywords)}")
    print("Client keys created.")

    print("Search observations unavailable: encrypted search is not implemented, so the attack was not run.")


if __name__ == "__main__":
    main()
