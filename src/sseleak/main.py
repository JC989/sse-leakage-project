import argparse
import json
import random
from pathlib import Path

from sseleak.attack import accuracy, baseline_accuracy, guess_keywords
from sseleak.search import SearchClient, lookup


def load_json(path):
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def run_attack(observed, reference_records, keywords, n_private, truth, seed):
    guesses, tie_count = guess_keywords(observed, n_private, reference_records, keywords, seed)
    return accuracy(guesses, truth), baseline_accuracy(len(keywords)), tie_count


def main():
    parser = argparse.ArgumentParser(description="Run the encrypted search experiment.")
    parser.add_argument("--data-dir", type=Path, required=True, help="Folder containing private.json, reference.json, and vocabulary.json")
    parser.add_argument("--query-seed", type=int, default=0, help="Seed that fixes the order of queries")
    parser.add_argument("--attack-seed", type=int, default=0, help="Seed for breaking ties between equally close guesses")
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

    client = SearchClient()

    print(f"Private records: {len(private_records)}")
    print(f"Reference records: {len(reference_records)}")
    print(f"Candidate keywords: {len(keywords)}")
    print("Client keys created.")

    index = client.build_index(private_records)
    queries = keywords[:]
    random.Random(args.query_seed).shuffle(queries)

    # Stable query IDs replace key-dependent token bytes; a repeated token keeps its first ID.
    query_ids, observed, truth = {}, {}, {}
    for keyword in queries:
        token = client.make_token(keyword)
        query_id = query_ids.setdefault(token, len(query_ids))
        observed[query_id] = len(lookup(index, token))
        truth[query_id] = keyword

    result, baseline, tie_count = run_attack(observed, reference_records, keywords, len(private_records), truth, args.attack_seed)
    print(f"Query seed: {args.query_seed}, attack seed: {args.attack_seed}, queries: {len(queries)}, distinct tokens: {len(observed)}")
    print(f"Attack accuracy: {result:.3f} (baseline {baseline:.3f}, ties {tie_count})")


if __name__ == "__main__":
    main()
