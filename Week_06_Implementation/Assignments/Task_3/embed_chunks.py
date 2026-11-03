"""Index Task 2 chunks as hashed embeddings and search them by cosine similarity."""

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re
import sqlite3


HERE = Path(__file__).resolve().parent
CHUNKS = HERE.parent / "Task_2" / "chunks.jsonl"
DATABASE = HERE / "chunk_embeddings.sqlite3"
DIMENSIONS = 384
TOKEN = re.compile(r"[A-Za-z_][A-Za-z_0-9]*|[0-9]+")
PART = re.compile(r"[A-Z]+(?=[A-Z][a-z]|\b)|[A-Z]?[a-z]+|[A-Z]+|[0-9]+")


def embed_chunk(text):
    """Return a unit-length, deterministic hashed term-frequency vector."""
    terms = []
    for match in TOKEN.finditer(text):
        word = match.group()
        terms.append(word.lower())
        parts = [part.lower() for part in PART.findall(word.replace("_", " "))]
        if len(parts) > 1:
            terms.extend(parts)

    vector = [0.0] * DIMENSIONS
    for term, count in Counter(terms).items():
        hashed = int.from_bytes(hashlib.blake2b(term.encode(), digest_size=8).digest())
        vector[hashed % DIMENSIONS] += (1 if hashed & (1 << 63) else -1) * (1 + math.log(count))

    norm = math.sqrt(sum(value * value for value in vector))
    return [value / norm for value in vector] if norm else vector


def index_chunks(source=CHUNKS, database=DATABASE):
    with sqlite3.connect(database) as connection:
        connection.execute("""CREATE TABLE IF NOT EXISTS chunks (
            id TEXT PRIMARY KEY, path TEXT NOT NULL, start_line INTEGER NOT NULL,
            end_line INTEGER NOT NULL, text TEXT NOT NULL, embedding TEXT NOT NULL
        )""")
        connection.execute("DELETE FROM chunks")
        count = 0
        with open(source, encoding="utf-8") as chunks:
            for line in chunks:
                chunk = json.loads(line)
                # Path and content are both useful for locating code by name or behavior.
                vector = embed_chunk(chunk["path"] + "\n" + chunk["text"])
                connection.execute(
                    "INSERT INTO chunks VALUES (?, ?, ?, ?, ?, ?)",
                    (chunk["id"], chunk["path"], chunk["start_line"],
                     chunk["end_line"], chunk["text"], json.dumps(vector)),
                )
                count += 1
    return count


def search(query, database=DATABASE, limit=5):
    vector = embed_chunk(query)
    with sqlite3.connect(database) as connection:
        rows = connection.execute(
            "SELECT id, path, start_line, end_line, embedding FROM chunks"
        ).fetchall()
    results = []
    for chunk_id, path, start, end, stored in rows:
        score = sum(a * b for a, b in zip(vector, json.loads(stored)))
        results.append((score, chunk_id, path, start, end))
    return sorted(results, key=lambda item: (-item[0], item[1]))[:limit]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("index", help="Rebuild the SQLite store from Task 2 chunks")
    embed = commands.add_parser("embed", help="Print a text chunk's embedding as JSON")
    embed.add_argument("text")
    find = commands.add_parser("search", help="Find similar repository chunks")
    find.add_argument("query")
    find.add_argument("--top", type=int, default=5)
    args = parser.parse_args()

    if args.command == "index":
        print(f"Indexed {index_chunks()} chunks in {DATABASE}")
    elif args.command == "embed":
        print(json.dumps(embed_chunk(args.text)))
    else:
        if args.top < 1:
            parser.error("--top must be positive")
        for score, chunk_id, path, start, end in search(args.query, limit=args.top):
            print(f"{score:.3f}  {chunk_id}")


if __name__ == "__main__":
    main()
