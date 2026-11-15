"""Reference solutions for 1.03. Try the exercises yourself first!"""


def dedupe(items: list) -> list:
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def word_frequency(text: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for word in text.lower().split():
        counts[word] = counts.get(word, 0) + 1
    return counts


def invert_dict(d: dict) -> dict:
    return {value: key for key, value in d.items()}


def merge_inventories(a: dict[str, int], b: dict[str, int]) -> dict[str, int]:
    merged = dict(a)
    for item, qty in b.items():
        merged[item] = merged.get(item, 0) + qty
    return merged


def common_elements(a: list, b: list) -> list:
    return sorted(set(a) & set(b))


def group_by_first_letter(words: list[str]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    for word in words:
        groups.setdefault(word[0].lower(), []).append(word)
    return groups


def transpose(matrix: list[list]) -> list[list]:
    return [list(col) for col in zip(*matrix)]


def rotate_left(items: list, k: int) -> list:
    if not items:
        return []
    k %= len(items)
    return items[k:] + items[:k]


def flatten_once(nested: list[list]) -> list:
    return [item for inner in nested for item in inner]


def top_scorers(scores: dict[str, int], n: int) -> list[tuple[str, int]]:
    ranked = sorted(scores.items(), key=lambda pair: (-pair[1], pair[0]))
    return ranked[:n]
