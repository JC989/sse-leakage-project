import json, math, random
from collections import Counter

SETTINGS = {
    "vocab_size": 200,
    "tiers": [
        {"name": "common", "n_words": 10,  "tier_total": 0.7},
        {"name": "medium", "n_words": 50,  "tier_total": 0.2},
        {"name": "rare",   "n_words": 140, "tier_total": 0.1},
    ],
    "private": 500, 
    "reference": 500,
    "record_len_min": 5, "record_len_max": 15,
    "private_seed": 5320, "reference_seed": 3197,
}

with open("vocab.json") as f:
    src = json.load(f)
words = src["words"]; vocab_seed = src["metadata"]["vocab_seed"]
assert len(words) == len(set(words)) == SETTINGS["vocab_size"]
ranked = words[:]; random.Random(vocab_seed).shuffle(ranked)
vocab, probs, tier_of = [], [], {}
start = 0

for t in SETTINGS["tiers"]:
    tw = ranked[start:start+t["n_words"]]; start += t["n_words"]
    for w in tw:
        vocab.append(w); probs.append(t["tier_total"]/t["n_words"]); tier_of[w] = t["name"]

def sample_unique(rng, k):
    keys = [(math.log(1.0 - rng.random())/p, w) for w, p in zip(vocab, probs)]
    keys.sort(reverse=True)
    return [w for _, w in keys[:k]]

def generate_records(seed, n):
    rng = random.Random(seed); out = []
    for _ in range(n):
        k = rng.randint(SETTINGS["record_len_min"], SETTINGS["record_len_max"])
        out.append(sample_unique(rng, k))
    return out

private = generate_records(SETTINGS["private_seed"], SETTINGS["private"])
reference = generate_records(SETTINGS["reference_seed"], SETTINGS["reference"])

def dump(p, o): json.dump(o, open(p, "w"), indent=2)
dump("vocabulary.json", {"metadata":{"vocab_seed":vocab_seed,"settings":SETTINGS},
     "words":[{"word":w,"tier":tier_of[w],"prob":p} for w,p in zip(vocab,probs)]})
dump("private.json", {"metadata":{"dataset":"private","seed":SETTINGS["private_seed"],"vocab_seed":vocab_seed,"settings":SETTINGS},"records":private})
dump("reference.json", {"metadata":{"dataset":"reference","seed":SETTINGS["reference_seed"],"vocab_seed":vocab_seed,"settings":SETTINGS},"records":reference})
