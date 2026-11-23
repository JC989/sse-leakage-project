import math
import random
from collections.abc import Hashable, Iterable, Mapping, Sequence


def reference_rates(reference_records: Sequence[Iterable[str]], candidates: Iterable[str]) -> dict[str, float]:
    """Fraction of reference records containing each candidate (each record counted once)."""
    if not reference_records:
        raise ValueError("reference_records must not be empty")

    record_sets = [set(record) for record in reference_records]
    total = len(record_sets)
    return {
        word: sum(word in record for record in record_sets) / total
        for word in candidates
    }


def closest_candidates(rate: float, ref_rates: Mapping[str, float]) -> list[str]:
    """All candidates whose reference rate is nearest to rate (more than one means a tie)."""
    if not ref_rates:
        raise ValueError("ref_rates must not be empty")

    distances = {word: abs(rate - ref) for word, ref in ref_rates.items()}
    best = min(distances.values())
    return sorted(
        word for word, d in distances.items() if math.isclose(d, best, abs_tol=1e-12)
    )


def guess_keywords(
    observed: Mapping[Hashable, int],
    n_private: int,
    reference_records: Sequence[Iterable[str]],
    candidates: Iterable[str],
    seed: int,
) -> tuple[dict[Hashable, str], int]:
    """Guess each token's keyword by closest occurrence rate; returns (guesses, tie_count)."""
    if n_private <= 0:
        raise ValueError("n_private must be positive")

    ref_rates = reference_rates(reference_records, candidates)
    rng = random.Random(seed)
    guesses, tie_count = {}, 0
    for token in sorted(observed):
        tied = closest_candidates(observed[token] / n_private, ref_rates)
        if len(tied) > 1:
            tie_count += 1
        guesses[token] = rng.choice(tied)
    return guesses, tie_count


def accuracy(guesses: Mapping[Hashable, str], truth: Mapping[Hashable, str]) -> float:
    """Evaluator: fraction of tokens in truth whose guess matches the true keyword."""
    if not truth:
        raise ValueError("truth must not be empty")
    return sum(guesses.get(token) == word for token, word in truth.items()) / len(truth)


def baseline_accuracy(n_candidates: int) -> float:
    """No-leakage baseline: a fixed guess is right 1/n of the time when each candidate is queried once."""
    if n_candidates <= 0:
        raise ValueError("n_candidates must be positive")
    return 1 / n_candidates
