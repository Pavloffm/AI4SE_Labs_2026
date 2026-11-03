"""Retrieve the nearest stored chunks for a JSON query embedding."""

import argparse
import json
import math
from pathlib import Path
import sqlite3


DATABASE = Path(__file__).resolve().parent.parent / "Task_3" / "chunk_embeddings.sqlite3"
DIMENSIONS = 384  # Task 3's hashed embedding size.


def match_embeddings(embedding, database=DATABASE, limit=5):
    """Return up to limit chunks ordered by descending cosine similarity."""
    if limit < 1:
        raise ValueError("top must be positive")
    if (not isinstance(embedding, list) or len(embedding) != DIMENSIONS
            or any(type(value) not in (int, float) or not math.isfinite(value)
                   for value in embedding)):
        raise ValueError(f"embedding must be a JSON array of {DIMENSIONS} finite numbers")
    norm = math.sqrt(sum(value * value for value in embedding))
    if not norm or not math.isfinite(norm):
        raise ValueError("embedding must have a finite, nonzero length")
    query = [value / norm for value in embedding]

    with sqlite3.connect(f"{Path(database).resolve().as_uri()}?mode=ro", uri=True) as connection:
        rows = connection.execute(
            "SELECT id, path, start_line, end_line, text, embedding FROM chunks"
        )
        results = []
        for chunk_id, path, start, end, text, stored in rows:
            vector = json.loads(stored)
            score = sum(a * b for a, b in zip(query, vector))
            results.append({"id": chunk_id, "path": path, "start_line": start,
                            "end_line": end, "text": text, "embedding": vector,
                            "score": score})

    return sorted(results, key=lambda item: (-item["score"], item["id"]))[:limit]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("embedding", type=argparse.FileType("r"),
                        help="JSON array file containing the task embedding (use - for stdin)")
    parser.add_argument("--top", type=int, default=5, help="number of chunks (default: 5)")
    parser.add_argument("--database", type=Path, default=DATABASE,
                        help="Task 3 SQLite database path")
    args = parser.parse_args()
    try:
        query = json.load(args.embedding)
        results = match_embeddings(query, args.database, args.top)
    except (ValueError, OSError, sqlite3.Error) as error:
        parser.error(str(error))
    print(json.dumps(results, ensure_ascii=False))


if __name__ == "__main__":
    main()
